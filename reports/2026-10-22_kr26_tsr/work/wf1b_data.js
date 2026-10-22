export const meta = {
  name: 'kr-equity-wf1b-data',
  description: '한국 26개 종목 식별·가격·재무·희석 데이터 검증(종목당 1 에이전트) + 거시 시나리오 수집',
  phases: [
    { title: '종목 데이터 검증', detail: '종목당 1 에이전트, WebSearch만 사용, 출처·기준일 필수' },
    { title: '거시 시나리오', detail: '금융시장 담당 + 산업사이클 담당' },
  ],
}

const S = (t) => ({ type: 'string' })
const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const SRC = { type: 'array', items: { type: 'object', properties: { url: STR, title: STR, date: STR }, required: ['url'] } }

const STOCK_SCHEMA = {
  type: 'object',
  properties: {
    input_name: STR,
    legal_name: STR,
    ticker: STR,
    market: STR,
    listed: { type: 'boolean' },
    tradable: { type: 'boolean' },
    status_notes: STR,
    share_class: STR,
    corporate_actions_24m: STR,
    price: { type: 'object', properties: { value: STR, date: STR, kind: STR, source_url: STR, source_date: STR, note: STR, alt_price_1021: STR }, required: ['value', 'date', 'kind', 'source_url', 'note'] },
    market_cap_bn: { type: 'object', properties: { value: STR, date: STR, source_url: STR, note: STR }, required: ['value', 'date', 'source_url'] },
    shares_outstanding: { type: 'object', properties: { value: STR, date: STR, source_url: STR, note: STR }, required: ['value', 'date', 'source_url'] },
    treasury_shares: { type: 'object', properties: { count: STR, pct: STR, note: STR, source_url: STR }, required: ['note'] },
    fiscal_year_end: STR,
    latest_report_period: STR,
    financials: { type: 'array', items: { type: 'object', properties: { period: STR, revenue_bn: STR, op_income_bn: STR, net_income_bn: STR, ocf_bn: STR, capex_bn: STR, source_url: STR, note: STR }, required: ['period', 'revenue_bn', 'op_income_bn', 'net_income_bn', 'source_url'] } },
    balance_sheet: { type: 'object', properties: { date: STR, cash_bn: STR, total_debt_bn: STR, net_cash_bn: STR, equity_bn: STR, source_url: STR, note: STR }, required: ['date', 'note'] },
    shareholder_returns: { type: 'object', properties: { dps_latest_krw: STR, dividend_yield_pct: STR, buyback_policy: STR, valueup_disclosure: STR, source_url: STR }, required: ['dps_latest_krw', 'dividend_yield_pct', 'buyback_policy'] },
    dilution: { type: 'object', properties: { convertibles: STR, stock_options: STR, rights_issues: STR, est_dilution_pct: STR, source_url: STR }, required: ['convertibles', 'stock_options', 'rights_issues', 'est_dilution_pct'] },
    ownership: { type: 'object', properties: { largest_holder: STR, largest_holder_pct: STR, overhang_notes: STR, source_url: STR }, required: ['largest_holder', 'largest_holder_pct', 'overhang_notes'] },
    business: { type: 'object', properties: { summary: STR, segments: STR, key_customers: STR, customer_concentration: STR, competitors: STR, industry_group: STR }, required: ['summary', 'segments', 'key_customers', 'customer_concentration', 'industry_group'] },
    consensus: { type: 'object', properties: { target_price_avg: STR, target_price_date: STR, n_brokers: STR, rev_2026e_bn: STR, op_2026e_bn: STR, rev_2027e_bn: STR, op_2027e_bn: STR, recent_report_summary: STR, source_url: STR }, required: ['target_price_avg', 'target_price_date', 'recent_report_summary'] },
    recent_events: { type: 'array', items: { type: 'object', properties: { event_date: STR, article_date: STR, event: STR, source_url: STR }, required: ['event', 'source_url'] } },
    data_quality: { type: 'string', enum: ['높음', '보통', '낮음'] },
    unresolved: STRARR,
    sources: SRC,
    search_count: STR,
  },
  required: ['input_name', 'legal_name', 'ticker', 'market', 'listed', 'tradable', 'status_notes', 'share_class', 'corporate_actions_24m', 'price', 'market_cap_bn', 'shares_outstanding', 'treasury_shares', 'fiscal_year_end', 'latest_report_period', 'financials', 'balance_sheet', 'shareholder_returns', 'dilution', 'ownership', 'business', 'consensus', 'recent_events', 'data_quality', 'unresolved', 'sources', 'search_count'],
}

