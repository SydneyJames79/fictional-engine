#!/usr/bin/env python3
"""Collect WF1/WF1b stock-data results from journals into wf1/stocks/<name>.json (only overwrite if the new result has search_count>0 or no file exists).
Usage: collect_wf1.py <scratchpad> <journal> [...]
"""
import json, os, sys, re

base = sys.argv[1]
for j in sys.argv[2:]:
    for line in open(j):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('type') != 'result':
            continue
        r = e.get('result')
        if not isinstance(r, dict) or 'input_name' not in r:
            continue
        name = r['input_name']
        m = re.search(r'\d+', str(r.get('search_count', '0')))
        n = int(m.group()) if m else 0
        p = os.path.join(base, 'wf1', 'stocks', f'{name}.json')
        old = json.load(open(p)) if os.path.exists(p) else None
        old_n = 0
        if old:
            mm = re.search(r'\d+', str(old.get('search_count', '0')))
            old_n = int(mm.group()) if mm else 0
        if n > 0 or old is None:
            json.dump(r, open(p, 'w'), ensure_ascii=False, indent=1)
            print(f'{name}: saved (searches {n}, prev {old_n}) price={r["price"]["value"]} ({r["price"]["date"]}) quality={r.get("data_quality")}')
        else:
            print(f'{name}: kept previous (new had 0 searches)')
# status
st = {'verified': [], 'unverified': []}
for f in sorted(os.listdir(os.path.join(base, 'wf1', 'stocks'))):
    r = json.load(open(os.path.join(base, 'wf1', 'stocks', f)))
    m = re.search(r'\d+', str(r.get('search_count', '0')))
    n = int(m.group()) if m else 0
    (st['verified'] if n > 0 else st['unverified']).append(r['input_name'])
json.dump(st, open(os.path.join(base, 'wf1', 'status.json'), 'w'), ensure_ascii=False, indent=1)
print('verified', len(st['verified']), 'unverified', st['unverified'])
