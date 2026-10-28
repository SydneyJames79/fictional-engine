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
                             'prob_perm_loss_gt50_5y_pct': b['prob_perm_loss_gt50_5y_pct']}
I = {r['code']: r for r in aux('I_').values()}
V = {r['code']: r for r in aux('V_').values()}


def short(s, n):
    s = s or ''
    return s if len(s) <= n else s[:n] + '…'


def grp_str(groups):
    return ' / '.join(f"{m} {g['p']}%: {g['tsr_pct']:+.1f}%" for m, g in groups.items())


def analyst(r, p0):
    b = analyst_brief(r, p0)
    if not b:
        return None
    d = b['dilution_assumed'] or {}
    return {'confidence': b['confidence'], 'why': short(b['confidence_reason'], 150),
            'view_vs_market': short(b['view_vs_market'], 260),
            'net_share_change_pct_1y3y5y': [d.get('h1'), d.get('h3'), d.get('h5')],
            'by_h': {h: f"E[TSR] {v['exp_tsr_pct']:+.1f}% (연 {v['exp_ann_pct']:+.1f}%) | {grp_str(v['groups'])}" for h, v in b['scenarios'].items()},
            'top_risks': [short(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False), 110) for x in b['risks'][:2]]}


# 코디네이터(A)가 데이터로 직접 확인한 사항. J가 같은 위험을 두 번 반영하지 않도록 전달한다.
COORD = {
    '005930': '코디네이터 확인: 두 분석가 모두 3Q26 배당(기준일 2026-09-30, 주당 약 4,600원)을 cum_dividends에서 이미 뺐다. '
              '1년 cum_dividends(전문가 8,000~12,800원, 일반 9,900~17,300원)는 4Q26~3Q27 기준일분이다. 반대심문이 제기한 약 2%p 차감은 필요 없다.',
}

# 선택: 두 번째 인자로 재심사할 종목 코드(쉼표 구분)를 주면 그 종목만 넣고, 이전 심사 결정을 함께 넘긴다.
SUBSET = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
PREV_J = {}
PREV0 = {}
if SUBSET:
    J0F = os.path.join(AUX, 'J0_final_judge_1차.json')
    if os.path.exists(J0F):
        for s_ in json.load(open(J0F))['result']['stocks']:
            PREV0[s_['code']] = {h: s_['adjustments'][h]['bear_mult'] for h in ('h1', 'h3', 'h5')}
    for f in sorted(os.listdir(AUX)):
        if f.startswith('J_'):
            for s_ in json.load(open(os.path.join(AUX, f)))['result'].get('stocks', []):
                PREV_J[s_['code']] = s_
    # 1차 사실검증(V1) 결과: 재실행으로 덮어써져 1차 심사에 전달되지 않았다.
    V1 = json.load(open(os.path.join(AUX, 'V1_verify_현대차_1차.json')))['result']
    law = next(x for x in V1['checks'] if '특별법' in x['correct_value'])
    note = ('1차 사실검증(V1) 결과로, 검증 재실행 때 파일이 덮어써져 1차 심사에 전달되지 않았다: ' + law['correct_value'] +
            ' 출처: ' + law['source'] + ' V1의 영향 평가: ' + law['impact'])
    COORD['005380'] = note
    for c_ in ('012330', '010690'):
        COORD[c_] = note + ' 이 종목의 비관 분기에도 미국 관세 25% 환원이 들어 있어 같은 사실이 적용될 수 있다.'
    # 자동차 3종목 재심사(J2_rereview_auto)가 일관성을 위해 같은 보정을 권고한 나머지 종목(비관 분기에 관세 25%를 넣은 종목)
    J2A = os.path.join(AUX, 'J2_rereview_auto.json')
    if os.path.exists(J2A):
        j2 = json.load(open(J2A))['result']
        prec = '; '.join(f"{s_['name']} 비관 배수 " + ', '.join(f"{h} {PREV0.get(s_['code'], {}).get(h, '?')}→{s_['adjustments'][h]['bear_mult']}" for h in ('h1', 'h3', 'h5'))
                         for s_ in j2['stocks'])
        for c_ in ('307950', '370090'):
            COORD[c_] = (note + ' 이 종목의 비관 분기에도 미국 관세 25%가 들어 있다(분석가 서술 기준). '
                         '같은 사실로 먼저 재심사한 자동차 3종목의 처리 방식: ' + j2['global_notes'].split('3)')[0].strip() +
                         ' 결과: ' + prec + '. 그 재심사는 비관 분기에 관세 25%를 넣은 다른 자동차·부품 종목에도 같은 보정이 필요하다고 권고했다. '
                         '이 종목의 노출 경로(그룹 IT 예산 또는 고객 설비투자 이연)가 완성차·부품사보다 간접적인지 따져 상향 폭을 정하라.')
    V1s = json.load(open(os.path.join(AUX, 'V1_verify_삼성전자_1차.json')))['result']
    COORD['005930'] = (COORD.get('005930', '') + ' 1차 사실검증(V1) 결과로, 검증 재실행 때 파일이 덮어써져 1차 심사에 전달되지 않았다: ' + V1s['material_errors'] +
                       ' 불일치 항목: ' + ' / '.join(f"{x['claim']} → {x['correct_value']}" for x in V1s['checks'] if x['status'] == '불일치'))

