export const meta = {
  name: 'kr-equity-wf4-verify',
  description: '최종 보고서 독립 검증: 식별·가격·산식 검증, 보고서-표 정합성, QC 체크리스트 감사 (+ 보조 문안 작성)',
  phases: [
    { title: '보조 문안', detail: '순위 변화 이유·데이터 특이사항·낙관 반영 종목 문안' },
    { title: '독립 검증', detail: '검증 에이전트 3명 병렬' },
  ],
}

const STR = { type: 'string' }
const STRARR = { type: 'array', items: STR }
const FINDINGS = { type: 'array', items: { type: 'object', properties: { id: STR, location: STR, severity: { type: 'string', enum: ['치명', '중요', '경미'] }, issue: STR, evidence: STR, suggested_fix: STR }, required: ['id', 'location', 'severity', 'issue', 'evidence', 'suggested_fix'] } }
const VERIFY_SCHEMA = { type: 'object', properties: { role: STR, checks_performed: STRARR, findings: FINDINGS, pass_summary: STR, overall: { type: 'string', enum: ['통과', '조건부 통과', '불통과'] } }, required: ['role', 'checks_performed', 'findings', 'pass_summary', 'overall'] }
const QC_SCHEMA = { type: 'object', properties: { role: STR, checklist: { type: 'array', items: { type: 'object', properties: { item: STR, status: { type: 'string', enum: ['충족', '부분충족', '미충족'] }, evidence: STR, fix: STR }, required: ['item', 'status', 'evidence', 'fix'] } }, findings: FINDINGS, overall: { type: 'string', enum: ['통과', '조건부 통과', '불통과'] } }, required: ['role', 'checklist', 'findings', 'overall'] }
const WRITER_SCHEMA = { type: 'object', properties: { part3_key_factors: { type: 'array', items: { type: 'object', properties: { stock: STR, factor: STR }, required: ['stock', 'factor'] } }, part4_reasons: { type: 'array', items: { type: 'object', properties: { stock: STR, reason: STR }, required: ['stock', 'reason'] } }, part2_notes: { type: 'array', items: { type: 'object', properties: { stock: STR, note: STR }, required: ['stock', 'note'] } }, priced_in_ranking: { type: 'array', items: { type: 'object', properties: { stock: STR, degree: STR, reason: STR }, required: ['stock', 'degree', 'reason'] } }, part8_analysis: STR, part7_summary: STR, biggest_disagreements: STRARR }, required: ['part3_key_factors', 'part4_reasons', 'part2_notes', 'priced_in_ranking', 'part8_analysis', 'part7_summary', 'biggest_disagreements'] }

const P = args.paths

const ENV = `[환경] WebSearch는 사용하지 않는다(검색 없이 파일만으로 수행). 모든 파일은 Read 도구로 끝까지 읽는다(큰 파일은 offset/limit으로 나눠 읽는다). 최종 출력은 JSON 스키마로만.`

