#!/usr/bin/env bash
# 체크포인트를 만들고 원격 브랜치에 커밋·푸시한다.
set -u
cd "$(dirname "$0")/.." || exit 1
python3 analysis/checkpoint.py "${1:-}" || exit 1
git add -A analysis
git commit -q -m "Checkpoint: ${1:-progress}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JkuJc6UJdsYLHbLtdzRt2b" || echo "nothing to commit"
for i in 1 2 3 4; do git push -q -u origin ccr-12243598-y78irj && break || sleep $((2**i)); done
git log --oneline -1
