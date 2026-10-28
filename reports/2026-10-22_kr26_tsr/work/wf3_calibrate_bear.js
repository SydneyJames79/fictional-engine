export const meta = {
  name: 'kr-equity-wf3-calibrate-bear',
  description: '베이스레이트 보정(산업군별) + 잠정 상위 종목 반대심문 + 종목별 최종 심사',
  phases: [
    { title: '베이스레이트 보정', detail: '산업군별 1 에이전트, 극단 추정 축소 가중치 제안' },
    { title: '반대심문', detail: '잠정 상위 종목마다 약세론 에이전트 1명' },
    { title: '최종 심사', detail: '반대심문 결과를 반영해 시나리오 트리 확정' },
  ],
}

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const SCEN_ITEM = { type: 'object', properties: { horizon: STR, name: { type: 'string', enum: ['bear', 'base', 'bull'] }, probability_pct: STR, end_price_krw: STR, cum_cash_per_share_krw: STR, dilution_pct: STR, cum_tsr_pct: STR, rationale: STR }, required: ['horizon', 'name', 'probability_pct', 'end_price_krw', 'cum_cash_per_share_krw', 'dilution_pct', 'cum_tsr_pct', 'rationale'] }

const CALIB_SCHEMA = {
  type: 'object',
  properties: {
    industry_group: STR,
    assessments: { type: 'array', items: { type: 'object', properties: { stock: STR, data_quality: STR, analyst_disagreement: STR, extreme_estimate_flag: STR, shrink_weight: STR, prior_used: STR, comparable_cases: STR, base_rate_evidence: STR, override_scenarios: { type: 'array', items: SCEN_ITEM }, override_reason: STR, rationale: STR }, required: ['stock', 'data_quality', 'analyst_disagreement', 'extreme_estimate_flag', 'shrink_weight', 'prior_used', 'comparable_cases', 'base_rate_evidence', 'override_scenarios', 'override_reason', 'rationale'] } },
    cross_stock_consistency: STR,
    sector_bias_check: STR,
    narrative_ko: STR,
  },
  required: ['industry_group', 'assessments', 'cross_stock_consistency', 'sector_bias_check', 'narrative_ko'],
}

const BEAR_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR,
    answers: { type: 'array', items: { type: 'object', properties: { question: STR, finding: STR, evidence: STR, severity: { type: 'string', enum: ['낮음', '보통', '높음'] } }, required: ['question', 'finding', 'evidence', 'severity'] } },
    strongest_arguments: STRARR,
    proposed_changes: { type: 'array', items: { type: 'object', properties: { horizon: STR, change: STR, from_value: STR, to_value: STR, reason: STR }, required: ['horizon', 'change', 'from_value', 'to_value', 'reason'] } },
    proposed_scenarios: { type: 'array', items: SCEN_ITEM },
    rank_should_change: STR,
    what_bulls_get_right: STR,
    narrative_ko: STR,
    search_count: STR,
  },
  required: ['stock', 'answers', 'strongest_arguments', 'proposed_changes', 'proposed_scenarios', 'rank_should_change', 'what_bulls_get_right', 'narrative_ko', 'search_count'],
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    stock: STR,
    final_scenarios: { type: 'array', items: SCEN_ITEM },
    accepted_bear_points: STRARR,
    rejected_bear_points: STRARR,
    calibration_applied: STR,
    changes_summary: STR,
    weighting_rationale: STR,
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    narrative_ko: STR,
  },
  required: ['stock', 'final_scenarios', 'accepted_bear_points', 'rejected_bear_points', 'calibration_applied', 'changes_summary', 'weighting_rationale', 'confidence', 'narrative_ko'],
}

const SEARCH_ALLOWED = !!(args && args.searchAllowed)
const SEARCH_RULE = SEARCH_ALLOWED
  ? '추가 자료가 꼭 필요할 때만 ToolSearch로 "select:WebSearch"를 로드한 뒤 WebSearch를 최대 3회 사용한다. 예산 소진 응답이 오면 즉시 중단한다.'
  : '이번 턴의 WebSearch 예산이 소진되어 검색을 할 수 없다. 검색을 시도하지 말고 제공된 파일만으로 수행한다.'

const COMMON = `[공통 기준] 분석 기준 2026-10-22(목) 15:40 KST, 원화. 기간 종료일 1년 2027-10-22 / 3년 2029-10-22 / 5년 2031-10-22. TSR = (기말 주가[희석 후 주당] + 누적 주당 현금환원) / 기준 주가 - 1. 세 시나리오 확률 합은 기간마다 정확히 100. 숫자는 순수 숫자 문자열(%는 숫자만, 금액은 원 또는 억원). 추측 금지, 확인 불가는 N/A.
[환경 제약] WebFetch·curl 직접 접속 차단. ${SEARCH_RULE} 파일은 Read 도구로 끝까지 읽는다. 최종 출력은 JSON 스키마로만.`

