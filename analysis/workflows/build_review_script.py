"""반대심문(I)·사실검증(V)·민감도(S) 워크플로 스크립트를 생성한다(도시에와 예비 지표 포함)."""
import json
import os
import sys

import pandas as pd

AN = '/home/user/fictional-engine/analysis'
sys.path.insert(0, AN)
from dossier import build  # noqa: E402
from workflows.build_stock_script import NAMES, SECTOR  # noqa: E402

ranks = pd.read_csv(f'{AN}/output/prelim_ranks.csv', dtype={'code': str})
risk = pd.read_csv(f'{AN}/data/risk_metrics_full_1021.csv', dtype={'code': str}).set_index('code')
br = pd.read_csv(f'{AN}/output/prelim_branches.csv', dtype={'code': str})
macro = json.load(open(f'{AN}/data/macro.json'))['synth']

D, summaries = {}, []
for c, n in NAMES.items():
    if not os.path.exists(f'{AN}/data/stocks/{c}.json'):
        continue
    p0 = float(risk.loc[c, 'close'])
    dz = build(c, p0)
    pre = {}
    for h in ('h1', 'h3', 'h5'):
        g = ranks[(ranks.code == c) & (ranks.h == h)]
        if len(g):
            r = g.iloc[0]
            grp = br[(br.code == c) & (br.h == h)].groupby('macro').apply(
                lambda t: {'p': round(t.prob.sum() * 100), 'tsr_pct': round(((t['prob'] * (t['price'] + t['div'])).sum() / t.prob.sum() / p0 - 1) * 100, 1)},
                include_groups=False).to_dict()
            pre[h] = {'exp_tsr_pct': round(r.exp_cum * 100, 1), 'exp_ann_pct': round(r.exp_ann * 100, 1), 'median_pct': round(r.median_cum * 100, 1),
                      'p10_pct': round(r.p10 * 100, 1), 'p90_pct': round(r.p90 * 100, 1), 'p_loss_pct': round(r.p_loss * 100), 'rank_balanced': int(r.rank_bal),
                      'rank_expected': int(r.rank_er), 'blended_groups_before_shrink': grp}
    D[c] = {'code': c, 'name': n, 'dossier': dz, 'prelim': pre}
    sp = dz.get('specialist') or {}
    summaries.append({'code': c, 'name': n, 'sector': SECTOR[c], 'market': risk.loc[c, 'market'], 'p0': p0,
                      'business': (json.load(open(f'{AN}/data/stocks/{c}.json')).get('spec', {}).get('result', {}) or {}).get('business_and_moat', '')[:700],
                      'market_implied': (sp.get('market_implied') or '')[:500]})
ctx = {'macro': f"Common macro scenarios (Agent C): 기준 50% / 낙관 20% / 비관 30%; probability-weighted index TSR KOSPI 1y 8.5%, 3y 7.7%/yr, 5y 8.9%/yr; KOSDAQ 6.0% / 5.7% / 7.0%. KTB 1y 3.688%, 3y 3.822%, 5y 3.965%. KOSPI closed 5,735.66 on 2026-10-21 and 5,533.77 on 2026-10-22 (-3.52%).",
       'sens_summaries': summaries}
# 스크립트 크기 한도(512KB) 때문에 도시에는 반대심문·검증 대상 종목만 넣는다(두 번째 인자: 쉼표로 구분한 코드).
if len(sys.argv) > 2 and sys.argv[2]:
    keep = set(sys.argv[2].split(','))
    D = {c: v for c, v in D.items() if c in keep}
t = open(f'{AN}/workflows/review_template.js').read()
t = t.replace('__DOSSIERS__', json.dumps(D, ensure_ascii=False)).replace('__CONTEXT__', json.dumps(ctx, ensure_ascii=False))
open(sys.argv[1], 'w').write(t)
print('wrote', sys.argv[1], len(t.encode()), 'bytes; dossiers', len(D))
