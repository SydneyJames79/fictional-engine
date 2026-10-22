export const meta = {
  name: 'kr-equity-wf1e-macro-reconcile',
  description: '금융시장·산업사이클 거시 보고서 2건을 모순 없는 공통 거시 시나리오 1건으로 통합',
  phases: [{ title: '거시 통합', detail: '총괄 조정 에이전트가 공통 가정 확정' }],
}

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const SCHEMA = {
  type: 'object',
  properties: {
    as_of: STR,
    base_dates: { type: 'object', properties: { analysis_datetime_kst: STR, price_basis_note: STR, horizon_1y_end: STR, horizon_3y_end: STR, horizon_5y_end: STR, currency: STR }, required: ['analysis_datetime_kst', 'price_basis_note', 'horizon_1y_end', 'horizon_3y_end', 'horizon_5y_end', 'currency'] },
    current_state: { type: 'array', items: { type: 'object', properties: { topic: STR, value: STR, as_of_date: STR, source_url: STR, note: STR }, required: ['topic', 'value', 'as_of_date', 'source_url'] } },
    risk_free: { type: 'object', properties: { rf_1y_pct: STR, rf_3y_pct: STR, rf_5y_pct: STR, basis_note: STR, date: STR, source_url: STR }, required: ['rf_1y_pct', 'rf_3y_pct', 'rf_5y_pct', 'basis_note', 'date', 'source_url'] },
    index_expectations: { type: 'array', items: { type: 'object', properties: { index: STR, horizon: STR, expected_annualized_pct: STR, expected_cum_pct: STR, rationale: STR }, required: ['index', 'horizon', 'expected_annualized_pct', 'expected_cum_pct', 'rationale'] } },
    scenarios: { type: 'array', items: { type: 'object', properties: { horizon: STR, name: STR, probability_pct: STR, description: STR, rates: STR, fx: STR, equity_market: STR, ai_capex_memory: STR, semicap_display: STR, autos: STR, bio: STR, space_satcom_defense_5g6g: STR, ess_materials: STR, medtech_dx: STR }, required: ['horizon', 'name', 'probability_pct', 'description', 'rates', 'fx', 'equity_market', 'ai_capex_memory', 'semicap_display', 'autos', 'bio', 'space_satcom_defense_5g6g', 'ess_materials', 'medtech_dx'] } },
    cycle_positions: { type: 'array', items: { type: 'object', properties: { industry: STR, position: STR, rationale: STR, base_rate_annual_return_pct: STR }, required: ['industry', 'position', 'rationale', 'base_rate_annual_return_pct'] } },
    sector_priors: { type: 'array', items: { type: 'object', properties: { industry_group: STR, prior_cum_tsr_1y_pct: STR, prior_cum_tsr_3y_pct: STR, prior_cum_tsr_5y_pct: STR, prior_ann_vol_pct: STR, rationale: STR }, required: ['industry_group', 'prior_cum_tsr_1y_pct', 'prior_cum_tsr_3y_pct', 'prior_cum_tsr_5y_pct', 'prior_ann_vol_pct', 'rationale'] } },
    conflicts_resolved: { type: 'array', items: { type: 'object', properties: { topic: STR, financial_view: STR, industry_view: STR, resolution: STR }, required: ['topic', 'financial_view', 'industry_view', 'resolution'] } },
    narrative_ko: STR,
    unresolved: STRARR,
  },
  required: ['as_of', 'base_dates', 'current_state', 'risk_free', 'index_expectations', 'scenarios', 'cycle_positions', 'sector_priors', 'conflicts_resolved', 'narrative_ko', 'unresolved'],
}

