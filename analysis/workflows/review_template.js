export const meta = {
  name: 'kr-review',
  description: 'Bear-case cross-examination (I), independent fact verification (V), sensitivity elasticities (S), base rates (H), price check (P)',
  phases: [
    { title: 'Cross-exam', detail: 'I: attack each preliminary top name' },
    { title: 'Verify', detail: 'V: independent check of key facts' },
    { title: 'Sensitivity', detail: 'S: elasticities for ranking stability' },
    { title: 'Base rates', detail: 'H: outside-view priors' },
    { title: 'Price check', detail: 'P: 2026-10-22 closes' },
  ],
}

const D = __DOSSIERS__
const CTX = __CONTEXT__

const common = (cap) => `
[Context]
- One role inside a multi-agent institutional research system ranking 26 Korean stocks by expected total shareholder return over 1y (to 2027-10-22), 3y (2029-10-22) and 5y (2031-10-22). Price basis: KRX official close of 2026-10-21. KRW. Analysis date 2026-10-22.
- ${CTX.macro}
- Built-in knowledge ends ~mid-2026; later facts must come from the dossier or search.
[Search budget - strict] WebSearch is limited to 200 calls per turn shared by ALL agents. Your personal hard cap: ${cap} WebSearch calls${cap === 0 ? ' (do NOT search)' : ''}. If a search returns "budget is used up", stop and finish. Load WebSearch via ToolSearch("select:WebSearch") if needed. Direct fetching of finance sites is blocked.
- Cite sources with dates; never invent numbers; write "확인 불가" when unverified. Narrative in Korean, concise.
`

const MULT = { type: 'object', properties: {
  base_mult: { type: 'number' }, bull_mult: { type: 'number' }, bear_mult: { type: 'number' },
  extra_tail_prob_pct: { type: 'number' }, extra_tail_price_frac: { type: 'number' } },
  required: ['base_mult', 'bull_mult', 'bear_mult', 'extra_tail_prob_pct', 'extra_tail_price_frac'] }

const I_SCHEMA = { type: 'object', properties: {
  code: { type: 'string' }, name: { type: 'string' },
  attacks: { type: 'array', items: { type: 'object', properties: {
    question: { type: 'string' }, finding: { type: 'string' }, severity: { type: 'string', enum: ['높음', '중간', '낮음'] } },
    required: ['question', 'finding', 'severity'] } },
  strongest_bear_argument: { type: 'string' },
  adjustments: { type: 'object', properties: { h1: MULT, h3: MULT, h5: MULT }, required: ['h1', 'h3', 'h5'] },
  adjustment_rationale: { type: 'string' },
  verdict: { type: 'string' } },
  required: ['code', 'name', 'attacks', 'strongest_bear_argument', 'adjustments', 'adjustment_rationale', 'verdict'] }

const V_SCHEMA = { type: 'object', properties: {
  code: { type: 'string' }, name: { type: 'string' },
  checks: { type: 'array', items: { type: 'object', properties: {
    claim: { type: 'string' }, status: { type: 'string', enum: ['확인', '불일치', '확인 불가'] }, correct_value: { type: 'string' }, source: { type: 'string' }, impact: { type: 'string' } },
    required: ['claim', 'status', 'correct_value', 'source', 'impact'] } },
  material_errors: { type: 'string' } },
  required: ['code', 'name', 'checks', 'material_errors'] }

const EL = { type: 'object', properties: { h1: { type: 'number' }, h3: { type: 'number' }, h5: { type: 'number' } }, required: ['h1', 'h3', 'h5'] }
const S_SCHEMA = { type: 'object', properties: {
  notes: { type: 'string' },
  stocks: { type: 'array', items: { type: 'object', properties: {
    code: { type: 'string' }, name: { type: 'string' },
    krw_strong_10pct: EL, rates_up_100bp: EL, exit_multiple_down_20pct: EL, memory_ai_capex_down: EL,
    auto_tariff_25pct: EL, bio_pos_down: EL, extra_dilution_5pct: EL, top_customer_loss: EL, rationale: { type: 'string' } },
    required: ['code', 'name', 'krw_strong_10pct', 'rates_up_100bp', 'exit_multiple_down_20pct', 'memory_ai_capex_down', 'auto_tariff_25pct', 'bio_pos_down', 'extra_dilution_5pct', 'top_customer_loss', 'rationale'] } } },
  required: ['notes', 'stocks'] }

