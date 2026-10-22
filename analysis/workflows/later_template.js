export const meta = {
  name: 'kr-calibration',
  description: 'Agent H base rates & priors, Agent G forward-risk review, KRX close update for 2026-10-22',
  phases: [
    { title: 'Base rates', detail: 'H: outside-view priors by bucket' },
    { title: 'Risk review', detail: 'G: forward volatility and tail-risk review (no web search)' },
    { title: 'Price update', detail: 'B2: 2026-10-22 official closes' },
  ],
}

const UNIVERSE = __UNIVERSE__
const RISK = __RISK__

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
