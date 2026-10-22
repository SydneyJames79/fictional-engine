"""워크플로 journal.jsonl에서 에이전트별 구조화 결과를 꺼낸다."""
import glob
import json
import os
import sys

BASE = '/root/.claude/projects/-home-user-fictional-engine/53597674-b69d-5832-baad-c5e925f14216/subagents/workflows'


def read_results(run_dir):
    out = {}
    labels = {}
    path = os.path.join(BASE, run_dir, 'journal.jsonl')
    for line in open(path):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('type') == 'started':
            labels[d.get('agentId')] = d.get('label')
        if d.get('type') in ('completed', 'result', 'finished', 'done'):
            aid = d.get('agentId')
            res = d.get('result', d.get('output', d.get('value')))
            out[labels.get(aid, aid)] = res
    return out, labels


if __name__ == '__main__':
    for run in sys.argv[1:]:
        res, labels = read_results(run)
        print(run, 'started:', len(labels), 'with results:', len(res))
        for k, v in res.items():
            print('  ', k, type(v).__name__, len(json.dumps(v, ensure_ascii=False)) if v is not None else None)
