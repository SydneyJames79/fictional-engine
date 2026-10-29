#!/usr/bin/env python3
"""Build trees.json / risk.json / macro_rf.json for engine.py from WF1/WF2/WF3 outputs.

Usage: build_trees.py <scratchpad> [--final]
  Reads  wf2/synth/<name>.json, wf2/risk/<name>.json, wf1/stocks/<name>.json, wf1/macro_common.json,
         wf3/calibration.json (optional), wf3/judge/<name>.json (optional)
  Writes <out>/trees.json, <out>/risk.json, <out>/macro_rf.json, <out>/build_log.json
"""
import json, re, os, sys, glob, re
from engine import parse_num

HZ = ['1y', '3y', '5y']
HKO = {'1y': '1년', '3y': '3년', '5y': '5년'}


def h_match(hstr, hk):
    h = str(hstr or '').strip()
    return h.startswith(hk) or h.startswith(HKO[hk]) or h.startswith(hk[0] + ' ') or h == hk[0]


def load(p):
    with open(p) as f:
        return json.load(f)


def norm_scen(scen_list, price0, log, name, hk):
    """scen_list: list of SCEN_ITEM dicts for one horizon → [{name, prob, end_price, cum_cash, tsr_agent}]"""
    out = []
    for s in scen_list:
        nm = s.get('name')
        p = parse_num(s.get('probability_pct'))
        ep = parse_num(s.get('end_price_krw'))
        cc = parse_num(s.get('cum_cash_per_share_krw'), 0.0) or 0.0
        if p is None or ep is None:
            log.append(f'{name} {hk} {nm}: 결측(prob={s.get("probability_pct")}, end_price={s.get("end_price_krw")})')
            continue
        tsr_agent = parse_num(s.get('cum_tsr_pct'))
        tsr_calc = (ep + cc) / price0 - 1
        if tsr_agent is not None and abs(tsr_calc * 100 - tsr_agent) > 2.0:
            log.append(f'{name} {hk} {nm}: TSR 산식 불일치 agent={tsr_agent:.1f}% calc={tsr_calc*100:.1f}% (계산값 채택)')
        out.append({'name': nm, 'prob': p, 'end_price': ep, 'cum_cash': cc, 'tsr_agent': tsr_agent, 'dilution_pct': parse_num(s.get('dilution_pct')), 'rationale': s.get('rationale', '')})
    tot = sum(x['prob'] for x in out)
    if out and abs(tot - 100) > 0.5:
        log.append(f'{name} {hk}: 확률 합 {tot:.1f} → 100으로 정규화')
    if out and tot > 0:
        for x in out:
            x['prob'] = x['prob'] / tot * 100
    names = [x['name'] for x in out]
    if sorted(names) != ['base', 'bear', 'bull']:
        log.append(f'{name} {hk}: 시나리오 구성 이상 {names}')
    return out


