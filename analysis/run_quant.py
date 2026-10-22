"""수집된 에이전트 결과로 정량 순위를 계산하고 결과 파일을 저장한다.

사용: python3 analysis/run_quant.py [prelim|final]
산출: analysis/output/{stage}_metrics.csv, {stage}_ranks.csv, {stage}_branches.csv, {stage}_settings.json
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pipeline import analyse, rank_table, forward_sigma, CONF  # noqa: E402
from workflows.build_stock_script import NAMES  # noqa: E402

OUT = os.path.join(HERE, 'output')
os.makedirs(OUT, exist_ok=True)
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'prelim'

macro = json.load(open(os.path.join(HERE, 'data', 'macro.json')))['synth']
RF = {'h1': macro['rf']['h1_pct'] / 100, 'h3': macro['rf']['h3_pct'] / 100, 'h5': macro['rf']['h5_pct'] / 100}
IDX = {'KOSPI': {k: v / 100 for k, v in {'h1': macro['index_expected_pct']['kospi']['h1_cum'], 'h3': macro['index_expected_pct']['kospi']['h3_ann'], 'h5': macro['index_expected_pct']['kospi']['h5_ann']}.items()},
       'KOSDAQ': {k: v / 100 for k, v in {'h1': macro['index_expected_pct']['kosdaq']['h1_cum'], 'h3': macro['index_expected_pct']['kosdaq']['h3_ann'], 'h5': macro['index_expected_pct']['kosdaq']['h5_ann']}.items()}}
risk = pd.read_csv(os.path.join(HERE, 'data', 'risk_metrics_full_1021.csv'), dtype={'code': str}).set_index('code')


def load_aux(prefix):
    out = []
    d = os.path.join(HERE, 'data', 'aux')
    for f in sorted(os.listdir(d)):
        if f.startswith(prefix):
            out.append(json.load(open(os.path.join(d, f))))
    return out


def beta_fwd(r):
    return 0.67 * (0.5 * r['beta_1y_KOSPI'] + 0.5 * r['beta_3y_KOSPI']) + 0.33


def build_inputs():
    stocks, settings = {}, {'dilution_fix': {}, 'w_spec': {}, 'prior_ann': {}, 'sigma': {}, 'notes': []}
    # H 사전값(버킷 알파). 없으면 0.
    h = load_aux('H_base_rates')
    alpha = {}
    if h:
        for b in h[-1]['result']['priors']:
            for m in b['members']:
                for c, n in NAMES.items():
                    if n in m or c in m:
                        alpha[c] = b['alpha_vs_capm_prior_pct'] / 100
    # G 위험 검토(시그마 덮어쓰기)
    g = load_aux('G_risk_review')
    gmap = {s['code']: s for s in g[-1]['result']['stocks']} if g else {}
    judge = load_aux('J_')
    jw = {}
    if judge:
        for s in judge[-1]['result'].get('stocks', []):
            jw[s['code']] = s
    for c, n in NAMES.items():
        p = os.path.join(HERE, 'data', 'stocks', f'{c}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        spec = d.get('spec', {}).get('result')
        gen = d.get('gen', {}).get('result')
        if spec is None and gen is None:
            continue
        r = risk.loc[c]
        p0 = float(r['close'])
        fo = d.get('foren') if d.get('foren', {}).get('searches', 0) > 0 else None
        dil = {}
        if fo:
            fr = fo['result']['expected_net_share_change_pct']
            for role, res in (('spec', spec), ('gen', gen)):
                if res is None:
                    continue
                a = res['net_share_change_assumed_pct']
                dil[role] = {}
                for k in ('h1', 'h3', 'h5'):
                    da, df_ = a[k] / 100, fr[k] / 100
                    f = 1.0
                    if df_ > da + 0.02:          # 포렌식이 더 큰 희석을 보면 차이만큼 주당가치를 낮춘다(보수적 비대칭)
                        f = max((1 + da) / (1 + df_), 0.80)
                    dil[role][k] = f
        settings['dilution_fix'][c] = dil
        cs = CONF.get(spec['confidence'], 1) if spec else 1
        cg = CONF.get(gen['confidence'], 1) if gen else 1
        w = min(max(0.5 + 0.1 * (cs - cg), 0.35), 0.65)
        if c in jw and jw[c].get('w_spec') is not None:
            w = jw[c]['w_spec']
        settings['w_spec'][c] = w
        b = beta_fwd(r)
        pr = {k: RF[k] + b * (IDX['KOSPI'][k] - RF[k]) + alpha.get(c, 0.0) for k in ('h1', 'h3', 'h5')}
        settings['prior_ann'][c] = pr
        s1, slr = forward_sigma(r.to_dict())
        if c in gmap:
            s1, slr = gmap[c]['sigma_1y_pct'] / 100, gmap[c]['sigma_lr_pct'] / 100
        settings['sigma'][c] = {'s1': s1, 'slr': slr}
        stocks[c] = {'name': n, 'p0': p0, 'market': r['market'], 'spec': spec, 'gen': gen, 'dil_fix': dil,
                     'sigma_override': {'s1': s1, 'slr': slr}, 'prior_by_h': pr}
    return stocks, settings


def main():
    stocks, settings = build_inputs()
    # 반대심문 채택분(최종 심사)
    adjustments = {}
    for j in load_aux('J_'):
        for s in j['result'].get('stocks', []):
            if s.get('adjustments'):
                adjustments[s['code']] = s['adjustments']
    # 기간별 사전값을 쓰기 위해 기간마다 따로 돌린다
    frames, br_frames, logs = [], [], []
    for key in ('h1', 'h3', 'h5'):
        pri = {c: s['prior_by_h'][key] for c, s in stocks.items()}
        df, br, log = analyse(stocks, risk.to_dict('index'), RF, IDX, pri, settings['w_spec'], adjustments, n_sim=200_000, horizons=[key])
        frames.append(df)
        br_frames.append(br)
        logs += log
    df = pd.concat(frames)
    br = pd.concat(br_frames)
    perm = {}
    for g in load_aux('G_risk_review'):
        for s in g['result']['stocks']:
            perm[s['code']] = s['perm_loss_risk_score']
    rk = rank_table(df, perm)
    rk.to_csv(os.path.join(OUT, f'{STAGE}_ranks.csv'), index=False)
    br.to_csv(os.path.join(OUT, f'{STAGE}_branches.csv'), index=False)
    json.dump({**settings, 'tree_fix_log': logs, 'rf': RF, 'index': IDX}, open(os.path.join(OUT, f'{STAGE}_settings.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    cols = ['name', 'h', 'rank_bal', 'rank_er', 'rank_ra', 'exp_cum', 'exp_ann', 'median_cum', 'p10', 'p90', 'p_loss', 'p_loss30', 'cvar10', 'sortino', 'shrink_w', 'e_spec_ann', 'e_gen_ann']
    pd.set_option('display.width', 250)
    for key in ('h1', 'h3', 'h5'):
        print(rk[rk.h == key].sort_values('rank_bal')[cols].round(3).to_string(index=False))
    print('tree fixes:', len(logs))


if __name__ == '__main__':
    main()
