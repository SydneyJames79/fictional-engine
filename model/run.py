# -*- coding: utf-8 -*-
import numpy as np, json, sys
from engine import Stock, HorizonSpec, simulate, metrics, NSIM, SEED
from priors import SECTOR_LAMBDA, prior_log_mult
from rank import build_table
import inputs as IN

rng = np.random.default_rng(SEED)
# ONE shared macro factor per horizon -> sector co-movement & index-relative stats are consistent
Z = {T: rng.standard_normal(NSIM) for T in (1, 3, 5)}

def mk(h):
    return HorizonSpec(p_bear=h[0], p_base=h[1], p_bull=h[2],
                       m_bear_surv=h[3], m_base=h[4], m_bull=h[5],
                       cash_bear=h[6], cash_base=h[7], cash_bull=h[8],
                       ruin_given_bear=h[9])

# ---- benchmarks first (needed for excess return) ----
idx_mean = {}
for nm, (p0, hs, lam, sg) in IN.INDEX.items():
    st = Stock("IDX", nm, "-", "index", p0, lam, "H", sg)
    st.horizons = {T: mk(h) for T, h in hs.items()}
    idx_mean[nm] = {}
    for T in (1, 3, 5):
        M = simulate(st, T, np.log(1.07 ** T), rng, Z[T])
        idx_mean[nm][T] = metrics(M, T, IN.RF[T])

results = []
for (nm, code, mkt, sec, p0, pdate, conf, lam_o, floor, shorth, hs) in IN.UNIVERSE:
    lam = lam_o if lam_o is not None else SECTOR_LAMBDA[sec]
    st = Stock(code, nm, mkt, sec, p0, lam, conf, floor, shorth)
    st.horizons = {T: mk(h) for T, h in hs.items()}
    bench = "KOSPI" if mkt == "KOSPI" else "KOSDAQ"
    m = {}
    for T in (1, 3, 5):
        M = simulate(st, T, prior_log_mult(sec, T), rng, Z[T])
        m[T] = metrics(M, T, IN.RF[T], idx_mean[bench][T]["e_ann"])
    results.append(dict(name=nm, code=code, market=mkt, sector=sec, p0=p0,
                        pdate=pdate, conf=conf, lam=lam, bench=bench, m=m,
                        why={}, drift=""))

for T in (1, 3, 5):
    build_table(results, T)

json.dump({"stocks": results, "index": {k: {str(t): v for t, v in d.items()} for k, d in idx_mean.items()}},
          open("results.json", "w"), ensure_ascii=False, default=float)

# ---- console summary ----
def pc(x): return f"{x*100:6.1f}%"
print(f"{'='*118}\n벤치마크 (공통 거시인자 공유)")
for k, d in idx_mean.items():
    print(f"  {k:7s} " + "  ".join(f"T={T}: 기대누적 {pc(d[T]['e_cum'])} 연환산 {pc(d[T]['e_ann'])} Sortino {d[T]['sortino']:5.2f}" for T in (1,3,5)))

for T in (1, 3, 5):
    print(f"\n{'='*118}\n[{T}년] 균형형 종합순위")
    print(f"{'균형':>3}{'기대':>4}{'위험':>4}  {'종목':<14}{'기대누적':>9}{'연환산':>8}{'중앙값':>8}{'P10':>8}{'P90':>8}{'손실%':>7}{'-30%':>7}{'Sortino':>8}{'CVaR10':>9}{'초과':>8} 신뢰")
    for r in sorted(results, key=lambda r: r["score"][T]["rank_bal"]):
        s, mm = r["score"][T], r["m"][T]
        print(f"{s['rank_bal']:>3}{s['rank_ret']:>4}{s['rank_risk']:>4}  {r['name']:<14}"
              f"{pc(mm['e_cum'])}{pc(mm['e_ann'])}{pc(mm['med_cum'])}{pc(mm['p10'])}{pc(mm['p90'])}"
              f"{pc(mm['p_loss'])}{pc(mm['p_loss30'])}{mm['sortino']:>8.2f}{pc(mm['cvar10'])}{pc(mm['excess_ann'])}  {r['conf']}")