S = []
for c, n in NAMES.items():
    if SUBSET and c not in SUBSET:
        continue
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
        gtxt = ' / '.join(f"{m} {g['p']}%: {g['tsr_pct_after_shrink']:+.1f}%" for m, g in grp.items())
        pre[h] = (f"E[TSR] {x.exp_cum*100:+.1f}% (연 {x.exp_ann*100:+.1f}%), 축소 전 혼합 {x.e_raw_cum*100:+.1f}%, 중앙 {x.median_cum*100:+.1f}%, "
                  f"P10 {x.p10*100:+.1f}%, P90 {x.p90*100:+.1f}%, 손실확률 {x.p_loss*100:.0f}%, CVaR10 {x.cvar10*100:+.1f}%, "
                  f"축소가중 w {x.shrink_w:.2f}, 사전값 연 {x.prior_ann*100:.1f}%, 균형순위 {int(x.rank_bal)}, 기대순위 {int(x.rank_er)} | 축소 후 그룹: {gtxt}")
    f = None
    if fo:
        fr = fo['result']
        f = {'risk_score': fr.get('forensic_risk_score'), 'expected_net_share_change_pct': {k: fr.get('expected_net_share_change_pct', {}).get(k) for k in ('h1', 'h3', 'h5')},
             'red_flags': [short(f"[{y['severity']}] {y['issue']}: {y['evidence']}", 160) for y in fr.get('red_flags', [])[:3]],
             'recommended_adjustments': short(fr.get('recommended_adjustments'), 300),
             'tail_risk_notes': short(fr.get('tail_risk_notes'), 200)}
    g = G.get(c, {})
    item = {'code': c, 'name': n, 'sector': SECTOR[c], 'market': r['market'], 'p0': p0,
            'mcap_bn_krw': round(float(r['mcap_krw_bn'])), 'adv60_bn_krw': round(float(r['adv60_krw_bn']), 1),
            'vol_1y_pct': round(float(r['vol_1y']) * 100), 'dd_from_52w_high_pct': round(float(r['dd_from_52w_high']) * 100),
            'default_w_spec': round(settings['w_spec'].get(c, 0.5), 2),
            'dilution_fix_applied': {r: {h: round(f, 3) for h, f in d.items() if f < 0.9999} for r, d in (settings['dilution_fix'].get(c) or {}).items() if any(f < 0.9999 for f in d.values())} or None,
            'prelim': pre, 'specialist': analyst(spec, p0), 'generalist': analyst(gen, p0), 'forensic': f,
            'risk_G': {'sigma_1y_pct': g.get('sigma_1y_pct'), 'sigma_lr_pct': g.get('sigma_lr_pct'), 'perm_loss_risk_score_1to5': g.get('perm_loss_risk_score'),
                       'liquidity': g.get('liquidity_risk'), 'discrete_events': short(g.get('discrete_event_risk'), 250)},
            'base_rate_H': bucket.get(c)}
    if c in V:
        item['verification_V'] = {'material_errors': short(V[c]['material_errors'], 1300),
                                  'mismatches': [short(f"{y['claim']} → {y['correct_value']}", 300) for y in V[c]['checks'] if y['status'] == '불일치']}
    if c in COORD:
        item['coordinator_note'] = COORD[c]
    if SUBSET and c in PREV_J:
        pj = PREV_J[c]
        item['previous_J_decision'] = {k: pj[k] for k in ('w_spec', 'w_spec_reason', 'adjustments', 'adjustment_reason', 'final_confidence', 'confidence_reason')}
    if c in I:
        item['cross_exam_I'] = {'proposed_adjustments': I[c]['adjustments'], 'rationale': short(I[c]['adjustment_rationale'], 1800),
                                'verdict': short(I[c]['verdict'], 700), 'strongest_bear_argument': short(I[c]['strongest_bear_argument'], 500)}
    S.append(item)

scope = ('This is a full review of all 26 stocks.' if not SUBSET else
         'This is a RE-REVIEW of only the stocks below, triggered after the first review: independent QA found that a first-round verification (V1) result was overwritten by a re-run and never reached you. '
         'Each summary includes your previous decision (previous_J_decision) and the recovered V1 finding in coordinator_note. Keep the same rules as the first review. '
         'Change your previous decision only where the recovered evidence justifies it, and say what changed and why in adjustment_reason. Keep everything else as it was.' + (' Stocks 307950 and 370090 were not in the first re-review: that re-review recommended giving every other auto/parts stock whose bear branches assume a 25% US tariff the same correction, ''so apply the same method for consistency, scaled to each stock\'s own exposure (its coordinator_note gives the precedent).' if SUBSET & {'307950', '370090'} else ''))
ctx = {
    'scope_note': scope,
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
