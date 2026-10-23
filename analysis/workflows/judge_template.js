export const meta = {
  name: 'kr-judge',
  description: 'Agent J final review: blend weights, adoption of cross-exam adjustments, final confidence for 26 Korean stocks',
  phases: [
    { title: 'Judge', detail: 'J: adopt or reject cross-exam and verification findings without double-counting' },
  ],
}

const S = __SUMMARIES__
const CTX = __CONTEXT__

const MULT = { type: 'object', properties: {
  base_mult: { type: 'number' }, bull_mult: { type: 'number' }, bear_mult: { type: 'number' },
  extra_tail_prob_pct: { type: 'number' }, extra_tail_price_frac: { type: 'number' } },
  required: ['base_mult', 'bull_mult', 'bear_mult', 'extra_tail_prob_pct', 'extra_tail_price_frac'] }

const J_SCHEMA = { type: 'object', properties: {
  global_notes: { type: 'string' },
  double_count_check: { type: 'string' },
  stocks: { type: 'array', items: { type: 'object', properties: {
    code: { type: 'string' }, name: { type: 'string' },
    w_spec: { type: 'number', description: 'weight on the industry specialist tree, 0.35-0.65 (generalist gets 1 - w_spec)' },
    w_spec_reason: { type: 'string' },
    adjustments: { type: 'object', properties: { h1: MULT, h3: MULT, h5: MULT }, required: ['h1', 'h3', 'h5'] },
    adjustment_reason: { type: 'string' },
    final_confidence: { type: 'string', enum: ['높음', '보통', '낮음'] },
    confidence_reason: { type: 'string' },
    key_monitoring: { type: 'array', items: { type: 'string' } },
    rank_caveat: { type: 'string' } },
    required: ['code', 'name', 'w_spec', 'w_spec_reason', 'adjustments', 'adjustment_reason', 'final_confidence', 'confidence_reason', 'key_monitoring', 'rank_caveat'] } } },
  required: ['global_notes', 'double_count_check', 'stocks'] }

const prompt = `
[Context]
- You are Agent J (최종심사) inside a multi-agent institutional research system ranking 26 Korean stocks by expected total shareholder return (TSR) over 1y (to 2027-10-22), 3y (2029-10-22) and 5y (2031-10-22). Price basis: KRX official close of 2026-10-21. KRW. Analysis date 2026-10-22.
- ${CTX.macro}
- ${CTX.price_basis}
- ${CTX.review_caveat}
- Do NOT use WebSearch or any web tool. Judge only from the material below. Write in Korean, concisely, as a report (하다체/명사형 is fine).

[How the numbers are produced after you]
${CTX.method}

[Your job]
For EVERY one of the 26 stocks below, decide:
1. w_spec: the weight on the industry specialist tree versus the independent generalist tree (0.35-0.65). Default is the value shown (from the two analysts' self-rated confidence). Move it only for a concrete reason: one analyst used materially better or more recent evidence, made a factual error that verification (V) or forensic (E) caught, or used the wrong price basis.
2. adjustments per horizon: multipliers on the branch prices of each macro group (base_mult for 기준, bull_mult for 낙관, bear_mult for 비관; 1.0 = no change) and an optional extra tail branch (extra_tail_prob_pct in %, taken pro-rata from all branches; extra_tail_price_frac = horizon-end value as a fraction of the 2026-10-21 close, dividends included).
   - Where a cross-examination (I) proposal exists, adopt it fully, partly, or not at all. Where none exists, keep 1.0 and 0 unless the verification (V), forensic (E) or risk (G) material shows a specific, evidenced error or omitted discrete event.
   - NO DOUBLE COUNTING. The quant step afterwards shrinks every stock's expected value ONCE toward an outside-view prior (CAPM + base-rate bucket alpha) with a weight that already falls with low confidence and with specialist-generalist disagreement. Therefore do NOT adopt generic "the case is too optimistic / multiple too high / growth above base rate" haircuts unless they rest on a specific fact the analysts missed or got wrong; generic optimism is what the shrinkage handles. Adopt evidence-based corrections: factual errors, omitted financing or dilution, omitted legal/regulatory/delisting events, a branch price inconsistent with stated facts, or a probability split inside a group that contradicts cited evidence. Adjustments can go UP as well as down (e.g., a downside driver that verification shows has been removed).
   - Add an extra tail only for a discrete event that the existing 비관 group does not already contain. Keep multipliers within 0.80-1.15 and extra_tail_prob_pct within 0-15.
3. final_confidence (높음/보통/낮음) for the stock's estimates, with the main reason (data quality, analyst disagreement, event dependence, verification results).
4. key_monitoring: 2-4 dated, checkable events or indicators that would change the view.
5. rank_caveat: one or two sentences on why the stock's rank could be wrong (e.g., depends on a 20% bull tail, analysts disagree by X%p, thin liquidity).
Also give global_notes (cross-stock consistency issues you noticed, e.g., analysts using different price bases, sector-wide assumptions that look inconsistent) and double_count_check (how you avoided penalising the same risk twice).

[Stock summaries]
Each summary has: market data, preliminary blended results before shrinkage and after (prelim), both analysts' expectations and group-level values, forensic flags, risk review (G), base-rate bucket (H), verification (V) and cross-examination (I) where they exist.
${JSON.stringify(S)}

Output strictly in the schema, one entry per stock, all 26 stocks.`

const res = await agent(prompt, { label: 'J final judge', phase: 'Judge', schema: J_SCHEMA })
return res
