#!/usr/bin/env python3
"""Prepare judge-stage args (3 batches) from wf3/args.json bear targets + collected bear/calibration files."""
import json, os, sys
base = sys.argv[1]
a = json.load(open(os.path.join(base, 'wf3', 'args.json')))
targets = []
for t in a['bearTargets']:
    bp = os.path.join(base, 'wf3', 'bear', f"{t['name']}.json")
    if not os.path.exists(bp):
        print('missing bear for', t['name'])
        continue
    t2 = dict(t)
    t2['bearPath'] = bp
    t2['calibPath'] = os.path.join(base, 'wf3', 'calibration.json')
    targets.append(t2)
n = len(targets)
batches = [targets[i::3] for i in range(3)]
for i, b in enumerate(batches):
    d = {'stage': 'judge', 'searchAllowed': False, 'groups': [], 'bearTargets': b}
    json.dump(d, open(os.path.join(base, 'wf3', f'args_judge_{i+1}.json'), 'w'), ensure_ascii=False)
    print(f'=== judge {i+1} ===', json.dumps(d, ensure_ascii=False))
