"""에이전트 산출물(시나리오 트리)을 결합해 기간별 수익·위험 지표와 순위를 만든다.

단계
1. 시나리오 트리 검증: 거시 태그(기준/낙관/비관)별 무조건부 확률 합이 50/20/30이 되도록 맞춘다.
2. 희석 조정: 분석가가 가정한 순주식수 변화와 포렌식 에이전트(E)의 추정이 크게 다르면 차이만큼 주당가치를 보정한다.
3. 결합: 산업 전문가와 독립 일반 분석가의 트리를 가중 혼합(linear opinion pool)한다. 가중치는 최종 심사(J)가 정한다.
4. 반대심문 조정: 최종 심사가 채택한 반대심문(I) 조정을 반영한다.
5. 축소: 기대 총수익 배수를 베이스레이트 사전값 쪽으로 한 번만 축소한다(가중치 = 자료 품질과 분석가 간 차이).
6. 시뮬레이션: 시나리오 혼합 + 로그정규 내부잡음(목표 총변동성에 보정)으로 누적 TSR 분포를 만든다.
7. 지표와 순위: 기대·중앙값·분위수·손실확률·CVaR·Forward Sortino, 기대수익/위험조정/균형·공격·방어 순위.
"""
import json
import math
import numpy as np
import pandas as pd

from quant_engine import HORIZONS, simulate, metrics, pct_rank, rank_desc

MACRO_P = {'기준': 0.50, '낙관': 0.20, '비관': 0.30}
CONF = {'높음': 2, '보통': 1, '낮음': 0}
MEANREV = {'h1': 1.0, 'h3': 0.88, 'h5': 0.80}   # 장기 분산비율(약 0.64~0.77) 반영
S_FLOOR = 0.10


def fix_tree(branches, log, tag):
    """거시 그룹별 확률 합을 고정 확률에 맞춘다. 반환: [(macro, name, p, price, div, narrative)]"""
    out = []
    for m, target in MACRO_P.items():
        grp = [b for b in branches if b.get('macro') == m]
        if not grp:
            log.append(f'{tag}: {m} 그룹 없음')
            continue
        s = sum(max(float(b['prob_pct']), 0.0) for b in grp)
        if s <= 0:
            log.append(f'{tag}: {m} 확률합 0')
            continue
        if abs(s - target * 100) > 0.6:
            log.append(f'{tag}: {m} 확률합 {s:.1f} → {target*100:.0f}로 비례조정')
        for b in grp:
            p = max(float(b['prob_pct']), 0.0) / s * target
            out.append((m, b['name'], p, float(b['price_at_horizon']), float(b.get('cum_dividends', 0.0)), b.get('narrative', '')))
    tot = sum(x[2] for x in out)
    if out and abs(tot - 1) > 1e-9:
        out = [(a, b, p / tot, c, d, e) for a, b, p, c, d, e in out]
    return out


def tree_expectation(tree, p0):
    return sum(p * (price + div) / p0 for _, _, p, price, div, _ in tree)


def forward_sigma(row):
    """연환산 선행 변동성(1년차, 장기)을 시장요인+고유요인으로 나눠 추정한다.

    - 시장 변동성: 1년차 37%(거시 시나리오별 KOSPI 변동성 기준 30~35%·낙관 약 28%·비관 45% 이상의 확률가중 RMS),
      장기 26%(2020년 이후 KOSPI 대용지수 28%, 2020~24년 20%, 반도체 2종목 비중 46% 반영).
    - 베타: 1년·3년 베타 평균을 1 쪽으로 1/3 축소(Blume 조정).
    - 고유변동성: 각 기간 총변동성에서 같은 기간 시장 몫을 뺀 값. 1년차는 최근1년·3년 평균,
      장기는 최근1년 20%·3년 40%·2020~24년(없으면 전체기간) 40%.
    """
    M1Y, M3Y, MPRE = 0.550, 0.355, 0.200
    SM1, SMLR = 0.37, 0.26
    v1, v3, vfull = row['vol_1y'], row['vol_3y'], row['vol_full']
    vpre = row.get('vol_2020_2024', np.nan)
    if vpre is None or (isinstance(vpre, float) and math.isnan(vpre)):
        vpre = vfull
    b1, b3 = row['beta_1y_KOSPI'], row['beta_3y_KOSPI']
    beta = 0.67 * (0.5 * b1 + 0.5 * b3) + 0.33
    i1 = math.sqrt(max(v1 ** 2 - (b1 * M1Y) ** 2, 0.01))
    i3 = math.sqrt(max(v3 ** 2 - (b3 * M3Y) ** 2, 0.01))
    ip = math.sqrt(max(vpre ** 2 - (b3 * MPRE) ** 2, 0.01))
    idio1 = 0.5 * i1 + 0.5 * i3
    idiolr = 0.2 * i1 + 0.4 * i3 + 0.4 * ip
    s1 = math.sqrt((beta * SM1) ** 2 + idio1 ** 2)
    slr = math.sqrt((beta * SMLR) ** 2 + idiolr ** 2)
    return s1, slr


