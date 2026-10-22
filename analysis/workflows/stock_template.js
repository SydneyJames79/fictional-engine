export const meta = {
  name: 'kr-stock-analysis',
  description: 'Per stock: industry specialist + valuation (D/F), then independent generalist and forensic (E) under a shared search budget',
  phases: [
    { title: 'Specialist', detail: 'industry specialist + valuation, writes neutral fact sheet' },
    { title: 'Generalist', detail: 'independent outside-view analyst (fact sheet only)' },
    { title: 'Forensic', detail: 'accounting, governance and dilution forensics' },
  ],
}

const DATA = __DATA__
const MACRO = __MACRO__
const GUIDE = __GUIDE__

const common = (cap) => `
[Context]
- You are one role inside a multi-agent, institutional-grade research system analysing 26 Korean listed equities. Other roles work independently; the coordinator combines the outputs.
- Analysis date: 2026-10-22 (Thu) KST. Price basis for TSR: official KRX close of 2026-10-20 (coordinator-verified KRX dataset). Horizons end 2027-10-22 (1y), 2029-10-22 (3y), 2031-10-22 (5y). Currency KRW. TSR = price change + dividends + buyback/cancellation effects - dilution.
- Your built-in knowledge ends around mid-2026; anything later must come from search or from the facts given here. 2026 was an extreme boom-bust year: KOSPI closed at a record 9,114.55 on 2026-06-22 and at 5,552.74 on 2026-10-20 (-39%); KOSDAQ 781.97. KOSPI rebounded +3.29% on 10-21 (5,735.66) and fell about 3% intraday on 10-22.

[Search budget - strict]
- WebSearch is limited to 200 calls per turn shared by ALL agents of this run. Your personal hard cap is ${cap} WebSearch calls in total. Plan compact queries that return several facts at once (e.g., "<회사명> 3분기 실적 컨센서스 목표주가 2026"). Never exceed the cap. If a search returns "budget is used up", stop searching immediately and finish with what you have, marking unverified items "확인 불가".
- Load WebSearch via ToolSearch with query "select:WebSearch" if it is not loaded. Use mode "standard"; use "extended" at most once, only for the single most important very recent fact.
- Direct page fetching (WebFetch/curl) of finance.naver.com, KRX, DART, FnGuide, Yahoo etc. is blocked by network policy - do not try.
- Source priority: KRX/DART filings > company IR > regulators > counterparties' official announcements > reputable data vendors & broker reports > reputable press. Never use anonymous posts, promotional content, blogs or YouTube.
- Every key number needs a source and a date; for news distinguish article date vs event date. If unverified write "확인 불가". Never invent numbers or claim access to paid databases.
- Narrative fields in Korean, concise and factual.
`

const BRANCH = {
  type: 'object',
  properties: {
    macro: { type: 'string', enum: ['기준', '낙관', '비관'] },
    name: { type: 'string' },
    prob_pct: { type: 'number' },
    price_at_horizon: { type: 'number', description: 'expected market price per CURRENT share (KRW) at the horizon end in this branch' },
    cum_dividends: { type: 'number', description: 'cumulative cash dividends per current share received during the horizon (KRW)' },
    narrative: { type: 'string', description: 'Korean, max ~60 words: revenue/margin/EPS-or-BPS/multiple assumptions and stock-specific sub-assumption' },
  },
  required: ['macro', 'name', 'prob_pct', 'price_at_horizon', 'cum_dividends', 'narrative'],
}
const HORIZON = { type: 'array', minItems: 3, items: BRANCH }

