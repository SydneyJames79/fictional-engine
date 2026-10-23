"""최종 심사(J) 워크플로 스크립트를 생성한다(종목별 압축 요약 포함).

사용: python3 analysis/workflows/build_judge_script.py <출력 .js>
입력: output/prelim_ranks.csv, output/prelim_branches.csv, output/prelim_settings.json,
      data/stocks/*.json, data/aux/{G_risk_review,H_base_rates,I_*,V_*}.json
"""
import json
import os
import sys

import pandas as pd

AN = '/home/user/fictional-engine/analysis'
sys.path.insert(0, AN)
from dossier import analyst_brief  # noqa: E402
from workflows.build_stock_script import NAMES, SECTOR  # noqa: E402

ranks = pd.read_csv(f'{AN}/output/prelim_ranks.csv', dtype={'code': str})
br = pd.read_csv(f'{AN}/output/prelim_branches.csv', dtype={'code': str})
settings = json.load(open(f'{AN}/output/prelim_settings.json'))
risk = pd.read_csv(f'{AN}/data/risk_metrics_full_1021.csv', dtype={'code': str}).set_index('code')
AUX = f'{AN}/data/aux'


def aux(prefix):
    return {f: json.load(open(os.path.join(AUX, f)))['result'] for f in sorted(os.listdir(AUX)) if f.startswith(prefix)}


G = {s['code']: s for s in aux('G_risk_review')['G_risk_review.json']['stocks']}
H = aux('H_base_rates')['H_base_rates.json']
bucket = {}
for b in H['priors']:
    for m in b['members']:
        for c, n in NAMES.items():
            if c in m or n in m:
                bucket[c] = {'bucket': b['bucket'], 'alpha_vs_capm_prior_pct': b['alpha_vs_capm_prior_pct'],
                             'prob_perm_loss_gt50_5y_pct': b['prob_perm_loss_gt50_5y_pct'], 'why': b['rationale'][:500]}
I = {r['code']: r for r in aux('I_').values()}
V = {r['code']: r for r in aux('V_').values()}


def short(s, n):
    s = s or ''
    return s if len(s) <= n else s[:n] + '…'


def analyst(r, p0):
    b = analyst_brief(r, p0)
    if not b:
        return None
    return {'confidence': b['confidence'], 'confidence_reason': short(b['confidence_reason'], 250),
            'view_vs_market': short(b['view_vs_market'], 450),
            'dilution_assumed_pct': b['dilution_assumed'],
            'by_h': {h: {'exp_tsr_pct': v['exp_tsr_pct'], 'exp_ann_pct': v['exp_ann_pct'], 'groups': v['groups']}
                     for h, v in b['scenarios'].items()},
            'top_risks': [short(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False), 160) for x in b['risks'][:3]]}


# 코디네이터(A)가 데이터로 직접 확인한 사항. J가 같은 위험을 두 번 반영하지 않도록 전달한다.
COORD = {
    '005930': '코디네이터 확인: 두 분석가 모두 3Q26 배당(기준일 2026-09-30, 주당 약 4,600원)을 cum_dividends에서 이미 뺐다. '
              '1년 cum_dividends(전문가 8,000~12,800원, 일반 9,900~17,300원)는 4Q26~3Q27 기준일분이다. 반대심문이 제기한 약 2%p 차감은 필요 없다.',
}