const calibPrompt = (g) => `당신은 '베이스레이트·예측 보정 에이전트'입니다. 산업군 "${g.industry}"에 속한 종목들의 종합 시나리오 트리와 몬테카를로 잠정 결과를 검토하고, 데이터가 부족하거나 분석가 간 의견 차이가 큰 종목의 극단적 추정을 산업 베이스레이트(사전분포) 쪽으로 축소할 가중치를 제안하세요.

${COMMON}

[읽을 파일]
- 공통 거시·산업 시나리오(sector_priors 포함): ${g.macroPath}
- 종목별 종합 시나리오 트리(각 JSON):
${g.stocks.map((s) => `  - ${s.name} (${s.ticker}): ${s.synthPath}`).join('\n')}
- 몬테카를로 잠정 결과 요약(모든 종목의 기대 TSR·중앙값·손실확률·순위): ${g.provisionalPath}

[원칙]
1. 비슷한 산업·성장단계·시가총액·재무구조를 가진 국내외 기업의 역사적 사례를 comparable_cases에 적고, 높은 성장률이나 대형 수주가 실제 주주수익률로 이어진 비율(base_rate_evidence)을 근거로 쓴다. 사례를 결과에 맞춰 고르는 체리피킹을 금지한다. 기억에 의존한 사례는 "(memory_unverified)"로 표시한다.
2. shrink_weight는 0.5~1.0: 종목 자체 추정에 둘 가중치. 1.0이면 축소 없음. 데이터 품질 '높음'+의견차 작음 → 0.9~1.0, '보통' → 0.75~0.9, '낮음' 또는 의견차 큼 → 0.5~0.75. 엔진은 각 시나리오 TSR을 w*종목추정 + (1-w)*산업 사전 기대 TSR로 조정한다(확률은 유지). 신뢰도 점수를 곱해 이중으로 벌점을 주지 않는다.
3. 시나리오 트리 자체가 내부 모순(확률 합≠100, TSR 산식 불일치, 1·3·5년 경로 비일관, 희석 누락, 5년 멀티플이 성숙기업으로서 비현실적)이면 override_scenarios에 수정된 전체 시나리오(해당 기간의 bear/base/bull 3개 모두)를 적고 override_reason에 이유를 적는다. 모순이 없으면 빈 배열.
4. 정보가 적다는 이유만으로 작은 종목에 비현실적으로 높은 기대수익률을 부여하지 않았는지, 반대로 데이터 부족을 이유로 과도하게 벌점을 주지 않았는지 점검한다.
5. cross_stock_consistency: 같은 산업군 안에서 동일 거시 가정이 일관되게 적용됐는지(예: 메모리 사이클 가정이 종목마다 다르지 않은지). sector_bias_check: 이 산업군의 낙관 가정이 다른 산업군 대비 과도한지.
6. narrative_ko: 보고서용 문단(보고서 문체, 5~10문장): 어떤 종목을 왜 얼마나 축소했는지.`

const bearPrompt = (s) => `당신은 '반대심문·약세론 에이전트'입니다. 잠정 상위권에 오른 종목 "${s.name} (${s.ticker})"의 투자논지를 공격하세요. 상위 종목을 방어하지 말고, 타당한 반론이면 시나리오 확률과 가격을 실제로 바꾸도록 제안하세요. 다만 근거 없는 비관도 금지합니다. 각 질문에 증거(데이터 파일의 수치·사실)를 붙이세요.

${COMMON}

[읽을 파일]
- 검증 데이터: ${s.dataPath}
- 종합 시나리오 트리(공격 대상): ${s.synthPath}
- 산업전문가 보고서: ${s.specPath}
- 독립일반분석가 보고서: ${s.genPath}
- 회계·포렌식 보고서: ${s.forPath}
- 공통 거시 시나리오: ${s.macroPath}
- 잠정 순위·통계: ${s.provisionalPath}

[반드시 답할 10개 질문]
1. 시장이 이미 낙관론을 주가에 반영하지 않았는가? (현재 주가가 암시하는 성장·마진을 역산)
2. 예상 성장률이 업계 베이스레이트보다 지나치게 높은가?
3. 매출이 증가해도 마진과 현금흐름이 악화될 수 있는가?
4. 고객사의 자체개발·이원화·가격인하 요구가 있는가?
5. 기술이 대체되거나 시장이 예상보다 작을 가능성은?
6. 자금조달이나 희석을 누락하지 않았는가?
7. 낮은 유동성이 기대수익률을 왜곡하지 않는가?
8. 단일 수주·임상·고객·정책에 과도하게 의존하지 않는가?
9. 성공 시나리오의 확률을 과대평가하지 않았는가?
10. 5년 뒤 적용한 멀티플이 성숙기업으로서 너무 높은가?

[출력] answers(10개), strongest_arguments(가장 강한 반론 3~5개), proposed_changes(기간별 구체 변경: 확률·기말주가·현금환원), proposed_scenarios(변경을 반영한 전체 9개 시나리오; 변경 불필요면 원안 그대로 복사), rank_should_change(순위가 내려가야 하는지와 정도: '크게 하락'/'소폭 하락'/'유지' + 이유), what_bulls_get_right(강세론이 맞는 점), narrative_ko(보고서용 문단 5~8문장).`

