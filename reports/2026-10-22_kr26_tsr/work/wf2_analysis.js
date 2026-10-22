export const meta = {
  name: 'kr-equity-wf2-analysis',
  description: '종목별 독립 분석(산업전문가·독립일반분석가·회계포렌식·위험정량) 후 종목별 종합 시나리오 트리 생성',
  phases: [
    { title: '독립 분석', detail: '종목당 4개 에이전트 병렬(서로의 결과를 보지 않음)' },
    { title: '종목별 종합', detail: '4개 결과를 통합해 1·3·5년 시나리오 트리 확정' },
  ],
}

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const FACTS = { type: 'array', items: { type: 'object', properties: { fact: STR, source_url: STR, date: STR }, required: ['fact', 'source_url'] } }
const SCEN_ITEM = { type: 'object', properties: { horizon: STR, name: { type: 'string', enum: ['bear', 'base', 'bull'] }, probability_pct: STR, end_price_krw: STR, cum_cash_per_share_krw: STR, dilution_pct: STR, cum_tsr_pct: STR, rationale: STR }, required: ['horizon', 'name', 'probability_pct', 'end_price_krw', 'cum_cash_per_share_krw', 'dilution_pct', 'cum_tsr_pct', 'rationale'] }
const FORECAST_ITEM = { type: 'object', properties: { year: STR, revenue_bn: STR, op_income_bn: STR, net_income_bn: STR, eps_krw: STR, fcf_bn: STR, note: STR }, required: ['year', 'revenue_bn', 'op_income_bn', 'net_income_bn', 'eps_krw'] }

const ANALYST_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR, role: STR,
    thesis_summary: STR,
    business_quality: { type: 'object', properties: { moat: STR, competitive_position: STR, customer_concentration: STR, cyclicality: STR, substitution_risk: STR, pricing_power: STR }, required: ['moat', 'competitive_position', 'customer_concentration', 'cyclicality', 'substitution_risk', 'pricing_power'] },
    implied_expectations: STR,
    forecasts: { type: 'array', items: FORECAST_ITEM },
    normalized_earnings: STR,
    valuation_methods: { type: 'array', items: { type: 'object', properties: { method: STR, key_assumptions: STR, fair_value_per_share_krw: STR, weight_pct: STR }, required: ['method', 'key_assumptions', 'fair_value_per_share_krw', 'weight_pct'] } },
    fair_value_range: { type: 'object', properties: { low_krw: STR, mid_krw: STR, high_krw: STR }, required: ['low_krw', 'mid_krw', 'high_krw'] },
    scenarios: { type: 'array', items: SCEN_ITEM },
    event_tree: STR,
    shareholder_return_assumptions: STR,
    catalysts: STRARR, key_risks: STRARR, thesis_breakers: STRARR, kpis_to_watch: STRARR,
    consensus_vs_own: STR,
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    additional_facts: FACTS,
    search_count: STR,
  },
  required: ['stock', 'role', 'thesis_summary', 'business_quality', 'implied_expectations', 'forecasts', 'normalized_earnings', 'valuation_methods', 'fair_value_range', 'scenarios', 'event_tree', 'shareholder_return_assumptions', 'catalysts', 'key_risks', 'thesis_breakers', 'kpis_to_watch', 'consensus_vs_own', 'confidence', 'additional_facts', 'search_count'],
}

