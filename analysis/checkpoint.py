"""체크포인트: 모든 워크플로 결과를 파일로 모으고 진행 현황 문서(CHECKPOINT.md)를 갱신한다.

사용: python3 analysis/checkpoint.py "메모(선택)"
그 뒤 checkpoint.sh가 git commit/push까지 한다. 세션이 끊겨도 원격 브랜치에서 이어갈 수 있게 하는 것이 목적이다.
"""
import datetime as dt
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from collect import collect  # noqa: E402
from journal_reader import BASE, search_count  # noqa: E402
from workflows.build_stock_script import NAMES  # noqa: E402

AUX = os.path.join(HERE, 'data', 'aux')
os.makedirs(AUX, exist_ok=True)
KST = dt.timezone(dt.timedelta(hours=9))


def scan_runs():
    """모든 워크플로 실행의 에이전트 상태를 모은다: {run: [(label, status, agentId)]}"""
    runs = {}
    for run in sorted(glob.glob(os.path.join(BASE, 'wf_*')), key=os.path.getmtime):
        jp = os.path.join(run, 'journal.jsonl')
        if not os.path.exists(jp):
            continue
        labels, status = {}, {}
        for line in open(jp):
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get('type')
            k = d.get('key')
            if t == 'started':
                labels[k] = d.get('label', '')
                status[k] = ('running', d.get('agentId'))
            elif t == 'result':
                status[k] = ('done', d.get('agentId'))
            elif t == 'failed':
                if status.get(k, ('',))[0] != 'done':
                    status[k] = ('failed', d.get('agentId'))
        runs[os.path.basename(run)] = [(labels.get(k, '?'), s, a) for k, (s, a) in status.items()]
    return runs


# 같은 라벨을 쓰는 재실행이 앞선 결과를 덮어쓰지 않도록 실행별 파일 이름을 따로 둔다.
# (예: 3종목 재심사는 26종목 최종심사 파일을 덮어쓰면 안 된다)
# 1차 최종심사 원본은 J0_으로 남기고, J_final_judge.json은 merge_judge.py가 1차와 재심사를 병합해 만든다.
RUN_FILE_OVERRIDE = {'wf_9f46b1d1-5df': 'J0_final_judge_1차', 'wf_64c36420-365': 'J2_rereview_auto', 'wf_e113a233-ce7': 'J2_rereview_samsung'}


def save_aux():
    """종목별이 아닌 결과(H, G, B2, I, V, S, J 등)를 data/aux에 저장한다."""
    saved = []
    for run in sorted(glob.glob(os.path.join(BASE, 'wf_*')), key=os.path.getmtime):
        jp = os.path.join(run, 'journal.jsonl')
        if not os.path.exists(jp):
            continue
        labels = {}
        for line in open(jp):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') == 'started':
                labels[d['agentId']] = d.get('label', '')
            elif d.get('type') == 'result' and d.get('result') is not None:
                lab = labels.get(d['agentId'], '')
                if lab.split(' ')[0] in ('D', 'G', 'E') and lab.split(' ')[1] in ('specialist', 'generalist', 'forensic'):
                    continue
                fn = RUN_FILE_OVERRIDE.get(os.path.basename(run)) or lab.replace(' ', '_').replace('/', '_') or d['agentId']
                json.dump({'label': lab, 'run': os.path.basename(run), 'searches': search_count(os.path.basename(run), d['agentId']),
                           'result': d['result']}, open(os.path.join(AUX, f'{fn}.json'), 'w'), ensure_ascii=False, indent=1)
                saved.append(lab)
    return saved


def write_md(found, runs, aux, note):
    now = dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')
    lines = [f'# 체크포인트 — 한국 26개 종목 기대수익률 순위 프로젝트', '', f'갱신: {now}', '']
    if note:
        lines += [f'메모: {note}', '']
    lines += ['## 고정된 설정', '',
              '- 분석 기준일: 2026-10-22(KST). 기준 주가: 2026-10-21 KRX 공식 종가(FinanceData/marcap 데이터셋). 에이전트 시나리오는 2026-10-20 종가 시점에 작성됐고, TSR은 10-21 종가로 다시 계산한다.',
              '- 기간 종료일: 1년 2027-10-22, 3년 2029-10-22, 5년 2031-10-22. 통화 KRW. 무위험수익률(국고, 10-21): 1년 3.688%, 3년 3.822%, 5년 3.965%.',
              '- 공통 거시 시나리오(Agent C): 기준 50 / 낙관 20 / 비관 30. 지수 기대 TSR: KOSPI 8.5% / 연 7.7% / 연 8.9%, KOSDAQ 6.0% / 5.7% / 7.0%. 원본: analysis/data/macro.json',
              '- 방법: 종목별 시나리오 트리(거시 태그 고정확률 × 종목 하위분기) → 전문가·일반 분석가 혼합 → 희석 조정 → 반대심문 조정 → 사전값 축소(한 번) → 혼합 로그정규 몬테카를로 → 지표·순위. 코드: analysis/pipeline.py, analysis/quant_engine.py',
              '- 제약: 웹검색은 턴당 200회(전 에이전트 합산). 직접 접속(네이버·KRX·DART 등)은 네트워크 정책상 차단, WebSearch만 가능.', '',
              '## 종목별 진행 현황', '', '| 코드 | 종목 | 전문가(D) | 일반(G) | 포렌식(E) |', '|---|---|---|---|---|']
    for c, n in NAMES.items():
        r = found.get(c, {})
        cell = lambda k: (f"완료({r[k]['searches']}회 검색)" if k in r else '대기/미완')
        fe = r.get('foren')
        fe_cell = (f"완료({fe['searches']}회)" if fe and fe['searches'] > 0 else ('검색없는 초안만' if fe else '대기/미완'))
        lines.append(f'| {c} | {n} | {cell("spec")} | {cell("gen")} | {fe_cell} |')
    lines += ['', '## 기타 에이전트 결과(파일: analysis/data/aux/)', '']
    lines += [f'- {a}' for a in sorted(set(aux))] or ['- 없음']
    lines += ['', '## 실행 기록(재개용 run ID)', '', '실패·미완 에이전트는 `Workflow({scriptPath, resumeFromRunId, args})`로 다시 돌리면 완료된 에이전트는 캐시로 재생된다.', '']
    for run, items in runs.items():
        desc = '; '.join(f'{l}={s}' for l, s, _ in items)
        lines.append(f'- `{run}`: {desc}')
    lines += ['', '## 다음 단계', '',
              '1. 남은 종목의 전문가·일반 분석가·포렌식 결과 수집',
              '2. 예비 정량 순위(pipeline.analyse) → 상위 종목 반대심문(I)·사실검증(V)·민감도(S)',
              '3. 최종 심사(J): 전문가/일반 가중치, 반대심문 채택 범위 결정 → 최종 순위·민감도 재계산',
              '4. 보고서(1~9부) 작성, 아티팩트 게시, 커밋', '']
    open(os.path.join(HERE, 'CHECKPOINT.md'), 'w').write('\n'.join(lines))


if __name__ == '__main__':
    note = sys.argv[1] if len(sys.argv) > 1 else ''
    found = collect()
    runs = scan_runs()
    aux = save_aux()
    write_md(found, runs, aux, note)
    done = sum(1 for c in NAMES if 'spec' in found.get(c, {}))
    print(f'checkpoint written: spec {done}/26, gen {sum(1 for c in NAMES if "gen" in found.get(c, {}))}/26, aux {len(set(aux))}')