const ANALYST_SCHEMA = {
  type: 'object',
  properties: {
    code: { type: 'string' }, name: { type: 'string' }, role: { type: 'string', enum: ['specialist', 'generalist'] },
    fact_sheet: { type: 'string', description: 'specialist: neutral sourced Korean fact sheet (max ~700 words); generalist: empty string' },
    business_and_moat: { type: 'string' },
    latest_results: { type: 'string' },
    consensus: { type: 'string' },
    forecasts: { type: 'string', description: 'own FY2026E-FY2028E revenue/OP/NI/FCF and normalized EPS or FCF per share, with units' },
    market_implied: { type: 'string', description: 'reverse valuation: what the 2026-10-20 price implies' },
    view_vs_market: { type: 'string' },
    valuation: { type: 'array', minItems: 2, items: { type: 'object', properties: {
      method: { type: 'string' }, fair_value_low: { type: 'number' }, fair_value_base: { type: 'number' }, fair_value_high: { type: 'number' },
      key_assumptions: { type: 'string' } }, required: ['method', 'fair_value_low', 'fair_value_base', 'fair_value_high', 'key_assumptions'] } },
    dps_last_fy: { type: 'number' }, dps_next_fy_expected: { type: 'number' }, payout_notes: { type: 'string' },
    net_share_change_assumed_pct: { type: 'object', properties: { h1: { type: 'number' }, h3: { type: 'number' }, h5: { type: 'number' }, notes: { type: 'string' } },
      required: ['h1', 'h3', 'h5', 'notes'] },
    scenarios: { type: 'object', properties: { h1: HORIZON, h3: HORIZON, h5: HORIZON }, required: ['h1', 'h3', 'h5'] },
    catalysts: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
    invalidation: { type: 'array', items: { type: 'string' } },
    kpis: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    confidence_reason: { type: 'string' },
    key_sources: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' }, date: { type: 'string' } }, required: ['claim', 'source', 'date'] } },
    data_gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['code', 'name', 'role', 'fact_sheet', 'business_and_moat', 'latest_results', 'consensus', 'forecasts', 'market_implied', 'view_vs_market',
    'valuation', 'dps_last_fy', 'dps_next_fy_expected', 'payout_notes', 'net_share_change_assumed_pct', 'scenarios', 'catalysts', 'risks',
    'invalidation', 'kpis', 'confidence', 'confidence_reason', 'key_sources', 'data_gaps'],
}

const FORENSIC_SCHEMA = {
  type: 'object',
  properties: {
    code: { type: 'string' }, name: { type: 'string' },
    earnings_quality: { type: 'string' }, one_offs: { type: 'string' }, capitalized_rnd: { type: 'string' }, related_party: { type: 'string' },
    audit: { type: 'string' }, contingencies: { type: 'string' }, concentration: { type: 'string' }, balance_sheet: { type: 'string' },
    dilutive_instruments: { type: 'array', items: { type: 'object', properties: {
      type: { type: 'string' }, issue_date: { type: 'string' }, amount: { type: 'string' }, conversion_price: { type: 'string' },
      potential_shares: { type: 'string' }, pct_of_current_shares: { type: 'number' }, status: { type: 'string' } },
      required: ['type', 'issue_date', 'amount', 'conversion_price', 'potential_shares', 'pct_of_current_shares', 'status'] } },
    share_count_changes_explained: { type: 'string' }, options_and_rsu: { type: 'string' },
    expected_net_share_change_pct: { type: 'object', properties: { h1: { type: 'number' }, h3: { type: 'number' }, h5: { type: 'number' }, basis: { type: 'string' } },
      required: ['h1', 'h3', 'h5', 'basis'] },
    shareholder_returns: { type: 'string' }, dividend_per_share_history: { type: 'string' }, treasury_shares: { type: 'string' },
    ownership_overhang: { type: 'string' }, governance: { type: 'string' },
    red_flags: { type: 'array', items: { type: 'object', properties: {
      issue: { type: 'string' }, severity: { type: 'string', enum: ['높음', '중간', '낮음'] }, evidence: { type: 'string' }, source: { type: 'string' } },
      required: ['issue', 'severity', 'evidence', 'source'] } },
    forensic_risk_score: { type: 'number' },
    tail_risk_notes: { type: 'string' }, recommended_adjustments: { type: 'string' },
    sources: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' }, date: { type: 'string' } }, required: ['claim', 'source', 'date'] } },
    data_gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['code', 'name', 'earnings_quality', 'one_offs', 'capitalized_rnd', 'related_party', 'audit', 'contingencies', 'concentration',
    'balance_sheet', 'dilutive_instruments', 'share_count_changes_explained', 'options_and_rsu', 'expected_net_share_change_pct',
    'shareholder_returns', 'dividend_per_share_history', 'treasury_shares', 'ownership_overhang', 'governance', 'red_flags',
    'forensic_risk_score', 'tail_risk_notes', 'recommended_adjustments', 'sources', 'data_gaps'],
}

const TASKS = `
[Tasks]
1. Business mix (segment revenue shares), key customers, competitive position and moat.
2. Latest results: FY2025, 1H/2Q 2026, and 3Q 2026 if released or pre-announced (revenue, operating profit, net profit, OCF/FCF, net cash/debt), guidance, orders/backlog, key KPIs, with sources and dates.
3. Consensus as reference only: FY2026E-FY2028E revenue/OP/EPS and average target price (date, source) or "확인 불가".
4. Own forecasts FY2026E-FY2028E (revenue, OP, NI, FCF) and a normalized (mid-cycle / steady-state) EPS or FCF per share.
5. Market-implied expectations: reverse valuation of the 2026-10-20 close (implied growth, margin, share or exit multiple) and whether it looks demanding.
6. Valuation with at least TWO methods suited to the business (DCF/FCFF, DDM, SOTP, normalized-earnings multiple, global & domestic peers, own historical range, reverse DCF, rNPV for biotech, scenario EV/Sales or gross-profit multiple for loss-making growth firms, backlog-conversion for order-driven firms): fair value per share low/base/high (KRW) with key assumptions.
7. Scenario tree per horizon (end dates 2027-10-22 / 2029-10-22 / 2031-10-22). Use the common macro scenarios with their FIXED probabilities 기준 50 / 낙관 20 / 비관 30. Inside each macro scenario add stock-specific sub-branches whenever stock-specific uncertainty is material (customer qualification, large order, clinical/regulatory result, technology selection, financing/dilution, competition) - typically two sub-branches (good/bad) per macro scenario for small and mid caps or event-driven names; a single branch per macro scenario only when stock-specific uncertainty is minor. prob_pct is the UNCONDITIONAL probability; branches tagged 기준 must sum to exactly 50, 낙관 to 20, 비관 to 30 in every horizon. For each branch give the expected market price per current share at the horizon end, the cumulative dividends per current share received during the horizon, and a short narrative.
8. Dated catalysts for the next 12 months, key risks, concrete measurable thesis-invalidation conditions, KPIs to check in the next results/disclosures.
9. View vs market: where and why your view differs from consensus and from what the price implies.
10. Confidence (높음/보통/낮음) with reason, key sources, data gaps.

[Scenario rules]
- price_at_horizon is the expected MARKET PRICE per CURRENT share at the horizon end (not today's intrinsic value). Reflect expected dilution (CB/BW/EB conversion, rights issues, options) and buyback cancellation per current share; report the net share-count change you assumed.
- Cyclicals (memory, semiconductor equipment, autos, materials): never capitalise peak 2026-27 earnings at historical average multiples; anchor 3y/5y on normalized mid-cycle earnings and cycle-consistent multiples; the June-2026 peak price/multiple is not a base-case target.
- 5-year: no perpetual hyper-growth; assume competition, margin mean reversion and mature-company multiples by 2031 unless a durable moat is evidenced.
- Biotech, diagnostics and regenerative medicine: probability-of-success-weighted values, cash burn, financing and dilution; never TAM x share without probabilities.
- Recent listings or short histories: lean on comparables and base rates; lower confidence.
- Beta consistency: high-beta names must fall more than the index in 비관 and rise more in 낙관 unless backed by firm backlog, net cash or defensiveness; state the reason if not.
- Bear branches must be genuinely adverse but plausible and may include permanent impairment, forced dilution or delisting where relevant; bull branches genuinely favourable but plausible. Do not force symmetry.
- Do not double count a risk in both a branch probability and its value. Values are nominal KRW prices; the coordinator computes TSR, adds volatility and blends independent analysts - do not apply extra risk discounts yourself.
- Broker target prices are reference only; your valuation must stand on its own assumptions.
- Keep every narrative field short; the whole answer should stay compact.
`

const CAPS = (typeof args !== 'undefined' && args && args.caps) ? args.caps : { spec: 12, gen: 4, foren: 5 }

const specialistPrompt = (d) => `${common(CAPS.spec)}
${MACRO}

[Sector guidance for ${d.sector}]
${GUIDE[d.sector]}

[Coordinator KRX data pack]
${d.pack}

[Agent B identity/status notes]
${d.bnote}

ROLE: Agent D - industry specialist (${d.sector}) who also performs the Agent F valuation for ${d.name} (KRX ${d.code}). Apply deep industry knowledge: product and technology roadmaps, customer capex and qualification status, pricing power, domestic and global competition, supply chain, and how this company's earnings respond to the sector cycle. An independent generalist and a forensic accountant will analyse the same stock separately using ONLY the neutral fact sheet you write (not your valuation, scenarios or opinions), so make "fact_sheet" complete, neutral and sourced: business mix, latest results (FY2025, 1H/2Q26, 3Q26 if out), guidance, consensus, orders/backlog, customers, balance sheet, share-count changes and dilution facts, dividends and buybacks, upcoming dated events. No opinions, valuations or scenarios in the fact sheet. Set role="specialist".
${TASKS}`

const generalistPrompt = (d, factSheet) => `${common(CAPS.gen)}
${MACRO}

[Sector guidance for ${d.sector}]
${GUIDE[d.sector]}

[Coordinator KRX data pack]
${d.pack}

[Agent B identity/status notes]
${d.bnote}

[Neutral fact sheet written by another agent - facts only. Use your few searches to verify or fill the most decision-relevant gaps.]
${factSheet}

ROLE: Independent generalist analyst (not attached to any industry desk) who also performs the Agent F valuation for ${d.name} (KRX ${d.code}). Your edge is the outside view and valuation discipline: base rates for growth persistence and post-boom behaviour, what the current price already implies, cross-industry comparables and what a mature version of this business is worth, balance-sheet and dilution realism. Be skeptical of industry narratives but not contrarian for its own sake - if the evidence supports a strong view, say so. An industry specialist is analysing the same stock separately; you will not see their valuation or scenarios and must not try to guess them. Set role="generalist" and fact_sheet="".
${TASKS}`

const forensicPrompt = (d, factSheet) => `${common(CAPS.foren)}
[Coordinator KRX data pack]
${d.pack}

[Agent B identity/status notes]
${d.bnote}

[Neutral fact sheet written by another agent - facts only]
${factSheet}
${d.draft ? `
[UNVERIFIED draft from an earlier forensic agent that could NOT search (built-in knowledge only, mid-2026 cutoff). Treat every claim as unverified; use it only to decide what to check; drop anything you cannot confirm.]
${d.draft}
` : ''}
ROLE: Agent E - 회계·지배구조·포렌식 에이전트 for ${d.name} (KRX ${d.code}). Investigate and report with evidence (figure, period, source, date):
1. Earnings quality: OCF vs net income (FY2023-FY2025 and latest 2026 interim), accruals, one-off gains/losses, capitalised development costs, receivable/inventory build.
2. Related-party and intra-group transactions; FY2025 audit opinion, key audit matters, emphasis-of-matter or going-concern language, auditor changes or restatements; contingent liabilities, lawsuits, guarantees, sanctions.
3. Customer and supplier concentration.
4. Net cash/debt at the latest date, debt maturities, interest coverage, cash runway if loss-making.
5. Dilution: every outstanding CB/BW/EB/RCPS/convertible preferred and stock options/RSUs (issue date, amount, conversion price and refixing floor, potential shares, % of current shares, status, put/maturity dates); rights offerings or third-party allotments in 2025-2026 or planned. Explain each share-count change listed in the data pack.
6. Shareholder returns: DPS history, payout policy, buybacks, treasury shares and cancellation likelihood (incl. any mandatory cancellation under the 2026 commercial act revision), value-up plans.
7. Ownership: largest shareholder and related parties %, insider/major-holder sales, lock-up expiries, financial-investor overhang, block-deal risk.
8. Governance: holding discount, group structure, controlling-shareholder vs minority conflicts, capital-allocation record.
9. Expected NET share-count change by horizon (1y, 3y, 5y; + = dilution, - = net cancellation).
10. Tail-risk notes (delisting criteria, going concern, forced dilution, fraud allegations), red flags with severity, and concrete recommended adjustments (Korean) for the valuation team.
Output strictly in the schema.`

const items = (args.codes || []).map(c => DATA[c]).filter(Boolean)
log(`stocks: ${items.map(d => d.name).join(', ')}`)

const results = await pipeline(items,
  (d) => agent(specialistPrompt(d), { label: `D specialist ${d.name}`, phase: 'Specialist', schema: ANALYST_SCHEMA }),
  (spec, d) => {
    const fs = (spec && spec.fact_sheet) ? spec.fact_sheet : '확인 불가(전문가 팩트시트 없음)'
    return parallel([
      () => agent(generalistPrompt(d, fs), { label: `G generalist ${d.name}`, phase: 'Generalist', schema: ANALYST_SCHEMA }),
      () => d.forensic_redo ? agent(forensicPrompt(d, fs), { label: `E forensic ${d.name}`, phase: 'Forensic', schema: FORENSIC_SCHEMA }) : Promise.resolve(null),
    ]).then(([gen, foren]) => ({ code: d.code, name: d.name, spec, gen, foren }))
  })

return results
