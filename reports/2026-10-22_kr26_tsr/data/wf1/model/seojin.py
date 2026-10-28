# 서진시스템 모델 (단위: 억원, 주가 원)
price=34000; shares=63.72  # 백만주
mcap=price*shares/100  # 억원
nd0=12876
ev0=mcap+nd0
print(f"mcap={mcap:.0f} EV={ev0:.0f}")

# 세그먼트 매출 전망 (억원)
seg = {
 2026:{'ESS':5500,'SEMI':6500,'SOFC':150,'TEL':1250,'EV':800,'OTH':1800},
 2027:{'ESS':8000,'SEMI':7300,'SOFC':900,'TEL':1250,'EV':900,'OTH':1850},
 2028:{'ESS':9000,'SEMI':7000,'SOFC':1300,'TEL':1250,'EV':1000,'OTH':1900},
 2029:{'ESS':9800,'SEMI':7700,'SOFC':1700,'TEL':1200,'EV':1100,'OTH':2000},
 2030:{'ESS':10400,'SEMI':8200,'SOFC':2000,'TEL':1150,'EV':1200,'OTH':2050},
 2031:{'ESS':11000,'SEMI':8500,'SOFC':2300,'TEL':1100,'EV':1300,'OTH':2100},
}
opm={2026:None,2027:0.080,2028:0.085,2029:0.085,2030:0.082,2031:0.080}
da={2026:900,2027:950,2028:1000,2029:1000,2030:1030,2031:1050}
capex={2026:1900,2027:1100,2028:900,2029:900,2030:950,2031:1000}
dwc={2026:-500,2027:700,2028:250,2029:350,2030:250,2031:250}  # +는 운전자본 증가(현금유출)
tax=0.20; r_debt=0.053
sh={2026:63.72,2027:65.55,2028:65.6,2029:66.0,2030:66.3,2031:66.5}

nd=nd0
rows={}
for y in range(2026,2032):
    rev=sum(seg[y].values())
    if y==2026:
        op_1h=-300; op_2h=780; op=op_1h+op_2h
        ni_1h=-600
        # 2H interest on ~13,000 avg for half year
        intr_2h=13200*r_debt/2
        ni_2h=(op_2h-intr_2h)*(1-tax)
        ni=ni_1h+ni_2h
        # 2H FCF only (nd0 is end-2Q26)
        fcf_2h=ni_2h+da[y]/2-capex[y]*0.55-(-500)  # WC 500 release in 2H
        fcf=fcf_2h
        nd_end=nd-fcf_2h
    else:
        op=rev*opm[y]
        nd_avg=nd  # approx beginning
        intr=nd_avg*r_debt
        ni=(op-intr)*(1-tax)
        fcf=ni+da[y]-capex[y]-dwc[y]
        nd_end=nd-fcf
    nopat=op*(1-tax)
    fcff=nopat+da[y]-capex[y]-dwc[y]
    eps=ni*1e4/ (sh[y]*1e6) *1e4/1e4  # 억원->원: ni*1e8 / (sh*1e6) = ni*100/sh
    eps=ni*100/sh[y]
    rows[y]=dict(rev=rev,op=op,opm=op/rev,ni=ni,eps=eps,fcf=fcf,fcff=fcff,nd_end=nd_end,ebitda=op+da[y])
    nd=nd_end
    print(f"{y}: rev={rev:.0f} op={op:.0f} opm={op/rev*100:.1f}% ni={ni:.0f} eps={eps:.0f} fcf={fcf:.0f} fcff={fcff:.0f} nd_end={nd_end:.0f} ebitda={op+da[y]:.0f}")

# DCF FCFF
wacc=0.09; g=0.02
pv=0
for i,y in enumerate(range(2027,2032),start=1):
    pv+=rows[y]['fcff']/(1+wacc)**(i+0.2)
tv=rows[2031]['fcff']*(1+g)/(wacc-g)
pv_tv=tv/(1+wacc)**(5.2)
ev=pv+pv_tv
# use end-2026E net debt
nd_use=rows[2026]['nd_end']
eq=ev-nd_use
print(f"DCF: PV={pv:.0f} TV={tv:.0f} PVTV={pv_tv:.0f} EV={ev:.0f} nd={nd_use:.0f} eq={eq:.0f} per_share={eq*1e4/65.55/1e2:.0f}")
for w in (0.085,0.09,0.10):
  for gg in (0.02,0.03):
    pv=sum(rows[y]['fcff']/(1+w)**(i+0.2) for i,y in enumerate(range(2027,2032),start=1))
    tv=rows[2031]['fcff']*(1+gg)/(w-gg); pvtv=tv/(1+w)**5.2
    print(f" wacc={w} g={gg}: EV={pv+pvtv:.0f} eq/sh={(pv+pvtv-nd_use)*100/65.55:.0f}")

