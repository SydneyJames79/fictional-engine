#!/usr/bin/env python3
"""Prepare WF3 args (calibration groups + bear targets) from provisional engine results.
Usage: prep_wf3_args.py <scratchpad> <engine_prov_dir>
Writes <scratchpad>/wf3/args.json and <engine_prov_dir>/provisional_summary.json
"""
import json, os, sys

base, eng = sys.argv[1], sys.argv[2]
res = json.load(open(os.path.join(eng, 'results.json')))
trees = json.load(open(os.path.join(eng, 'trees.json')))
R, RK = res['results'], res['rankings']
HZ = ['1y', '3y', '5y']

# provisional summary for agents (compact)
summary = {'note': '잠정 몬테카를로 결과(베이스레이트 보정·반대심문 전). 순위는 균형형 종합순위.', 'rf': res['rf'], 'stocks': {}}
for n in R:
    s = {'ticker': trees[n]['ticker'], 'price0': trees[n]['price0'], 'price_date': trees[n]['price_date'], 'industry': trees[n]['industry'], 'confidence': trees[n].get('confidence')}
    for hk in HZ:
        if hk in R[n]['horizons']:
            r = R[n]['horizons'][hk]
            s[hk] = {'exp_cum_pct': round(r['exp_cum'] * 100, 1), 'exp_ann_pct': round(r['exp_ann'] * 100, 1), 'median_pct': round(r['median'] * 100, 1), 'p10_pct': round(r['p10'] * 100, 1), 'p90_pct': round(r['p90'] * 100, 1), 'p_loss_pct': round(r['p_loss'] * 100, 1), 'p_loss30_pct': round(r['p_loss30'] * 100, 1), 'sortino': round(r['sortino'], 2), 'cvar10_pct': round(r['cvar10'] * 100, 1), 'scen_tsr_pct': {k: round(v * 100, 1) for k, v in r['scen_tsr'].items()}, 'probs': [round(p, 0) for p in r['probs']],
                     'balanced_rank': RK[hk][n]['balanced_rank'], 'ret_rank': RK[hk][n]['ret_rank'], 'ra_rank': RK[hk][n]['ra_rank']}
    summary['stocks'][n] = s
json.dump(summary, open(os.path.join(eng, 'provisional_summary.json'), 'w'), ensure_ascii=False, indent=1)

macro = os.path.join(base, 'wf1', 'macro_common.json')
prov = os.path.join(eng, 'provisional_summary.json')
groups = {}
for n in trees:
    g = trees[n]['industry']
    groups.setdefault(g, []).append({'name': n, 'ticker': trees[n]['ticker'], 'synthPath': os.path.join(base, 'wf2', 'synth', f'{n}.json')})
group_args = [{'industry': g, 'stocks': lst, 'macroPath': macro, 'provisionalPath': prov} for g, lst in groups.items()]

# bear targets: union of balanced top-5 and ret top-3 per horizon
targets = []
for hk in HZ:
    rk = RK[hk]
    for n in sorted(rk, key=lambda x: rk[x]["balanced_rank"])[:7] + sorted(rk, key=lambda x: rk[x]["ret_rank"])[:4]:
        if n not in targets:
            targets.append(n)
target_args = [{'name': n, 'ticker': trees[n]['ticker'], 'dataPath': os.path.join(base, 'wf1', 'stocks', f'{n}.json'), 'synthPath': os.path.join(base, 'wf2', 'synth', f'{n}.json'),
                'specPath': os.path.join(base, 'wf2', 'spec', f'{n}.json'), 'genPath': os.path.join(base, 'wf2', 'gen', f'{n}.json'), 'forPath': os.path.join(base, 'wf2', 'forensic', f'{n}.json'),
                'macroPath': macro, 'provisionalPath': prov} for n in targets]
os.makedirs(os.path.join(base, 'wf3'), exist_ok=True)
json.dump({'searchAllowed': False, 'groups': group_args, 'bearTargets': target_args}, open(os.path.join(base, 'wf3', 'args.json'), 'w'), ensure_ascii=False, indent=1)
print('groups:', {g: len(l) for g, l in groups.items()})
print('bear targets:', targets)
