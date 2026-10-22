export const meta = {
  name: 'kr-equity-wf1c-price-refresh',
  description: '종목별 2026-10-22 종가(없으면 10-21 종가) 확정 - 종목 묶음당 1 에이전트, 검색 상한 엄수',
  phases: [{ title: '기준가 확정', detail: '10/22 종가 우선, 10/21 대체, 출처·날짜 기록' }],
}

const STR = { type: 'string' }
const SCHEMA = {
  type: 'object',
  properties: {
    prices: { type: 'array', items: { type: 'object', properties: { name: STR, ticker: STR, close_1022: STR, close_1021: STR, adopted_price: STR, adopted_date: STR, kind: STR, source_url: STR, source_date: STR, market_cap_bn: STR, shares_outstanding: STR, note: STR }, required: ['name', 'ticker', 'close_1022', 'close_1021', 'adopted_price', 'adopted_date', 'kind', 'source_url', 'note'] } },
    search_count: STR,
    unresolved: { type: 'array', items: STR },
  },
  required: ['prices', 'search_count', 'unresolved'],
}

const prompt = (batch, maxSearches) => `당신은 '종목 식별·데이터 검증 에이전트(기준가 확정 담당)'입니다. 아래 종목들의 2026-10-22(목) 종가를 확정하세요. 10/22 종가를 찾지 못하면 10/21 종가를 쓰고 날짜를 명시하세요.

[환경 제약] WebFetch·curl 등 직접 접속은 차단되어 있습니다. ToolSearch로 "select:WebSearch"를 로드한 뒤 WebSearch만 사용하세요. 이 턴의 검색 예산은 모든 에이전트가 공유하므로 당신은 최대 ${maxSearches}회까지만 검색할 수 있습니다(종목당 평균 ${Math.floor(maxSearches / batch.length)}회). '예산 소진' 응답이 오면 즉시 중단하세요. 확인되지 않은 값은 추측하지 말고 "N/A"로 두세요.

[배경] 2026-10-22 코스피는 5,533.77(-3.52%), 코스닥은 764.10(-3.62%)로 급락 마감했습니다. 10/21 코스피는 5,735.66(+3.29%)였습니다. 장중가와 종가를 구분하고, 기사 게시일과 거래일을 구분하세요. 검색어는 종목당 2가지를 다르게 조합하세요(모두 mode:"extended"): ① "<종목명> <종목코드> 22일 마감" 또는 "<종목명> 22일 코스닥 하락 마감 종가", ② "<종목명> 주가 10월 21일 종가" 또는 "<종목명> <종목코드> 10월 종가 시가총액". 기사 날짜가 '22일'로만 표시되면 전후 가격 흐름(직전 확인가와의 등락률 정합성, 코스피 -3.52%·코스닥 -3.62% 급락일)과 기사 게시일로 10월인지 판별하고, 판별이 안 되면 채택하지 마세요. 시가총액·상장주식수가 함께 나오면 기록하세요.

[종목 목록 (현재 보유 기준가와 날짜)]
${batch.map((b) => `- ${b.name} (${b.ticker}): 현재 기준가 ${b.price}원 (${b.date}, ${b.kind || '종가'})`).join('\n')}

[출력] 각 종목에 대해 close_1022(10/22 종가, 없으면 N/A), close_1021(10/21 종가, 없으면 N/A), adopted_price(채택 기준가: 10/22 종가 > 10/21 종가 > 기존 기준가 순), adopted_date, kind(종가/장중체결가), source_url, source_date, market_cap_bn(억원, 있으면), shares_outstanding(주, 있으면), note(근거·충돌·주의사항). 숫자는 순수 숫자 문자열. 최종 출력은 JSON 스키마로만.`

const batches = (args && args.batches) || []
const maxSearches = (args && args.maxSearches) || 10
log(`기준가 확정: ${batches.length}개 묶음, 묶음당 최대 ${maxSearches}회 검색`)
const out = await parallel(batches.map((b, i) => () => agent(prompt(b, maxSearches), { label: `price:batch${i + 1}`, phase: '기준가 확정', schema: SCHEMA, effort: 'medium' })))
return out
