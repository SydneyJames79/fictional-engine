# 한국 주식 26종목 1·3·5년 TSR 전망 — 산출물 안내

- `report.md` — 최종 보고서(9부 + 부록 A~E). 분석 기준일 2026-10-22 15:40 KST, 작성·확정 2026-10-29.
- `STATE.json` — 파이프라인 진행 상태와 재개 메모.
- `work/` — 재현용 스크립트. 실행 순서: `collect_wf2.py` → `build_trees.py --final` → `engine.py engine_final` → `report_tables.py` → `price_sens.py` → `report_build.py`. 에이전트 워크플로 정의는 `wf1b_data.js`, `wf1c_price_refresh.js`, `wf1e_macro_reconcile.js`, `wf2_analysis.js`, `wf3_calibrate_bear.js`, `wf4_verify.js`.
- `data/wf1/` — 종목별 데이터 검증 결과(26개 JSON, 출처·기준일 포함)와 공통 거시 시나리오(`macro_common.json`).
- `data/wf2/` — 종목별 산업 전문가·독립 분석가·포렌식·정량 위험 보고서와 종합(`synth/`) 시나리오 트리.
- `data/wf3/` — 산업군별 베이스레이트 보정(`calibration.json`), 반대심문(`bear/`), 최종 심사(`judge/`).
- `data/wf4/` — 보조 문안 작성 에이전트 출력(`writer.json`).
- `data/engine_final/` — 최종 시나리오 트리(`trees.json`), 위험 모수(`risk.json`), 몬테카를로 결과(`results.json`), 순위표(`tables.json`/`tables.md`), 빌드 로그.
- `data/engine_sens/` — 기준가 날짜 통일 민감도(8-2) 결과.

주의: 모든 수치는 2026-10-22 자료 스냅샷 기준이며, 투자 비중이나 매매 지시를 담지 않는다. 자료 접근 제약(KRX·DART 직접 조회 불가, 검색 기반 수집)은 보고서 머리말과 부록 A에 적혀 있다.
