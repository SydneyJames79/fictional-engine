# Lyra 한국어 말투 분석 (v3.1.2 → v3.1.3)

Lyra 지침을 쓸 때 가끔 나오는 기계 같은 한국어("한 번만 세게 밀고", "한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요")의 원인을 분석하고, 금지어 목록 없이 고친 패치를 실험으로 검증한 기록이에요.

## 요약

- **원인은 두 겹이에요.** 하나는 규칙 낭독이에요. 모델이 CANDOR 조항("state it once, early, at full strength", "say plainly that you have not heard a new argument")을 사용자에게 하는 약속이나 선언으로 바꿔 말해요. 다른 하나는 직역이에요. 영어로 짠 생각에 한국어 낱말만 끼워 넣는 거예요('밀다'는 지침에 없는 말로, push back에서 왔어요).
- **규칙 낭독은 지침 탓이에요.** 두 모델 모두 원본 지침에서 압박 장면마다(7/7) 토론 심판투 문장을 냈고, CANDOR 문구를 고친 판에서는 한 번도 안 냈어요(0/18).
- **직역은 모델 능력도 작용해요.** 원본 지침에서 모델 B는 14개 중 13개, 모델 A는 30개 중 13개에 직역 표시가 붙었어요. 목표 말투를 적어 넣은 패치에서는 31개 중 1개였어요.
- **고칠 곳은 네 군데예요.** 금지 목록도, 한국어 예문도 넣지 않았어요. 자세한 내용은 [FINAL_PATCH.md](FINAL_PATCH.md)에 있어요.

## 바로 적용하기

- 통째로 바꾸려면: [instructions/lyra-v3.1.3.md](instructions/lyra-v3.1.3.md)를 그대로 붙여 넣으면 돼요.
- 고칠 곳만 보려면: [FINAL_PATCH.md](FINAL_PATCH.md) 또는 [instructions/v3.1.2-to-v3.1.3.diff](instructions/v3.1.2-to-v3.1.3.diff)를 보세요.

## 진행 방식

| 단계 | 내용 |
|---|---|
| 분석 (독립 4건) | A1 지침 원문 추적, A2 한국어학(편집자 관점), A3 메커니즘·1차 출처 조사, A4 반론과 실험 설계 |
| 실행 | 서브에이전트 하나가 응답 하나를 생성(지침 파일을 시스템 지침처럼 받고 대화를 이어 답하는 방식). 반대 의견 시나리오 7개(S1–S7), 대조군 2개(C1–C2), 미사용 검증 시나리오 4개(H1–H4) |
| 변형 | V0 원본 / V1 전체 패치(영어) / V2 전체 패치(새 문단을 한국어로) / V3 일반 원칙만 / V4 CANDOR 문구만 / V5 최종안 / 페르소나 없음 |
| 생성 모델 | 모델 A(기본 생성 모델, 상위 등급), 모델 B(한 단계 아래 등급) |
| 검증 | 블라인드 평가자 3명 × 88건(통제 문항 4건 포함, 어느 지침에서 나온 응답인지 모름), 패치 비평 2건(규칙 충돌, 설계 의도 보존), 1차 출처 대조, 최종안 재검증 |

평가자 간 일치도는 자연스러움 점수의 순위상관 0.66–0.82, '부자연스러운 낭독' 표시 일치율 0.95–1.00이에요. 사용자 예시 문장을 넣은 통제 문항은 2.67점, 자연스럽게 쓴 통제 문항은 5.00점이 나와서, 평가자들이 변별은 제대로 한다고 봤어요.

## 결과 1: 규칙 낭독 (압박 장면 S5, 미사용 H3)

사용자가 "그냥 좀 내 편 들어 주면 안 돼?"처럼 새 논거 없이 조르는 장면이에요.

| 변형 | 응답 수 | '새 이유 없음' 낭독(정규식) | 평가자 다수의 '부자연스러운 낭독' 표시 |
|---|---|---|---|
| V0 원본, 모델 A | 5 | 5 | 5 |
| V0 원본, 모델 B | 2 | 2 | 2 |
| V3 일반 원칙만 | 3 | 3 | 2 |
| V4 CANDOR 문구만 | 3 | 0 | 0 |
| V1 전체(영어), 모델 A 5 + 모델 B 2 | 7 | 0 | 0 |
| V2 전체(한국어 문단) | 3 | 0 | 0 |
| V5 최종안 | 5 | 0 | 0 |
| 페르소나 없음 | 3 | 0 | 0 |

원본 7/7 대 CANDOR 문구를 고친 변형 0/18이에요(정확 검정 p ≈ 2×10⁻⁶). 일반 원칙만 넣은 V3과 CANDOR만 고친 V4의 차이(3/3 대 0/3)는 표본이 작아서 방향만 보여 줘요(p = 0.1). 명시적으로 '말하라'는 지시는 일반 원칙만으로는 꺾이지 않았어요.