const iPrompt = (d) => `${common(args.capI ?? 5)}
ROLE: Agent I - 반대심문·약세론 에이전트 for ${d.name} (${d.code}). This stock ranks near the top in the preliminary quantitative ranking. Attack the bullish case honestly; do not defend it, and do not be contrarian for its own sake. Preliminary quantitative result (after blending the specialist and generalist trees, before shrinkage): ${JSON.stringify(d.prelim)}
Dossier (fact sheet, specialist and independent generalist briefs, forensic brief):
${JSON.stringify(d.dossier)}
Answer each of these, with evidence: (1) Is the optimism already priced in? (2) Is the assumed growth above sector base rates? (3) Can margins and cash flow deteriorate even as revenue grows? (4) Customer in-sourcing, dual-sourcing or price-down pressure? (5) Technology substitution or a smaller-than-expected market? (6) Omitted financing or dilution? (7) Does low liquidity distort the expected return? (8) Excessive reliance on a single order, trial, customer or policy? (9) Is the success-scenario probability overstated? (10) Is the 5-year exit multiple too high for a mature company?
Then propose concrete adjustments to the blended scenario values per horizon: multipliers on the branch prices of each macro group (1.0 = no change; e.g., 0.9 cuts that group's prices by 10%) and an optional extra tail branch (probability in % taken pro-rata from all branches, price as a fraction of the 2026-10-21 close). Only propose changes your evidence supports; otherwise leave 1.0 and 0. Output strictly in the schema.`

const vPrompt = (d) => `${common(args.capV ?? 5)}
ROLE: Agent V - 독립 사실검증 에이전트 for ${d.name} (${d.code}). Independently verify the most decision-relevant factual claims in the dossier below (latest results, guidance, share count/dilution events, buybacks/dividends, major orders/contracts, regulatory or clinical events, index/price facts). Pick 5-8 claims that drive the valuation, search for primary or reputable sources, and mark each 확인 / 불일치 (give the correct value) / 확인 불가. Report any material error that would change the valuation.
Dossier: ${JSON.stringify(d.dossier)}
Output strictly in the schema.`

const tasks = []
for (const d of (args.cross || []).map(c => D[c]).filter(Boolean)) tasks.push(() => agent(iPrompt(d), { label: `I cross-exam ${d.name}`, phase: 'Cross-exam', schema: I_SCHEMA }))
for (const d of (args.verify || []).map(c => D[c]).filter(Boolean)) tasks.push(() => agent(vPrompt(d), { label: `V verify ${d.name}`, phase: 'Verify', schema: V_SCHEMA }))
if (args.sens) tasks.push(() => agent(`${common(0)}
ROLE: Agent S - 순위 민감도 에이전트. For each of the 26 stocks, estimate how the probability-weighted horizon-end value per share would change (in %, e.g., -8 means -8%) under each shock, for 1y, 3y and 5y: (a) KRW 10% stronger vs USD than the base path, (b) discount rates/risk-free +100bp, (c) exit/terminal multiples 20% lower, (d) memory prices and AI capex 20% below the base path, (e) US auto tariff on Korea raised to 25%, (f) clinical/regulatory/commercial success probabilities 20% lower (relative), (g) extra 5% equity dilution, (h) loss of a meaningful part of the top customer's business (if no concentration, small). Base each number on the company's actual exposures in the summaries below (FX exposure, duration/growth profile, cyclicality, customer concentration). Use 0 where there is no exposure.
Summaries: ${JSON.stringify(CTX.sens_summaries)}
Output strictly in the schema.`, { label: 'S sensitivity', phase: 'Sensitivity', schema: S_SCHEMA }))

const res = await parallel(tasks)
return res