const FORENSIC_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR,
    accounting_quality: { type: 'object', properties: { ocf_vs_earnings: STR, one_offs: STR, capitalized_dev_costs: STR, related_party: STR, audit_opinion: STR, contingent_liabilities: STR, customer_supplier_concentration: STR, inventory_receivables: STR }, required: ['ocf_vs_earnings', 'one_offs', 'capitalized_dev_costs', 'related_party', 'audit_opinion', 'contingent_liabilities', 'customer_supplier_concentration', 'inventory_receivables'] },
    balance_sheet_risk: { type: 'object', properties: { net_cash_or_debt: STR, debt_maturity: STR, funding_need_3y: STR, prob_equity_raise_3y_pct: STR, expected_dilution_1y_pct: STR, expected_dilution_3y_pct: STR, expected_dilution_5y_pct: STR }, required: ['net_cash_or_debt', 'debt_maturity', 'funding_need_3y', 'prob_equity_raise_3y_pct', 'expected_dilution_1y_pct', 'expected_dilution_3y_pct', 'expected_dilution_5y_pct'] },
    governance: { type: 'object', properties: { largest_holder: STR, holding_discount: STR, overhang: STR, treasury_shares: STR, minority_conflicts: STR, capital_allocation_track_record: STR }, required: ['largest_holder', 'holding_discount', 'overhang', 'treasury_shares', 'minority_conflicts', 'capital_allocation_track_record'] },
    shareholder_returns_forecast: { type: 'object', properties: { dps_2026_krw: STR, dps_2027_krw: STR, dps_2028_krw: STR, buyback_yield_pct: STR, total_yield_pct: STR, cancellation_policy: STR }, required: ['dps_2026_krw', 'dps_2027_krw', 'dps_2028_krw', 'buyback_yield_pct', 'total_yield_pct', 'cancellation_policy'] },
    red_flags: STRARR,
    severity: { type: 'string', enum: ['낮음', '보통', '높음'] },
    prob_permanent_loss_5y_pct: STR,
    recommended_adjustments: STR,
    facts: FACTS,
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    search_count: STR,
  },
  required: ['stock', 'accounting_quality', 'balance_sheet_risk', 'governance', 'shareholder_returns_forecast', 'red_flags', 'severity', 'prob_permanent_loss_5y_pct', 'recommended_adjustments', 'facts', 'confidence', 'search_count'],
}

const RISK_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR,
    hist_vol_1y_pct: STR, hist_vol_3y_pct: STR, downside_vol_pct: STR, beta: STR,
    mdd_1y_pct: STR, mdd_3y_pct: STR, mdd_5y_pct: STR,
    price_history_notes: STR,
    avg_daily_turnover_bn: STR, liquidity_note: STR, gap_risk: STR,
    cyclicality: STR, financial_leverage: STR, earnings_estimate_volatility: STR, discrete_event_risk: STR,
    p_zero_annual_pct: STR,
    fwd_vol_1y_pct: STR, fwd_vol_3y_pct: STR, fwd_vol_5y_pct: STR,
    implied_vol_note: STR,
    rationale: STR,
    facts: FACTS,
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    search_count: STR,
  },
  required: ['stock', 'hist_vol_1y_pct', 'hist_vol_3y_pct', 'downside_vol_pct', 'beta', 'mdd_1y_pct', 'mdd_3y_pct', 'mdd_5y_pct', 'price_history_notes', 'avg_daily_turnover_bn', 'liquidity_note', 'gap_risk', 'cyclicality', 'financial_leverage', 'earnings_estimate_volatility', 'discrete_event_risk', 'p_zero_annual_pct', 'fwd_vol_1y_pct', 'fwd_vol_3y_pct', 'fwd_vol_5y_pct', 'implied_vol_note', 'rationale', 'facts', 'confidence', 'search_count'],
}

