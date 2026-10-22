# 체크포인트 — 한국 26개 종목 기대수익률 순위 프로젝트

갱신: 2026-10-23 03:29 KST

메모: 삼성에피스홀딩스 3개 역할 완료

## 고정된 설정

- 분석 기준일: 2026-10-22(KST). 기준 주가: 2026-10-21 KRX 공식 종가(FinanceData/marcap 데이터셋). 에이전트 시나리오는 2026-10-20 종가 시점에 작성됐고, TSR은 10-21 종가로 다시 계산한다.
- 기간 종료일: 1년 2027-10-22, 3년 2029-10-22, 5년 2031-10-22. 통화 KRW. 무위험수익률(국고, 10-21): 1년 3.688%, 3년 3.822%, 5년 3.965%.
- 공통 거시 시나리오(Agent C): 기준 50 / 낙관 20 / 비관 30. 지수 기대 TSR: KOSPI 8.5% / 연 7.7% / 연 8.9%, KOSDAQ 6.0% / 5.7% / 7.0%. 원본: analysis/data/macro.json
- 방법: 종목별 시나리오 트리(거시 태그 고정확률 × 종목 하위분기) → 전문가·일반 분석가 혼합 → 희석 조정 → 반대심문 조정 → 사전값 축소(한 번) → 혼합 로그정규 몬테카를로 → 지표·순위. 코드: analysis/pipeline.py, analysis/quant_engine.py
- 제약: 웹검색은 턴당 200회(전 에이전트 합산). 직접 접속(네이버·KRX·DART 등)은 네트워크 정책상 차단, WebSearch만 가능.

## 종목별 진행 현황

| 코드 | 종목 | 전문가(D) | 일반(G) | 포렌식(E) |
|---|---|---|---|---|
| 000660 | SK하이닉스 | 완료(12회 검색) | 대기/미완 | 완료(16회) |
| 005930 | 삼성전자 | 완료(12회 검색) | 완료(4회 검색) | 완료(16회) |
| 207940 | 삼성바이오로직스 | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |
| 0126Z0 | 삼성에피스홀딩스 | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |
| 005380 | 현대차 | 완료(12회 검색) | 완료(4회 검색) | 완료(12회) |
| 012330 | 현대모비스 | 완료(12회 검색) | 완료(4회 검색) | 완료(13회) |
| 307950 | 현대오토에버 | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |
| 295310 | 에이치브이엠 | 완료(12회 검색) | 대기/미완 | 대기/미완 |
| 452430 | 사피엔반도체 | 대기/미완 | 대기/미완 | 대기/미완 |
| 418420 | 라온텍 | 대기/미완 | 대기/미완 | 대기/미완 |
| 370090 | 퓨런티어 | 대기/미완 | 대기/미완 | 검색없는 초안만 |
| 010690 | 화신 | 대기/미완 | 대기/미완 | 검색없는 초안만 |
| 290650 | 엘앤씨바이오 | 대기/미완 | 대기/미완 | 대기/미완 |
| 314930 | 바이오다인 | 대기/미완 | 대기/미완 | 대기/미완 |
| 171090 | 선익시스템 | 완료(12회 검색) | 대기/미완 | 대기/미완 |
| 178320 | 서진시스템 | 대기/미완 | 대기/미완 | 대기/미완 |
| 007660 | 이수페타시스 | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |
| 107640 | 한중엔시에스 | 완료(12회 검색) | 대기/미완 | 대기/미완 |
| 218410 | RFHIC | 대기/미완 | 대기/미완 | 대기/미완 |
| 189300 | 인텔리안테크 | 대기/미완 | 대기/미완 | 대기/미완 |
| 099320 | 쎄트렉아이 | 대기/미완 | 대기/미완 | 대기/미완 |
| 403870 | HPSP | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |
| 032500 | 케이엠더블유 | 대기/미완 | 대기/미완 | 대기/미완 |
| 098460 | 고영 | 완료(12회 검색) | 대기/미완 | 대기/미완 |
| 232140 | 와이씨 | 완료(12회 검색) | 대기/미완 | 검색없는 초안만 |
| 042700 | 한미반도체 | 완료(12회 검색) | 완료(4회 검색) | 완료(5회) |

## 기타 에이전트 결과(파일: analysis/data/aux/)

- B verify 1
- B verify 2
- B verify 3
- C1 markets-rates-FX
- C2 sector drivers
- C3 macro synthesis

## 실행 기록(재개용 run ID)

실패·미완 에이전트는 `Workflow({scriptPath, resumeFromRunId, args})`로 다시 돌리면 완료된 에이전트는 캐시로 재생된다.