const prompt = `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '총괄 조정 에이전트'입니다. 두 거시 에이전트(금융시장 담당, 산업 사이클 담당)의 보고서를 하나의 '공통 거시·산업 시나리오'로 통합하세요. 이 결과는 26개 종목을 분석하는 모든 산업 전문가·일반 분석가·종합 에이전트가 동일하게 사용하므로, 서로 모순되는 가정이 남지 않게 하는 것이 최우선입니다.

[환경 제약] 이번 턴의 WebSearch 예산이 모두 소진되어 검색을 할 수 없습니다. 검색을 시도하지 말고, 아래 두 보고서에 담긴 사실(출처·날짜 포함)만으로 통합하세요. 두 보고서가 다루지 않은 사항은 N/A로 두거나 '가정'이라고 명시하세요. 기억에 의존한 수치는 "(memory_unverified)"로 표시하세요.

[분석 기준] 기준 시각 2026-10-22(목) 15:40 KST. 기준 통화 원화. 기간 종료일: 1년 2027-10-22, 3년 2029-10-22, 5년 2031-10-22. 확인된 10/22 종가: KOSPI 5,533.77(-3.52%), KOSDAQ 764.10(-3.62%).

[보고서 A: 금융시장 담당] 다음 파일을 Read 도구로 전부 읽으세요: ${args.finPath}

[보고서 B: 산업 사이클 담당] 다음 파일을 Read 도구로 전부 읽으세요: ${args.indPath}

(두 파일은 JSON이며 각각 2만~4만 자입니다. 끝까지 읽은 뒤 통합을 시작하세요.)

[산출물]
1. base_dates: 분석 기준일시, 주가 기준일 원칙(원칙: 2026-10-22 종가, 확인 불가 시 가장 최근 확인된 종가와 날짜를 종목별로 명시), 기간 종료일, 통화.
2. current_state: 핵심 현재 수치 목록(한은 기준금리, 연준 금리, 미 10년물, 국고채 3·5·10년, 원/달러, KOSPI·KOSDAQ 종가와 고점 대비 조정폭, PBR, 수출, 관세 상태, 제도 변화 등). 각 항목에 날짜·출처.
3. risk_free: Sortino 계산용 무위험수익률. 1년물은 확인되지 않았으므로 대체 기준을 정하고(예: 한은 기준금리 3.00% 또는 3년물 3.822%, 또는 둘의 중간) basis_note에 명시. 3년 3.822%(10/21), 5년 4.014%(10/19 확인치; 10/21 추정치는 미검증) 중 어느 값을 채택할지 결정하고 근거를 적는다.
4. index_expectations: KOSPI와 KOSDAQ의 1·3·5년 기대 연환산·누적 수익률(확률가중). 현재 조정 국면(5월 고점 7,384 대비 -25%)과 밸류에이션, 금리, 이익 사이클을 반영.
5. scenarios: 1년·3년·5년 각 기간별 비관/기준/낙관 3개(총 9개). 각 기간 확률 합 정확히 100. 각 시나리오에 금리·환율·주식시장·AI capex와 메모리·반도체장비와 디스플레이·자동차·바이오·우주위성방산5G6G·ESS와 소재·의료기기진단 항목별 핵심 가정을 숫자로 적는다. 두 보고서의 확률이 다르면 조정 결과와 근거를 conflicts_resolved에 기록.
6. cycle_positions: 10개 산업의 사이클 위치와, 그 위치에서 역사적으로 관찰된 연평균 주가수익률 베이스레이트(추정치, 근거 명시).
7. sector_priors: 5개 산업군(반도체·AI하드웨어·디스플레이장비 / 자동차·전장·SDV·부품 / 바이오의약품·의료기기·진단 / 우주항공·위성통신·5G6G / ESS·산업재·특수소재)별로 '정보가 부족한 종목의 추정을 축소시킬 때 쓸 사전분포': 1·3·5년 누적 TSR 사전 기대값(%)과 연환산 변동성 사전값(%)과 근거. 산업 평균 수준이며 낙관적이지 않게.
8. conflicts_resolved: 두 보고서 사이의 충돌(확률, 사이클 위치, 금리 경로 등)과 해결.
9. narrative_ko: 최종 보고서에 실릴 '거시·시장체제 요약' 문단(보고서 문체, 평서문, 10~20문장, 숫자·날짜·출처 포함). 시나리오 확률과 산업별 함의를 담되 장황하지 않게.
10. unresolved: 확인하지 못한 항목.
숫자 표기: % 숫자만, 금액은 단위 명시. 최종 출력은 JSON 스키마로만.`

const out = await agent(prompt, { label: 'macro:통합', phase: '거시 통합', schema: SCHEMA, effort: 'max' })
return out