const SYNTH_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR, ticker: STR, price0_krw: STR, price_date: STR, industry_group: STR,
    horizons: { type: 'array', items: { type: 'object', properties: { horizon: STR, end_date: STR, scenarios: { type: 'array', items: SCEN_ITEM }, expected_cum_tsr_pct: STR, treatment_note: STR }, required: ['horizon', 'end_date', 'scenarios', 'expected_cum_tsr_pct', 'treatment_note'] } },
    event_tree: STR,
    forecast_table: { type: 'array', items: FORECAST_ITEM },
    valuation_summary: { type: 'object', properties: { methods_used: STR, fair_value_low_krw: STR, fair_value_mid_krw: STR, fair_value_high_krw: STR, implied_expectations: STR }, required: ['methods_used', 'fair_value_low_krw', 'fair_value_mid_krw', 'fair_value_high_krw', 'implied_expectations'] },
    disagreements: { type: 'array', items: { type: 'object', properties: { topic: STR, specialist_view: STR, generalist_view: STR, forensic_or_risk_view: STR, resolution: STR, weighting_rationale: STR }, required: ['topic', 'specialist_view', 'generalist_view', 'forensic_or_risk_view', 'resolution', 'weighting_rationale'] } },
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    report_sections: { type: 'object', properties: { thesis: STR, implied_expectations: STR, vs_consensus: STR, financial_outlook: STR, valuation: STR, scenarios: STR, catalysts: STR, downside_risks: STR, thesis_breakers: STR, kpis_to_watch: STR, one_line_driver: STR, low_rank_reasons: STR, what_would_lift_rank: STR }, required: ['thesis', 'implied_expectations', 'vs_consensus', 'financial_outlook', 'valuation', 'scenarios', 'catalysts', 'downside_risks', 'thesis_breakers', 'kpis_to_watch', 'one_line_driver', 'low_rank_reasons', 'what_would_lift_rank'] },
    flags: { type: 'object', properties: { optimism_priced_in: STR, data_quality: STR, rank_instability_risk: STR, discrete_outcome_stock: STR, prob_permanent_loss_5y_pct: STR }, required: ['optimism_priced_in', 'data_quality', 'rank_instability_risk', 'discrete_outcome_stock', 'prob_permanent_loss_5y_pct'] },
    sensitivities: { type: 'object', properties: { fx: STR, rates_discount: STR, terminal_multiple: STR, semis_ai_capex: STR, auto_demand_tariff: STR, bio_success_prob: STR, dilution: STR, key_customer: STR }, required: ['fx', 'rates_discount', 'terminal_multiple', 'semis_ai_capex', 'auto_demand_tariff', 'bio_success_prob', 'dilution', 'key_customer'] },
  },
  required: ['stock', 'ticker', 'price0_krw', 'price_date', 'industry_group', 'horizons', 'event_tree', 'forecast_table', 'valuation_summary', 'disagreements', 'confidence', 'report_sections', 'flags', 'sensitivities'],
}

const SEARCH_ALLOWED = !!(args && args.searchAllowed)
const SEARCH_RULE = SEARCH_ALLOWED
  ? '추가 자료가 꼭 필요할 때만 ToolSearch로 "select:WebSearch"를 로드한 뒤 WebSearch를 최대 3회 사용한다(mode:"extended"). 예산이 소진됐다는 응답이 오면 즉시 중단하고 가진 자료로 진행한다. 검색으로 얻은 새 사실은 additional_facts/facts에 출처 URL·날짜와 함께 기록한다.'
  : '이번 턴의 WebSearch 예산(모든 에이전트 공유 200회)이 이미 소진되어 검색을 할 수 없다. WebSearch를 시도하지 말고, 제공된 검증 데이터·거시 시나리오·자신의 지식(표시)으로 분석한다. additional_facts/facts에는 데이터 파일에서 가져온 사실만 적는다.'

const COMMON = `[공통 분석 기준]
- 분석 기준일·시각: 2026-10-22(목) 15:40 KST. 기준 통화: 원화(KRW). 수익률은 현재 주가 대비 세전·수수료 차감 전 원화 기준 총주주수익률(TSR).
- 기간 종료일: 1년 = 2027-10-22, 3년 = 2029-10-22, 5년 = 2031-10-22.
- TSR 정의: (기말 주당가치 + 기간 중 주당 현금환원[배당 + 자사주 매입·소각의 주당가치 환산]) / 기준 주가 - 1. 유상증자·CB·BW·스톡옵션 등 희석은 기말 주당가치에 반영한다(기말 주가는 '희석 후 주당 기준'). 자사주 소각은 주당가치 상승으로 반영한다.
- 기준 주가는 아래 데이터의 price.value(날짜 명시). 장중가가 아니라 종가다.
- 경기순환주는 고점 이익에 낮은 PER을 적용하지 말고 정상화(중간사이클) 이익을 함께 계산한다. 5년 전망에서는 영구 고성장을 가정하지 말고 경쟁 심화와 멀티플 정상화를 반영한다. 바이오·진단은 임상·허가·급여·상업화 성공확률, 현금 소진, 추가 증자 가능성을 반영한다. 신규 상장·이력 짧은 기업은 비교기업과 산업 베이스레이트를 쓰되 신뢰도를 낮춘다.
- 증권사 목표주가는 참고자료일 뿐 독립 평가를 대체하지 않는다. 투자 확률을 확정적 사실처럼 쓰지 않는다. 데이터가 없으면 추측하지 말고 N/A로 둔다.
- 숫자 표기: 금액 억원(순수 숫자 문자열), 주가 원, 비율 %. 쉼표·단위 문자 금지. 세 시나리오 확률 합은 기간마다 정확히 100.

[환경 제약]
- WebFetch·curl 등 직접 접속은 차단되어 있다. ${SEARCH_RULE}
- 검증된 데이터 파일과 거시 시나리오 파일은 Read 도구로 끝까지 읽는다(JSON, 각 1만~4만 자). 읽지 않고 분석을 시작하지 않는다.
- 데이터 파일에 없는 사실을 보태야 할 때는 자신의 지식임을 "(memory_unverified)"로 명시하고, 그런 수치가 결론을 좌우하지 않게 한다.
- 최종 출력은 지정된 JSON 스키마(StructuredOutput)로만 반환한다.`