# Reverse DCF: what steady FCFF needed to justify EV0 at wacc 9%, g 2%
print(f"Reverse: FCFF perpetuity needed = {ev0*(wacc-g):.0f}")
# ramp version: FCFF grows linearly from 600 (2027) to X (2031), TV on X
import numpy as np
def ev_for_X(X):
    f=np.linspace(600,X,5)
    pv=sum(f[i]/(1+wacc)**(i+1.2) for i in range(5))
    tv=X*(1+g)/(wacc-g)/(1+wacc)**5.2
    return pv+tv
lo,hi=500,10000
for _ in range(60):
    mid=(lo+hi)/2
    if ev_for_X(mid)<ev0: lo=mid
    else: hi=mid
X=lo
print(f"Reverse DCF: 2031 FCFF needed={X:.0f}; implied EBIT (FCFF/NOPAT ratio ~0.9, tax 20%) = {X/0.9/0.8:.0f}")
# multiples
for y in (2027,2028,2029):
    r=rows[y]
    print(f"{y}: PER={price/r['eps']:.1f}x  EV/EBITDA={(mcap+r['nd_end'])/r['ebitda']:.1f}x (nd end)")

# ---- 시나리오 TSR 검산 ----
print("\n--- Scenario TSR check ---")
sc = {
 '1y':[('bear',25,15000,0,12.0),('base',50,30000,0,2.9),('bull',25,48000,0,2.9)],
 '3y':[('bear',25,12000,0,15.0),('base',50,31000,0,3.5),('bull',25,58000,200,3.0)],
 '5y':[('bear',25,10000,0,18.0),('base',50,33000,300,5.0),('bull',25,62000,800,3.0)],
}
for h,lst in sc.items():
    ew=0
    for n,p,endp,cash,dil in lst:
        tsr=(endp+cash)/price-1
        ew+=p/100*tsr
        print(f"{h} {n}: p={p} end={endp} cash={cash} dil={dil} TSR={tsr*100:.1f}%")
    print(f"{h} prob-weighted TSR = {ew*100:.1f}%")

# ---- 정상화이익 멀티플 ----
norm_rev=20000; norm_opm=0.075; norm_op=norm_rev*norm_opm; norm_int=650
norm_ni=(norm_op-norm_int)*0.8; norm_eps=norm_ni*100/65.55
print(f"\nNormalized: OP={norm_op:.0f} NI={norm_ni:.0f} EPS={norm_eps:.0f}")
for per in (12,15,18,20): print(f" PER {per}x -> {norm_eps*per:.0f}")
# EV/EBITDA on 2028E
ebitda28=2823; nd28=11950
for m in (8,9,10,12):
    eq=m*ebitda28-nd28; print(f" EV/EBITDA {m}x on 2028E -> eq={eq:.0f} -> {eq*100/65.6:.0f}/sh")
# PER on 2028E EPS discounted 1y at 11.7%
eps28=1401
for per in (15,18,20,22): print(f" PER {per}x on 2028E EPS {eps28:.0f} disc 1y -> {eps28*per/1.117:.0f}")
# implied: what 2028 OP needed for PER 15x at 34000 with 65.6M shares
ni_need=34000*65.6/100/15; op_need=ni_need/0.8+650
print(f"Implied for PER15x: NI={ni_need:.0f} OP={op_need:.0f}; at OPM 9% rev={op_need/0.09:.0f}; at OPM 12% rev={op_need/0.12:.0f}")
ni_need20=34000*65.6/100/20; op_need20=ni_need20/0.8+650
print(f"Implied for PER20x: NI={ni_need20:.0f} OP={op_need20:.0f}; at OPM 9% rev={op_need20/0.09:.0f}")
# consensus TP 68,500 implied
ni_c=68500*65.6/100/18; print(f"Consensus TP 68500 at PER18x -> NI {ni_c:.0f}, OP {(ni_c/0.8+650):.0f}")