const MACRO_SCHEMA = {
  type: 'object',
  properties: {
    role: STR,
    as_of: STR,
    facts: { type: 'array', items: { type: 'object', properties: { topic: STR, value: STR, as_of_date: STR, source_url: STR, source_date: STR, note: STR }, required: ['topic', 'value', 'as_of_date', 'source_url'] } },
    risk_free: { type: 'object', properties: { ktb_1y: STR, ktb_2y: STR, ktb_3y: STR, ktb_5y: STR, ktb_10y: STR, date: STR, source_url: STR, note: STR }, required: ['ktb_3y', 'ktb_5y', 'date', 'note'] },
    scenarios: { type: 'array', items: { type: 'object', properties: { horizon: STR, name: STR, probability_pct: STR, description: STR, key_numbers: STR, sector_implications: STR }, required: ['horizon', 'name', 'probability_pct', 'description', 'key_numbers', 'sector_implications'] } },
    cycle_positions: { type: 'array', items: { type: 'object', properties: { industry: STR, position: STR, rationale: STR, key_dates: STR }, required: ['industry', 'position', 'rationale'] } },
    narrative: STR,
    unresolved: STRARR,
    sources: SRC,
    search_count: STR,
  },
  required: ['role', 'as_of', 'facts', 'scenarios', 'cycle_positions', 'narrative', 'unresolved', 'sources', 'search_count'],
}

const ENV_RULES = `[환경 제약 - 매우 중요]
- 이 환경에서는 WebFetch, curl 등 웹페이지 직접 접속이 모두 차단되어 있습니다(DNS 미해석·403). 시도하지 마세요.
- 유일한 자료 수집 수단은 WebSearch 도구입니다. 먼저 ToolSearch에 "select:WebSearch"를 넣어 스키마를 로드한 뒤 사용하세요.
- WebSearch는 검색 결과 요약과 URL 목록을 돌려줍니다. 요약문의 수치는 해당 URL(기사·공시 요약)에서 나온 것으로 기록하되, 기사 게시일과 사건 발생일을 구분하세요. 요약문이 서로 다른 날짜의 수치를 섞을 수 있으니 날짜를 꼭 확인하세요.
- 핵심 항목은 mode:"extended", 보조 항목은 mode:"standard"로 검색하세요. 한국어 검색을 기본으로 하고 영문 검색을 보조로 쓰세요.
- 확인되지 않은 수치는 절대 추측하지 말고 "N/A"로 두고 unresolved에 사유를 적으세요. 기억에만 의존한 수치는 쓰지 말거나 반드시 "(memory_unverified)" 표시를 붙이세요.
- 숫자 표기: 금액은 억원(1억원 = 1e8 KRW) 단위의 순수 숫자 문자열(예: "12345.6"), 주가는 원 단위 순수 숫자(예: "183000"), 주식수는 주 단위 순수 숫자, 비율은 % 숫자만(예: "3.2"). 쉼표·단위 문자를 넣지 마세요. 모르면 "N/A".
- 최종 출력은 지정된 JSON 스키마(StructuredOutput)로만 반환합니다.

[분석 기준 시각] 2026-10-22(목) 15:40 KST. 한국 증시는 15:30에 마감했고, 오늘 코스피는 5,533.77(-3.52%)로 마감했습니다(아시아경제 마감 기사). 전날 급등분을 반납한 급락일이므로 10/21과 10/22 종가가 크게 다를 수 있습니다.`