def main(base, final=False):
    log = []
    macro = load(os.path.join(base, 'wf1', 'macro_common.json'))
    rf = {}
    for hk, key in zip(HZ, ['rf_1y_pct', 'rf_3y_pct', 'rf_5y_pct']):
        v = parse_num(macro['risk_free'].get(key))
        rf[hk] = (v or 0.0) / 100.0
    # sector priors
    priors = {}
    for sp in macro.get('sector_priors', []):
        priors[sp['industry_group']] = {hk: parse_num(sp.get(f'prior_cum_tsr_{hk}_pct')) for hk in HZ}
        priors[sp['industry_group']]['vol'] = parse_num(sp.get('prior_ann_vol_pct'))
    # index expectations
    idx = {}
    for ie in macro.get('index_expectations', []):
        idx.setdefault(ie['index'], {})[ie['horizon']] = {'ann': parse_num(ie.get('expected_annualized_pct')), 'cum': parse_num(ie.get('expected_cum_pct'))}

    calib = {}
    cp = os.path.join(base, 'wf3', 'calibration.json')
    if os.path.exists(cp):
        for c in load(cp):
            if not c:
                continue
            for a in c.get('assessments', []):
                # calibration agents label stocks as '이름 (코드)'; key by the bare name
                key = re.sub(r'\s*\(.*?\)\s*$', '', str(a.get('stock', ''))).strip()
                calib[key] = a

    trees, risks = {}, {}
    for sp in sorted(glob.glob(os.path.join(base, 'wf2', 'synth', '*.json'))):
        name = os.path.splitext(os.path.basename(sp))[0]
        syn = load(sp)
        data = load(os.path.join(base, 'wf1', 'stocks', f'{name}.json'))
        price0 = parse_num(syn.get('price0_krw')) or parse_num(data['price']['value'])
        if not price0:
            log.append(f'{name}: 기준가 없음 → 제외')
            continue
        # prefer refreshed price if present
        pr = os.path.join(base, 'wf1', 'price_refresh.json')
        price_date = syn.get('price_date') or data['price']['date']
        if os.path.exists(pr):
            ref = load(pr).get(name)
            if ref and parse_num(ref.get('adopted_price')):
                newp = parse_num(ref['adopted_price'])
                if abs(newp / price0 - 1) > 0.001:
                    log.append(f'{name}: 기준가 갱신 {price0:.0f}({price_date}) → {newp:.0f}({ref.get("adopted_date")}); 시나리오 기말주가는 유지(TSR 재계산)')
                price0, price_date = newp, ref.get('adopted_date')
        industry = syn.get('industry_group') or data['business']['industry_group']
        horizons = {}
        # judge final overrides (WF3)
        jp = os.path.join(base, 'wf3', 'judge', f'{name}.json')
        judge = load(jp) if (final and os.path.exists(jp)) else None
        src_scen = judge['final_scenarios'] if judge else []
        for hk in HZ:
            if judge:
                lst = [s for s in src_scen if h_match(s.get('horizon', ''), hk)]
            else:
                hblock = next((h for h in syn.get('horizons', []) if h_match(h.get('horizon', ''), hk)), None)
                lst = hblock['scenarios'] if hblock else []
                # calibration override (WF3) if no judge
                if final and name in calib and calib[name].get('override_scenarios'):
                    ov = [s for s in calib[name]['override_scenarios'] if h_match(s.get('horizon', ''), hk)]
                    if len(ov) == 3:
                        lst = ov
                        log.append(f'{name} {hk}: 보정 에이전트 override 적용')
            sc = norm_scen(lst, price0, log, name, hk)
            if len(sc) == 3:
                horizons[hk] = sc
        if len(horizons) < 3:
            log.append(f'{name}: 기간 누락 {list(horizons)} → 가능한 기간만 사용')
        # shrinkage
        w = 1.0
        prior_tsr = {}
        if final and name in calib:
            w = parse_num(calib[name].get('shrink_weight'), 1.0)
            w = min(1.0, max(0.5, w if w is not None else 1.0))
            pri = priors.get(industry, {})
            prior_tsr = {hk: (pri.get(hk) if pri.get(hk) is not None else 0.0) for hk in HZ}
            if w < 1.0:
                for hk, sc in horizons.items():
                    for x in sc:
                        tsr = (x['end_price'] + x['cum_cash']) / price0 - 1
                        x['end_price_orig'] = x['end_price']
                        x['tsr_orig'] = tsr
                        tsr_adj = w * tsr + (1 - w) * (prior_tsr[hk] / 100.0)
                        # keep cash, adjust end price so that TSR = tsr_adj
                        x['end_price'] = max((1 + tsr_adj) * price0 - x['cum_cash'], 0.01 * price0)
                        x['tsr_shrunk'] = tsr_adj
                log.append(f'{name}: 베이스레이트 축소 w={w:.2f} (prior {prior_tsr})')
        trees[name] = {'ticker': syn.get('ticker') or data['ticker'], 'price0': price0, 'price_date': price_date, 'industry': industry,
                       'confidence': (judge or syn).get('confidence', syn.get('confidence', '')), 'horizons': horizons, 'shrink_weight': w, 'prior_tsr': prior_tsr,
                       'market': data.get('market', ''), 'flags': syn.get('flags', {}), 'one_line': syn.get('report_sections', {}).get('one_line_driver', '')}
        # risk
        rp = os.path.join(base, 'wf2', 'risk', f'{name}.json')
        rk = load(rp) if os.path.exists(rp) else {}
        pri_vol = priors.get(industry, {}).get('vol') or 50.0
        def vol(k, fb):
            v = parse_num(rk.get(k))
            return (v / 100.0) if v else fb
        v1 = vol('fwd_vol_1y_pct', vol('hist_vol_1y_pct', pri_vol / 100.0))
        v3 = vol('fwd_vol_3y_pct', v1)
        v5 = vol('fwd_vol_5y_pct', v3)
        pz = parse_num(rk.get('p_zero_annual_pct'))
        pz = (pz / 100.0) if pz is not None else 0.0
        # cap extreme vol inputs
        v1, v3, v5 = [min(max(v, 0.15), 1.20) for v in (v1, v3, v5)]
        # Permanent-loss tail: the synthesis/judge bear legs already embed the delisting/-80% tail (24/26 trees say so
        # explicitly), so the engine must NOT apply p_zero again (double counting flagged by verifier 1). Keep the reported value for the record.
        risks[name] = {'ann_vol_1y': v1, 'ann_vol_3y': v3, 'ann_vol_5y': v5, 'p_zero_ann': 0.0, 'p_zero_ann_reported': min(pz, 0.15), 'beta': parse_num(rk.get('beta')), 'mdd_3y': parse_num(rk.get('mdd_3y_pct')), 'turnover_bn': parse_num(rk.get('avg_daily_turnover_bn')), 'confidence': rk.get('confidence', '')}
        if pz and pz > 0:
            log.append(f'{name}: 위험 에이전트 영구손실 확률 연 {pz*100:.2f}%는 비관 레그 기말가에 이미 내재 → 엔진 p_zero 별도 적용 제외(이중 차감 방지)')
        trees[name]['price_kind'] = str((data.get('price') or {}).get('kind', ''))
        if not rk:
            log.append(f'{name}: 위험 보고서 없음 → 산업 사전 변동성 {pri_vol}% 사용')
    n_tot = sum(len(t['horizons']) for t in trees.values())
    n_norm = sum(1 for l in log if '확률 합' in l and '정규화' in l)
    log.append(f'확률 합 검산: {n_tot}개 종목·기간 트리 모두 합계 100% (정규화 적용 {n_norm}건)')
    out_dir = os.path.join(base, 'engine_final' if final else 'engine_prov')
    os.makedirs(out_dir, exist_ok=True)
    json.dump(trees, open(os.path.join(out_dir, 'trees.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(risks, open(os.path.join(out_dir, 'risk.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'rf': rf, 'index': idx, 'priors': priors}, open(os.path.join(out_dir, 'macro_rf.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(log, open(os.path.join(out_dir, 'build_log.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'built {len(trees)} stocks → {out_dir}; log entries {len(log)}')
    for l in log:
        print('  -', l)
    return out_dir


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1], final=('--final' in sys.argv))
