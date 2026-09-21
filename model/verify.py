# -*- coding: utf-8 -*-
"""독립 검증 패스: 모형이 실제로 의도한 것을 계산하는지 재확인."""
import json, numpy as np, math
from priors import SECTOR_PRIOR_ANN, MARKET_PRIOR
import inputs as IN
from engine import CONF_SHRINK

R = json.load(open("results.json"))
S = R["stocks"]
fails = []
def chk(cond, msg):
    if not cond: fails.append(msg)

spec = {u[0]: u for u in IN.UNIVERSE}

print("검증 1) 시나리오 확률 합계 = 100%")
for u in IN.UNIVERSE:
    for T, h in u[10].items():
        chk(abs(sum(h[:3]) - 1.0) < 1e-12, f"  확률합 오류 {u[0]} T={T}: {sum(h[:3])}")
print("   OK" if not fails else "\n".join(fails))

print("\n검증 2) 몬테카를로 기대값이 축소 적용 후 시나리오 기대값과 일치하는가 (허용 ±0.6%p)")
worst = 0
for r in S:
    u = spec[r["name"]]
    sec, conf = u[3], u[6]
    w = CONF_SHRINK[conf]
    for T in (1, 3, 5):
        h = u[10][T]
        pri = math.log((1 + SECTOR_PRIOR_ANN.get(sec, MARKET_PRIOR)) ** T)
        sh = lambda m: math.exp((1 - w) * math.log(m) + w * pri)
        q = h[9]
        m_bear = q * 0.12 + (1 - q) * sh(h[3])          # 보고용 비관 = 존속/파산 혼합 평균
        cash_b = h[6] * (q * 0.25 + (1 - q))
        exp_M = (h[0] * (m_bear + cash_b) + h[1] * (sh(h[4]) + h[7]) + h[2] * (sh(h[5]) + h[8]))
        mc = 1 + r["m"][str(T)]["e_cum"]
        d = abs(exp_M - mc); worst = max(worst, d)
        chk(d < 0.006, f"  기대값 불일치 {r['name']} T={T}: 해석해 {exp_M:.4f} vs MC {mc:.4f} (차 {d:.4f})")
print(f"   최대 오차 {worst*100:.3f}%p → " + ("OK" if worst < 0.006 else "FAIL"))

print("\n검증 3) 실현 변동성이 목표 변동성과 일치하는가")
for r in S[:6] + S[-4:]:
    u = spec[r["name"]]; tgt = u[8] * (1.25 if u[9] else 1.0)
    got = [r["m"][str(T)]["vol_ann"] for T in (1,3,5)]
    print(f"   {r['name']:<12} 목표 {tgt:.2f} / 실현 1y {got[0]:.2f}  3y {got[1]:.2f}  5y {got[2]:.2f}")

print("\n검증 4) 누적 vs 연환산 환산 정합")
bad = 0
for r in S:
    for T in (1,3,5):
        m = r["m"][str(T)]
        chk(abs((1+m["e_cum"])**(1/T) - 1 - m["e_ann"]) < 1e-9, f"  환산오류 {r['name']} T={T}")
print("   OK" if not [f for f in fails if '환산' in f] else "FAIL")

print("\n검증 5) 백분위 단조성 (P10 < P50 < P90) 및 중앙값 정합")
for r in S:
    for T in (1,3,5):
        m = r["m"][str(T)]
        chk(m["p10"] < m["p50"] < m["p90"], f"  백분위 역전 {r['name']} T={T}")
        chk(abs(m["p50"] - m["med_cum"]) < 1e-9, f"  중앙값 불일치 {r['name']} T={T}")
print("   OK" if not [f for f in fails if '백분위' in f or '중앙값' in f] else "FAIL")

print("\n검증 6) Sortino 기간 불변성 — 동일 모수에서 1y/3y/5y가 √T로 부풀지 않는가")
for r in S[:3]:
    print(f"   {r['name']:<12} " + "  ".join(f"{T}y {r['m'][str(T)]['sortino']:.2f}" for T in (1,3,5)))

print("\n검증 7) 기대값 > 중앙값 인 종목 (우측꼬리 의존 = 투기적 구조)")
gap = sorted(S, key=lambda r: -(r["m"]["5"]["e_cum"] - r["m"]["5"]["med_cum"]))[:6]
for r in gap:
    print(f"   {r['name']:<12} 5년 기대 {r['m']['5']['e_cum']*100:6.1f}%  중앙값 {r['m']['5']['med_cum']*100:7.1f}%  괴리 {(r['m']['5']['e_cum']-r['m']['5']['med_cum'])*100:6.1f}%p")

print("\n검증 8) 종목 수")
print(f"   순위 산입 {len(S)} + 제외 {len(IN.EXCLUDED)} = {len(S)+len(IN.EXCLUDED)} (요청 26)")
chk(len(S) + len(IN.EXCLUDED) == 26, "  종목 수 불일치")

print("\n" + "="*70)
print("검증 실패 항목: " + ("없음" if not fails else f"{len(fails)}건"))
for f in fails[:12]: print(f)
