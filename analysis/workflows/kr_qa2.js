export const meta = {
  name: 'kr-qa2',
  description: 'Agent Q2 narrow re-verification: confirm the fixes for the 21 QA findings and check what the re-reviews changed',
  phases: [
    { title: 'Verify', detail: 'Q2: fixes, re-review merge, new narrative claims' },
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
You are Agent Q2 (재검증) in a multi-agent research system that ranked 26 Korean stocks by expected total shareholder return over 1y/3y/5y. An earlier independent verifier (Q) reviewed the report and raised 21 issues. The coordinator then fixed them, re-ran the final judge (J) for 6 stocks, and recomputed everything. Your job is a NARROW re-verification: confirm the fixes and catch anything the fixes broke. Do NOT redo Q's full review. Do NOT use WebSearch or any web tool. Use only local files (Read, Bash with python3/pandas are fine). Write findings in Korean (report style, 하다체).

Files (all under /home/user/fictional-engine/analysis):
- data/aux/Q_independent_verification.json: Q's original findings (issues[i] with where/problem/fix).
- report/narrative.json: the report text; key q_fixes maps each Q issue index (string) to the action the coordinator says it took.
- report/report.html: the regenerated report. report/write_narrative.py and report/build_report.py generate it.
- data/aux/J0_final_judge_1차.json (first judge decision), data/aux/J2_rereview_auto.json, J2_rereview_samsung.json, J2_rereview_tariff.json (re-reviews), data/aux/J_final_judge.json (merged by merge_judge.py; its rereview key lists the re-reviewed stocks).
- data/aux/V1_verify_현대차_1차.json and V1_verify_삼성전자_1차.json: first-round verification results that had been overwritten and were restored.
- output/final_ranks.csv, final_branches.csv, final_settings.json, rank_stability.csv, sens_runs.csv: recomputed outputs. pipeline.py, run_quant.py, sensitivity.py: code.
- ../REPORT.md (repository root): short summary generated from the same outputs.

Check at least the following, each as a check with status 통과/부분/미흡 and concrete evidence:
1. For each of Q's 21 issues: is the problem actually gone in the current report.html / code / outputs, and is the q_fixes text for that index accurate? Group them in a few checks if convenient, but name every index that is not fully fixed.
2. Re-review merge: J_final_judge.json equals J0 with exactly the J2 stocks replaced; the merged adjustments reach output/final_settings.json (adjustments per stock and horizon, as macro_value_mult) and the Part 7 table of report.html shows the merged multipliers. Confirm the V1 facts that the re-reviews cite (대미투자특별법 2026-03-12 통과, 다년 보상용 자사주) are actually present in the V1 files with sources.
3. Sensitivity: the base run in sens_runs.csv reproduces final_ranks.csv exactly (rank_bal, exp_cum); the prior_heavy (축소 강화) run now differs from base; the stability counts in Part 8's 요약 and the labels in Parts 1/3/8 match rank_stability.csv.
4. Narrative vs data, only for text that changed: Parts 1, 4, 5, 6, 7, 8, 9, the 분석 이후 사건 box, the checklist and Appendix B/C/F. Recompute every number they state (ranks, expected TSRs, excess vs index, adoption ratios in Part 7, same-side-fix counts, gap medians in Part 8, bull-group contributions, dilution range) and flag any mismatch, wrong particle/grammar that changes meaning, or claim the files do not support.
5. Expected TSR now uses the exact branch expectation: check that exp_cum in final_ranks.csv equals sum(prob*(price+div))/p0 - 1 from final_branches.csv for every stock-horizon.
6. Compliance spot check on changed text: no buy/sell instruction or portfolio weight; probabilities not stated as certain; unverified values labelled (미검증/확인 불가); returns to one decimal place.
7. REPORT.md agrees with final_ranks.csv on the top-5 per horizon.

Report only real problems as issues (severity, where, problem, exact fix). If everything checks out, say so briefly. Output strictly in the schema.`

const res = await agent(prompt, { label: 'Q2 re-verification', phase: 'Verify', schema: Q_SCHEMA })
return res