def target_total_sigma(s1, slr, key):
    T = HORIZONS[key]
    var = s1 ** 2 + (T - 1) * slr ** 2
    return math.sqrt(var) * MEANREV[key]


def within_sigma(probs, gross, target, T):
    lg = np.log(np.maximum(gross, 1e-6))
    m = np.sum(probs * lg)
    between = np.sum(probs * (lg - m) ** 2)
    s2 = target ** 2 - between
    floor = S_FLOOR * math.sqrt(T)
    return max(math.sqrt(s2) if s2 > 0 else 0.0, floor), math.sqrt(between)


D0 = {'h1': 0.15, 'h3': 0.08, 'h5': 0.06}   # 기간별 '정상적인' 분석가 간 연환산 차이 폭


def shrink_weight(conf_spec, conf_gen, e_spec_ann, e_gen_ann, key):
    """사전값으로의 축소 가중치(1이면 축소 없음). 자료 품질(낮은 쪽 신뢰도)과 분석가 간 차이로 정한다."""
    base = {2: 0.85, 1: 0.70, 0: 0.50}[min(conf_spec, conf_gen)]
    d = abs(math.log1p(e_spec_ann) - math.log1p(e_gen_ann))
    return base / (1.0 + (d / D0[key]) ** 2), d


def analyse(stocks, risk, rf, index_exp, priors, weights, adjustments, seed=20261022, n_sim=200_000,
            macro_probs=None, value_shocks=None, horizons=None):
    """stocks: {code: {'name','p0','market','spec','gen','dil_fix':{h:factor}}}.
    priors: {code: prior expected annual TSR (소수)}. weights: {code: w_spec}.
    adjustments: {code: {h: {'value_mult': x, 'macro_value_mult': {macro: x}}}} (반대심문 채택분).
    macro_probs: 민감도 분석용 거시확률 대체값. value_shocks: {code: {h: mult}} 민감도 충격."""
    global MACRO_P
    saved = MACRO_P
    if macro_probs:
        MACRO_P = macro_probs
    rng = np.random.default_rng(seed)
    rows, branches_out, log = [], [], []
    try:
        for code, s in stocks.items():
            r = risk[code]
            s1, slr = forward_sigma(r)
            s1 = s.get('sigma_override', {}).get('s1', s1)
            slr = s.get('sigma_override', {}).get('slr', slr)
            p0 = s['p0']
            w_spec = weights.get(code, 0.5)
            for key, T in HORIZONS.items():
                if horizons and key not in horizons:
                    continue
                trees = {}
                for role in ('spec', 'gen'):
                    if s.get(role) is None:
                        continue
                    t = fix_tree(s[role]['scenarios'][key], log, f'{code} {role} {key}')
                    f = s.get('dil_fix', {}).get(role, {}).get(key, 1.0)
                    t = [(m, n, p, price * f, div, nar) for m, n, p, price, div, nar in t]
                    trees[role] = t
                if not trees:
                    continue
                if 'spec' in trees and 'gen' in trees:
                    ws = {'spec': w_spec, 'gen': 1 - w_spec}
                else:
                    ws = {k: 1.0 for k in trees}
                mix = []
                for role, t in trees.items():
                    for m, n, p, price, div, nar in t:
                        mix.append((m, f'{role}:{n}', p * ws[role], price, div, nar))
                # 반대심문 조정(최종 심사 채택분)
                adj = adjustments.get(code, {}).get(key, {})
                vm = adj.get('value_mult', 1.0)
                mvm = adj.get('macro_value_mult', {})
                mix = [(m, n, p, price * vm * mvm.get(m, 1.0), div, nar) for m, n, p, price, div, nar in mix]
                tail = adj.get('extra_tail')
                if tail and tail.get('prob', 0) > 0:
                    tp = tail['prob']
                    tot = sum(x[2] for x in mix)
                    mix = [(m, n, p * (1 - tp) / tot, price, div, nar) for m, n, p, price, div, nar in mix]
                    mix.append(('비관', 'cross:극단 손실', tp, p0 * tail['price_frac'], 0.0, '반대심문 채택 꼬리 시나리오'))
                # 민감도 충격
                if value_shocks and code in value_shocks:
                    sh = value_shocks[code].get(key, 1.0)
                    mix = [(m, n, p, price * sh, div, nar) for m, n, p, price, div, nar in mix]
                probs = np.array([x[2] for x in mix])
                probs = probs / probs.sum()
                gross = np.array([(x[3] + x[4]) / p0 for x in mix])
                e_raw = float(np.sum(probs * gross))
                # 분석가별 기대(연환산) — 축소 가중치 계산용
                e_role = {}
                for role, t in trees.items():
                    e = tree_expectation(t, p0) * (vm)
                    e_role[role] = e ** (1 / T) - 1
                cs = CONF.get(s['spec']['confidence'], 1) if s.get('spec') else 1
                cg = CONF.get(s['gen']['confidence'], 1) if s.get('gen') else 1
                es = e_role.get('spec', e_role.get('gen'))
                eg = e_role.get('gen', e_role.get('spec'))
                w, d = shrink_weight(cs, cg, es, eg, key)
                prior_ann = priors.get(code, 0.08)
                e_prior = (1 + prior_ann) ** T
                e_target = w * e_raw + (1 - w) * e_prior
                shift = e_target / e_raw if e_raw > 0 else 1.0
                gross_s = gross * shift
                target = target_total_sigma(s1, slr, key)
                sw, between = within_sigma(probs, gross_s, target, T)
                tsr = simulate(probs, gross_s, sw, rng, n_sim)
                rf_ann = rf[key]
                met = metrics(tsr, T, rf_ann)
                idx_ann = index_exp['KOSDAQ' if s['market'].startswith('KOSDAQ') else 'KOSPI'][key]
                exp_ann = met['exp_ann']
                rows.append({'code': code, 'name': s['name'], 'h': key, 'T': T, 'p0': p0,
                             'e_raw_cum': e_raw - 1, 'e_spec_ann': e_role.get('spec', np.nan), 'e_gen_ann': e_role.get('gen', np.nan),
                             'disagree_log_ann': d, 'shrink_w': w, 'prior_ann': prior_ann, 'shift': shift,
                             'sigma_target': target, 'sigma_within': sw, 'sigma_between': between,
                             'excess_vs_index_ann': exp_ann - idx_ann, 'index_ann': idx_ann, 'w_spec': w_spec,
                             **met})
                for (m, n, p, price, div, nar), g in zip(mix, gross_s):
                    branches_out.append({'code': code, 'h': key, 'macro': m, 'branch': n, 'prob': p / sum(x[2] for x in mix),
                                         'price': price * shift, 'div': div * shift, 'tsr': g - 1, 'narrative': nar})
    finally:
        MACRO_P = saved
    return pd.DataFrame(rows), pd.DataFrame(branches_out), log


