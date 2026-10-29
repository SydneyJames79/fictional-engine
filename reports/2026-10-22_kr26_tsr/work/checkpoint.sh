#!/usr/bin/env bash
# Checkpoint: copy pipeline artifacts from the scratchpad into the repo and commit+push.
# Usage: checkpoint.sh "<commit message>"
set -euo pipefail
SP=/tmp/claude-0/-home-user-fictional-engine/ff335beb-4d53-52b1-a2ba-4fe6e5b2979b/scratchpad
REPO=/home/user/fictional-engine
OUT=$REPO/reports/2026-10-22_kr26_tsr
mkdir -p "$OUT/work" "$OUT/data"
# scripts
cp "$SP"/*.py "$SP"/*.js "$SP"/*.sh "$OUT/work/" 2>/dev/null || true
cp "$SP"/manual_sections.json "$OUT/work/" 2>/dev/null || true
# data + agent outputs
for d in wf1 wf2 wf3 wf4 engine_prov engine_final; do
  if [ -d "$SP/$d" ]; then
    rm -rf "$OUT/data/$d"; mkdir -p "$OUT/data/$d"
    cp -r "$SP/$d"/. "$OUT/data/$d/"
  fi
done
# state file
python3 - "$SP" "$OUT" <<'EOF'
import json, os, sys, glob, datetime
sp, out = sys.argv[1], sys.argv[2]
def names(p): return sorted(os.path.basename(x)[:-5] for x in glob.glob(os.path.join(sp, p, '*.json')))
state = {
  'updated_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
  'analysis_basis': '2026-10-22 15:40 KST; horizons 2027-10-22 / 2029-10-22 / 2031-10-22; KRW',
  'wf1_stocks_verified': names('wf1/stocks'),
  'wf1_macro_common': os.path.exists(os.path.join(sp, 'wf1', 'macro_common.json')),
  'wf2': {k: names('wf2/' + k) for k in ['spec', 'gen', 'forensic', 'risk', 'synth']},
  'wf3': {'calibration': os.path.exists(os.path.join(sp, 'wf3', 'calibration.json')), 'bear': names('wf3/bear'), 'judge': names('wf3/judge')},
  'engine_final': os.path.exists(os.path.join(sp, 'engine_final', 'results.json')),
  'report': os.path.exists(os.path.join(out, 'report.md')),
  'resume_notes': [
    'WF2 workflow run ids (resume with scriptPath work/wf2_analysis.js + resumeFromRunId): wf_ab38b784-c89, wf_eef957b7-41c, wf_09747591-3dc, wf_c0202b56-fc7, wf_52821627-8a5, wf_09fc0278-88b',
    'WF3 run ids (scriptPath work/wf3_calibrate_bear.js): calib wf_693073ee-80a, wf_1d4a3052-2e4, wf_d3fcdfc3-e7a; bear wf_5a264304-350, wf_753db09c-1ef, wf_2bd496e4-c3a; judge wf_4fff849e-a5a, wf_5112a154-f41, wf_02838b94-35b',
    'Pipeline: collect_wf2.py -> build_trees.py (prov) -> engine.py -> prep_wf3_args.py -> wf3_calibrate_bear.js -> collect_wf3.py -> build_trees.py --final -> engine.py -> report_tables.py -> report_build.py -> wf4_verify.js',
    'Scratchpad path used by scripts: /tmp/claude-0/-home-user-fictional-engine/ff335beb-4d53-52b1-a2ba-4fe6e5b2979b/scratchpad (restore data/ from this repo there if lost)',
  ],
}
json.dump(state, open(os.path.join(out, 'STATE.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()}) for k, v in state.items() if k != 'resume_notes'}, ensure_ascii=False))
EOF
cd "$REPO"
git add -A reports/
if git diff --cached --quiet; then echo "nothing to commit"; exit 0; fi
git -c user.name="Lyra (Claude Code)" -c user.email="noreply@anthropic.com" commit -q -m "$1

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GuwdQtYrUZPasFK4huC1Xx"
for i in 1 2 3 4 5; do
  if git push -u origin ccr-fb7514aa-cprqf6 -q 2>/tmp/push.err; then echo "pushed"; exit 0; fi
  echo "push failed (attempt $i): $(tail -1 /tmp/push.err)"; sleep $((2**i))
done
exit 1
