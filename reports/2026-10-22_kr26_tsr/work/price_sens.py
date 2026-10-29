#!/usr/bin/env python3
"""Unified price-date sensitivity: for stocks whose basis price predates 10/22 (or is undated), estimate a 10/22 price
as price0 x (1 + beta x index_return_1022) and re-run the engine. Usage: price_sens.py <scratchpad> <engine_final>"""
import json, os, re, shutil, subprocess, sys
base, eng = sys.argv[1], sys.argv[2]
IDX = {'KOSPI': -0.0352, 'KOSDAQ': -0.0362}
trees = json.load(open(os.path.join(eng, 'trees.json')))
risk = json.load(open(os.path.join(eng, 'risk.json')))
res = json.load(open(os.path.join(eng, 'results.json')))
out = os.path.join(base, 'engine_sens'); os.makedirs(out, exist_ok=True)
t2 = json.loads(json.dumps(trees)); adj = {}
for n, t in t2.items():
    m = re.search(r'2026-(\d\d)-(\d\d)', str(t.get('price_date', '')))
    stale = (not m) or (m.group(1), m.group(2)) < ('10', '22')
    if not stale:
        continue
    beta = risk[n].get('beta') or 1.0
    p_old = t['price0']; p_new = p_old * (1 + beta * IDX.get(t.get('market') or 'KOSPI', -0.0352))
    w = t.get('shrink_weight', 1.0); prior = t.get('prior_tsr', {})
    for hk, sc in t['horizons'].items():
        for x in sc:
            ep0 = x.get('end_price_orig', x['end_price'])
            tsr0 = (ep0 + x['cum_cash']) / p_new - 1
            tsr_adj = w * tsr0 + (1 - w) * (prior.get(hk, 0.0) / 100.0) if w < 1.0 else tsr0
            x['end_price'] = max((1 + tsr_adj) * p_new - x['cum_cash'], 0.01 * p_new)
    t['price0'] = p_new; adj[n] = (p_old, p_new, beta)
json.dump(t2, open(os.path.join(out, 'trees.json'), 'w'), ensure_ascii=False)
shutil.copy(os.path.join(eng, 'risk.json'), os.path.join(out, 'risk.json'))
shutil.copy(os.path.join(eng, 'macro_rf.json'), os.path.join(out, 'macro_rf.json'))
subprocess.run([sys.executable, os.path.join(base, 'engine.py'), out], check=True, stdout=subprocess.DEVNULL)
r2 = json.load(open(os.path.join(out, 'results.json')))
rows = []
for n in sorted(trees, key=lambda x: res['rankings']['1y'][x]['balanced_rank']):
    rows.append({'name': n, 'ticker': trees[n]['ticker'], 'price0': trees[n]['price0'], 'price_adj': t2[n]['price0'], 'adjusted': n in adj,
                 'e1_base': res['results'][n]['horizons']['1y']['exp_cum'], 'e1_sens': r2['results'][n]['horizons']['1y']['exp_cum'],
                 'b1_base': res['rankings']['1y'][n]['balanced_rank'], 'b1_sens': r2['rankings']['1y'][n]['balanced_rank'],
                 'b3_base': res['rankings']['3y'][n]['balanced_rank'], 'b3_sens': r2['rankings']['3y'][n]['balanced_rank'],
                 'b5_base': res['rankings']['5y'][n]['balanced_rank'], 'b5_sens': r2['rankings']['5y'][n]['balanced_rank']})
changed = [(r['name'], r['b1_base'], r['b1_sens'], r['b3_base'], r['b3_sens'], r['b5_base'], r['b5_sens']) for r in rows if (r['b1_base'], r['b3_base'], r['b5_base']) != (r['b1_sens'], r['b3_sens'], r['b5_sens'])]
top5_same = all(res['rankings'][h] and sorted(res['rankings'][h], key=lambda x: res['rankings'][h][x]['balanced_rank'])[:5] == sorted(r2['rankings'][h], key=lambda x: r2['rankings'][h][x]['balanced_rank'])[:5] for h in ['1y', '3y', '5y'])
intro = (f"기준가가 10/22 이전이거나 날짜가 확인되지 않은 {len(adj)}개 종목의 기준가에 10/22 지수 수익률(KOSPI -3.52%, KOSDAQ -3.62%) × 베타(정량·위험 에이전트 추정)를 곱해 '통일 추정 기준가'를 만들고, 시나리오 기말주가·현금환원은 그대로 둔 채 베이스레이트 축소와 몬테카를로를 다시 돌렸다. "
         "10/22 이전 날짜의 중간 등락(예: 케이엠더블유 10/07 이후, 엘앤씨바이오 10/16 급등)은 반영하지 않은 어림이며, 실제 10/22 종가를 확인하면 이 표를 대체해야 한다.")
summary = ("균형형 종합순위가 바뀐 종목(1년/3년/5년): " + (', '.join(f"{c[0]} {c[1]}→{c[2]} / {c[3]}→{c[4]} / {c[5]}→{c[6]}" for c in changed) if changed else '없음') + '. ' +
           ("세 기간의 균형형 상위 5개 구성은 바뀌지 않았다." if top5_same else "상위 5개 구성이 일부 바뀌므로 해당 구간은 '순위 불안정'으로 본다."))
json.dump({'intro': intro, 'rows': rows, 'summary': summary, 'adjusted': {n: {'old': v[0], 'new': v[1], 'beta': v[2]} for n, v in adj.items()}}, open(os.path.join(out, 'sens_table.json'), 'w'), ensure_ascii=False, indent=1)
print('adjusted', len(adj), '| rank changes:', len(changed)); print(summary[:1500])
