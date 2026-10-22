#!/usr/bin/env python3
"""Monte Carlo + ranking engine for the KR equity multi-agent report.

Inputs (JSON):
  trees.json   : per-stock scenario trees (from WF2 synthesizers, after WF3 adjustments)
  risk.json    : per-stock risk parameters (annual vol estimates, confidence)
  macro.json   : risk-free rates (1y/3y/5y), index expected returns per horizon

Outputs:
  results.json : per stock/horizon statistics + rankings
  tables.md    : markdown tables ready to paste into the report
"""
import json, math, sys, os
import numpy as np

HORIZONS = {'1y': 1.0, '3y': 3.0, '5y': 5.0}
N_SIM = 200_000
SEED = 20261022

def parse_num(x, default=None):
    if x is None:
        return default
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(',', '').replace('%', '').replace('원', '').replace('억', '')
    if s in ('', 'N/A', 'NA', 'null', 'None', '-', '확인 불가'):
        return default
    try:
        return float(s)
    except ValueError:
        # try to extract leading number
        import re
        m = re.search(r'-?\d+(?:\.\d+)?', s)
        return float(m.group()) if m else default


def simulate(tree, risk, rf, h_key, rng):
    """tree: {'scenarios':[{name, probability_pct, end_price_krw, cum_cash_krw}], 'price0': float}
       risk: {'ann_vol_1y':..., 'ann_vol_3y':..., 'ann_vol_5y':...} annualized forward vol (decimal)
    """
    h = HORIZONS[h_key]
    p0 = tree['price0']
    sc = tree['scenarios']
    probs = np.array([s['prob'] for s in sc], dtype=float)
    probs = probs / probs.sum()
    gross = np.array([(s['end_price'] + s['cum_cash']) / p0 for s in sc], dtype=float)  # 1+TSR per scenario
    gross = np.maximum(gross, 1e-4)
    # scenario-level mean & dispersion in log space
    mu_log = np.log(gross)
    m = float(np.sum(probs * mu_log))
    var_scen = float(np.sum(probs * (mu_log - m) ** 2))
    sigma_target = risk[f'ann_vol_{h_key}'] * math.sqrt(h)
    var_within = max(sigma_target ** 2 - var_scen, (0.35 * sigma_target) ** 2)
    sig_w = math.sqrt(var_within)
    # per-scenario within-vol scaling: bear scenario gets 1.15x, bull 1.0x, base 0.9x (asymmetry)
    scale = {'bear': 1.15, 'base': 0.9, 'bull': 1.0}
    sig_k = np.array([sig_w * scale.get(s['name'], 1.0) for s in sc])
    n = N_SIM
    choice = rng.choice(len(sc), size=n, p=probs)
    z = rng.standard_normal(n)
    g = gross[choice] * np.exp(sig_k[choice] * z - 0.5 * sig_k[choice] ** 2)
    # permanent loss / extreme tail: with prob 'p_zero' (annual) the stock goes to ~0 (delisting). Applied cumulatively.
    p_zero_ann = risk.get('p_zero_ann', 0.0)
    p_zero = 1 - (1 - p_zero_ann) ** h
    if p_zero > 0:
        wipe = rng.random(n) < p_zero
        g = np.where(wipe, 0.05, g)
    cum = g - 1.0
    ann = np.sign(g) * np.abs(g) ** (1.0 / h) - 1.0
    exp_cum = float(cum.mean())
    exp_ann = (1 + exp_cum) ** (1 / h) - 1 if exp_cum > -1 else -1.0
    med = float(np.median(cum))
    p10, p50, p90 = [float(np.percentile(cum, q)) for q in (10, 50, 90)]
    p_loss = float((cum < 0).mean())
    p_loss30 = float((cum < -0.30).mean())
    cvar10 = float(np.sort(cum)[: int(0.10 * n)].mean())
    # downside deviation of annualized path returns vs rf (MAR)
    dd = float(np.sqrt(np.mean(np.minimum(ann - rf, 0.0) ** 2)))
    sortino = (exp_ann - rf) / dd if dd > 1e-9 else float('nan')
    scen_tsr = {s['name']: float((s['end_price'] + s['cum_cash']) / p0 - 1) for s in sc}
    return dict(exp_cum=exp_cum, exp_ann=exp_ann, median=med, p10=p10, p50=p50, p90=p90, p_loss=p_loss,
                p_loss30=p_loss30, cvar10=cvar10, dd=dd, sortino=sortino, sig_within=sig_w,
                sigma_target=sigma_target, var_scen=var_scen, scen_tsr=scen_tsr, probs=probs.tolist())


