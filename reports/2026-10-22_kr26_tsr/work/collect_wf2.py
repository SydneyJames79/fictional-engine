#!/usr/bin/env python3
"""Collect WF2 agent outputs from workflow journals into per-stock files.
Usage: collect_wf2.py <scratchpad> <journal1> [<journal2> ...]
Writes wf2/{spec,gen,forensic,risk,synth}/<name>.json
"""
import json, os, sys

base = sys.argv[1]
journals = sys.argv[2:]
for d in ['spec', 'gen', 'forensic', 'risk', 'synth']:
    os.makedirs(os.path.join(base, 'wf2', d), exist_ok=True)

count = {}
for j in journals:
    label_by_key = {}
    for line in open(j):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('type') == 'started':
            label_by_key[e.get('key')] = e.get('label')
        if e.get('type') != 'result':
            continue
        label = label_by_key.get(e.get('key')) or e.get('label') or ''
        r = e.get('result')
        if not isinstance(r, dict) or not label:
            continue
        kind, _, name = label.partition(':')
        folder = {'spec': 'spec', 'gen': 'gen', 'forensic': 'forensic', 'risk': 'risk', 'synth': 'synth'}.get(kind)
        if not folder:
            continue
        with open(os.path.join(base, 'wf2', folder, f'{name}.json'), 'w') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        count[folder] = count.get(folder, 0) + 1
print('collected:', count)
