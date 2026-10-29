#!/usr/bin/env python3
"""Merge WF4 writer output (journal) into manual_sections.json. Usage: merge_writer.py <scratchpad> <journal>"""
import json, os, sys, re
base, j = sys.argv[1], sys.argv[2]
lab = {}; w = None
for line in open(j):
    try: e = json.loads(line)
    except Exception: continue
    if e.get('type') == 'started': lab[e.get('key')] = e.get('label')
    if e.get('type') == 'result' and str(lab.get(e.get('key'), '')).startswith('writer') and isinstance(e.get('result'), dict):
        w = e['result']
if not w:
    print('no writer result'); sys.exit(1)
os.makedirs(os.path.join(base, 'wf4'), exist_ok=True)
json.dump(w, open(os.path.join(base, 'wf4', 'writer.json'), 'w'), ensure_ascii=False, indent=1)
mp = os.path.join(base, 'manual_sections.json'); m = json.load(open(mp))
def bare(s): return re.sub(r'\s*\(.*?\)\s*$', '', str(s)).strip()
m['part4_reasons'] = {bare(x['stock']): x['reason'] for x in w.get('part4_reasons', [])}
m['part3_key_factors'] = {bare(x['stock']): x['factor'] for x in w.get('part3_key_factors', [])}
m['part2_notes'] = {bare(x['stock']): x['note'] for x in w.get('part2_notes', [])}
pi = w.get('priced_in_ranking', [])
m['part1_priced_in'] = '; '.join(f"{i+1}. {bare(x['stock'])}({x['degree']}: {x['reason']})" for i, x in enumerate(pi))
m['part8_analysis'] = w.get('part8_analysis', '')
bd = w.get('biggest_disagreements', [])
m['part7_summary'] = w.get('part7_summary', '') + ('\n\n**분석가 간 전망 차이가 가장 컸던 종목**: ' + ' / '.join(bd) if bd else '')
json.dump(m, open(mp, 'w'), ensure_ascii=False, indent=1)
print('merged: part4', len(m['part4_reasons']), 'part2', len(m['part2_notes']), 'priced_in', len(pi), 'part8', len(m['part8_analysis']), 'part7', len(m['part7_summary']))