def pct_rank(values, higher_better=True):
    """0..100 percentile by rank (ties averaged)."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    order = arr.argsort()
    ranks = np.empty(n)
    # average ranks for ties
    sorted_vals = arr[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    pct = ranks / (n - 1) * 100.0 if n > 1 else np.full(n, 50.0)
    return pct if higher_better else 100.0 - pct


def run(trees, risks, macro, out_dir):
    rng = np.random.default_rng(SEED)
    rf = {k: macro['rf'][k] for k in HORIZONS}
    results = {}
    for name, tree in trees.items():
        results[name] = {'ticker': tree['ticker'], 'price0': tree['price0'], 'price_date': tree.get('price_date', ''),
                         'industry': tree.get('industry', ''), 'confidence': tree.get('confidence', ''),
                         'horizons': {}}
        for hk in HORIZONS:
            if hk not in tree['horizons']:
                continue
            t = {'price0': tree['price0'], 'scenarios': tree['horizons'][hk]}
            results[name]['horizons'][hk] = simulate(t, risks[name], rf[hk], hk, rng)
    # rankings per horizon
    rankings = {}
    weights = {'balanced': (0.60, 0.25, 0.15), 'aggressive': (0.75, 0.15, 0.10), 'defensive': (0.40, 0.35, 0.25)}
    for hk in HORIZONS:
        names = [n for n in results if hk in results[n]['horizons']]
        if not names:
            continue
        metric_ret = [results[n]['horizons'][hk]['exp_cum'] if hk == '1y' else results[n]['horizons'][hk]['exp_ann'] for n in names]
        sortino = [results[n]['horizons'][hk]['sortino'] for n in names]
        cvar = [results[n]['horizons'][hk]['cvar10'] for n in names]
        ploss = [results[n]['horizons'][hk]['p_loss'] for n in names]
        pr_ret = pct_rank(metric_ret)
        pr_sort = pct_rank(sortino)
        pr_cvar = pct_rank(cvar)  # less negative = higher = better
        # risk-adjusted ordering: sortino desc, then cvar desc, then p_loss asc
        ra_order = sorted(range(len(names)), key=lambda i: (-sortino[i], -cvar[i], ploss[i]))
        ret_order = sorted(range(len(names)), key=lambda i: -metric_ret[i])
        comp = {}
        for wname, (a, b, c) in weights.items():
            score = a * pr_ret + b * pr_sort + c * pr_cvar
            order = sorted(range(len(names)), key=lambda i: -score[i])
            comp[wname] = {'score': score.tolist(), 'order': order}
        rk = {}
        for i, n in enumerate(names):
            rk[n] = {
                'ret_rank': ret_order.index(i) + 1,
                'ra_rank': ra_order.index(i) + 1,
                'balanced_rank': comp['balanced']['order'].index(i) + 1,
                'aggressive_rank': comp['aggressive']['order'].index(i) + 1,
                'defensive_rank': comp['defensive']['order'].index(i) + 1,
                'balanced_score': float(comp['balanced']['score'][i]),
                'aggressive_score': float(comp['aggressive']['score'][i]),
                'defensive_score': float(comp['defensive']['score'][i]),
                'pr_ret': float(pr_ret[i]), 'pr_sortino': float(pr_sort[i]), 'pr_cvar': float(pr_cvar[i]),
            }
        rankings[hk] = rk
    out = {'results': results, 'rankings': rankings, 'rf': rf, 'n_sim': N_SIM, 'seed': SEED}
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'results.json'), 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


if __name__ == '__main__':
    base = sys.argv[1]
    trees = json.load(open(os.path.join(base, 'trees.json')))
    risks = json.load(open(os.path.join(base, 'risk.json')))
    macro = json.load(open(os.path.join(base, 'macro_rf.json')))
    out = run(trees, risks, macro, base)
    for hk in HORIZONS:
        if hk not in out['rankings']:
            continue
        print(f'=== {hk} ===')
        rk = out['rankings'][hk]
        for n in sorted(rk, key=lambda x: rk[x]['balanced_rank']):
            r = out['results'][n]['horizons'][hk]
            print(f"{rk[n]['balanced_rank']:2d} ret#{rk[n]['ret_rank']:2d} ra#{rk[n]['ra_rank']:2d} {n:12s} Ecum={r['exp_cum']*100:7.1f}% Eann={r['exp_ann']*100:6.1f}% med={r['median']*100:7.1f}% P10={r['p10']*100:7.1f}% P90={r['p90']*100:7.1f}% Ploss={r['p_loss']*100:5.1f}% P30={r['p_loss30']*100:5.1f}% Sort={r['sortino']:5.2f} CVaR={r['cvar10']*100:7.1f}%")
