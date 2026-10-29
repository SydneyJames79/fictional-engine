#!/usr/bin/env python3
"""Write WF4 args: prep_wf4_args.py <scratchpad> <engine_dir> <report_md> [stage]"""
import json, os, sys
base, eng, rep = sys.argv[1], sys.argv[2], sys.argv[3]
stage = sys.argv[4] if len(sys.argv) > 4 else 'all'
P = {'tables': os.path.join(eng, 'tables.json'), 'trees': os.path.join(eng, 'trees.json'), 'results': os.path.join(eng, 'results.json'),
     'synthDir': os.path.join(base, 'wf2', 'synth'), 'stocksDir': os.path.join(base, 'wf1', 'stocks'), 'macro': os.path.join(base, 'wf1', 'macro_common.json'),
     'risk': os.path.join(eng, 'risk.json'), 'macroRf': os.path.join(eng, 'macro_rf.json'), 'engine': os.path.join(base, 'engine.py'), 'report': rep}
os.makedirs(os.path.join(base, 'wf4'), exist_ok=True)
out = {'stage': stage, 'paths': P}
fp = os.path.join(base, 'wf4', f'args_{stage}.json')
json.dump(out, open(fp, 'w'), ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
