export const meta = {
  name: 'kr-calibration',
  description: 'Agent H base rates & priors, Agent G forward-risk review, KRX close update for 2026-10-22',
  phases: [
    { title: 'Base rates', detail: 'H: outside-view priors by bucket' },
    { title: 'Risk review', detail: 'G: forward volatility and tail-risk review (no web search)' },
    { title: 'Price update', detail: 'B2: 2026-10-22 official closes' },
  ],
}

const UNIVERSE = [{"code": "000660", "name": "SK하이닉스", "market": "KOSPI", "mcap": "893,392", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "1,223,000"}, {"code": "005930", "name": "삼성전자", "market": "KOSPI", "mcap": "1,236,488", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "211,500"}, {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI", "mcap": "64,391", "sector": "바이오의약품·의료기기·진단", "close": "1,391,000"}, {"code": "0126Z0", "name": "삼성에피스홀딩스", "market": "KOSPI", "mcap": "8,187", "sector": "바이오의약품·의료기기·진단", "close": "329,000"}, {"code": "005380", "name": "현대차", "market": "KOSPI", "mcap": "63,075", "sector": "자동차·전장·SDV·부품", "close": "310,000"}, {"code": "012330", "name": "현대모비스", "market": "KOSPI", "mcap": "31,258", "sector": "자동차·전장·SDV·부품", "close": "348,000"}, {"code": "307950", "name": "현대오토에버", "market": "KOSPI", "mcap": "9,228", "sector": "자동차·전장·SDV·부품", "close": "336,500"}, {"code": "295310", "name": "에이치브이엠", "market": "KOSDAQ", "mcap": "810", "sector": "ESS·산업재·특수소재", "close": "64,100"}, {"code": "452430", "name": "사피엔반도체", "market": "KOSDAQ", "mcap": "227", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "27,550"}, {"code": "418420", "name": "라온텍", "market": "KOSDAQ", "mcap": "97", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "3,160"}, {"code": "370090", "name": "퓨런티어", "market": "KOSDAQ", "mcap": "48", "sector": "자동차·전장·SDV·부품", "close": "5,640"}, {"code": "010690", "name": "화신", "market": "KOSPI", "mcap": "246", "sector": "자동차·전장·SDV·부품", "close": "7,040"}, {"code": "290650", "name": "엘앤씨바이오", "market": "KOSDAQ", "mcap": "1,707", "sector": "바이오의약품·의료기기·진단", "close": "63,300"}, {"code": "314930", "name": "바이오다인", "market": "KOSDAQ", "mcap": "183", "sector": "바이오의약품·의료기기·진단", "close": "6,140"}, {"code": "171090", "name": "선익시스템", "market": "KOSDAQ", "mcap": "795", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "78,500"}, {"code": "178320", "name": "서진시스템", "market": "KOSDAQ", "mcap": "2,431", "sector": "ESS·산업재·특수소재", "close": "38,150"}, {"code": "007660", "name": "이수페타시스", "market": "KOSPI", "mcap": "7,040", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "95,900"}, {"code": "107640", "name": "한중엔시에스", "market": "KOSDAQ", "mcap": "443", "sector": "ESS·산업재·특수소재", "close": "48,850"}, {"code": "218410", "name": "RFHIC", "market": "KOSDAQ", "mcap": "1,261", "sector": "우주항공·위성통신·5G·6G", "close": "47,450"}, {"code": "189300", "name": "인텔리안테크", "market": "KOSDAQ", "mcap": "614", "sector": "우주항공·위성통신·5G·6G", "close": "57,200"}, {"code": "099320", "name": "쎄트렉아이", "market": "KOSDAQ", "mcap": "611", "sector": "우주항공·위성통신·5G·6G", "close": "55,800"}, {"code": "403870", "name": "HPSP", "market": "KOSDAQ GLOBAL", "mcap": "4,140", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "50,300"}, {"code": "032500", "name": "케이엠더블유", "market": "KOSDAQ", "mcap": "776", "sector": "우주항공·위성통신·5G·6G", "close": "18,400"}, {"code": "098460", "name": "고영", "market": "KOSDAQ", "mcap": "2,067", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "30,300"}, {"code": "232140", "name": "와이씨", "market": "KOSDAQ", "mcap": "1,094", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "13,330"}, {"code": "042700", "name": "한미반도체", "market": "KOSPI", "mcap": "19,053", "sector": "반도체·AI하드웨어·디스플레이장비", "close": "199,900"}]
const RISK = "000660 SK하이닉스: vol 1y 91%, 3y 66%, full 52%, 2020-24 39%, beta1y 1.52, beta3y 1.56, MDD since 2020 -58%, ADV60 6,866.9bn KRW, days |ret|>10% (1y) 9.2%, first trading date 2020-01-02 -> default sigma_1y 62%, sigma_LR 47%\n005930 삼성전자: vol 1y 76%, 3y 50%, full 39%, 2020-24 27%, beta1y 1.30, beta3y 1.27, MDD since 2020 -45%, ADV60 5,602.3bn KRW, days |ret|>10% (1y) 4.4%, first trading date 2020-01-02 -> default sigma_1y 50%, sigma_LR 36%\n207940 삼성바이오로직스: vol 1y 43%, 3y 34%, full 34%, 2020-24 33%, beta1y 0.25, beta3y 0.31, MDD since 2020 -39%, ADV60 86.2bn KRW, days |ret|>10% (1y) 0.4%, first trading date 2020-01-02 -> default sigma_1y 41%, sigma_LR 37%\n0126Z0 삼성에피스홀딩스: vol 1y 85%, 3y 85%, full 85%, 2020-24 nan%, beta1y 0.59, beta3y 0.59, MDD since 2020 -59%, ADV60 20.7bn KRW, days |ret|>10% (1y) 5.5%, first trading date 2025-11-24 -> default sigma_1y 84%, sigma_LR 84%\n005380 현대차: vol 1y 69%, 3y 48%, full 42%, 2020-24 36%, beta1y 0.80, beta3y 0.84, MDD since 2020 -61%, ADV60 229.7bn KRW, days |ret|>10% (1y) 4.4%, first trading date 2020-01-02 -> default sigma_1y 56%, sigma_LR 45%\n012330 현대모비스: vol 1y 70%, 3y 48%, full 42%, 2020-24 35%, beta1y 0.70, beta3y 0.71, MDD since 2020 -56%, ADV60 133.5bn KRW, days |ret|>10% (1y) 3.6%, first trading date 2020-01-02 -> default sigma_1y 58%, sigma_LR 46%\n307950 현대오토에버: vol 1y 104%, 3y 70%, full 60%, 2020-24 49%, beta1y 0.94, beta3y 0.96, MDD since 2020 -67%, ADV60 30.1bn KRW, days |ret|>10% (1y) 9.2%, first trading date 2020-01-02 -> default sigma_1y 84%, sigma_LR 66%\n295310 에이치브이엠: vol 1y 119%, 3y 104%, full 104%, 2020-24 110%, beta1y 0.82, beta3y 0.75, MDD since 2020 -77%, ADV60 8.6bn KRW, days |ret|>10% (1y) 16.0%, first trading date 2024-06-28 -> default sigma_1y 110%, sigma_LR 108%\n452430 사피엔반도체: vol 1y 90%, 3y 85%, full 85%, 2020-24 93%, beta1y 0.89, beta3y 1.01, MDD since 2020 -81%, ADV60 1.4bn KRW, days |ret|>10% (1y) 6.4%, first trading date 2024-02-19 -> default sigma_1y 85%, sigma_LR 86%\n418420 라온텍: vol 1y 92%, 3y 75%, full 81%, 2020-24 76%, beta1y 0.94, beta3y 0.99, MDD since 2020 -83%, ADV60 0.7bn KRW, days |ret|>10% (1y) 7.6%, first trading date 2023-03-09 -> default sigma_1y 80%, sigma_LR 75%\n370090 퓨런티어: vol 1y 68%, 3y 64%, full 68%, 2020-24 72%, beta1y 0.63, beta3y 0.78, MDD since 2020 -87%, ADV60 0.2bn KRW, days |ret|>10% (1y) 3.2%, first trading date 2022-02-23 -> default sigma_1y 65%, sigma_LR 66%\n010690 화신: vol 1y 83%, 3y 63%, full 62%, 2020-24 59%, beta1y 0.62, beta3y 0.79, MDD since 2020 -71%, ADV60 2.7bn KRW, days |ret|>10% (1y) 6.4%, first trading date 2020-01-02 -> default sigma_1y 72%, sigma_LR 64%\n290650 엘앤씨바이오: vol 1y 89%, 3y 70%, full 63%, 2020-24 53%, beta1y 0.40, beta3y 0.50, MDD since 2020 -71%, ADV60 16.0bn KRW, days |ret|>10% (1y) 6.4%, first trading date 2020-01-02 -> default sigma_1y 80%, sigma_LR 67%\n314930 바이오다인: vol 1y 53%, 3y 63%, full 61%, 2020-24 65%, beta1y 0.45, beta3y 0.59, MDD since 2020 -78%, ADV60 0.2bn KRW, days |ret|>10% (1y) 1.2%, first trading date 2021-03-17 -> default sigma_1y 59%, sigma_LR 61%\n171090 선익시스템: vol 1y 88%, 3y 76%, full 76%, 2020-24 76%, beta1y 0.70, beta3y 0.86, MDD since 2020 -62%, ADV60 4.2bn KRW, days |ret|>10% (1y) 4.8%, first trading date 2020-01-02 -> default sigma_1y 81%, sigma_LR 77%\n178320 서진시스템: vol 1y 92%, 3y 68%, full 57%, 2020-24 49%, beta1y 0.93, beta3y 0.95, MDD since 2020 -65%, ADV60 40.5bn KRW, days |ret|>10% (1y) 8.8%, first trading date 2020-01-02 -> default sigma_1y 77%, sigma_LR 62%\n007660 이수페타시스: vol 1y 94%, 3y 84%, full 74%, 2020-24 69%, beta1y 1.07, beta3y 1.23, MDD since 2020 -64%, ADV60 77.2bn KRW, days |ret|>10% (1y) 7.6%, first trading date 2020-01-02 -> default sigma_1y 83%, sigma_LR 75%\n107640 한중엔시에스: vol 1y 94%, 3y 80%, full 72%, 2020-24 68%, beta1y 0.82, beta3y 0.83, MDD since 2020 -66%, ADV60 4.7bn KRW, days |ret|>10% (1y) 7.2%, first trading date 2020-01-02 -> default sigma_1y 85%, sigma_LR 76%\n218410 RFHIC: vol 1y 99%, 3y 70%, full 57%, 2020-24 45%, beta1y 1.03, beta3y 1.03, MDD since 2020 -78%, ADV60 22.5bn KRW, days |ret|>10% (1y) 10.4%, first trading date 2020-01-02 -> default sigma_1y 80%, sigma_LR 62%\n189300 인텔리안테크: vol 1y 92%, 3y 67%, full 61%, 2020-24 55%, beta1y 0.90, beta3y 0.95, MDD since 2020 -71%, ADV60 4.7bn KRW, days |ret|>10% (1y) 7.6%, first trading date 2020-01-02 -> default sigma_1y 76%, sigma_LR 64%\n099320 쎄트렉아이: vol 1y 97%, 3y 71%, full 62%, 2020-24 54%, beta1y 0.90, beta3y 0.91, MDD since 2020 -75%, ADV60 4.0bn KRW, days |ret|>10% (1y) 9.6%, first trading date 2020-01-02 -> default sigma_1y 81%, sigma_LR 67%\n403870 HPSP: vol 1y 97%, 3y 75%, full 73%, 2020-24 67%, beta1y 1.10, beta3y 1.19, MDD since 2020 -66%, ADV60 120.6bn KRW, days |ret|>10% (1y) 8.8%, first trading date 2022-07-15 -> default sigma_1y 80%, sigma_LR 71%\n032500 케이엠더블유: vol 1y 97%, 3y 77%, full 61%, 2020-24 51%, beta1y 0.93, beta3y 0.96, MDD since 2020 -92%, ADV60 4.0bn KRW, days |ret|>10% (1y) 10.4%, first trading date 2020-01-02 -> default sigma_1y 84%, sigma_LR 68%\n098460 고영: vol 1y 98%, 3y 75%, full 62%, 2020-24 51%, beta1y 1.00, beta3y 1.02, MDD since 2020 -74%, ADV60 38.9bn KRW, days |ret|>10% (1y) 9.6%, first trading date 2020-01-02 -> default sigma_1y 82%, sigma_LR 66%\n232140 와이씨: vol 1y 87%, 3y 84%, full 67%, 2020-24 64%, beta1y 1.04, beta3y 1.18, MDD since 2020 -70%, ADV60 25.8bn KRW, days |ret|>10% (1y) 8.0%, first trading date 2020-01-02 -> default sigma_1y 79%, sigma_LR 71%\n042700 한미반도체: vol 1y 103%, 3y 81%, full 69%, 2020-24 60%, beta1y 1.29, beta3y 1.35, MDD since 2020 -69%, ADV60 154.8bn KRW, days |ret|>10% (1y) 9.2%, first trading date 2020-01-02 -> default sigma_1y 83%, sigma_LR 70%"

const COMMON = (cap) => `
[Context]
- One role inside a multi-agent institutional research system analysing 26 Korean listed equities (list below). Analysis date 2026-10-22 KST; price basis 2026-10-20 KRX close; horizons end 2027-10-22, 2029-10-22, 2031-10-22; KRW.
- Built-in knowledge ends ~mid-2026. 2026 was an extreme boom-bust year (KOSPI record close 9,114.55 on 2026-06-22, 5,552.74 on 2026-10-20; KOSDAQ 781.97).
- Common macro scenarios (Agent C): 기준 50% / 낙관 20% / 비관 30%. Probability-weighted index TSR: KOSPI 1y 8.5%, 3y 7.7%/yr, 5y 8.9%/yr; KOSDAQ 6.0% / 5.7% / 7.0%. KTB yields 1y 3.688%, 3y 3.822%, 5y 3.965% (2026-10-21).
[Search budget - strict] WebSearch is limited to 200 calls per turn shared by ALL agents. Your personal hard cap: ${cap} WebSearch calls${cap === 0 ? ' (do NOT search at all)' : ''}. If a search returns "budget is used up", stop searching and finish. Load WebSearch via ToolSearch("select:WebSearch") if needed. Direct fetching of finance sites is blocked.
- Cite sources with dates; mark anything from memory as "(사전지식, 미검증)". Never invent numbers. Narrative in Korean.
`

const H_SCHEMA = {
  type: 'object',
  properties: {
    base_rates: { type: 'array', items: { type: 'object', properties: {
      topic: { type: 'string' }, finding: { type: 'string' }, numbers: { type: 'string' }, source: { type: 'string' }, applicability: { type: 'string' } },
      required: ['topic', 'finding', 'numbers', 'source', 'applicability'] } },
    priors: { type: 'array', items: { type: 'object', properties: {
      bucket: { type: 'string' }, members: { type: 'array', items: { type: 'string' } },
      alpha_vs_capm_prior_pct: { type: 'number', description: 'annual expected return adjustment vs a zero-alpha CAPM prior consistent with the macro index expectations (e.g., -2 for post-IPO small caps)' },
      prob_perm_loss_gt50_5y_pct: { type: 'number' }, rationale: { type: 'string' } },
      required: ['bucket', 'members', 'alpha_vs_capm_prior_pct', 'prob_perm_loss_gt50_5y_pct', 'rationale'] } },
    growth_persistence: { type: 'string' },
    post_bubble_evidence: { type: 'string' },
    calibration_rules: { type: 'array', items: { type: 'string' } },
    cautions: { type: 'array', items: { type: 'string' } },
  },
  required: ['base_rates', 'priors', 'growth_persistence', 'post_bubble_evidence', 'calibration_rules', 'cautions'],
}

const G_SCHEMA = {
  type: 'object',
  properties: {
    method_review: { type: 'string' },
    stocks: { type: 'array', items: { type: 'object', properties: {
      code: { type: 'string' }, name: { type: 'string' },
      sigma_1y_pct: { type: 'number' }, sigma_lr_pct: { type: 'number' },
      changed: { type: 'boolean' }, reason: { type: 'string' },
      liquidity_risk: { type: 'string', enum: ['높음', '중간', '낮음'] }, gap_risk: { type: 'string', enum: ['높음', '중간', '낮음'] },
      cyclicality: { type: 'string', enum: ['높음', '중간', '낮음'] }, leverage_risk: { type: 'string', enum: ['높음', '중간', '낮음'] },
      discrete_event_risk: { type: 'string' }, perm_loss_risk_score: { type: 'number', description: '1 (low) to 5 (high) risk of permanent capital loss / delisting over 5y' } },
      required: ['code', 'name', 'sigma_1y_pct', 'sigma_lr_pct', 'changed', 'reason', 'liquidity_risk', 'gap_risk', 'cyclicality', 'leverage_risk', 'discrete_event_risk', 'perm_loss_risk_score'] } },
  },
  required: ['method_review', 'stocks'],
}

const P_SCHEMA = {
  type: 'object',
  properties: {
    kospi_close_1022: { type: 'string' }, kosdaq_close_1022: { type: 'string' },
    stocks: { type: 'array', items: { type: 'object', properties: {
      code: { type: 'string' }, name: { type: 'string' },
      close_1021: { type: 'number', description: '0 if not found' }, close_1022: { type: 'number', description: '0 if not found' },
      source_1022: { type: 'string' }, confidence: { type: 'string', enum: ['높음', '보통', '낮음', '없음'] } },
      required: ['code', 'name', 'close_1021', 'close_1022', 'source_1022', 'confidence'] } },
  },
  required: ['kospi_close_1022', 'kosdaq_close_1022', 'stocks'],
}

const uni = UNIVERSE.map(u => `${u.code} ${u.name} (${u.market}, 시총 ${u.mcap}십억원, ${u.sector}, 2026-10-20 종가 ${u.close}원)`).join('\n')

const tasks = []
if (args.run.includes('H')) tasks.push(() => agent(`${COMMON(args.capH || 12)}
Universe:
${uni}

ROLE: Agent H - 베이스레이트·예측 보정 에이전트. Provide outside-view base rates and priors so the coordinator can shrink extreme stock-level forecasts once. Avoid cherry-picking: report full distributions and contrary evidence. Prefer classic, well-documented sources (Mauboussin/Callahan "Base Rate Book", Credit Suisse Global Investment Returns Yearbook, Ritter IPO studies, BIO/Informa/Citeline clinical success studies, KRX/KCMI/자본시장연구원 studies, academic papers on long-horizon mean reversion and post-bubble returns). Use searches mainly to confirm 2-4 key numbers; the rest may come from memory but must be labelled "(사전지식, 미검증)".
Cover: (1) KOSPI/KOSDAQ long-run return distributions and loss frequencies over 1/3/5 years; (2) returns 1/3/5 years after an equity mania peak and a 40-60% drawdown (Nasdaq 2000, KOSDAQ 2000, Japan 1990, Taiwan 1990, Korea 2007-08, KOSDAQ bio 2018 & 2021, Korean battery stocks 2023-24) - both rebounds and stagnation; (3) memory semis after cycle earnings peaks (peak-to-trough, recovery time, trough/peak P/B); (4) growth persistence (probability of sustaining 15/20/30% revenue CAGR for 3 and 5 years by size); (5) Korean small caps and tech-special IPOs (기술특례상장) long-run returns, delisting/관리종목 rates, CB-related dilution; (6) clinical/regulatory success probabilities, biosimilar and device approval base rates, CDMO growth/margins; (7) auto OEM and parts valuation ranges and cyclicality; (8) space/telecom-equipment small caps after hype cycles; (9) mature multiples by sector.
Then assign every one of the 26 stocks to exactly one of 6-10 buckets and give each bucket an annual expected-return adjustment versus a zero-alpha CAPM prior that is already consistent with the macro index expectations (alpha_vs_capm_prior_pct; usually between -4 and +2), plus the probability of a >50% permanent loss over 5 years. Add calibration rules and cautions.`, { label: 'H base rates', phase: 'Base rates', schema: H_SCHEMA }))

if (args.run.includes('G')) tasks.push(() => agent(`${COMMON(0)}
Universe:
${uni}

Coordinator risk data (KRX daily data 2020-01-02..2026-10-20; KOSPI cap-weighted proxy vol: 1y 55%, 3y 35.5%, 2020-24 20.0%; KOSDAQ proxy 1y 48.9%, 3y 34.3%) and the coordinator's default forward-vol model output:
${RISK}

Default model: market vol 37% for the first year (probability-weighted RMS of the macro scenario vols: base 30-35%, bull ~28%, bear 45%+), 26% long-run; beta = average of 1y/3y beta shrunk 1/3 toward 1; idiosyncratic vol from each window's total minus market part; first-year idio = mean of 1y and 3y idio, long-run idio = 20% 1y + 40% 3y + 40% 2020-24 (or full sample). Total horizon dispersion = sqrt(s1^2 + (T-1) sLR^2) x (1, 0.88, 0.80) for T = 1, 3, 5. Within-scenario noise is calibrated so the scenario mixture matches that total, with a 10%/yr floor.

ROLE: Agent G - 정량·위험 에이전트. Review this default and, stock by stock, give your forward sigma_1y and sigma_LR (annualised %). Do not extrapolate past volatility mechanically: adjust for business-structure changes, the 2026 mania regime fading, very short histories (e.g., re-listings, recent IPOs whose realized vol includes post-listing price discovery), illiquidity and gap risk, leverage, scheduled discrete events. Do not invent option implied vols (none are available). Mark changed=true only where you deviate from the default by more than ~3 points, with a reason. Also rate liquidity, gap, cyclicality, leverage risk, discrete-event risk and permanent-loss risk (1-5). Do not search.`, { label: 'G risk review', phase: 'Risk review', schema: G_SCHEMA }))

if (args.run.includes('P')) tasks.push(() => agent(`${COMMON(args.capP || 30)}
Universe:
${uni}

ROLE: Agent B2 - price verification. Find the official KRX closing prices of 2026-10-22 (today) and 2026-10-21 for all 26 stocks, plus KOSPI and KOSDAQ closes on 2026-10-22. Efficient strategy: market-close wrap-up articles (마감시황) that list many stocks; '특징주' articles; automatic quote articles (e.g., 톱스타뉴스·한경·이데일리 자동시세 기사) that state a close with date. Cross-check each figure with the reported change vs the previous close (2026-10-20 closes are given above). Only report a close if the article explicitly dates it; otherwise use 0 and confidence "없음". Never guess.`, { label: 'B2 price update', phase: 'Price update', schema: P_SCHEMA }))

const res = await parallel(tasks)
return res