const writerPrompt = `당신은 리서치 시스템의 '최종 심사 보조 작성 에이전트'입니다. 아래 산출물을 읽고 보고서에 들어갈 보조 문안을 작성하세요. 보고서 문체(평서문, '~다/~이다'), 숫자 포함, 각 문장 짧게.
[수치 인용 규칙(최우선)] 순위·기대 TSR·연환산·중앙값·손실확률·Sortino·CVaR·기준가는 반드시 tables.json(최종 엔진 결과)에서만 인용한다. 종목별 종합 보고서(synth)와 종목 데이터 파일에 적힌 확률가중 TSR·기준주가·시가총액은 반대심문·베이스레이트 축소·기준가 갱신 이전의 '원안' 값이라 최종과 다르므로 절대 인용하지 않는다(정성 근거·사업 내용·위험 요인만 가져온다). 영구손실 확률(p_zero)은 비관 시나리오에 내재돼 엔진이 별도 적용하지 않았으므로 '영구손실 확률 n%가 분포 꼬리를 키운다'는 식의 서술도 쓰지 않는다. 문장을 쓰기 전에 tables.json의 해당 종목 행을 다시 확인한다.
${ENV}
[읽을 파일]
- 순위·통계 요약(tables.json): ${P.tables}
- 시나리오 트리(trees.json; 종목별 기준가·기간별 시나리오·축소 가중치): ${P.trees}
- 몬테카를로 결과(results.json): ${P.results}
- 종목별 종합 보고서(JSON) 폴더: ${P.synthDir} (각 파일의 report_sections·flags·sensitivities 참고)
- 종목 데이터 폴더: ${P.stocksDir} (status_notes·price.note·unresolved 참고)
- 공통 거시 시나리오: ${P.macro}
[작성 항목]
0. part3_key_factors: 26개 종목 각각 3부 순위표 '핵심 요인' 열에 들어갈 한 문장(60~140자). 기대 TSR을 만드는 정성적 원천과 순위를 제한하는 핵심 위험을 적되, 숫자는 tables.json의 최종값(기대 TSR·손실확률·순위)만 쓰거나 아예 쓰지 않는다. 기준주가·시가총액·원안 TSR은 쓰지 않는다.
1. part4_reasons: 26개 종목 각각 '장기로 갈수록 순위가 상승·하락·유지되는 이유' 한 문장(1년 vs 5년 균형형 순위와 기대수익률 수치를 근거로. 예: 1년에는 사이클 고점 이익과 주주환원이 받치지만 5년에는 멀티플 정상화와 공급 증가로 연환산 기대수익률이 x%로 낮아져 순위가 n→m으로 하락한다).
2. part2_notes: 26개 종목 각각 '데이터상 특이사항' 한 문장(기준가 날짜가 10/22가 아닌 경우 그 사실, 분할·증자·무상증자·CB 등 주당가치 이벤트, 데이터 품질, 확인 불가 항목).
3. priced_in_ranking: 현재 주가에 낙관론이 가장 많이 반영된 종목 상위 6개(정도: 매우 높음/높음 + 근거: 현재 주가가 암시하는 성장·멀티플 vs 자체 전망).
4. part8_analysis: 민감도 분석 문단(8~15문장): 원/달러, 무위험금리·할인율, 최종 멀티플, 반도체 가격·AI 설비투자, 자동차 수요·관세, 바이오 임상·허가 확률, 추가 자금조달·희석, 핵심 고객 의존도 각각이 어느 종목의 순위를 어떻게 바꾸는지와 '순위 불안정' 종목 목록(flags.rank_instability_risk 높음 + 기대값-중앙값 괴리 큰 종목).
5. part7_summary: 의견 차이 요약 문단(6~10문장): 전망 차이가 가장 컸던 종목과 핵심 가정, 약세론의 가장 강한 반론, 반대심문 후 순위가 크게 바뀐 종목(있다면), 최종 심사가 어느 쪽에 가중치를 둔 이유.
6. biggest_disagreements: 분석가 간 전망 차이가 가장 컸던 종목 5개(종목명 + 한 줄 이유).`

const v1Prompt = `당신은 '독립 검증 에이전트 1(식별·가격·산식)'입니다. 다른 에이전트의 결론을 신뢰하지 말고 직접 재계산하세요. 가능한 검산은 Bash의 python3로 수행하세요(파일 읽기·계산만, 네트워크 금지).
${ENV}
[읽을 파일]
- 종목 데이터 폴더(26개 JSON): ${P.stocksDir}
- trees.json: ${P.trees}
- risk.json: ${P.risk}
- results.json: ${P.results}
- macro_rf.json: ${P.macroRf}
- 엔진 코드(산식 확인용): ${P.engine}
- 보고서: ${P.report}
[검증 항목]
1. 26개 종목이 모두 식별됐는지, 종목코드 6자리·시장(KOSPI/KOSDAQ)이 보고서 2부 표와 데이터 파일에서 일치하는지, 이름이 비슷한 다른 회사나 분할 전후 회사와 혼동한 흔적이 있는지(예: 삼성바이오로직스 vs 삼성에피스홀딩스, 화신 vs 화신정공, 와이씨 구 와이아이케이).
2. 종목별 기준 주가와 날짜가 명시돼 있는지, 시가총액 ≈ 기준가 × 상장주식수(±3%)인지, 장중가를 종가로 썼는지.
3. trees.json의 각 기간 세 시나리오 확률 합이 100인지, cum TSR = (기말주가+누적현금)/기준가 - 1 이 맞는지(보고서 5부 시나리오 표와 대조).
4. results.json: 기대 연환산 = (1+기대 누적)^(1/h) - 1 인지, 중앙값·P10/P50/P90·손실확률·CVaR의 부호와 크기가 상식적인지(예: P10 ≤ P50 ≤ P90, CVaR ≤ P10), Sortino = (기대연환산 - rf)/하방편차 인지 rf 값(1y 3.688%, 3y 3.822%, 5y 3.965%)이 쓰였는지.
5. 순위: 기대수익률 순위가 1년은 기대 누적 TSR, 3·5년은 기대 연환산 기준인지, 위험조정 순위가 Sortino→CVaR→손실확률 순인지, 균형형 점수 = 60/25/15 백분위 가중인지(results.json의 pr_* 값으로 재계산해 1~2개 종목 표본 검산).
6. 누적수익률과 연환산수익률이 보고서 본문에서 혼동된 곳이 있는지.
7. 배당·희석 반영 여부(trees의 cum_cash, 데이터의 dilution·무상증자·유상증자 등 주당가치 이벤트가 시나리오에 반영됐는지; 특히 엘앤씨바이오 1:1 무상증자·유상증자, SK하이닉스 ADR 신주·자사주 소각).
findings에는 치명/중요/경미 심각도와 구체적 수정안을 적으세요. 문제가 없으면 빈 배열과 통과.`

