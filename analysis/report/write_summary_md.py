"""저장소 루트의 REPORT.md(요약)를 최종 산출 파일에서 만든다. 사용: python3 analysis/report/write_summary_md.py"""
import json
import os

import pandas as pd

AN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = pd.read_csv(f'{AN}/output/final_ranks.csv', dtype={'code': str})
st = pd.read_csv(f'{AN}/output/rank_stability.csv', dtype={'code': str})
J = {s['code']: s for s in json.load(open(f'{AN}/data/aux/J_final_judge.json'))['result']['stocks']}


def pc(x, signed=True):
    s = f'{x*100:+.1f}%' if signed else f'{x*100:.1f}%'
    return s.replace('+0.0%', '0.0%').replace('-0.0%', '0.0%').replace('-', '−')


L = ['# 한국 26종목 1·3·5년 기대수익 순위', '',
     '기준: 2026-10-21 KRX 종가, 분석일 2026-10-22, 기간 종료 2027/2029/2031-10-22, 원화·배당 포함 총수익(TSR).',
     '모든 확률·기대값은 모형 추정치다. 개인의 위험선호와 재무상황을 모르므로 매매 판단이나 투자비중은 제시하지 않는다.', '',
     '전체 보고서(1~9부, 품질 체크리스트, 부록)는 `analysis/report/report.html`이다. 수치는 `analysis/output/`의 산출 파일에서 직접 만든다.', '']
for h, lab in (('h1', '1년'), ('h3', '3년'), ('h5', '5년')):
    g = r[r.h == h].sort_values('rank_bal')
    L += [f'## {lab} 균형형 순위', '',
          '| 균형 | 종목 | 기대 TSR' + ('(누적)' if h == 'h1' else '(연)') + ' | 중앙값(누적) | P10 | P90 | 손실확률 | CVaR10 | Sortino | 지수 대비(연) | 신뢰도 | 안정성 |',
          '|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for _, x in g.iterrows():
        e = x.exp_cum if h == 'h1' else x.exp_ann
        s = st[(st.code == x.code) & (st.h == h)].stability.iloc[0]
        so = f'{x.sortino:.2f}'.replace('-', '−')
        L.append(f'| {int(x.rank_bal)} | {x["name"]} | {pc(e)} | {pc(x.median_cum)} | {pc(x.p10)} | {pc(x.p90)} | {pc(x.p_loss, False)} | {pc(x.cvar10)} | {so} | '
                 f'{pc(x.excess_vs_index_ann)} | {J[x.code]["final_confidence"]} | {s} |')
    L.append('')
L += ['## 방법 요약', '',
      '1. 역할별 에이전트 108개: 식별·검증(B) 4, 거시(C) 3, 산업 전문가(D, 가치평가 겸) 26, 독립 일반 분석가 26, 포렌식(E) 26, 정량·위험(G) 1, 베이스레이트(H) 1, 반대심문(I) 9, 사실검증(V) 9, 민감도(S) 1, 최종심사(J) 1, 독립 검증(Q) 1.',
      '2. 종목·기간별 시나리오 트리(거시 기준 50·낙관 20·비관 30 고정, 하위분기 무조건부 확률)를 전문가·일반 분석가가 각각 작성했다.',
      '3. 포렌식이 더 큰 신주 발행을 보면 희석 보정, 두 트리를 가중 혼합, 최종심사가 채택한 반대심문 조정을 적용했다.',
      '4. 사전값(무위험 + 선행 베타 × 지수 초과기대 + 베이스레이트 버킷 알파) 쪽으로 한 번만 축소했다. 두 분석가가 사전값의 같은 쪽에 있으면 불일치 감쇠가 과하게 작동하지 않게 했다.',
      '5. 혼합 로그정규 몬테카를로(종목·기간별 200,000 경로)로 분포 지표를 계산했다. 균형형 = 기대 60 / Sortino 25 / CVaR10 15(백분위). 공격형 75/15/10, 방어형 40/35/25.',
      '6. 가정 변경 8종과 추정오차 부트스트랩으로 순위 안정성을 판정했고, 스트레스 충격 8종은 따로 계산했다.', '',
      '## 파일', '',
      '- `analysis/report/report.html`: 최종 보고서. `analysis/report/build_report.py`, `write_narrative.py`로 생성한다.',
      '- `analysis/output/final_ranks.csv`, `final_branches.csv`, `final_settings.json`: 최종 지표·분기·설정.',
      '- `analysis/output/rank_stability.csv`, `sens_runs.csv`: 순위 안정성과 민감도.',
      '- `analysis/data/stocks/*.json`: 종목별 산업 전문가·일반 분석가·포렌식 결과. `analysis/data/aux/*.json`: 식별·거시·위험·베이스레이트·반대심문·사실검증·민감도·최종심사·독립 검증 결과.',
      '- `analysis/pipeline.py`, `quant_engine.py`, `run_quant.py`, `sensitivity.py`: 정량 단계 코드. `analysis/workflows/`: 에이전트 워크플로 스크립트.', '',
      '## 한계', '',
      '- 공시 원문(DART·KRX)을 직접 열람하지 못했고 유료 데이터베이스에는 접근하지 않았다. 일부 수치는 2차 집계 출처라 "미검증"으로 표시했다.',
      '- 대부분 종목의 3Q26 실적이 분석 시점에 발표 전이었다.',
      '- 2026년 급등락으로 변동성 가정이 커서 손실확률·CVaR가 베이스레이트보다 보수적으로 나온다(순위 영향은 작음).', '']
open(os.path.join(os.path.dirname(AN), 'REPORT.md'), 'w').write('\n'.join(L))
print('wrote REPORT.md', len(L))