def rank_table(df, perm_risk):
    """기간별 기대수익·위험조정·균형/공격/방어 순위."""
    out = []
    for key, g in df.groupby('h'):
        g = g.copy()
        er = g['exp_cum'] if key == 'h1' else g['exp_ann']
        g['rank_er'] = rank_desc(er.values)
        # 위험조정: Sortino → CVaR(덜 부정적) → 손실확률(낮음) → 영구손실위험(낮음)
        g['perm'] = g['code'].map(perm_risk).fillna(3)
        order = g.sort_values(['sortino', 'cvar10', 'p_loss', 'perm'], ascending=[False, False, True, True]).index
        g.loc[order, 'rank_ra'] = range(1, len(g) + 1)
        p_er = pct_rank(er.values)
        p_so = pct_rank(g['sortino'].values)
        p_cv = pct_rank(g['cvar10'].values)
        g['pct_er'], g['pct_sortino'], g['pct_cvar'] = p_er, p_so, p_cv
        g['score_bal'] = 0.60 * p_er + 0.25 * p_so + 0.15 * p_cv
        g['score_agg'] = 0.75 * p_er + 0.15 * p_so + 0.10 * p_cv
        g['score_def'] = 0.40 * p_er + 0.35 * p_so + 0.25 * p_cv
        for c in ['bal', 'agg', 'def']:
            g[f'rank_{c}'] = rank_desc(g[f'score_{c}'].values)
        out.append(g)
    return pd.concat(out)
