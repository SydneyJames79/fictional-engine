# Seojin System (178320) generalist valuation arithmetic. Units: 억원 unless noted.
price=34000; shares=63.72e6; mcap=21666; net_debt=12876; cb=606
ev=mcap+net_debt+cb
print("EV(억)=",ev, "EV/Sales 2026E(16000)=",round(ev/16000,2))
# ---- Base forecasts
yrs=[2026,2027,2028,2029,2030,2031]
rev={2026:16000,2027:20500,2028:23500,2029:24500,2030:26500,2031:29000}
opm={2026:0.028,2027:0.080,2028:0.085,2029:0.075,2030:0.075,2031:0.075}
nonop={2026:-800,2027:-700,2028:-600,2029:-550,2030:-480,2031:-400}
da_rate=0.047
capex={2026:2500,2027:1600,2028:1250,2029:1300,2030:1400,2031:1500}
nwc_rate=0.12
tax=0.22
dil_shares={2026:63.72e6,2027:65.5e6,2028:67.0e6,2029:68.0e6,2030:68.5e6,2031:69.0e6}
prev_rev=10663
print("year rev op ni eps fcf")
fcff={}
for y in yrs:
    op=rev[y]*opm[y]; pretax=op+nonop[y]
    ni=pretax*(1-tax) if pretax>0 else pretax
    da=rev[y]*da_rate; dnwc=(rev[y]-prev_rev)*nwc_rate
    nopat=op*(1-tax) if op>0 else op
    f=nopat+da-capex[y]-dnwc  # FCFF
    fcfe=ni+da-capex[y]-dnwc   # FCF to equity (approx, pre net borrowing)
    fcff[y]=f
    print(y, round(rev[y]), round(op), round(ni), round(ni*1e8/dil_shares[y]), "FCFF",round(f),"FCFE",round(fcfe), "EBITDA",round(op+da))
    prev_rev=rev[y]
# ---- DCF
wacc=0.095; g=0.025
pv=0
# 4Q26 remaining FCFF ~ -600 (0.2y)
pv+= -600/(1+wacc)**0.2
for i,y in enumerate(yrs[1:]):
    t=1.2+i
    pv+=fcff[y]/(1+wacc)**t
tv=fcff[2031]*(1+g)/(wacc-g)
pv_tv=tv/(1+wacc)**5.2
ev_dcf=pv+pv_tv
eq=ev_dcf-net_debt-cb
print("DCF base: PV explicit",round(pv),"PV TV",round(pv_tv),"EV",round(ev_dcf),"Equity",round(eq),"per share(dil 65.5M)",round(eq*1e8/65.5e6))
# DCF sensitivity: OPM +2pp on 2028-31, wacc 9%
for opm_add,w in [(0.0,0.09),(0.02,0.095),(0.02,0.09),(0.035,0.09)]:
    pv2=-600/(1+w)**0.2; prev=10663
    for i,y in enumerate(yrs):
        o=rev[y]*(opm[y]+ (opm_add if y>=2027 else 0))
        da=rev[y]*da_rate; dnwc=(rev[y]-prev)*nwc_rate; prev=rev[y]
        f=o*(1-tax)+da-capex[y]-dnwc
        if y>2026: pv2+=f/(1+w)**(1.2+i-1)
        last=f
    tv2=last*(1+g)/(w-g)/(1+w)**5.2
    e2=pv2+tv2-net_debt-cb
    print(f"DCF sens opm+{opm_add} wacc {w}: EV {round(pv2+tv2)} equity {round(e2)} /sh {round(e2*1e8/65.5e6)}")
# ---- Reverse DCF: find constant OPM (2027-31) s.t. equity = mcap, given base revenue path & wacc 9.5
def eq_for(opm_c, rev_mult=1.0, w=0.095):
    pv2=-600/(1+w)**0.2; prev=10663
    for i,y in enumerate(yrs):
        r=rev[y]*(rev_mult**(max(0,y-2026)) if y>2026 else 1)
        o=r*(opm_c if y>=2027 else opm[2026])
        da=r*da_rate; dnwc=(r-prev)*nwc_rate; prev=r
        f=o*(1-tax)+da-capex[y]*(r/rev[y])-dnwc
        if y>2026: pv2+=f/(1+w)**(1.2+i-1)
        last=f
    tv2=last*(1+g)/(w-g)/(1+w)**5.2
    return pv2+tv2-net_debt-cb, r
