P0=3250
shares=30.700933  # M
mcap=P0*shares/1e4  # 억원
print("mcap 억원", round(mcap,1))
# net debt assumption: CB 150억 debt, cash est ~90억 (memory-based assumption) -> net debt ~60
nd=60
EV=mcap+nd
print("EV 억원", round(EV,1))

# Scenario TSR check
scen={
 "1y":[("bear",30,1500),("base",50,2700),("bull",20,6000)],
 "3y":[("bear",35,800),("base",45,2500),("bull",20,5200)],
 "5y":[("bear",40,500),("base",40,2400),("bull",20,8500)],
}
for h,l in scen.items():
    ew=0
    for n,p,px in l:
        tsr=(px+0)/P0-1
        ew+=p/100*tsr
        print(h,n,p,px,"TSR %.1f%%"%(tsr*100))
    print(h,"prob-weighted TSR %.1f%%"%(ew*100), "sum prob", sum(p for _,p,_ in l))

# Reverse DCF: what 2031 FCF justifies EV at r=15%, g=3%
r=0.15; g=0.03
fcf_path={2026:-72,2027:-48,2028:-22,2029:-3,2030:12}
pv_int=sum(v/(1+r)**(y-2025.8) for y,v in fcf_path.items())
print("PV interim FCF", round(pv_int,1))
tv_pv_needed=EV-pv_int
tv_2031=tv_pv_needed*(1+r)**(2031-2025.8)
fcf2031=tv_2031*(r-g)/(1+g)
print("needed TV(2031)",round(tv_2031),"needed FCF2031",round(fcf2031))
for opm in (0.15,0.20,0.25):
    op=fcf2031/0.85  # FCF≈NI≈OP*0.85 (loss carryforward tax shield partial)
    rev=op/opm
    cagr=(rev/87.46)**(1/6)-1
    print("OPM %.0f%% -> OP %.0f, rev %.0f, CAGR25-31 %.1f%%"%(opm*100,op,rev,cagr*100))
# Exit multiple approach: PER 20x on 2031 NI, discount 15%, 40M shares
ni_needed=mcap*(1+r)**5/20
print("NI2031 needed @PER20:",round(ni_needed),"-> rev @12% NPM",round(ni_needed/0.12), "CAGR", round(((ni_needed/0.12)/87.46)**(1/6)*100-100,1))

# Valuation methods
# M1: scenario-weighted rNPV on 3y end prices, discount 15%
e3=0.35*800+0.45*2500+0.20*5200
print("E[P3y]",e3,"PV",round(e3/1.15**3))
e5=0.40*500+0.40*2400+0.20*8500
print("E[P5y]",e5,"PV",round(e5/1.15**5))
# M2: EV/Sales 2027E 130억 at 5x-7x, net debt 60, shares 32M (post SO), 
for m in (5,7):
    eq=m*130-60
    print("EV/S",m,"x -> equity",eq,"per share",round(eq/32*1e4/1e4*1e4/1e4*10000/10000*1e4/1e4*10000/1e4*1e4/1e4*1,0) if False else round(eq*1e4/32e2,0))
# per share = equity(억원)*1e8 / shares(M*1e6) = equity*100/sharesM
for m in (5,6,7):
    eq=m*130-60
    print("EV/S",m,"x -> equity",eq,"억 -> per share",round(eq*100/32))
# M3: normalized earnings PER: NI 27억 (normalized 2030-31), PER 22x, discounted 4y @15%, shares 40M
val=27*22
print("normalized equity",val,"per share today",round(val*100/40/1.15**4))
# M4 bull-only option check