- 원본의 전형: "다만 생각을 바꿀 만한 새 이유가 나온 건 아니라서, 제 의견은 그대로예요. 같은 얘기를 또 늘어놓진 않을게요." / "근데 친구들이 괜찮다고 한 게 새로운 이유는 아니라서, 제 생각은 그대로예요."
- 최종안의 전형: "제가 누구 편인데요. 그 메일 편을 안 드는 것뿐이에요." / "다들 괜찮다는데 저만 말리면 유난처럼 보이긴 하겠네요. 그래도 제 생각은 그대로예요. … 친구들한테 괜찮은 거랑 이번 할부가 괜찮은 거랑은 다른 얘기예요."

(정규식 집계에서 V1의 다른 시나리오에 잡힌 1건은 "사용자 눈엔 달라진 게 없는 제안이에요"라는, 낭독과 무관한 문장이에요.)

## 결과 2: 직역(번역투)

| 묶음 | 응답 수 | 자연스러움 평균(1–5) | 평가자 다수가 직역을 표시한 응답 |
|---|---|---|---|
| V0 원본, 모델 A (반대 21 + 미사용 5 + 대조 4) | 30 | 4.35 | 13 |
| V0 원본, 모델 B (반대 14) | 14 | 3.98 | 13 |
| 목표 말투 문단이 들어간 패치 (V1·V2·V5) | 31 | 4.97 | 1 |

원본 모델 A 13/30 대 패치 1/31(p ≈ 0.0002), 원본 모델 B 13/14 대 원본 모델 A 13/30(p ≈ 0.0025)이에요.

- 원본에서 표시된 예: "그 얄미움이 이 책의 엔진이니까"(the engine of), "퇴사와 창업은 꼭 같이 갈 필요가 없는 두 결정이에요"(two separate decisions), "예전에 고친 버그를 새 코드에서 또 만나게 돼요"(run into), "처음 만난 사람이랑 대화를 여는 데는 꽤 좋은 도구예요"(open a conversation, a good tool), "팀장도 예스라고 하기 쉬워요"(say yes).
- 패치에서 남은 예: "느낌이 맞다면 숫자도 같은 얘기를 할 테니"(the numbers will tell the same story).

## 한계

- 시뮬레이션이에요. 서브에이전트는 지침을 파일로 읽었고 자체 시스템 지침도 따로 있어서, 실제 채팅 앱 환경과 같지 않아요.
- 사용자 예시와 똑같은 "한 번만 세게…" 식 예고문은 원본 지침으로 44번 생성하는 동안 한 번도 나오지 않았어요. 같은 메커니즘의 다른 형태(압박 장면의 낭독)는 매번 재현됐어요. 그래서 예고문에 대한 처방(일반 원칙, "at full strength" 수정)은 분석에 근거한 것이지 실험으로 확인한 건 아니에요.
- 평가자도 같은 계열의 모델이라 생성 모델과 맹점을 공유할 수 있어요. 통제 문항으로 변별력은 확인했지만, 최종 판단은 한국어 화자의 몫이에요.
- 패치 변형은 S1–S7 표본이 원본보다 적어요. 직역이 줄어든 것을 목표 말투 문단의 효과로 보는 건 타당한 추론이지만, 그 문단만 따로 떼어 시험하지는 않았어요(V3·V4는 S5에서만 돌림).
- '영어로 먼저 계획을 세우면 그 표현이 답변에 새어 나온다'는 가설(확장 사고)은 시험하려다 안전장치에 걸려서 하지 않았어요.
- 학술 논문(Wendler 2024, Li 2025 등)은 원문 사이트에 접속하지 못해 초록 수준으로만 확인돼서, 핵심 근거로 쓰지 않았어요.

## 1차 출처 (2026-10-06에 내려받아 대조)

- Anthropic, "Prompting best practices": "Tell Claude what to do instead of what not to do" / "Providing context or motivation behind your instructions … can help Claude better understand your goals" / "Include 3–5 examples for best results."
- Anthropic, 최신 세대 모델용 프롬프트 가이드: "… narrates readily during agentic work: it tends to announce what it is about to do" / "Positive examples of the communication style you want tend to be more effective than instructions about what not to do."
- Anthropic, "Multilingual support": "you can prompt Claude to use 'idiomatic speech as if it were a native speaker.'"
- Anthropic, "Tracing the thoughts of a large language model"(2025): "Claude sometimes thinks in a conceptual space that is shared between languages" / 방법론이 "only captures a fraction of the total computation"이라는 단서.
- Anthropic의 Claude 헌법 문서: "we want Claude to push back and challenge us".

## 폴더 안내

| 경로 | 내용 |
|---|---|
| [FINAL_PATCH.md](FINAL_PATCH.md) | 고칠 네 군데와 이유, 선택 사항 |
| [instructions/](instructions/) | 원본(v3.1.2), 패치 적용본(v3.1.3), 두 판의 차이 |
| [analysis/](analysis/) | 독립 분석 보고서 4건(A1–A4) |
| [verification/](verification/) | 패치 비평 2건 |
| [experiment/](experiment/) | 시나리오, 지침 변형, 생성 응답 84건, 블라인드 평가 원자료, 집계 스크립트 |
