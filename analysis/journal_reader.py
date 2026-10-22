"""워크플로 journal.jsonl에서 에이전트별 결과와 검색 횟수를 꺼낸다."""
import glob
import json
import os
import sys

BASE = '/root/.claude/projects/-home-user-fictional-engine/53597674-b69d-5832-baad-c5e925f14216/subagents/workflows'


def search_count(run_dir, agent_id):
    ok = 0
    for f in glob.glob(os.path.join(BASE, run_dir, f'agent-{agent_id}.jsonl')):
        for line in open(f):
            try:
                y = json.loads(line)
            except Exception:
                continue
            c = y.get('message', {}).get('content')
            if isinstance(c, list):
                for b in c:
                    if b.get('type') == 'tool_result':
                        t = json.dumps(b.get('content'), ensure_ascii=False)
                        if t.startswith('"Web search results') and 'budget is used up' not in t:
                            ok += 1
    return ok


def read_results(run_dir):
    """{label: {'result': ..., 'searches': n}}"""
    labels, out = {}, {}
    for line in open(os.path.join(BASE, run_dir, 'journal.jsonl')):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('type') == 'started':
            labels[d['agentId']] = d.get('label')
        elif d.get('type') == 'result':
            aid = d.get('agentId')
            res = d.get('result', d.get('value', d.get('output')))
            out[labels.get(aid, aid)] = {'result': res, 'searches': search_count(run_dir, aid), 'agentId': aid}
    return out


if __name__ == '__main__':
    for run in sys.argv[1:]:
        res = read_results(run)
        for k, v in res.items():
            print(run, k, 'searches=%d' % v['searches'], 'size=%d' % len(json.dumps(v['result'], ensure_ascii=False)))