- `wf_cbe96be2-a39`: B verify 1=done; B verify 2=done; B verify 3=done; H base rates=running
- `wf_5001a290-3a7`: C1 markets-rates-FX=done; C2 sector drivers=done; C3 macro synthesis=done
- `wf_186cfa78-ec7`: E forensic SK하이닉스=done; E forensic 삼성전자=done; E forensic 한미반도체=done; E forensic HPSP=done; E forensic 와이씨=done; E forensic 이수페타시스=running; E forensic 고영=running
- `wf_d4f4b1cd-657`: E forensic 현대차=done; E forensic 현대모비스=done; E forensic 현대오토에버=done; E forensic 화신=done; E forensic 퓨런티어=done; E forensic 삼성바이오로직스=done; E forensic 삼성에피스홀딩스=running; E forensic 엘앤씨바이오=running
- `wf_86f1ebc6-b8f`: D specialist HPSP=done; E forensic HPSP=done; G generalist HPSP=done
- `wf_8b27352d-8ee`: D specialist SK하이닉스=done; G generalist SK하이닉스=running
- `wf_e5c79c65-5c0`: D specialist 삼성전자=done; G generalist 삼성전자=done
- `wf_d9ca0087-923`: D specialist 현대모비스=done; G generalist 현대모비스=done
- `wf_7e65be40-75c`: D specialist 현대차=done; G generalist 현대차=done
- `wf_df0e3ba4-2c1`: D specialist 한미반도체=done; E forensic 한미반도체=done; G generalist 한미반도체=done
- `wf_3f2f13d0-370`: D specialist 삼성에피스홀딩스=done; E forensic 삼성에피스홀딩스=done; G generalist 삼성에피스홀딩스=done
- `wf_5f8f46b4-9d4`: D specialist 삼성바이오로직스=done; E forensic 삼성바이오로직스=done; G generalist 삼성바이오로직스=done
- `wf_53fa0f1f-009`: D specialist 현대오토에버=done; E forensic 현대오토에버=done; G generalist 현대오토에버=done
- `wf_2bf524a6-d21`: D specialist 이수페타시스=done; E forensic 이수페타시스=done; G generalist 이수페타시스=done
- `wf_55bd304a-62d`: ?=failed
- `wf_f8f8df06-d24`: ?=failed
- `wf_4f8d980c-7ef`: ?=failed
- `wf_4d120433-106`: ?=failed
- `wf_c2caf6a2-003`: ?=failed
- `wf_cb78a0ed-9ff`: ?=failed
- `wf_56d7a284-8d5`: D specialist 서진시스템=running
- `wf_7ef3a569-7e6`: G risk review=running
- `wf_4d027186-9f0`: H base rates=running
- `wf_abf1369d-9e6`: D specialist 라온텍=running
- `wf_ffdae734-e40`: D specialist 화신=running
- `wf_2a198423-31c`: D specialist 퓨런티어=running
- `wf_e56340d8-53d`: D specialist 엘앤씨바이오=running
- `wf_1972a1d9-1a0`: D specialist 바이오다인=running
- `wf_058659ad-5a5`: D specialist 사피엔반도체=running
- `wf_372974de-9cf`: D specialist 인텔리안테크=running
- `wf_1de1e803-013`: D specialist 쎄트렉아이=running
- `wf_bfa81d1d-efd`: D specialist 케이엠더블유=running
- `wf_d819d401-b55`: D specialist RFHIC=running
- `wf_37871eed-ee1`: B2 price update=running
- `wf_66a46537-1ed`: D specialist 한중엔시에스=done; E forensic 한중엔시에스=running; G generalist 한중엔시에스=running
- `wf_8e4ab4e3-16b`: D specialist 와이씨=done; E forensic 와이씨=running; G generalist 와이씨=running
- `wf_065961e6-e11`: D specialist 선익시스템=done; E forensic 선익시스템=running; G generalist 선익시스템=running
- `wf_96ebbf83-b0f`: D specialist 에이치브이엠=done; E forensic 에이치브이엠=running; G generalist 에이치브이엠=running
- `wf_b4e8daa5-88c`: D specialist 고영=done; E forensic 고영=running; G generalist 고영=running

## 다음 단계

1. 남은 종목의 전문가·일반 분석가·포렌식 결과 수집
2. 예비 정량 순위(pipeline.analyse) → 상위 종목 반대심문(I)·사실검증(V)·민감도(S)
3. 최종 심사(J): 전문가/일반 가중치, 반대심문 채택 범위 결정 → 최종 순위·민감도 재계산
4. 보고서(1~9부) 작성, 아티팩트 게시, 커밋
