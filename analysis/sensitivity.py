"""민감도와 순위 안정성.

사용: python3 analysis/sensitivity.py
입력: run_quant.build_inputs(최종 단계 설정), output/final_ranks.csv, data/aux/S_sensitivity*.json(있으면)
산출
- output/sens_runs.csv: 종목·기간·실행별 기대수익과 균형 순위
- output/rank_stability.csv: 종목·기간별 순위 범위, 추정오차 부트스트랩 순위 구간, 상위5 확률, 불안정 표시

실행 목록(최종 계산과 같은 난수 시드·같은 경로 수(20만)를 써서 몬테카를로 잡음이 아니라 가정 차이만 비교한다)
- base: 최종 설정
- macro_bear / macro_bull: 거시 확률 45/10/45, 45/35/20(사전값의 지수 기대도 함께 바꾼다)
- w_spec_lo / w_spec_hi: 전문가 가중 0.35 / 0.65 일괄
- prior_heavy: 분석가 쪽 축소 가중치를 절반으로(사전값 쪽으로 더 끌어당김)
- vol_low: 목표 변동성을 15% 낮춤(모형 꼬리가 베이스레이트보다 두꺼운 점 점검)
- S 충격 8종: 원화 10% 강세, 금리 +100bp, 출구배수 -20%, 메모리·AI capex 하향, 자동차 관세 25%,
  임상·인허가 성공확률 -20%, 추가 희석 5%, 최대 고객 이탈(종목별 탄력도는 Agent S 추정)
- 가중치 프로필: 공격형(75/15/10), 방어형(40/35/25)은 기본 실행의 점수로 계산한다.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_quant as rq  # noqa: E402
import pipeline  # noqa: E402
from pipeline import analyse, rank_table  # noqa: E402
from quant_engine import rank_desc, pct_rank  # noqa: E402

rq.STAGE = 'final'
OUT = os.path.join(HERE, 'output')
N_SIM = 200_000   # 최종 계산과 같은 경로 수·시드라 base 실행이 최종 결과와 같다
SEED = 20261022
macro = json.load(open(os.path.join(HERE, 'data', 'macro.json')))['synth']
SC = {s['name'].split(' ')[0]: s for s in macro['scenarios']}


def index_exp(probs):
    """거시 확률을 바꿨을 때의 KOSPI·KOSDAQ 기대 TSR(1년 누적, 3·5년 연환산)."""
    out = {}
    for idx, key in (('KOSPI', 'kospi_tsr_pct'), ('KOSDAQ', 'kosdaq_tsr_pct')):
        e1 = sum(probs[m] * SC[m][key]['h1_cum'] / 100 for m in probs)
        e3 = sum(probs[m] * (1 + SC[m][key]['h3_ann'] / 100) ** 3 for m in probs) ** (1 / 3) - 1
        e5 = sum(probs[m] * (1 + SC[m][key]['h5_ann'] / 100) ** 5 for m in probs) ** (1 / 5) - 1
        out[idx] = {'h1': e1, 'h3': e3, 'h5': e5}
    return out


def load_adjustments():
    adj = {}
    for j in rq.load_aux('J_'):
        for s in j['result'].get('stocks', []):
            if s.get('adjustments'):
                adj[s['code']] = rq.to_pipeline_adj(s['adjustments'])
    return adj


def run(stocks, settings, adjustments, macro_probs=None, value_shocks=None, w_override=None, shrink_scale=1.0, vol_scale=1.0):
    idx = index_exp(macro_probs) if macro_probs else rq.IDX
    weights = dict(settings['w_spec'])
    if w_override is not None:
        weights = {c: w_override for c in weights}
    saved_mr = dict(pipeline.MEANREV)
    if vol_scale != 1.0:
        pipeline.MEANREV.update({k: v * vol_scale for k, v in saved_mr.items()})
    pipeline.SHRINK_SCALE = shrink_scale   # 같은 방향 보정 뒤 최종 축소 결과에 적용(분석가 쪽 비중을 줄임)
    frames = []
    try:
        for key in ('h1', 'h3', 'h5'):
            pri = {c: rq.RF[key] + settings['beta_fwd'][c] * (idx['KOSPI'][key] - rq.RF[key]) + settings['alpha_H'][c] for c in stocks}
            df, _, _ = analyse(stocks, rq.risk.to_dict('index'), rq.RF, idx, pri, weights, adjustments, seed=SEED,
                               n_sim=N_SIM, macro_probs=macro_probs, value_shocks=value_shocks, horizons=[key])
            frames.append(df)
    finally:
        pipeline.SHRINK_SCALE = 1.0
        pipeline.MEANREV.update(saved_mr)
    return pd.concat(frames)


def main():
    stocks, settings = rq.build_inputs()
    adjustments = load_adjustments()
    perm = {}
    for g in rq.load_aux('G_risk_review'):
        for s in g['result']['stocks']:
            perm[s['code']] = s['perm_loss_risk_score']
    runs = {'base': {}, 'macro_bear': {'macro_probs': {'기준': 0.45, '낙관': 0.10, '비관': 0.45}},
            'macro_bull': {'macro_probs': {'기준': 0.45, '낙관': 0.35, '비관': 0.20}},
            'w_spec_lo': {'w_override': 0.35}, 'w_spec_hi': {'w_override': 0.65}, 'prior_heavy': {'shrink_scale': 0.5},
            'vol_low': {'vol_scale': 0.85}}
    shocks = {}
    S = rq.load_aux('S_')
    if S:
        for s in S[-1]['result']['stocks']:
            for k in ('krw_strong_10pct', 'rates_up_100bp', 'exit_multiple_down_20pct', 'memory_ai_capex_down', 'auto_tariff_25pct',
                      'bio_pos_down', 'extra_dilution_5pct', 'top_customer_loss'):
                shocks.setdefault(k, {})[s['code']] = {h: max(1 + s[k][h] / 100, 0.05) for h in ('h1', 'h3', 'h5')}
        for k, v in shocks.items():
            runs[f'shock_{k}'] = {'value_shocks': v}
    rows = []
    base_df = None
    for name, kw in runs.items():
        df = run(stocks, settings, adjustments, **kw)
        rk = rank_table(df, perm)
        if name == 'base':
            base_df = rk.copy()
        for _, r in rk.iterrows():
            rows.append({'run': name, 'code': r.code, 'name': r['name'], 'h': r.h, 'exp_cum': r.exp_cum, 'exp_ann': r.exp_ann,
                         'sortino': r.sortino, 'cvar10': r.cvar10, 'p_loss': r.p_loss, 'p_loss50': r.p_loss50, 'rank_bal': int(r.rank_bal), 'rank_er': int(r.rank_er),
                         'rank_agg': int(r.rank_agg), 'rank_def': int(r.rank_def)})
        print('done', name, flush=True)
    sr = pd.DataFrame(rows)
    sr.to_csv(os.path.join(OUT, 'sens_runs.csv'), index=False)

    # 추정오차 부트스트랩: 기대수익에 두 가지 오차를 더해 균형 점수 순위를 다시 매긴다.
    # (1) 종목 고유 오차(분석가 쪽): sd = w x sqrt(d^2 + d_med^2) / sqrt(2) x k(신뢰도).
    #     d는 전문가-일반 분석가 차이(로그, 1년은 누적·3·5년은 연환산), d_med는 같은 기간의 중앙값,
    #     w는 축소 가중치, k는 최종 신뢰도 높음 0.8 / 보통 1.0 / 낮음 1.3. 두 분석가가 같은 팩트시트를 써서
    #     차이가 실제 오차를 과소평가할 수 있으므로 중앙값을 하한처럼 더한다.
    # (2) 사전값 오차(베이스레이트 버킷 공통): sd = (1 - w) x 1.5%p, 같은 H 버킷 종목에 같은 충격.
    conf = {}
    for j in rq.load_aux('J_'):
        for s_ in j['result'].get('stocks', []):
            conf[s_['code']] = s_.get('final_confidence', '보통')
    KCONF = {'높음': 0.8, '보통': 1.0, '낮음': 1.3}
    bucket_of = {}
    hb = rq.load_aux('H_base_rates')
    if hb:
        for bi, b in enumerate(hb[-1]['result']['priors']):
            for m in b['members']:
                for c in stocks:
                    if c in m:
                        bucket_of[c] = bi
    SIG_ALPHA = 0.015
    final = pd.read_csv(os.path.join(OUT, 'final_ranks.csv'), dtype={'code': str})
    rng = np.random.default_rng(7)
    stab = []
    for key, g in final.groupby('h'):
        g = g.reset_index(drop=True)
        T = {'h1': 1, 'h3': 3, 'h5': 5}[key]
        rf = rq.RF[key]
        d_med = float(g.disagree_log_ann.median())
        tau = np.array([r.shrink_w * math.sqrt(r.disagree_log_ann ** 2 + d_med ** 2) / math.sqrt(2) * KCONF.get(conf.get(r.code, '보통'), 1.0)
                        for r in g.itertuples()])
        tau_b = np.array([(1 - r.shrink_w) * SIG_ALPHA for r in g.itertuples()])
        bidx = np.array([bucket_of.get(c, 100 + k) for k, c in enumerate(g.code)])
        ub = np.unique(bidx)
        B = 4000
        top5 = np.zeros(len(g))
        rank_draws = np.zeros((B, len(g)), int)
        for b in range(B):
            zb = dict(zip(ub, rng.standard_normal(len(ub))))
            delta = rng.standard_normal(len(g)) * tau + np.array([zb[x] for x in bidx]) * tau_b
            if key == 'h1':
                er = g.exp_cum.values + delta
                er_ann = er
                cv = g.cvar10.values + delta
            else:
                er_ann = (1 + g.exp_ann.values) * np.exp(delta) - 1
                er = er_ann
                cv = (1 + g.cvar10.values) * np.exp(delta * T) - 1
            so = (er_ann - rf) / g.downdev_ann.values
            score = 0.60 * pct_rank(er) + 0.25 * pct_rank(so) + 0.15 * pct_rank(cv)
            r = rank_desc(score)
            rank_draws[b] = r
            top5 += (r <= 5)
        ASSUMP = ['base', 'macro_bear', 'macro_bull', 'w_spec_lo', 'w_spec_hi', 'prior_heavy', 'vol_low']
        for i, r in g.iterrows():
            sub = sr[(sr.code == r.code) & (sr.h == key)]
            a_ranks = list(sub[sub.run.isin(ASSUMP)].rank_bal) + [int(r.rank_agg), int(r.rank_def)]
            s_ranks = list(sub[sub.run.str.startswith('shock_')].rank_bal)
            lo, hi = np.percentile(rank_draws[:, i], [10, 90])
            stab.append({'code': r.code, 'name': r['name'], 'h': key, 'rank_bal': int(r.rank_bal),
                         'rank_agg': int(r.rank_agg), 'rank_def': int(r.rank_def),
                         'assump_min': int(min(a_ranks)), 'assump_max': int(max(a_ranks)),
                         'stress_min': int(min(s_ranks)) if s_ranks else None, 'stress_max': int(max(s_ranks)) if s_ranks else None,
                         'boot_p10': int(lo), 'boot_p90': int(hi), 'p_top5': top5[i] / B, 'tau': tau[i]})
    st = pd.DataFrame(stab)

    def flag(r):
        """가정 변경(가중 프로필·거시 확률·전문가 가중·축소 강도)과 추정오차 부트스트랩으로 판정한다.
        스트레스 충격(S)은 확률가중이 아닌 가상 상황이라 판정에 넣지 않고 따로 보여 준다."""
        wb = r.boot_p90 - r.boot_p10
        ra = r.assump_max - r.assump_min
        if wb <= 4 and ra <= 3:
            return '안정'
        if wb <= 9 and ra <= 6:
            return '주의'
        return '불안정'
    st['stability'] = st.apply(flag, axis=1)
    st.to_csv(os.path.join(OUT, 'rank_stability.csv'), index=False)
    pd.set_option('display.width', 220)
    for key in ('h1', 'h3', 'h5'):
        print(st[st.h == key].sort_values('rank_bal').round(2).to_string(index=False))


if __name__ == '__main__':
    main()
