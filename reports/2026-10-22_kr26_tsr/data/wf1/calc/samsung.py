# All amounts in 조원 unless noted; per-share in KRW
P = 223500.0
sh_common = 5_846_278_608
sh_pref   = 802_371_203
sh_total  = sh_common + sh_pref
sh_eps    = 6.572e9   # 2Q26 EPS 10,849 on NI(attr) 71.3조 -> implied share base
mcap_common = P*sh_common/1e12
mcap_pref   = 174300*sh_pref/1e12
mcap = mcap_common+mcap_pref
print(f"shares total {sh_total:,}  EPS-base {sh_eps:.3e}")
print(f"mcap common {mcap_common:.1f}, pref {mcap_pref:.1f}, total {mcap:.1f} 조")

# 2Q26 check: NI attr 71.3조 / 10,849 won
print("implied shares from 2Q EPS:", 71.3e12/10849/1e9, "bn")

# Forecasts (base)  year: rev, op, ni, shares(bn), fcf
F = {
 2026:(710.0,370.0,296.0,6.57,245.0),
 2027:(790.0,450.0,360.0,6.45,300.0),
 2028:(700.0,230.0,185.0,6.35,175.0),
 2029:(750.0,280.0,225.0,6.28,190.0),
 2030:(800.0,310.0,248.0,6.22,200.0),
 2031:(820.0,250.0,200.0,6.15,175.0),
}
for y,(r,o,n,s,f) in F.items():
    print(y, "OPM %.1f%%"%(o/r*100), "NI/OP %.2f"%(n/o), "EPS %.0f"%(n*0.993e12/(s*1e9)), "FCF", f)

# cumulative 1~3Q26
print("1-3Q26 OP", 57.2+89.5+107.4, "Rev", 133.9+171.5+195)

# DCF
def dcf(wacc, g, term_fcf, netcash=210.0):
    t0 = 0.2  # from 2026-10-22 to 2026-12-31
    pv = 70.0/(1+wacc)**t0  # 4Q26 FCF
    for i,y in enumerate(range(2027,2032)):
        pv += F[y][4]/(1+wacc)**(t0+1+i)
    tv = term_fcf*(1+g)/(wacc-g)
    pv_tv = tv/(1+wacc)**(t0+5)
    ev = pv+pv_tv
    eq = ev+netcash
    return pv, pv_tv, ev, eq, eq*1e12/sh_eps
for w,g,tf in [(0.095,0.02,165),(0.10,0.02,140),(0.11,0.01,120),(0.095,0.02,120),(0.10,0.015,150)]:
    pv,pvtv,ev,eq,ps = dcf(w,g,tf)
    print(f"WACC {w:.3f} g {g:.3f} TFCF {tf}: PV_exp {pv:.0f} PV_TV {pvtv:.0f} EV {ev:.0f} EQ {eq:.0f} per-share {ps:,.0f}")

# Reverse DCF: what steady-state FCF does mcap imply?
netcash = 160.0  # cash 190 - 30 declared div (debt N/A, conservative)
ev_mkt = mcap - netcash
for w,g in [(0.095,0.02),(0.10,0.02),(0.09,0.025)]:
    ss = ev_mkt*(w-g)/(1+g)
    print(f"Reverse (perpetuity) WACC {w} g {g}: EV {ev_mkt:.0f} -> steady FCF {ss:.0f}조, NI~{ss/0.9:.0f}, OP~{ss/0.9/0.8:.0f}")
# Reverse with 2027-2028 explicit accepted
w,g=0.095,0.02
pv_exp = 70/(1+w)**0.2 + 300/(1+w)**1.2 + 175/(1+w)**2.2
rem = ev_mkt - pv_exp
tv_2028 = rem*(1+w)**2.2
fcf_term = tv_2028*(w-g)/(1+g)
print(f"explicit 4Q26-2028 PV {pv_exp:.0f}; remaining EV {rem:.0f}; TV@2028 {tv_2028:.0f}; implied FCF from 2029 {fcf_term:.0f}, OP~{fcf_term/0.9/0.8:.0f}")

# Multiples
for lbl,ni in [("2026E",296),("2027E",360),("normalized",160)]:
    print(lbl, "P/E", round(mcap/ni,2))

# PBR
eq_2q26 = 553.0
bps_2q26 = eq_2q26*1e12/sh_eps
eq_26 = eq_2q26 + 86+94 - 30 - 15 - 2.5
eq_27 = eq_26 + 360 - 70 - 100
print("BPS 2Q26 %.0f, end26 %.0f, end27 %.0f"%(bps_2q26, eq_26*1e12/6.57e9, eq_27*1e12/6.45e9))
bps27 = eq_27*1e12/6.45e9
for pb in [1.4,1.6,1.8,2.0]:
    print(" PBR", pb, "-> end27", round(bps27*pb), "disc 1y", round(bps27*pb/1.095))

# normalized PER
norm_eps = 160e12*0.993/6.4e9
print("norm EPS", round(norm_eps))
for pe in [8,10,12]:
    print(" PER", pe, round(norm_eps*pe), "+cash credit 30000 ->", round(norm_eps*pe+30000))

# Cash per share
print("30조/6.57bn =", 30e12/6.572e9, "; 70조 =", 70e12/6.572e9, "; 60조=",60e12/6.572e9,"; 80조=",80e12/6.572e9)
print("current net cash/share (210조)", 210e12/6.572e9)

# Scenarios
S = {
 "1Y":[("bear",25,150000,14000),("base",50,235000,16000),("bull",25,350000,17500)],
 "3Y":[("bear",25,135000,32000),("base",50,270000,47000),("bull",25,400000,65000)],
 "5Y":[("bear",25,115000,40000),("base",50,290000,75000),("bull",25,450000,115000)],
}
for h,rows in S.items():
    ew=0
    for n,p,px,cash in rows:
        tsr=(px+cash)/P-1
        ew+=p/100*tsr
        print(h,n,p,px,cash,"TSR %.1f%%"%(tsr*100))
    print(h,"prob-weighted TSR %.1f%%"%(ew*100))
# weighted fair value
print("weighted FV", 0.40*320000+0.35*280000+0.25*225000)