const dataBlock = (s) => `[검증된 종목 데이터] 종목 식별·데이터 검증 에이전트가 2026-10-22에 수집한 JSON 파일을 Read 도구로 전부 읽으세요: ${s.dataPath}
(데이터 품질: ${s.dataQuality}. 검색 횟수: ${s.searchCount}. 'N/A' 항목은 확인 불가였다는 뜻이며 추측으로 채우지 않는다.)`

const macroBlock = (m) => `[공통 거시·산업 시나리오] 총괄 조정 에이전트가 확정한 공통 시나리오 JSON 파일을 Read 도구로 전부 읽으세요(모든 종목에 동일 적용): ${m}`

const DELIVERABLES = `[산출물 - 반드시 모두 작성]
1. 사업 구조와 경쟁 지위: 해자, 점유율·경쟁 지위, 고객 집중도, 경기민감도, 기술 대체 위험, 가격결정력.
2. 현재 주가가 암시하는 기대 역산(implied_expectations): 현재 시가총액을 정당화하려면 2028~2031년에 어떤 매출성장률·영업이익률·점유율·멀티플이 필요한지 숫자로. Reverse DCF 또는 implied growth 방식.
3. 재무 전망(forecasts): 2026E, 2027E, 2028E, 2029E, 2031E의 매출·영업이익·순이익·EPS(희석 반영)·FCF(억원, EPS는 원). 경기순환주는 normalized_earnings에 중간사이클 이익과 그 근거를 적는다.
4. 가치평가(valuation_methods): 기업에 적합한 방법을 최소 2개(DCF/FCFF, 배당할인, SOTP, 정상화이익 멀티플, 국내외 비교기업 멀티플, 자체 역사적 밸류에이션 밴드, Reverse DCF, rNPV, 시나리오별 EV/Sales, 수주잔고 전환 분석 등). 방법별 핵심 가정과 주당 적정가치, 가중치. fair_value_range에 저·중·고.
5. 시나리오(scenarios): 1년·3년·5년 각각 비관(bear)/기준(base)/낙관(bull) 3개씩 총 9개. 각 항목: 확률(기간별 합 100), 기말 주가(희석 후 주당 기준, 원), 기간 누적 주당 현금환원(원), 희석률(%), 누적 TSR(%) = (기말주가 + 누적현금환원)/기준주가 - 1 (직접 계산해 검산). 각 시나리오의 근거(어떤 이익·멀티플 조합인지 숫자로).
   - 이산적 결과(임상·대형 수주·고객 채택·기술표준·M&A)가 핵심인 종목은 event_tree에 사건확률 트리를 서술하고, 그것이 세 시나리오에 어떻게 접히는지 설명.
6. shareholder_return_assumptions: 배당·자사주 매입·소각 가정과 근거.
7. 촉매·핵심 하방위험·논지 무효화 조건(구체적 수치 조건)·다음 실적/공시에서 확인할 지표.
8. consensus_vs_own: 증권사 컨센서스(목표주가·이익 추정)와 자체 전망의 차이와 이유.
9. confidence: 높음/보통/낮음과 그 이유(thesis_summary 끝에 한 줄).`