const judgePrompt = (s, bear, calib) => `당신은 '최종 심사 에이전트'입니다. 종목 "${s.name} (${s.ticker})"에 대해 종합 시나리오 트리(원안), 약세론 에이전트의 반대심문 결과, 베이스레이트 보정 의견을 통합해 최종 시나리오 트리를 확정하세요. 단순 산술평균이 아니라 데이터 품질·산업 전문성·가정의 타당성에 따라 가중치를 정하고, 어느 쪽 전망에 더 큰 가중치를 둔 이유를 밝히세요. 반대심문이 타당하면 실제로 분포와 순위가 바뀌게 반영하고, 타당하지 않으면 기각 이유를 적으세요.

${COMMON}

[읽을 파일]
- 종합 시나리오 트리(원안): ${s.synthPath}
- 검증 데이터: ${s.dataPath}
- 공통 거시 시나리오: ${s.macroPath}

[약세론 에이전트 결과]
${typeof bear === 'string' ? '다음 파일을 Read 도구로 전부 읽으세요: ' + bear : JSON.stringify(bear, null, 1)}

[베이스레이트 보정 의견(이 종목 해당분)]
${typeof calib === 'string' ? '다음 파일을 Read 도구로 전부 읽으세요(해당 종목 항목만 참고): ' + calib : JSON.stringify(calib, null, 1)}

[출력 규칙]
- final_scenarios: 1y/3y/5y 각 bear/base/bull 총 9개. 확률 합 100, cum_tsr_pct를 직접 재계산해 검산. 기말 주가는 희석 후 주당 기준.
- calibration_applied: 보정 에이전트의 shrink_weight를 어떻게 다뤘는지(엔진이 별도로 축소를 적용하므로 여기서는 시나리오 값에 이중 적용하지 말고, 구조적 모순 수정만 반영했다고 명시).
- changes_summary: 원안 대비 무엇이 얼마나 바뀌었는지 숫자로.
- narrative_ko: 보고서 7부('에이전트 의견 차이와 반대심문 결과')에 실릴 문단(보고서 문체, 5~8문장).`

const stage = (args && args.stage) || 'all'
const groups = (args && args.groups) || []
const targets = (args && args.bearTargets) || []
const calibIn = (args && args.calibByStock) || {}

log(`WF3 stage=${stage}: 보정 ${groups.length}개 산업군, 반대심문 ${targets.length}개 종목`)

let calibs = []
const calibByStock = { ...calibIn }
if (stage === 'all' || stage === 'calib') {
  calibs = await parallel(groups.map((g) => () => agent(calibPrompt(g), { label: `calib:${g.industry}`, phase: '베이스레이트 보정', schema: CALIB_SCHEMA, effort: 'xhigh' })))
  calibs.filter(Boolean).forEach((c) => (c.assessments || []).forEach((a) => { calibByStock[a.stock] = { ...a, industry_group: c.industry_group } }))
}

let judged = []
if (stage === 'bearonly') {
  judged = await parallel(targets.map((s) => () => agent(bearPrompt(s), { label: `bear:${s.name}`, phase: '반대심문', schema: BEAR_SCHEMA, effort: 'xhigh' }).then((b) => ({ bear: b, judge: null }))))
}
if (stage === 'judge') {
  judged = await parallel(targets.map((s) => () => agent(judgePrompt(s, s.bearPath, s.calibPath), { label: `judge:${s.name}`, phase: '최종 심사', schema: JUDGE_SCHEMA, effort: 'max' }).then((j) => ({ bear: null, judge: j }))))
}
if (stage === 'all' || stage === 'bear') {
  judged = await pipeline(
    targets,
    (s) => agent(bearPrompt(s), { label: `bear:${s.name}`, phase: '반대심문', schema: BEAR_SCHEMA, effort: 'xhigh' }),
    (bear, s) => {
      if (!bear) { log(`${s.name}: 반대심문 결과 없음 - 심사 생략`); return { bear: null, judge: null } }
      return agent(judgePrompt(s, bear, calibByStock[s.name] || null), { label: `judge:${s.name}`, phase: '최종 심사', schema: JUDGE_SCHEMA, effort: 'max' }).then((j) => ({ bear, judge: j }))
    },
  )
}

return { calibrations: calibs, bear_judge: targets.map((s, i) => ({ name: s.name, ...(judged[i] || { bear: null, judge: null }) })) }
