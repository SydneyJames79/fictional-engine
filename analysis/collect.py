"""모든 워크플로 journal에서 종목별 에이전트 결과를 모아 data/stocks/{code}.json으로 저장한다.

같은 역할의 결과가 여러 번 있으면 가장 나중 것을 쓴다(재실행 대비). 검색 횟수도 함께 기록한다.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from journal_reader import BASE, search_count  # noqa: E402
from workflows.build_stock_script import NAMES  # noqa: E402

BYNAME = {v: k for k, v in NAMES.items()}
OUT = os.path.join(os.path.dirname(__file__), 'data', 'stocks')
os.makedirs(OUT, exist_ok=True)


def collect():
    found = {}
    runs = sorted(glob.glob(os.path.join(BASE, 'wf_*')), key=os.path.getmtime)
    for run in runs:
        labels = {}
        jp = os.path.join(run, 'journal.jsonl')
        if not os.path.exists(jp):
            continue
        for line in open(jp):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') == 'started':
                labels[d['agentId']] = d.get('label', '')
            elif d.get('type') == 'result':
                lab = labels.get(d.get('agentId'), '')
                parts = lab.split(' ', 2)
                if len(parts) < 3 or parts[0] not in ('D', 'G', 'E'):
                    continue
                name = parts[2]
                code = BYNAME.get(name)
                if not code or d.get('result') is None:
                    continue
                role = {'D': 'spec', 'G': 'gen', 'E': 'foren'}[parts[0]]
                n = search_count(os.path.basename(run), d['agentId'])
                found.setdefault(code, {})[role] = {'result': d['result'], 'searches': n, 'run': os.path.basename(run)}
    for code, roles in found.items():
        json.dump({'code': code, 'name': NAMES[code], **roles}, open(os.path.join(OUT, f'{code}.json'), 'w'), ensure_ascii=False, indent=1)
    return found


if __name__ == '__main__':
    f = collect()
    for c in NAMES:
        r = f.get(c, {})
        print(c, NAMES[c], {k: (v['searches'], v['run'][-6:]) for k, v in r.items()})
