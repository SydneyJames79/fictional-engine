#!/usr/bin/env python3
"""Generate markdown tables for the report from engine results + WF1 data.
Usage: report_tables.py <scratchpad> <engine_dir>  → writes <engine_dir>/tables.md and tables.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import parse_num

HZ = ['1y', '3y', '5y']
HZN = {'1y': '1년', '3y': '3년', '5y': '5년'}


def fmt_pct(x, nd=1):
    if x is None:
        return 'N/A'
    return f'{x*100:+.{nd}f}%' if x < 0 or x > 0 else f'{0:.{nd}f}%'


def fmt_pct_plain(x, nd=1):
    if x is None:
        return 'N/A'
    return f'{x*100:.{nd}f}%'


def fmt_krw(x):
    if x is None:
        return 'N/A'
    return f'{x:,.0f}원'


def fmt_mcap(bn):
    v = parse_num(bn)
    if v is None:
        return 'N/A'
    if v >= 10000:
        return f'{v/10000:,.1f}조원'
    return f'{v:,.0f}억원'


def main(base, eng):
    res = json.load(open(os.path.join(eng, 'results.json')))
    trees = json.load(open(os.path.join(eng, 'trees.json')))
    macro_rf = json.load(open(os.path.join(eng, 'macro_rf.json')))
    R, RK = res['results'], res['rankings']
    names = list(R.keys())
    # expected index returns (price basis) from the common macro scenario, keyed by market and horizon
    idx = {}
    try:
        macro = json.load(open(os.path.join(base, 'wf1', 'macro_common.json')))
        for ie in macro.get('index_expectations', []):
            hk2 = '1y' if ie['horizon'].startswith('1') else ('3y' if ie['horizon'].startswith('3') else '5y')
            idx.setdefault(ie['index'], {})[hk2] = float(str(ie.get('expected_cum_pct')).replace('+', '').replace('%', '')) / 100.0
    except Exception:
        idx = {}
    out = []
    tj = {}

    # ---------- Part 3: per-horizon tables ----------
    for hk in HZ:
        if hk not in RK:
            continue
        rk = RK[hk]
        rows = sorted(rk.keys(), key=lambda n: rk[n]['balanced_rank'])
        out.append(f'\n### {HZN[hk]} 전체 순위표 (종료일 { {"1y":"2027-10-22","3y":"2029-10-22","5y":"2031-10-22"}[hk] }, 무위험수익률 {macro_rf["rf"][hk]*100:.2f}%)\n')
        out.append('| 종합순위 | 기대수익률순위 | 위험조정순위 | 종목(코드) | 현재가 | 기대 누적 TSR | 기대 연환산 | 중앙값 누적 TSR | P10 | P50 | P90 | 손실확률 | 30%↑손실확률 | Fwd Sortino | CVaR 10% | 시장 대비 초과(기대 누적) | 신뢰도 | 핵심 요인 |')
        out.append('|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|---|')
        tj[hk] = []
        for n in rows:
            r = R[n]['horizons'][hk]
            t = trees[n]
            mkt = t.get('market') or 'KOSPI'
            ix = idx.get(mkt, {}).get(hk)
            excess = (r['exp_cum'] - ix) if ix is not None else None
            row = {
                'index': mkt, 'index_exp_cum': ix, 'excess_vs_index': excess,
                'balanced_rank': rk[n]['balanced_rank'], 'ret_rank': rk[n]['ret_rank'], 'ra_rank': rk[n]['ra_rank'],
                'aggressive_rank': rk[n]['aggressive_rank'], 'defensive_rank': rk[n]['defensive_rank'],
                'name': n, 'ticker': t['ticker'], 'price0': t['price0'], 'price_date': t['price_date'],
                'exp_cum': r['exp_cum'], 'exp_ann': r['exp_ann'], 'median': r['median'], 'p10': r['p10'], 'p50': r['p50'], 'p90': r['p90'],
                'p_loss': r['p_loss'], 'p_loss30': r['p_loss30'], 'sortino': r['sortino'], 'cvar10': r['cvar10'],
                'confidence': t.get('confidence', ''), 'one_line': t.get('one_line', ''), 'balanced_score': rk[n]['balanced_score'],
                'scen_tsr': r['scen_tsr'], 'probs': r['probs'], 'shrink_weight': t.get('shrink_weight', 1.0),
            }
            tj[hk].append(row)
            out.append(f"| {row['balanced_rank']} | {row['ret_rank']} | {row['ra_rank']} | {n}({t['ticker']}) | {fmt_krw(t['price0'])} | {fmt_pct(r['exp_cum'])} | {fmt_pct(r['exp_ann'])} | {fmt_pct(r['median'])} | {fmt_pct(r['p10'])} | {fmt_pct(r['p50'])} | {fmt_pct(r['p90'])} | {fmt_pct_plain(r['p_loss'])} | {fmt_pct_plain(r['p_loss30'])} | {r['sortino']:.2f} | {fmt_pct(r['cvar10'])} | {(fmt_pct(excess) + 'p vs ' + mkt) if excess is not None else 'N/A'} | {t.get('confidence','')} | {t.get('one_line','')} |")

    # ---------- Part 4: rank change table ----------
    out.append('\n### 기간별 순위 변화표\n')
    out.append('| 종목(코드) | 1년 종합 | 3년 종합 | 5년 종합 | 1년 공격형 | 3년 공격형 | 5년 공격형 | 1년 방어형 | 3년 방어형 | 5년 방어형 | 추세 |')
    out.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|')
    tj['rank_change'] = []
    for n in sorted(names, key=lambda n: sum(RK[h][n]['balanced_rank'] for h in HZ if h in RK and n in RK[h])):
        b = [RK[h][n]['balanced_rank'] if (h in RK and n in RK[h]) else None for h in HZ]
        a = [RK[h][n]['aggressive_rank'] if (h in RK and n in RK[h]) else None for h in HZ]
        d = [RK[h][n]['defensive_rank'] if (h in RK and n in RK[h]) else None for h in HZ]
        trend = ''
        if b[0] and b[2]:
            diff = b[0] - b[2]
            trend = '장기로 갈수록 상승' if diff >= 3 else ('장기로 갈수록 하락' if diff <= -3 else '비슷')
        tj['rank_change'].append({'name': n, 'ticker': trees[n]['ticker'], 'balanced': b, 'aggressive': a, 'defensive': d, 'trend': trend})
        f = lambda x: str(x) if x else '-'
        out.append(f"| {n}({trees[n]['ticker']}) | {f(b[0])} | {f(b[1])} | {f(b[2])} | {f(a[0])} | {f(a[1])} | {f(a[2])} | {f(d[0])} | {f(d[1])} | {f(d[2])} | {trend} |")

    # ---------- Part 1 lists ----------
    p1 = {}
    for hk in HZ:
        if hk not in RK:
            continue
        rk = RK[hk]
        p1[f'{hk}_ret_top5'] = sorted(rk, key=lambda n: rk[n]['ret_rank'])[:5]
        p1[f'{hk}_ra_top5'] = sorted(rk, key=lambda n: rk[n]['ra_rank'])[:5]
        p1[f'{hk}_bal_top5'] = sorted(rk, key=lambda n: rk[n]['balanced_rank'])[:5]
        p1[f'{hk}_bal_bottom5'] = sorted(rk, key=lambda n: -rk[n]['balanced_rank'])[:5]
    # consistency: average balanced rank across horizons
    avg = {n: sum(RK[h][n]['balanced_rank'] for h in HZ if h in RK and n in RK[h]) / 3 for n in names}
    p1['consistent_top5'] = sorted(avg, key=lambda n: avg[n])[:5]
    # high return but high risk: ret rank top-10 and p_loss30 high (3y)
    hk = '3y'
    if hk in RK:
        p1['high_ret_high_risk'] = [n for n in sorted(RK[hk], key=lambda n: RK[hk][n]['ret_rank']) if RK[hk][n]['ret_rank'] <= 10 and R[n]['horizons'][hk]['p_loss30'] >= 0.30][:6]
        p1['mid_ret_good_ra'] = [n for n in sorted(RK[hk], key=lambda n: RK[hk][n]['ra_rank']) if RK[hk][n]['ra_rank'] <= 8 and RK[hk][n]['ret_rank'] > 8][:6]
        p1['exp_vs_median_gap'] = sorted(names, key=lambda n: -(R[n]['horizons'][hk]['exp_cum'] - R[n]['horizons'][hk]['median']))[:6]
    tj['part1'] = p1
    tj['avg_balanced_rank'] = avg

    with open(os.path.join(eng, 'tables.md'), 'w') as f:
        f.write('\n'.join(out))
    json.dump(tj, open(os.path.join(eng, 'tables.json'), 'w'), ensure_ascii=False, indent=1)
    print('\n'.join(out)[:6000])
    print('\nPART1:', json.dumps(p1, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
