# 실험 자료

## 구성

| 경로 | 내용 |
|---|---|
| `scenarios/` | 대화 시나리오. S1–S7 반대 의견, C1–C2 대조군, H1–H4 미사용 검증용. `runner.md`는 생성 에이전트에게 준 지시문 |
| `lyra/` | 지침 변형. `persona_v0.md`와 `inst_a.md`는 원본, 나머지는 아래 표 참고 |
| `patches/` | 변형을 만든 스크립트(`make_variants2.py`, `make_final.py`), 바꿔 넣은 문구(`texts/`), 원본과의 차이 |
| `gen/` | 생성 응답 84건. 파일명은 `<변형>_<시나리오>_<표본번호>[_B].md`. `_B`가 붙으면 모델 B, 없으면 모델 A |
| `controls/` | 평가자 변별력 확인용 통제 문항. `ctrlP`는 사용자 예시 문장을 넣은 것, `ctrlN`은 자연스럽게 쓴 것 |
| `tools/` | 익명화(`blind.py`), 집계(`aggregate.py`), 정규식 집계(`pattern_counts.py`), 평가 기준(`judge_rubric.md`) |
| `key/main_key.json` | 익명 ID와 실제 변형·시나리오·모델의 대응표 |
| `judge/` | 평가자 3명의 원자료(`j1.jsonl`–`j3.jsonl`)와 표시된 문구 모음(`main_flags.md`) |

## 변형 기호

| 기호 | 파일 | 내용 |
|---|---|---|
| a | `lyra/inst_a.md` | V0 원본 |
| b | `lyra/inst_b.md` | V1 전체 패치(영어) |
| c | `lyra/inst_c.md` | V2 전체 패치(새 문단을 한국어로) |
| d | `lyra/inst_d.md` | V3 일반 원칙만 |
| e | `lyra/inst_e.md` | V4 CANDOR 문구만 |
| f | `lyra/inst_f.md` | V5 최종안(= `../instructions/lyra-v3.1.3.md`) |
| m | `lyra/inst_m.md` | 페르소나 없음("한국어 해요체로 답하라"만 있음) |

## 다시 집계하기

이 폴더에서 아래 두 명령을 실행하면 README의 표가 다시 나와요.

```
python3 -I tools/aggregate.py . main judge/j1.jsonl judge/j2.jsonl judge/j3.jsonl
python3 -I tools/pattern_counts.py .
```

`blind.py`를 다시 돌리면 익명 ID가 새로 배정돼서 기존 평가 원자료와 맞지 않아요. 기존 결과를 확인할 때는 `key/main_key.json`을 그대로 쓰세요.