S = []
for c, n in NAMES.items():
    p = f'{AN}/data/stocks/{c}.json'
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    r = risk.loc[c]
    p0 = float(r['close'])
    spec = (d.get('spec') or {}).get('result')
    gen = (d.get('gen') or {}).get('result')
    fo = d.get('foren') if (d.get('foren') or {}).get('searches', 0) > 0 else None
    pre = {}
    for h in ('h1', 'h3', 'h5'):
        g = ranks[(ranks.code == c) & (ranks.h == h)]
        if not len(g):
            continue
        x = g.iloc[0]
        grp = {}
        for m, t in br[(br.code == c) & (br.h == h)].groupby('macro'):
            grp[m] = {'p': round(t.prob.sum() * 100), 'tsr_pct_after_shrink': round(((t.prob * (t.price + t['div'])).sum() / t.prob.sum() / p0 - 1) * 100, 1)}
        pre[h] = {'exp_tsr_pct': round(x.exp_cum * 100, 1), 'exp_ann_pct': round(x.exp_ann * 100, 1),
                  'blend_before_shrink_tsr_pct': round(x.e_raw_cum * 100, 1),
                  'median_pct': round(x.median_cum * 100, 1), 'p10_pct': round(x.p10 * 100, 1), 'p90_pct': round(x.p90 * 100, 1),
                  'p_loss_pct': round(x.p_loss * 100), 'cvar10_pct': round(x.cvar10 * 100, 1),
                  'shrink_weight_on_analysts': round(x.shrink_w, 2), 'prior_ann_pct': round(x.prior_ann * 100, 1),
                  'rank_balanced': int(x.rank_bal), 'rank_expected': int(x.rank_er), 'groups_after_shrink': grp}
    f = None
    if fo:
        fr = fo['result']
        f = {'risk_score': fr.get('forensic_risk_score'), 'expected_net_share_change_pct': fr.get('expected_net_share_change_pct'),
             'red_flags': [short(f"[{y['severity']}] {y['issue']}: {y['evidence']}", 220) for y in fr.get('red_flags', [])[:4]],
             'recommended_adjustments': short(fr.get('recommended_adjustments'), 500),
             'tail_risk_notes': short(fr.get('tail_risk_notes'), 350)}
    g = G.get(c, {})
    item = {'code': c, 'name': n, 'sector': SECTOR[c], 'market': r['market'], 'p0': p0,
            'mcap_bn_krw': round(float(r['mcap_krw_bn'])), 'adv60_bn_krw': round(float(r['adv60_krw_bn']), 1),
            'vol_1y_pct': round(float(r['vol_1y']) * 100), 'dd_from_52w_high_pct': round(float(r['dd_from_52w_high']) * 100),
            'default_w_spec': round(settings['w_spec'].get(c, 0.5), 2),
            'dilution_fix_applied': settings['dilution_fix'].get(c) or None,
            'prelim': pre, 'specialist': analyst(spec, p0), 'generalist': analyst(gen, p0), 'forensic': f,
            'risk_G': {'sigma_1y_pct': g.get('sigma_1y_pct'), 'sigma_lr_pct': g.get('sigma_lr_pct'), 'perm_loss_risk_score_1to5': g.get('perm_loss_risk_score'),
                       'liquidity': g.get('liquidity_risk'), 'gap': g.get('gap_risk'), 'discrete_events': short(g.get('discrete_event_risk'), 400)},
            'base_rate_H': bucket.get(c)}
    if c in V:
        item['verification_V'] = {'material_errors': short(V[c]['material_errors'], 1300),
                                  'mismatches': [short(f"{y['claim']} → {y['correct_value']}", 300) for y in V[c]['checks'] if y['status'] == '불일치']}
    if c in COORD:
        item['coordinator_note'] = COORD[c]
    if c in I:
        item['cross_exam_I'] = {'proposed_adjustments': I[c]['adjustments'], 'rationale': short(I[c]['adjustment_rationale'], 1800),
                                'verdict': short(I[c]['verdict'], 700), 'strongest_bear_argument': short(I[c]['strongest_bear_argument'], 500)}
    S.append(item)

ctx = {
    'macro': "Common macro scenarios (Agent C): 기준 50% / 낙관 20% / 비관 30%; probability-weighted index TSR KOSPI 1y 8.5%, 3y 7.7%/yr, 5y 8.9%/yr; "
             "KOSDAQ 6.0% / 5.7% / 7.0%. KTB 1y 3.688%, 3y 3.822%, 5y 3.965%. KOSPI closed 5,735.66 on 2026-10-21 and 5,533.77 on 2026-10-22 (-3.52%). "
             "2026 was an extreme boom-bust year (KOSPI record 9,114.55 on 2026-06-22).",
    'review_caveat': "Cross-examination (I) agents were shown macro-group values labelled 'before shrink' that were in fact after shrinkage (the prior shift was already applied). "
                     "Their multipliers act on pre-shrink branch prices, so the direction and size of each proposed multiplier is usable, but the 'expected TSR after adjustment' figures they quote can be off by the shrink shift.",
    'price_basis': "All TSRs are recomputed from the analysts' structured horizon prices (price_at_horizon + cum_dividends) against the 2026-10-21 close. "
                   "Some analyst narratives quote returns against the 2026-10-20 close; those narrative numbers are not used.",
    'method': "(1) Each analyst's tree is rescaled so that macro groups carry exactly 50/20/30. (2) If the forensic agent expects materially more dilution than an analyst assumed (+2pp or more), "
              "that analyst's prices are cut by the difference (floor 0.80x). (3) Trees are mixed with w_spec / (1 - w_spec). (4) Your adopted multipliers and extra tail are applied. "
              "(5) Shrinkage, applied once: expected gross return = w x blended + (1 - w) x prior, where prior = KTB + forward beta x (KOSPI expectation - KTB) + base-rate bucket alpha (H), "
              "and w = {높음 0.85, 보통 0.70, 낮음 0.50 by the LOWER of the two analysts' confidence} / (1 + (d / D0)^2), d = |log specialist - log generalist annualised expectation|, "
              "D0 = 15%/8%/6% for 1y/3y/5y. (6) Monte Carlo: scenario mixture plus lognormal within-branch noise calibrated to forward volatility (G), 200,000 paths. "
              "(7) Ranks: expected TSR; risk-adjusted (forward Sortino, ties by CVaR10, loss probability, permanent-loss score); balanced = 60% expected / 25% Sortino / 15% CVaR percentile ranks."}

t = open(f'{AN}/workflows/judge_template.js').read()
t = t.replace('__SUMMARIES__', json.dumps(S, ensure_ascii=False)).replace('__CONTEXT__', json.dumps(ctx, ensure_ascii=False))
open(sys.argv[1], 'w').write(t)
print('wrote', sys.argv[1], len(t), 'stocks', len(S), 'with I', sum('cross_exam_I' in s for s in S), 'with V', sum('verification_V' in s for s in S))