const v2Prompt = `당신은 '독립 검증 에이전트 2(보고서-표 정합성)'입니다. 보고서 본문의 결론·숫자·순위가 표(tables.json/results.json)와 일치하는지 검증하세요.
${ENV}
[읽을 파일]
- 보고서(Markdown): ${P.report}
- tables.json: ${P.tables}
- results.json: ${P.results}
- trees.json: ${P.trees}
[검증 항목]
1. 1부 핵심 결론의 상위 5개 목록(기간별 기대수익률·위험조정·일관성 상위)이 3부 표의 순위와 정확히 일치하는지.
2. 4부 순위 변화표의 순위가 3부 표와 일치하는지.
3. 5부 상세 분석 대상이 각 기간 균형형 상위 5개의 합집합인지, 6부 대상이 하위 5개·고손실확률 종목인지.
4. 본문에서 인용한 수치(기대 TSR, 손실확률, Sortino, 기준가, 시가총액)가 표와 다른 곳.
5. 9부 최종 판단의 후보 종목이 표의 순위·지표와 모순되지 않는지(가장 높은 기대수익률 후보 = 기대수익률 1위 등).
6. 보고서 첫머리에 분석 기준일시(KST), 주가 기준일, 1·3·5년 종료일, 기준 통화가 명시돼 있는지. 장중가와 종가 구분, 유료 DB에 접근한 것처럼 쓴 표현이 없는지, 확률을 확정적 사실처럼 쓴 표현이 없는지, 투자비중·매매지시가 없는지.
7. 수익률 표기(소수점 첫째 자리), 원화·% 통일, 확률 합 100 표기.
findings에 위치(섹션·종목)와 수정안을 구체적으로.`

const v3Prompt = `당신은 '독립 검증 에이전트 3(품질 통제 체크리스트 감사)'입니다. 아래 17개 항목을 보고서와 산출물에 대해 하나씩 감사하세요.
${ENV}
[읽을 파일]
- 보고서(Markdown): ${P.report}
- trees.json: ${P.trees}
- results.json: ${P.results}
- 종목 데이터 폴더: ${P.stocksDir}
- 종목별 종합 보고서 폴더: ${P.synthDir}
[체크리스트]
1. 26개 종목을 모두 확인했는가? 2. 정확한 종목코드와 상장·거래 상태를 확인했는가? 3. 분할 전후 회사나 유사한 이름을 혼동하지 않았는가? 4. 모든 가격과 재무자료에 기준일이 있는가? 5. 배당과 예상 희석을 반영했는가? 6. 시나리오 확률의 합이 100%인가? 7. 기대값과 중앙값을 구분했는가? 8. 누적수익률과 연환산수익률을 혼동하지 않았는가? 9. 경기순환주의 고점 이익을 장기화하지 않았는가?(SK하이닉스·삼성전자·한미반도체·HPSP·와이씨 등 5년 시나리오의 이익·멀티플 가정 점검) 10. 바이오기업의 성공확률과 자금조달 위험을 반영했는가?(엘앤씨바이오·바이오다인·삼성에피스홀딩스·삼성바이오로직스) 11. 동일한 위험을 현금흐름, 성공확률, 할인율에 중복 반영하지 않았는가? 12. 신규·소형주에 데이터 부족으로 인한 과도한 낙관을 부여하지 않았는가? 13. 현재 주가에 이미 반영된 기대를 역산했는가? 14. 기대수익률 순위와 위험조정 순위를 별도로 공개했는가? 15. 표의 순위와 본문의 결론이 일치하는가? 16. 모든 핵심 수치와 사실에 검증 가능한 출처가 있는가?(출처·기준일 표기 여부) 17. 지나치게 정밀한 숫자로 허위 확신을 만들지 않았는가?
각 항목에 충족/부분충족/미충족, 증거(보고서 어느 부분), 수정안을 적으세요.`

const stage = args.stage || 'all'
let writer = null
if (stage === 'writer' || stage === 'all') {
  writer = await agent(writerPrompt, { label: 'writer:보조문안', phase: '보조 문안', schema: WRITER_SCHEMA, effort: 'xhigh' })
}
let verifies = null
if (stage === 'verify2') {
  verifies = await parallel([
    () => agent(v2Prompt, { label: 'verify:보고서-표 정합성', phase: '독립 검증', schema: VERIFY_SCHEMA, effort: 'xhigh' }),
  ])
}
if (stage === 'verify' || stage === 'all') {
  verifies = await parallel([
    () => agent(v1Prompt, { label: 'verify:식별·가격·산식', phase: '독립 검증', schema: VERIFY_SCHEMA, effort: 'xhigh' }),
    () => agent(v2Prompt, { label: 'verify:보고서-표 정합성', phase: '독립 검증', schema: VERIFY_SCHEMA, effort: 'xhigh' }),
    () => agent(v3Prompt, { label: 'verify:QC체크리스트', phase: '독립 검증', schema: QC_SCHEMA, effort: 'xhigh' }),
  ])
}
return { writer, verifies }
