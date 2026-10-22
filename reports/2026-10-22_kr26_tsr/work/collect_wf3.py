#!/usr/bin/env python3
"""Collect WF3 outputs: wf3/calibration.json (list), wf3/bear/<name>.json, wf3/judge/<name>.json
Usage: collect_wf3.py <scratchpad> <journal> [...]
"""
import json, os, sys

base = sys.argv[1]
os.makedirs(os.path.join(base, 'wf3', 'bear'), exist_ok=True)
os.makedirs(os.path.join(base, 'wf3', 'judge'), exist_ok=True)
calibs = {}
nb = nj = 0
for j in sys.argv[2:]:
    lab = {}
    for line in open(j):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('type') == 'started':
            lab[e.get('key')] = e.get('label')
        if e.get('type') != 'result':
            continue
        label = lab.get(e.get('key')) or ''
        r = e.get('result')
        if not isinstance(r, dict) or not label:
            continue
        kind, _, name = label.partition(':')
        if kind == 'calib':
            calibs[r.get('industry_group') or name] = r
        elif kind == 'bear':
            json.dump(r, open(os.path.join(base, 'wf3', 'bear', f'{name}.json'), 'w'), ensure_ascii=False, indent=1); nb += 1
        elif kind == 'judge':
            json.dump(r, open(os.path.join(base, 'wf3', 'judge', f'{name}.json'), 'w'), ensure_ascii=False, indent=1); nj += 1
json.dump(list(calibs.values()), open(os.path.join(base, 'wf3', 'calibration.json'), 'w'), ensure_ascii=False, indent=1)
print('calibrations:', list(calibs.keys()), '| bear:', nb, '| judge:', nj)