lo,hi=0.05,0.30
for _ in range(60):
    m=(lo+hi)/2
    e,_r=eq_for(m)
    if e<mcap: lo=m
    else: hi=m
print("Reverse DCF: required constant OPM 2027-31 on base rev path (2031 rev 29000) =",round(m*100,1),"%")
# with faster revenue growth: 2031 rev 40000 (CAGR ~20% from 2026)
rev_fast={2026:16000,2027:21500,2028:27000,2029:32000,2030:36000,2031:40000}
def eq_for2(opm_c,w=0.095):
    pv2=-600/(1+w)**0.2; prev=10663
    for i,y in enumerate(yrs):
        r=rev_fast[y]; o=r*(opm_c if y>=2027 else opm[2026])
        da=r*da_rate; dnwc=(r-prev)*nwc_rate; prev=r
        cap= capex[y] if y<=2027 else r*0.055
        f=o*(1-tax)+da-cap-dnwc
        if y>2026: pv2+=f/(1+w)**(1.2+i-1)
        last=f
    tv2=last*(1+g)/(w-g)/(1+w)**5.2
    return pv2+tv2-net_debt-cb
lo,hi=0.05,0.30
for _ in range(60):
    m=(lo+hi)/2
    if eq_for2(m)<mcap: lo=m
    else: hi=m
print("Reverse DCF: required OPM with 2031 rev 40000 (CAGR 20%) =",round(m*100,1),"%; 2031 NI approx",round(40000*m*0.78-300))
# Implied multiples
print("Current P/E on base 2027E EPS, 2028E EPS:", round(price/ (20500*0.08-700)/0.78*65.5e6/1e8,1) if False else "")
ni27=(20500*0.08-700)*0.78; eps27=ni27*1e8/65.5e6
ni28=(23500*0.085-600)*0.78; eps28=ni28*1e8/67e6
print("Base EPS27",round(eps27),"PER",round(price/eps27,1),"EPS28",round(eps28),"PER",round(price/eps28,1))
print("PBR on BPS 13127:",round(price/13127,2))
# ---- Scenario TSR
sc={
 "1Y":[("bear",25,16000,0,10),("base",50,30000,0,1),("bull",25,52000,0,0)],
 "3Y":[("bear",25,10000,0,20),("base",50,26000,0,5),("bull",25,60000,300,3)],
 "5Y":[("bear",25,8000,0,25),("base",50,28000,300,8),("bull",25,78000,1500,3)],
}
for h,rows in sc.items():
    ev_=0
    for n,p,endp,cash,dil in rows:
        tsr=(endp+cash)/price-1
        ev_+=p/100*tsr
        print(h,n,p,endp,cash,dil,"TSR%",round(tsr*100,1))
    print(h,"prob-weighted TSR%",round(ev_*100,1))
# ---- valuation methods
mid_eps=(eps27+eps28+ (24500*0.075-550)*0.78*1e8/68e6)/3
print("mid-cycle EPS avg 27-29:",round(mid_eps),"x14=",round(mid_eps*14))
ebitda28=23500*0.085+23500*da_rate
nd27=net_debt-( (20500*0.08*0.78+20500*da_rate-1600-(20500-16000)*0.12) ) + 600  # net debt end-2027 approx (FCFF minus interest)
print("EBITDA28",round(ebitda28),"net debt end-27 approx",round(nd27))
for mult in [8,10,12]:
    e=mult*ebitda28-nd27-cb
    print("EV/EBITDA",mult,"x -> equity",round(e),"/sh(67M)",round(e*1e8/67e6),"disc 1y@11%",round(e*1e8/67e6/1.11))