const stockPrompt = (s) => `당신은 한국 주식시장 기관투자자급 리서치 시스템의 '종목 식별·데이터 검증 에이전트'입니다. 아래 한 종목을 맡아 사실을 확인하고 JSON 스키마로만 반환하세요.

[대상 종목] 입력명: ${s.name} / 추정 종목코드(검증 필요): ${s.code} / 추정 시장(검증 필요): ${s.market} / 메모: ${s.hint}

${ENV_RULES}

[검색 횟수 상한 - 엄격] 이 턴의 WebSearch 예산은 200회이며 동시에 도는 모든 에이전트가 나눠 씁니다. 당신은 최대 ${s.maxSearches || 9}회까지만 검색할 수 있습니다. 이 상한을 넘기면 다른 종목 에이전트가 검색을 못 하게 되므로 절대 초과하지 마세요. '예산 소진' 응답을 받으면 즉시 검색을 멈추고 가진 자료로 마무리하세요.
권장 검색 순서(각 1회, 모두 extended): (1) "${s.name} 주가 10월 22일 종가" 또는 "${s.name} 22일 마감" — 10/22 종가와 시가총액·상장주식수, (2) "${s.name} 2분기 실적 2026 매출 영업이익" — 2Q26·1H26 실적, (3) "${s.name} 2025년 실적 매출 영업이익 순이익" — FY2025·FY2024, (4) "${s.name} 전환사채 유상증자 2026" — 희석 요인·자금조달, (5) "${s.name} 목표주가 컨센서스 2026년 10월" — 컨센서스·최근 리포트, (6) "${s.name} 최대주주 지분율 자사주 배당 2026" — 지배구조·주주환원, (7) "${s.name} 수주 계약 2026년 9월 10월" — 최근 이벤트, (8)~(9) 위에서 비어 있는 핵심 항목(주가 날짜 확정, 순현금, 종목코드·시장 확인 등) 보강. 10/22 종가를 (1)에서 못 찾으면 (8)에서 "${s.name} 주가 10월 21일"로 1회만 더 시도하세요.

[확정해야 할 항목]
1. 식별: 정확한 법인명, 6자리 종목코드, 상장시장(KOSPI/KOSDAQ/기타), 상장 여부, 현재 거래 가능 여부(거래정지·관리종목·투자주의환기종목·상장폐지 심사 여부), 보통주/우선주/지주회사/사업회사 구분, 최근 24개월 내 사명 변경·인적분할·물적분할·합병·재상장·이전상장 여부. 이름이 비슷한 다른 회사나 분할 전후 회사와 혼동하지 마세요. 추정 종목코드가 틀렸으면 바로잡으세요.
2. 기준 주가: 2026-10-22 종가를 최우선으로 찾으세요(검색어 예: "${s.name} 주가 10월 22일", "${s.name} 22일 마감", "${s.name} 종가 2026.10.22", "${s.name} 급락 22일", "${s.name} 주가" extended). 찾지 못하면 2026-10-21 종가, 그것도 없으면 확인 가능한 가장 최근 종가를 쓰고 날짜를 명시하세요. 반드시 가격·날짜·(종가/장중체결가 구분)·출처 URL·기사 게시일을 기록하고, 10/21 종가도 찾았다면 alt_price_1021에 적으세요. 장중가를 종가로 오인하지 마세요.
3. 시가총액(억원)과 그 기준일, 상장주식수(보통주), 자기주식 수와 비율, 완전희석에 필요한 정보(CB·BW·EB·RCPS·스톡옵션 미행사 잔량), 최대주주와 특수관계인 지분율, 보호예수 해제·블록딜·오버행.
4. 최근 결산: 회계연도 말, 최신 공시 보고서 기간(2026년 반기/2분기, 3분기 실적이 이미 나왔다면 그것도), 매출액·영업이익·순이익(억원)을 FY2024, FY2025, 2026년 상반기(또는 최신 분기·TTM) 각각. 영업현금흐름·CAPEX·순현금(순차입금)·자기자본도 가능한 범위에서. 분할·합병 전후 수치 비교 가능 여부를 note에 적으세요.
5. 주주환원: 최근 주당배당금(결산 기준 연도 명시), 배당수익률, 자사주 매입·소각 정책과 최근 공시, 밸류업 공시 여부.
6. 자금조달·희석: 최근 24개월 유상증자·CB·BW·EB 발행(규모·전환가·잔량), 예정된 증자, 스톡옵션 규모, 추정 희석률(%).
7. 사업: 핵심 사업과 제품, 부문별 매출 비중, 핵심 고객과 고객 집중도(상위 고객 비중), 경쟁사, 산업군 분류(반도체·AI하드웨어·디스플레이장비 / 자동차·전장·SDV·부품 / 바이오의약품·의료기기·진단 / 우주항공·위성통신·5G6G / ESS·산업재·특수소재 중 택1, 복수면 주된 것).
8. 컨센서스: 증권사 평균 목표주가와 기준일·증권사 수, 2026E·2027E 매출·영업이익 컨센서스(있으면), 최근 1~2개월 리포트 요지(상향·하향 방향 포함).
9. 최근 6개월 핵심 이벤트(최대 10개): 수주·계약·실적 서프라이즈/쇼크·임상/허가·규제·소송·경영진·M&A·지분 변동 등. 사건일과 기사일을 구분해 기록.
10. 데이터 품질(높음/보통/낮음)과 미해결 항목.

[주의] 출처 간 수치가 충돌하면 둘 다 note에 적고 어느 쪽을 채택했는지 밝히세요. 유료 DB에 접근한 것처럼 쓰지 마세요. 시가총액이 '주가 x 상장주식수'와 크게 어긋나면 그 사실을 note에 적으세요.`

