price=48400; shares_out=82.3e6; treasury=0.9e6; sh=shares_out-treasury
mcap=price*shares_out/1e8
net_cash=2000  # memory_unverified assumption, 억원
ev=mcap-net_cash
print("mcap(억)",round(mcap,1),"EV(억)",round(ev,1),"shares ex-treasury(M)",sh/1e6)

# --- DCF (FCFF), 억원 ---
wacc=0.11; g=0.025
fcf={2026:850,2027:1100,2028:1150,2029:1250,2030:1380,2031:1480}
for y in range(2032,2036): fcf[y]=round(fcf[y-1]*1.05)
# valuation date ~ end Oct 2026: discount 2026 FCF partial (0.2 yr remaining) ignore; discount from 2027 at mid-year convention
pv=0
for y in range(2027,2036):
    t=(y-2026)-0.5+0.2  # approx from Oct 2026
    pv+=fcf[y]/(1+wacc)**t
tv=fcf[2035]*(1+g)/(wacc-g)
pv_tv=tv/(1+wacc)**((2035-2026)+0.2)
eq=pv+pv_tv+net_cash
print("DCF: PV explicit",round(pv),"PV TV",round(pv_tv),"TV share",round(pv_tv/(pv+pv_tv)*100,1),"% equity",round(eq),"per share",round(eq/sh*1e8))

# sensitivity
for w in (0.10,0.11,0.12):
    for gg in (0.02,0.025,0.03):
        pv=0
        for y in range(2027,2036):
            t=(y-2026)-0.5+0.2; pv+=fcf[y]/(1+w)**t
        tv=fcf[2035]*(1+gg)/(w-gg); pv_tv=tv/(1+w)**(9.2)
        print(f"  WACC {w:.2f} g {gg:.3f} -> {round((pv+pv_tv+net_cash)/sh*1e8)}")

# --- Reverse DCF: constant FCF growth 2027-2035 needed to hit EV ---
def ev_for(gr):
    f=850; pv=0
    for y in range(2027,2036):
        f=f*(1+gr); t=(y-2026)-0.5+0.2; pv+=f/(1+wacc)**t
    tv=f*(1+g)/(wacc-g); return pv+tv/(1+wacc)**9.2
lo,hi=0.0,0.6
for _ in range(60):
    mid=(lo+hi)/2
    if ev_for(mid)<ev: lo=mid
    else: hi=mid
print("Reverse DCF implied FCF CAGR 2026->2035:",round(mid*100,1),"% ; FCF 2031 =",round(850*(1+mid)**5),"FCF 2035 =",round(850*(1+mid)**9))

# implied 2028 NI at exit PER
for per in (25,30,35):
    req_cap=mcap*(1.11**2)
    ni=req_cap/per; op=ni/0.8-110; rev=op/0.55
    print(f"  exit PER {per}x 2028: req NI {round(ni)} OP {round(op)} rev {round(rev)} (CAGR vs 2025 rev 1730: {round(((rev/1730)**(1/3)-1)*100,1)}%)")

# --- forecasts EPS ---
shares={2026:81.4,2027:80.9,2028:80.4,2029:79.9,2031:78.9}
ni={2026:1000,2027:1250,2028:1170,2029:1350,2031:1600}
for y in ni: print(y,"EPS",round(ni[y]/shares[y]*100))

# --- normalized multiple ---
norm_ni=(1000+1250+1170+1350)/4
print("norm NI",norm_ni,"x27 + cash ->",round((norm_ni*27+net_cash)/sh*1e8))
print("hist band 33x * 2027E EPS 1545 ->",33*1545)
# scenario-weighted PV (3y)
w3=0.25*22000+0.5*52000+0.25*83000; print("3y weighted end",w3,"+div 1750 PV@11%:",round((w3+1750)/1.11**3))

# --- TSR check ---
sc={('1y','bear'):(29000,500),('1y','base'):(47000,500),('1y','bull'):(68000,500),
    ('3y','bear'):(22000,1300),('3y','base'):(52000,1750),('3y','bull'):(83000,2300),
    ('5y','bear'):(20000,2200),('5y','base'):(54000,3350),('5y','bull'):(89600,4500)}
for k,(p,c) in sc.items(): print(k,p,c,"TSR",round(((p+c)/price-1)*100,1))
for h in ('1y','3y','5y'):
    w=0.25*((sc[(h,'bear')][0]+sc[(h,'bear')][1])/price-1)+0.5*((sc[(h,'base')][0]+sc[(h,'base')][1])/price-1)+0.25*((sc[(h,'bull')][0]+sc[(h,'bull')][1])/price-1)
    print(h,"prob-weighted TSR",round(w*100,1))
# fair value weighted
dcf=None
