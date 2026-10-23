export const meta = {
  name: 'kr-qa',
  description: 'Agent Q independent verification: reconcile the final report against output files and check quality rules',
  phases: [
    { title: 'Verify', detail: 'Q: numbers, internal consistency, compliance' },
  ],
}

const Q_SCHEMA = { type: 'object', properties: {
  summary: { type: 'string' },
  checks: { type: 'array', items: { type: 'object', properties: {
    item: { type: 'string' }, status: { type: 'string', enum: ['통과', '부분', '미흡'] }, evidence: { type: 'string' } },
    required: ['item', 'status', 'evidence'] } },
  issues: { type: 'array', items: { type: 'object', properties: {
    severity: { type: 'string', enum: ['높음', '중간', '낮음'] }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } },
    required: ['severity', 'where', 'problem', 'fix'] } } },
  required: ['summary', 'checks', 'issues'] }

const prompt = `
You are Agent Q (독립 검증) in a multi-agent research system that ranked 26 Korean stocks by expected total shareholder return over 1y/3y/5y. You did not take part in the analysis. Your job is to verify the final report independently. Do NOT use WebSearch or any web tool. Use only local files (Read, Bash with python3/pandas are fine). Write findings in Korean (report style).

Files (all under /home/user/fictional-engine/analysis):
- report/report.html: the final report (HTML). Parts 1-9, 품질 체크리스트, 부록.
- output/final_ranks.csv: one row per stock and horizon (h1/h3/h5) with all metrics and ranks (exp_cum, exp_ann, median_cum, p10, p90, p_loss, p_loss30, p_loss50, cvar10, sortino, downdev_ann, excess_vs_index_ann, rank_er, rank_ra, rank_bal, rank_agg, rank_def, score_*, shrink_w, prior_ann, e_spec_ann, e_gen_ann, w_spec ...).
- output/final_branches.csv: every scenario branch after blending, adjustments and shrinkage (code, h, macro, branch, prob, price, div, tsr).
- output/final_settings.json: weights, priors, sigmas, adjustments adopted by the final judge, dilution fixes, tree-fix log.
- output/rank_stability.csv and output/sens_runs.csv: sensitivity and rank-stability results.
- data/aux/J_final_judge.json: the final judge's decisions. data/aux/I_*.json, V_*.json: cross-examination and verification.
- data/risk_metrics_full_1021.csv: market data (close = 2026-10-21 base price).
- pipeline.py, quant_engine.py, run_quant.py, sensitivity.py: the code.

Check at least the following and report each as a check with status 통과/부분/미흡 and concrete evidence (numbers, row names):
1. Probabilities: for every stock and horizon in final_branches.csv, branch probabilities sum to 1 and the macro groups sum to 0.50/0.20/0.30 (allow a cross-exam tail branch tagged 비관 if present; then groups are pro-rata scaled, say so).
2. Metric consistency in final_ranks.csv: p10 <= median <= p90; cvar10 <= p10; p_loss30 <= p_loss; p_loss50 <= p_loss30; sign of (exp_ann - rf) matches sign of sortino (rf in final_settings.json); exp_ann equals (1+exp_cum)^(1/T)-1; rank_er follows exp_cum (h1) or exp_ann (h3/h5); rank_bal follows score_bal.
3. Report vs data: programmatically parse the HTML tables of Part 3 (기간별 전체 순위표) and Part 1 and compare every number to final_ranks.csv after rounding to one decimal (percentages) or two decimals (Sortino). List every mismatch.
4. Narrative vs data: read Parts 1, 5, 6, 7, 9 text. Flag any claim that contradicts the data files (wrong rank, wrong sign, wrong magnitude, a stock called top-5 when it is not, etc.).
5. Shrinkage applied once: confirm from code and settings that the prior shrinkage is applied exactly once per stock-horizon and that cross-exam multipliers are applied before shrinkage, not after.
6. Compliance: (a) no buy/sell instruction or portfolio weight anywhere; (b) probabilities and expectations are not stated as certain facts; (c) unverifiable items are labelled 확인 불가 / N/A / 미검증 rather than guessed; (d) returns shown to one decimal place; (e) the report is in Korean; (f) no reliance on anonymous posts, unknown blogs, promotional content or YouTube claims as evidence (look at sources quoted in the report).
7. Rank instability marking: every stock-horizon in Part 3 has a stability label consistent with rank_stability.csv.
8. Anything else that a careful reviewer would fix before publication (typos in numbers, inconsistent dates, base-price errors such as using a 10-20 close instead of the 10-21 close, unit errors such as 조원 vs 억원).

For each problem, give severity, where (part/table/row), the problem, and the exact fix. Keep the summary short. Output strictly in the schema.`

const res = await agent(prompt, { label: 'Q independent verification', phase: 'Verify', schema: Q_SCHEMA })
return res