const MACRO_A = `당신은 '거시경제·시장체제 에이전트(금융시장 담당)'입니다. 2026-10-22 15:40 KST 기준 최신 정보를 WebSearch로 확인하고 출처·날짜를 붙여 JSON 스키마로 보고하세요.

${ENV_RULES}

[검색 횟수] 최소 18회, 필요하면 35회. 핵심 수치(국고채 수익률, 환율, 지수, 기준금리)는 extended로 검색하세요.

[확인 항목]
1. 한국은행 기준금리: 현재 수준, 최근 결정일과 결정 내용, 다음 금통위 일정, 시장의 향후 경로 기대.
2. 미국: 연방기금금리 현재 범위, 최근 FOMC 결정일과 내용, 점도표·선물시장이 반영한 경로, 미국 10년물 수익률(최근 날짜).
3. 국고채 1년·2년·3년·5년·10년 수익률: 가장 최근 마감일(10/21 또는 10/22) 기준. 금융투자협회·연합인포맥스·SBS Biz 등 마감 기사 활용. 1년물을 못 찾으면 통안채 1년이나 2년물로 대체하고 note에 밝히세요.
4. 원/달러 환율: 가장 최근 주간 종가(3시30분)와 날짜, 2026년 추이(고점·저점·평균), 최근 변동 원인.
5. KOSPI·KOSDAQ: 10/22 종가, 전일 대비, 2026년 YTD와 최근 1년 수익률, 사상 최고치와 날짜, 최근 조정 배경, 12개월 선행 PER·PBR(출처·기준일), 역사적 밴드 대비 위치, 외국인·기관 수급 추세, 신용잔고·거래대금.
6. 한국 증시 제도: 상법 개정(이사 충실의무·집중투표 등) 시행 상태, 밸류업 프로그램, 배당소득 분리과세, 자사주 소각 의무화 논의, 공매도 재개 상태, 세제 변경. 각 항목의 현재 상태와 일정.
7. 글로벌 경기·지정학: 미국 성장·고용·물가 최신, 중국 경기, 미국 관세 정책 현황과 한미 관세 협상 결과(자동차·반도체·의약품 관세율, 시행 상태), 대만·중동·러-우 상황, AI 투자 거품 논쟁과 미국 증시 밸류에이션.
8. 한국 수출: 최근 월 수출 증가율, 반도체 수출, 자동차 수출(산업부·관세청 발표, 날짜).
9. 자금조달 환경: 국내 IPO·유상증자 시장, 회사채 스프레드, 코스닥 바이오·중소형주 자금조달 분위기, 밸류에이션 디스카운트 논쟁.
10. 리스크 프리미엄: 한국 CDS 프리미엄, 신용등급 변화.

[시나리오] 그 다음, 1년(2026-10-22~2027-10-22), 3년(~2029-10-22), 5년(~2031-10-22) 각 기간에 대해 비관/기준/낙관 거시 시나리오와 확률(각 기간 합 100%)을 제시하세요. 각 시나리오에 국고채 수익률 경로, 원/달러 범위, KOSPI·KOSDAQ 기대 연환산수익률, 미국 금리, 밸류에이션 멀티플 방향을 숫자로 적고 산업별 함의를 간단히 적으세요. risk_free에는 Sortino 계산용 1년·3년·5년 국고채 수익률(가장 최근 날짜)을 적으세요. 모든 수치에 출처와 날짜를 붙이고, 확인하지 못한 것은 N/A로 두세요.`

