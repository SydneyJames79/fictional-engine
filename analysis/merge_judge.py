"""1차 최종심사(J0)에 재심사(J2_*) 결과를 덮어써 최종 심사 파일(J_final_judge.json)을 만든다.

사용: python3 analysis/merge_judge.py
재심사는 독립 검증(Q)이 찾은 문제(덮어써진 1차 사실검증 V1)를 반영하려고 일부 종목에만 돌렸다.
재심사 파일은 이름순으로 적용하므로 같은 종목이 두 번 재심사되면 뒤 파일이 이긴다.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
AUX = os.path.join(HERE, 'data', 'aux')

j0 = json.load(open(os.path.join(AUX, 'J0_final_judge_1차.json')))
stocks = {s['code']: s for s in j0['result']['stocks']}
order = [s['code'] for s in j0['result']['stocks']]
rereview = {}
for f in sorted(glob.glob(os.path.join(AUX, 'J2_*.json'))):
    d = json.load(open(f))
    for s in d['result']['stocks']:
        stocks[s['code']] = s
        rereview[s['code']] = {'file': os.path.basename(f), 'run': d['run'],
                               'global_notes': d['result'].get('global_notes', ''), 'double_count_check': d['result'].get('double_count_check', '')}
out = {'label': 'J final judge (1차 심사 + 재심사 병합)', 'run': j0['run'], 'searches': 0,
       'result': {**j0['result'], 'stocks': [stocks[c] for c in order]}, 'rereview': rereview}
json.dump(out, open(os.path.join(AUX, 'J_final_judge.json'), 'w'), ensure_ascii=False, indent=1)
print('merged', len(order), 'stocks; re-reviewed', sorted(rereview))