const specialistPrompt = (s, macro) => `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '산업별 전문 에이전트'이며, 담당 산업군은 "${s.industry}"입니다. 이 산업의 밸류체인·기술·경쟁구도·고객사 투자 사이클에 정통한 섹터 애널리스트로서 아래 종목 하나를 깊이 분석하세요. 산업 전문가의 강점(기술·고객사·제품가격·경쟁사 동향의 구체성)을 살리되, 산업 내부의 낙관에 휩쓸리지 말고 숫자로 검증 가능한 전망을 내세요.

[대상 종목] ${s.name} (${s.ticker})

${COMMON}

${dataBlock(s)}

${macroBlock(macro)}

${DELIVERABLES}

[추가 지침] 산업 전문가로서 특히 다음을 구체적으로 다루세요: 고객사의 투자 계획과 발주 시점, 제품·서비스 가격 추이, 경쟁사(국내외) 점유율 변화, 기술 로드맵과 다음 세대 전환 시 지위 변화, 고객사의 자체개발·이원화·단가인하 압력, 산업 사이클상 현재 위치. 검색 규칙은 위 환경 제약을 따르세요. role 필드에는 "산업전문가:${s.industry}"라고 적으세요.`

const generalistPrompt = (s, macro) => `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '독립 일반 분석가'입니다. 특정 산업에 소속되지 않은 제너럴리스트로서, 산업 내부자의 낙관에 영향받지 않고 아래 종목 하나를 독립적으로 분석하세요. 산업 전문가의 분석은 볼 수 없으며 보지 않은 상태에서 수행합니다.

[대상 종목] ${s.name} (${s.ticker})

${COMMON}

${dataBlock(s)}

${macroBlock(macro)}

${DELIVERABLES}

[추가 지침] 제너럴리스트로서 특히 다음을 중시하세요: (1) 유사한 산업·성장단계·시가총액·재무구조를 가진 국내외 기업의 역사적 베이스레이트(높은 성장률이나 대형 수주가 실제 주주수익률로 이어진 비율), (2) 경기순환과 멀티플 정상화, (3) 희석·자금조달, (4) 경쟁 심화와 마진 회귀, (5) 현재 주가에 이미 반영된 기대. 극단적 추정은 산업 평균 쪽으로 축소하되 그 이유를 밝히세요. 검색 규칙은 위 환경 제약을 따르세요. role 필드에는 "독립일반분석가"라고 적으세요.`

const forensicPrompt = (s, macro) => `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '회계·지배구조·포렌식 에이전트'입니다. 아래 종목 하나의 회계 품질, 재무 위험, 희석, 지배구조를 점검하고 JSON 스키마로 보고하세요.

[대상 종목] ${s.name} (${s.ticker})

${COMMON}

${dataBlock(s)}

[점검 항목 - 모두 작성]
1. 회계 품질: 영업현금흐름과 회계이익의 괴리(최근 2~3년), 일회성 이익·비용, 자본화된 개발비, 관계사 거래·내부거래, 감사의견과 감사보고서 주석의 특이사항(핵심감사사항·계속기업 불확실성), 우발채무·소송·보증, 고객·공급자 집중도, 재고·매출채권 추이.
2. 재무 위험: 순현금·순차입금, 차입 만기 구조, 향후 3년 자금 소요(CAPEX·운전자본·R&D·현금 소진)와 조달 필요성, 3년 내 유상증자·CB 발행 확률(%), 1·3·5년 기대 희석률(%: 기존 CB·BW·스톡옵션 + 예상 신규 발행).
3. 지배구조: 최대주주와 지분율, 지주회사 할인이나 복잡한 지배구조, 보호예수·오버행, 자사주 보유·소각·처분 가능성, 소액주주-대주주 이해상충(합병·분할·내부거래·승계), 자본배분 실적(M&A·투자 성과).
4. 주주환원 전망: 2026~2028년 주당배당금, 자사주 매입수익률, 총주주환원수익률, 소각 정책.
5. 레드플래그 목록과 전체 심각도(낮음/보통/높음), 5년 내 영구자본손실(주가 -80% 이상 또는 상장폐지) 확률(%) 추정과 근거.
6. recommended_adjustments: 가치평가 에이전트가 반영해야 할 조정(희석률, 현금환원, 할인율 프리미엄, 확률 하향 등)을 구체적으로. 동일한 위험을 현금흐름·확률·할인율에 중복 반영하지 않도록 어디에 반영할지 지정.
검색 규칙은 위 환경 제약을 따르세요.`

