P0=5720; shares_total=29764103; treasury=287343; sh=shares_total-treasury
cap=P0*shares_total/1e8
print("cap(억)",round(cap,1),"outstanding ex-treasury",sh)
net_cash=300  # inferred: FY25 financial income 10.5억 / ~3.5% ≈ 300억; equity 432 / debt 11 at FY24
EV=cap-net_cash; print("EV",round(EV,1), "EV/S FY25",round(EV/70.3,1))

def dcf(fcfs, wacc, g, tail_growth, tail_years):
    pv=0; t=0
    for f in fcfs:
        t+=1; pv+=f/(1+wacc)**t
    last=fcfs[-1]
    for i in range(tail_years):
        t+=1; last*=(1+tail_growth); pv+=last/(1+wacc)**t
    tv=last*(1+g)/(wacc-g); pv_tv=tv/(1+wacc)**t
    return pv, pv_tv

# base FCF 2027..2031
base=[12,26,42,56,70]; bull=[25,70,130,180,220]; bear=[2,5,8,10,10]
for name,f,tg in [("base",base,0.06),("bull",bull,0.08),("bear",bear,0.0)]:
    for w in (0.12,0.105):
        pv,pvtv=dcf(f,w,0.025,tg,5)
        ev=pv+pvtv; eq=ev+net_cash
        print(name,w,"PV",round(pv),"PVTV",round(pvtv),"EV",round(ev),"Eq",round(eq),"per share",round(eq*1e8/sh))

# reverse DCF: what FCF2032 is needed at WACC 12%, interim ramp
for w in (0.12,0.10):
    ramp=[20,50,90,130,170]
    pv=sum(f/(1+w)**(i+1) for i,f in enumerate(ramp))
    tv_needed=(EV-pv)*(1+w)**5
    fcf2032=tv_needed*(w-0.025)
    nopat=fcf2032/0.8; op=nopat/0.78; rev=op/0.40
    print("reverse",w,"PV interim",round(pv),"TV needed",round(tv_needed),"FCF2032",round(fcf2032),"OP",round(op),"Rev@40%OPM",round(rev),"CAGR25-31",round(((rev/70.3)**(1/6)-1)*100,1))

# EPS
ni={2026:12,2027:23,2028:38,2029:52,2031:80}; shs={2026:29.6,2027:29.8,2028:30.0,2029:30.2,2031:30.5}
for y in ni: print(y,"EPS",round(ni[y]*1e8/(shs[y]*1e6)))

# scenarios TSR
sc={ "1y":[("bear",30,3400,0),("base",45,5200,0),("bull",25,8400,0)],
     "3y":[("bear",30,2200,0),("base",45,5700,100),("bull",25,12000,200)],
     "5y":[("bear",30,2300,50),("base",45,6500,360),("bull",25,14000,800)]}
for h,lst in sc.items():
    e=0
    for n,p,px,cash in lst:
        tsr=((px+cash)/P0-1)*100; e+=p*tsr/100
        print(h,n,p,px,cash,"TSR",round(tsr,1))
    print(h,"expected",round(e,1))

# valuation weighting
vm=[(3200,35),(4000,30),(4440,20),(3200,15)]
print("weighted FV",round(sum(v*w for v,w in vm)/100))
# comps: 2027E sales 125 x 8 + cash
print("comps",round((125*8+310)*1e8/sh))
# normalized PE: 2028E EPS 127 x 30 discounted 1.5y @12%
print("normPE",round(127*30/1.12**1.5))
# multiple checks
print("P/E on 2029E NI 52:",round(cap/52,1), "needed NI for 20x:",round(cap/20,1))
