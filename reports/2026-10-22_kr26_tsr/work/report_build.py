#!/usr/bin/env python3
"""Assemble the final Korean report (Markdown) from all artifacts.
Usage: report_build.py <scratchpad> <engine_dir> <out_md>
Manual sections (Part 1 commentary, Part 9, extra notes) are read from <scratchpad>/manual_sections.json if present.
"""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import parse_num
from report_tables import fmt_pct, fmt_pct_plain, fmt_krw, fmt_mcap, HZ, HZN

END = {'1y': '2027-10-22', '3y': '2029-10-22', '5y': '2031-10-22'}


def load(p, default=None):
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


def na(x):
    return x if (x not in (None, '', 'N/A', 'null')) else 'N/A'


def main(base, eng, out_md):
    res = load(os.path.join(eng, 'results.json'))
    trees = load(os.path.join(eng, 'trees.json'))
    tables_md = open(os.path.join(eng, 'tables.md')).read()
    tj = load(os.path.join(eng, 'tables.json'))
    macro = load(os.path.join(base, 'wf1', 'macro_common.json'))
    manual = load(os.path.join(base, 'manual_sections.json'), {})
    build_log = load(os.path.join(eng, 'build_log.json'), [])
    R, RK = res['results'], res['rankings']
    names = list(trees.keys())
    stocks_data = {n: load(os.path.join(base, 'wf1', 'stocks', f'{n}.json')) for n in sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(base, 'wf1', 'stocks', '*.json')))}
    synth = {n: load(os.path.join(base, 'wf2', 'synth', f'{n}.json')) for n in names}
    judge = {n: load(os.path.join(base, 'wf3', 'judge', f'{n}.json')) for n in names}
    bear = {n: load(os.path.join(base, 'wf3', 'bear', f'{n}.json')) for n in names}
    calib = load(os.path.join(base, 'wf3', 'calibration.json'), [])
    price_refresh = load(os.path.join(base, 'wf1', 'price_refresh.json'), {})

    L = []
    A = L.append
    A(manual.get('title', '# 한국 주식 26종목 1·3·5년 총주주수익률(TSR) 전망 — 멀티에이전트 리서치 보고서'))
    A('')
    A(manual.get('header', ''))
    A('')
    # ---------- Part 1 ----------
    A('## 1부. 핵심 결론')
    A('')
    A(manual.get('part1_intro', ''))
    p1 = tj['part1']
    def lst(key):
        items = p1.get(key, [])
        return ', '.join(f'{i+1}. {n}({trees[n]["ticker"]})' for i, n in enumerate(items))
    for hk in HZ:
        if f'{hk}_ret_top5' in p1:
            A(f'- **{HZN[hk]} 기대수익률 상위 5개**: {lst(f"{hk}_ret_top5")}')
            A(f'- **{HZN[hk]} 위험조정(Forward Sortino) 상위 5개**: {lst(f"{hk}_ra_top5")}')
    A(f'- **세 기간 전체에서 가장 일관되게 높은 종목 5개(균형형 종합순위 평균 기준)**: {lst("consistent_top5")}')
    A(f'- **기대수익률은 높지만 손실위험도 큰 종목(3년 기대수익률 상위 10 & 30% 이상 손실확률 30% 이상)**: {lst("high_ret_high_risk") or "해당 없음"}')
    A(f'- **기대수익률은 중간이지만 위험조정 성과가 좋은 종목(3년 Sortino 상위 8 & 기대수익률 9위 이하)**: {lst("mid_ret_good_ra") or "해당 없음"}')
    A(f'- **기대값과 중앙값의 괴리가 큰 종목(3년, 소수 대박 시나리오 의존)**: {lst("exp_vs_median_gap")}')
    if manual.get('part1_priced_in'):
        A(f'- **현재 주가에 낙관론이 가장 많이 반영된 종목**: {manual["part1_priced_in"]}')
    A('')
    A(manual.get('part1_commentary', ''))
    A('')
    # ---------- Part 2 ----------
    A('## 2부. 종목 식별 및 데이터 검증표')
    A('')
    A(manual.get('part2_intro', ''))
    A('')
    A('| # | 회사명 | 종목코드 | 시장 | 거래 가능 | 기준 주가(기준일) | 시가총액(기준일) | 최근 결산 기준 | 핵심 사업 | 데이터상 특이사항 |')
    A('|---:|---|---|---|:--:|---|---|---|---|---|')
    order = manual.get('stock_order') or list(stocks_data.keys())
    for i, n in enumerate(order, 1):
        d = stocks_data.get(n)
        if not d:
            A(f'| {i} | {n} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 데이터 없음 |')
            continue
        t = trees.get(n, {})
        pr = price_refresh.get(n, {})
        price = t.get('price0') or parse_num(d['price']['value'])
        pdate = t.get('price_date') or d['price']['date']
        mcap = pr.get('market_cap_bn') if parse_num(pr.get('market_cap_bn')) else d['market_cap_bn']['value']
        mcap_date = pr.get('adopted_date') if parse_num(pr.get('market_cap_bn')) else d['market_cap_bn']['date']
        if t.get('price0') and parse_num(d['shares_outstanding']['value']):
            mcap = t['price0'] * parse_num(d['shares_outstanding']['value']) / 1e8
            mcap_date = pdate
        trad = '가능' if d.get('tradable') else '불가'
        note = (d.get('status_notes') or '')[:160].replace('|', '/').replace('\n', ' ')
        special = manual.get('part2_notes', {}).get(n) or note
        A(f"| {i} | {n} ({d.get('legal_name','')[:45].replace('|','/')}) | {d.get('ticker','')} | {d.get('market','')} | {trad} | {fmt_krw(price) if price else 'N/A'} ({pdate}) | {fmt_mcap(mcap)} ({mcap_date}) | {na(d.get('latest_report_period'))[:40].replace('|','/')} | {(d['business'].get('summary') or '')[:70].replace('|','/').replace(chr(10),' ')} | {special.replace(chr(10),' ')} |")
    A('')
    A(manual.get('part2_exclusions', ''))
    A('')
    # ---------- Part 3 ----------
    A('## 3부. 기간별 전체 순위표')
    A('')
    A(manual.get('part3_intro', ''))
    A(tables_md.split('### 기간별 순위 변화표')[0])
    A('')
    A(manual.get('part3_notes', ''))
    A('')
    # ---------- Part 4 ----------
    A('## 4부. 기간별 순위 변화표')
    A('')
    A(manual.get('part4_intro', ''))
    A('')
    A('| 종목(코드) | 1년 종합 | 3년 종합 | 5년 종합 | 공격형(1/3/5년) | 방어형(1/3/5년) | 장기로 갈수록 순위가 변하는 이유 |')
    A('|---|---:|---:|---:|---|---|---|')
    reasons = manual.get('part4_reasons', {})
    for row in tj['rank_change']:
        n = row['name']
        f = lambda x: str(x) if x else '-'
        a = '/'.join(f(x) for x in row['aggressive'])
        d = '/'.join(f(x) for x in row['defensive'])
        reason = reasons.get(n) or (trees[n].get('one_line') or '')
        A(f"| {n}({row['ticker']}) | {f(row['balanced'][0])} | {f(row['balanced'][1])} | {f(row['balanced'][2])} | {a} | {d} | {reason.replace('|','/')} |")
    A('')
    A(manual.get('part4_notes', ''))
    A('')
    # ---------- Part 5 ----------
    A('## 5부. 상위 종목 상세 분석')
    A('')
    A(manual.get('part5_intro', ''))
    top_union = []
    for hk in HZ:
        for n in p1.get(f'{hk}_bal_top5', []):
            if n not in top_union:
                top_union.append(n)
    for n in top_union:
        s = synth[n] or {}
        rs = s.get('report_sections', {})
        t = trees[n]
        ranks = ' / '.join(f'{HZN[h]} {RK[h][n]["balanced_rank"]}위(기대수익률 {RK[h][n]["ret_rank"]}위, 위험조정 {RK[h][n]["ra_rank"]}위)' for h in HZ if h in RK and n in RK[h])
        A(f'### {n} ({t["ticker"]}) — 균형형 종합순위: {ranks}')
        A('')
        A(f'기준 주가 {fmt_krw(t["price0"])} ({t["price_date"]}), 산업군 {t["industry"]}, 추정 신뢰도 {t.get("confidence","")}.')
        A('')
        vs = s.get('valuation_summary', {})
        A(f'- **핵심 투자논지**: {rs.get("thesis","N/A")}')
        A(f'- **현재 주가가 암시하는 기대**: {rs.get("implied_expectations","N/A")}')
        A(f'- **시장 전망과 자체 전망의 차이**: {rs.get("vs_consensus","N/A")}')
        A(f'- **매출·이익·현금흐름 전망**: {rs.get("financial_outlook","N/A")}')
        ft = s.get('forecast_table', [])
        if ft:
            A('')
            A('| 연도 | 매출(억원) | 영업이익(억원) | 순이익(억원) | EPS(원) | FCF(억원) |')
            A('|---|---:|---:|---:|---:|---:|')
            for r in ft:
                A(f"| {r.get('year','')} | {na(r.get('revenue_bn'))} | {na(r.get('op_income_bn'))} | {na(r.get('net_income_bn'))} | {na(r.get('eps_krw'))} | {na(r.get('fcf_bn'))} |")
            A('')
        A(f'- **가치평가 방법과 적정가치 범위**: {rs.get("valuation","N/A")} (방법: {vs.get("methods_used","N/A")}; 적정가치 범위 {na(vs.get("fair_value_low_krw"))}~{na(vs.get("fair_value_high_krw"))}원, 중간값 {na(vs.get("fair_value_mid_krw"))}원)')
        A(f'- **비관·기준·낙관 시나리오**: {rs.get("scenarios","N/A")}')
        # scenario table (final)
        A('')
        A('| 기간 | 시나리오 | 확률 | 기말 주가(희석 후) | 누적 현금환원/주 | 누적 TSR |')
        A('|---|---|---:|---:|---:|---:|')
        for hk in HZ:
            for sc in t['horizons'].get(hk, []):
                A(f"| {HZN[hk]} | {sc['name']} | {sc['prob']:.0f}% | {fmt_krw(sc['end_price'])} | {fmt_krw(sc['cum_cash'])} | {fmt_pct((sc['end_price']+sc['cum_cash'])/t['price0']-1)} |")
        if t.get('shrink_weight', 1.0) < 1.0:
            A(f'(베이스레이트 축소 가중치 {t["shrink_weight"]:.2f} 적용 후 값)')
        A('')
        A(f'- **가장 중요한 촉매**: {rs.get("catalysts","N/A")}')
        A(f'- **가장 중요한 하방위험**: {rs.get("downside_risks","N/A")}')
        A(f'- **투자논지가 무효화되는 조건**: {rs.get("thesis_breakers","N/A")}')
        A(f'- **다음 실적·공시에서 확인할 지표**: {rs.get("kpis_to_watch","N/A")}')
        if judge.get(n):
            A(f'- **반대심문 후 조정**: {judge[n].get("changes_summary","")}')
        A('')
    # ---------- Part 6 ----------
    A('## 6부. 하위 종목 및 고위험 종목')
    A('')
    A(manual.get('part6_intro', ''))
    bottom_union = []
    for hk in HZ:
        for n in p1.get(f'{hk}_bal_bottom5', []):
            if n not in bottom_union and n not in top_union:
                bottom_union.append(n)
    # add high loss-prob names
    for n in names:
        if n not in bottom_union and n not in top_union and R[n]['horizons'].get('3y', {}).get('p_loss', 0) >= 0.45:
            bottom_union.append(n)
    for n in bottom_union:
        s = synth[n] or {}
        rs = s.get('report_sections', {})
        fl = s.get('flags', {})
        t = trees[n]
        ranks = ' / '.join(f'{HZN[h]} {RK[h][n]["balanced_rank"]}위' for h in HZ if h in RK and n in RK[h])
        pl = ' / '.join(f'{HZN[h]} 손실확률 {fmt_pct_plain(R[n]["horizons"][h]["p_loss"])}' for h in HZ if h in R[n]['horizons'])
        A(f'### {n} ({t["ticker"]}) — 균형형 종합순위 {ranks}; {pl}')
        A('')
        A(f'- **낮은 순위의 핵심 원인**: {rs.get("low_rank_reasons","N/A")}')
        A(f'- **현재 주가에 반영된 기대**: {rs.get("implied_expectations","N/A")} (낙관 반영도: {fl.get("optimism_priced_in","N/A")})')
        A(f'- **재무·희석·기술·고객·규제 위험**: {rs.get("downside_risks","N/A")}')
        A(f'- **순위가 크게 오를 수 있는 변화**: {rs.get("what_would_lift_rank","N/A")}')
        A('')
    # ---------- Part 7 ----------
    A('## 7부. 에이전트 의견 차이와 반대심문 결과')
    A('')
    A(manual.get('part7_intro', ''))
    A('')
    A('### 7-1. 산업군별 베이스레이트 보정 요약')
    A('')
    for c in calib:
        if c:
            A(f'- **{c.get("industry_group","")}**: {c.get("narrative_ko","")} (산업 편향 점검: {c.get("sector_bias_check","")})')
    A('')
    A('### 7-2. 종목별 분석가 의견 차이(종합 에이전트 기록)')
    A('')
    for n in names:
        s = synth[n] or {}
        dis = s.get('disagreements', [])
        if not dis:
            continue
        A(f'**{n}**')
        for d in dis[:4]:
            A(f'- {d.get("topic","")}: 산업전문가 — {d.get("specialist_view","")} / 독립분석가 — {d.get("generalist_view","")} / 포렌식·위험 — {d.get("forensic_or_risk_view","")} → 결론: {d.get("resolution","")} (가중치 근거: {d.get("weighting_rationale","")})')
        A('')
    A('### 7-3. 반대심문(약세론) 결과와 최종 심사')
    A('')
    for n in names:
        if not bear.get(n):
            continue
        b, j = bear[n], judge.get(n) or {}
        A(f'**{n}** — 약세론 에이전트의 판단: {b.get("rank_should_change","")}')
        A('')
        A(f'- 가장 강한 반론: ' + ' / '.join(b.get('strongest_arguments', [])[:4]))
        A(f'- 강세론이 맞는 점: {b.get("what_bulls_get_right","")}')
        A(f'- 약세론 요약: {b.get("narrative_ko","")}')
        if j:
            A(f'- 최종 심사: {j.get("narrative_ko","")}')
            A(f'- 수용한 반론: ' + ' / '.join(j.get('accepted_bear_points', [])[:4]))
            A(f'- 기각한 반론: ' + ' / '.join(j.get('rejected_bear_points', [])[:4]))
            A(f'- 변경 요약: {j.get("changes_summary","")}')
        A('')
    A(manual.get('part7_summary', ''))
    A('')
    # ---------- Part 8 ----------
    A('## 8부. 순위 민감도')
    A('')
    A(manual.get('part8_intro', ''))
    A('')
    A('| 종목 | 원/달러 환율 | 무위험금리·할인율 | 최종 멀티플 | 반도체 가격·AI 설비투자 | 자동차 수요·관세 | 바이오 임상·허가 확률 | 추가 자금조달·희석 | 핵심 고객 의존도 | 순위 불안정 |')
    A('|---|---|---|---|---|---|---|---|---|:--:|')
    for n in names:
        s = synth[n] or {}
        se = s.get('sensitivities', {})
        fl = s.get('flags', {})
        unstable = '예' if str(fl.get('rank_instability_risk', '')).startswith('높') else ''
        c = lambda k: (se.get(k, 'N/A') or 'N/A').replace('|', '/').replace('\n', ' ')[:90]
        A(f"| {n} | {c('fx')} | {c('rates_discount')} | {c('terminal_multiple')} | {c('semis_ai_capex')} | {c('auto_demand_tariff')} | {c('bio_success_prob')} | {c('dilution')} | {c('key_customer')} | {unstable} |")
    A('')
    A(manual.get('part8_analysis', ''))
    A('')
    # ---------- Part 9 ----------
    A('## 9부. 최종 판단')
    A('')
    A(manual.get('part9', ''))
    A('')
    # ---------- Appendix ----------
    A('## 부록 A. 방법론·산식·데이터 제약')
    A('')
    A(manual.get('appendix_method', ''))
    A('')
    A('## 부록 B. 품질 통제 체크리스트')
    A('')
    A(manual.get('appendix_qc', ''))
    A('')
    A('## 부록 C. 거시·시장체제 요약(총괄 조정 에이전트)')
    A('')
    A(macro.get('narrative_ko', ''))
    A('')
    A('| 기간 | 시나리오 | 확률 | 핵심 가정(금리·환율·증시) |')
    A('|---|---|---:|---|')
    for sc in macro.get('scenarios', []):
        A(f"| {sc['horizon'][:10]} | {sc['name'][:40].replace('|','/')} | {sc['probability_pct']}% | {(sc.get('rates','')+' / '+sc.get('fx','')+' / '+sc.get('equity_market',''))[:220].replace('|','/')} |")
    A('')
    A('## 부록 D. 엔진 빌드 로그(산식 검산·정규화·축소 기록)')
    A('')
    for l in build_log:
        A(f'- {l}')
    A('')
    A('## 부록 E. 주요 출처')
    A('')
    A(manual.get('appendix_sources', ''))
    for n in order:
        d = stocks_data.get(n)
        if not d:
            continue
        srcs = d.get('sources', [])[:6]
        if srcs:
            A(f'- **{n}**: ' + '; '.join(f"{(s.get('title') or '')[:40]} ({s.get('url','')}, {s.get('date','')})" for s in srcs))
    A('')
    with open(out_md, 'w') as f:
        f.write('\n'.join(L))
    print(f'wrote {out_md}: {len("".join(L))} chars, {len(L)} lines')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