const riskPrompt = (s, macro) => `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '정량·위험 에이전트'입니다. 아래 종목 하나의 위험 특성을 추정하고 JSON 스키마로 보고하세요.

[대상 종목] ${s.name} (${s.ticker})

${COMMON}

${dataBlock(s)}

${macroBlock(macro)}

[추정 항목 - 모두 작성, 숫자는 % 단위 순수 숫자]
1. 역사적 변동성: 최근 1년·3년 연환산 변동성(%). 정확한 일별 데이터가 없으면 WebSearch로 52주 고저, 연초 대비 등락, 급등락 사례, 기간별 수익률을 찾아 추정하고 추정 방법을 price_history_notes에 적는다. 추정치임을 명시.
2. 하방 변동성(%), 시장 베타(KOSPI 또는 KOSDAQ 대비, 추정), 최대낙폭(최근 1·3·5년, %; 상장 기간이 짧으면 가능한 범위).
3. 일평균 거래대금(억원)과 유동성 평가, 주가 급락·갭 위험(실적 쇼크·공시·보호예수 해제·블록딜 사례).
4. 사업모델 경기민감도, 재무레버리지, 이익추정치 변동성(컨센서스 변화 폭), 이산적 사건위험(임상·수주·기술전환·고객 이탈·M&A).
5. 극단 시나리오: 주가가 0에 가까워지거나 상장폐지되는 연간 확률(%) 추정(p_zero_annual_pct). 대형 우량주는 0.0~0.1, 적자 소형주는 더 높게, 근거 명시.
6. 미래지향 연환산 변동성: 1년(fwd_vol_1y_pct), 3년 평균(fwd_vol_3y_pct), 5년 평균(fwd_vol_5y_pct). 과거 변동성을 그대로 외삽하지 말고 사업구조 변화·예정된 사건·시가총액 변화·시장 국면(현재 코스피 급락 국면)을 반영해 조정하고 rationale에 설명. 옵션 내재변동성은 실제로 확보하지 못하면 implied_vol_note에 "확보 불가"라고 적고 만들어내지 않는다.
검색 규칙은 위 환경 제약을 따르세요.`