const MACRO_B = `당신은 '거시경제·시장체제 에이전트(산업 사이클 담당)'입니다. 2026-10-22 15:40 KST 기준 최신 정보를 WebSearch로 확인하고 출처·날짜를 붙여 JSON 스키마로 보고하세요.

${ENV_RULES}

[검색 횟수] 최소 20회, 필요하면 40회. 각 산업마다 최소 2회(그중 1회는 extended) 검색하세요.

[확인 항목 - 각 항목은 '현재 상태(날짜)', '최근 변화', '2027~2031 전망 근거'로 정리]
1. 글로벌 AI·데이터센터 투자: 2026년·2027년 하이퍼스케일러(MS·구글·아마존·메타·오라클) CAPEX 가이던스와 2026년 3분기 실적 시즌 발언, OpenAI·xAI 등 투자 계획, AI 거품 논쟁과 투자 둔화 신호, 전력·GPU 공급 제약, 엔비디아 최근 실적·가이던스.
2. 메모리 사이클: HBM3E·HBM4 수요·공급과 가격 협상(2027년 물량), DRAM·NAND 고정가격·계약가격 추이(TrendForce 등 2026년 3·4분기 발표), 삼성전자·SK하이닉스·마이크론 최근 분기 실적과 가이던스, 2027년 공급 증설 계획, 사이클 고점 논쟁, CXMT·YMTC 등 중국 추격.
3. 반도체 장비·설비투자: WFE 2026·2027 전망(SEMI·주요 장비사), 삼성·SK하이닉스·TSMC·마이크론 CAPEX, 후공정(HBM 본딩·테스트·하이브리드 본딩) 투자, 미국 대중 수출규제 상태, 삼성 파운드리 상황(테슬라·애플 수주 등).
4. 디스플레이: OLED IT 투자와 8.6세대 투자 집행 상태, 삼성디스플레이·LG디스플레이·BOE 투자, 애플 폴더블 아이폰, 마이크로LED, 마이크로디스플레이·XR(애플 비전프로·메타·삼성 XR·스마트글라스) 시장.
5. 자동차: 글로벌·미국·유럽·한국 판매, 미국 관세(한국산 자동차·부품 관세율과 한미 협상 결과·시행 상태), EV 전환 속도·보조금 변화, 하이브리드 수요, 중국 업체 경쟁, SDV 전환, 현대차그룹 미국 투자·실적, 관세 비용.
6. 바이오: 글로벌 바이오텍 자금조달·IPO 환경, 미국 생물보안법 상태, CDMO 수요·가격, 바이오시밀러 미국 시장(PBM·인터체인저블·가격 경쟁), 의약품 관세, 국내 코스닥 바이오 투자심리, 중국 의료 시장 상황.
7. 우주항공·위성통신·방산·5G/6G: 저궤도 위성(스타링크·원웹·카이퍼) 전개와 지상 단말·안테나 수요, 한국 위성 사업과 예산, 방산 수출, 5G 투자(미국·인도·유럽·일본 통신사 CAPEX), 6G 일정, 국방 예산 추세, 우주항공청.
8. ESS·에너지저장: 글로벌·미국 ESS 설치 전망, 미국 관세·FEOC·IRA 변경 사항, 한국 ESS 업체 수혜 구조, LFP 가격, 삼성SDI·LG에너지솔루션 ESS 수주, 데이터센터 전력·ESS 수요.
9. 특수소재·산업재: 우주항공·방산용 특수합금·티타늄·초내열합금 수요와 공급망.
10. 의료기기·진단: 글로벌 진단 시장, 재생의학·인체조직 시장, 중국 의료기기 규제.

[사이클 위치] 각 산업의 현재 사이클 위치(초기/중기/고점/하강)를 근거와 함께 평가하고, 1·3·5년 비관/기준/낙관 시나리오(확률 합 100%)를 산업별로 제시하세요. 모든 수치에 출처와 날짜를 붙이고 확인하지 못한 것은 N/A로 두세요.`

const stocks = (args && args.stocks) || []
const doMacro = !!(args && args.macro)

log(`종목 ${stocks.length}개 데이터 검증 시작` + (doMacro ? ' + 거시 2개' : ''))

const tasks = stocks.map((s) => () => agent(stockPrompt(s), { label: `data:${s.name}`, phase: '종목 데이터 검증', schema: STOCK_SCHEMA, effort: 'high' }))
if (doMacro) {
  tasks.push(() => agent(MACRO_A, { label: 'macro:금융시장', phase: '거시 시나리오', schema: MACRO_SCHEMA, effort: 'high' }))
  tasks.push(() => agent(MACRO_B, { label: 'macro:산업사이클', phase: '거시 시나리오', schema: MACRO_SCHEMA, effort: 'high' }))
}

const out = await parallel(tasks)
const stockResults = out.slice(0, stocks.length).map((r, i) => ({ input: stocks[i], result: r }))
const macro = doMacro ? { financial: out[stocks.length], industry: out[stocks.length + 1] } : null
const missing = stockResults.filter((r) => !r.result).map((r) => r.input.name)
if (missing.length) log(`결과 없음(에이전트 실패/스킵): ${missing.join(', ')}`)
return { stocks: stockResults, macro, missing }