const synthPrompt = (s, macro, r) => `당신은 한국 주식시장 기관투자자급 멀티에이전트 리서치 시스템의 '기업가치·펀더멘털 종합 에이전트'입니다. 한 종목에 대해 서로 독립적으로 작성된 4개 보고서(산업전문가, 독립일반분석가, 회계·포렌식, 정량·위험)를 통합해 최종 시나리오 트리를 확정하세요. 단순 산술평균이 아니라 데이터 품질·산업 전문성·가정의 타당성에 따라 가중치를 정하고, 중요한 의견 차이는 숨기지 말고 disagreements에 기록하세요.

[대상 종목] ${s.name} (${s.ticker}) / 산업군: ${s.industry}

${COMMON}

${dataBlock(s)}

${macroBlock(macro)}

[보고서 1: 산업전문가]
${JSON.stringify(r.specialist, null, 1)}

[보고서 2: 독립일반분석가]
${JSON.stringify(r.generalist, null, 1)}

[보고서 3: 회계·지배구조·포렌식]
${JSON.stringify(r.forensic, null, 1)}

[보고서 4: 정량·위험]
${JSON.stringify(r.risk, null, 1)}

[통합 원칙]
1. 두 분석가의 시나리오 가격이 크게 다르면 어느 쪽 가정이 데이터(검증된 실적·컨센서스·산업 사이클)에 더 부합하는지 판단해 가중치를 정하고 weighting_rationale에 적는다. 데이터 품질이 낮거나 의견 차이가 크면 극단 추정을 산업 베이스레이트 쪽으로 축소하고 그 사실을 treatment_note에 밝힌다.
2. 포렌식 보고서의 희석률·현금환원·영구손실 확률을 반영한다. 동일 위험을 확률·현금흐름·할인율에 중복 반영하지 않는다.
3. 위험 보고서의 변동성과 사건위험을 참고해 비관·낙관 시나리오의 폭이 현실적인지 점검한다(너무 좁거나 넓지 않게).
4. 각 기간(1y/3y/5y)마다 bear/base/bull 3개 시나리오, 확률 합 정확히 100, 기말 주가(희석 후 주당, 원), 누적 주당 현금환원(원), 희석률(%), 누적 TSR(%)을 적고 TSR을 직접 재계산해 검산한다. 시나리오 기말 주가는 '이익 x 멀티플' 근거를 rationale에 숫자로 쓴다. 3년·5년은 1년과 일관되게(기준 시나리오의 이익 경로가 이어지게) 구성한다.
5. 5년 시나리오에서는 현재 최고 성장률·최고 마진이 유지된다고 자동 가정하지 않는다. 성숙기 정상 마진과 합리적 최종 멀티플을 쓴다.
6. forecast_table에는 최종 채택한 2026E~2031E 전망(기준 시나리오)을 적는다.
7. flags: optimism_priced_in(현재 주가에 낙관론이 얼마나 반영됐는지: 높음/보통/낮음 + 한 줄), data_quality, rank_instability_risk(작은 가정 변화에 순위가 크게 바뀔 위험: 높음/보통/낮음 + 이유), discrete_outcome_stock(예/아니오 + 사건), prob_permanent_loss_5y_pct.
8. sensitivities: 원/달러 환율, 무위험금리·할인율, 최종 멀티플, 반도체 가격·AI 설비투자, 자동차 수요·관세, 바이오 임상·허가 확률, 추가 자금조달·희석, 핵심 고객 의존도 각각에 대해 이 종목의 기대 TSR이 어느 방향으로 얼마나 민감한지 한두 문장(해당 없으면 "해당 없음").
9. report_sections는 최종 보고서에 그대로 실릴 한국어 문단이다. 보고서 문체(평서문, '~다/~이다' 또는 명사형 종결)로 쓰고, 각 항목 3~8문장, 숫자와 출처 연도를 포함한다. one_line_driver는 순위를 결정한 핵심 요인 한 문장. low_rank_reasons는 이 종목이 하위권일 경우의 핵심 원인(현재 주가에 반영된 과도한 기대, 재무·희석·기술·고객·규제 위험), what_would_lift_rank는 어떤 변화가 생기면 순위가 크게 오를 수 있는지.
10. 검색 규칙은 위 환경 제약을 따르되 종합 단계에서는 원칙적으로 검색하지 않는다. 확인 불가 항목은 N/A.`

const stocks = (args && args.stocks) || []
const macro = (args && args.macroPath) || '(거시 시나리오 파일 미제공: 보수적 중립 가정 사용)'

log(`WF2: ${stocks.length}개 종목 독립 분석 시작`)

const results = await pipeline(
  stocks,
  (s) => parallel([
    () => agent(specialistPrompt(s, macro), { label: `spec:${s.name}`, phase: '독립 분석', schema: ANALYST_SCHEMA, effort: 'xhigh' }),
    () => agent(generalistPrompt(s, macro), { label: `gen:${s.name}`, phase: '독립 분석', schema: ANALYST_SCHEMA, effort: 'xhigh' }),
    () => agent(forensicPrompt(s, macro), { label: `forensic:${s.name}`, phase: '독립 분석', schema: FORENSIC_SCHEMA, effort: 'high' }),
    () => agent(riskPrompt(s, macro), { label: `risk:${s.name}`, phase: '독립 분석', schema: RISK_SCHEMA, effort: 'high' }),
  ]).then((r) => ({ specialist: r[0], generalist: r[1], forensic: r[2], risk: r[3] })),
  (r, s) => {
    const have = ['specialist', 'generalist', 'forensic', 'risk'].filter((k) => r[k])
    if (have.length < 2) { log(`${s.name}: 독립 분석 결과 부족(${have.join(',')}) - 종합 생략`); return { ...r, synthesis: null } }
    if (have.length < 4) log(`${s.name}: 일부 분석 누락(${['specialist', 'generalist', 'forensic', 'risk'].filter((k) => !r[k]).join(',')})`)
    return agent(synthPrompt(s, macro, r), { label: `synth:${s.name}`, phase: '종목별 종합', schema: SYNTH_SCHEMA, effort: 'max' }).then((syn) => ({ ...r, synthesis: syn }))
  },
)

return stocks.map((s, i) => ({ name: s.name, ticker: s.ticker, industry: s.industry, ...(results[i] || { failed: true }) }))
