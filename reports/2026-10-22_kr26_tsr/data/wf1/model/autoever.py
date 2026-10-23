# Hyundai AutoEver generalist model (units: 억원 unless noted; EPS in KRW)
P = 336000; SH = 27423982; MCAP = P*SH/1e8
print("mcap(억)", round(MCAP))
# --- historical back-outs
q1_25 = 212/(1-0.207); q2_25 = 905/1.113
h1_25_op = q1_25+q2_25; h2_25_op = 2553-h1_25_op
h1_25_rev = 9357/1.123 + 12507.4/1.20; h2_25_rev = 42521-h1_25_rev
print("1H25 op",round(h1_25_op),"2H25 op",round(h2_25_op),"3Q25 708 -> 4Q25",round(h2_25_op-708))
print("1H25 rev",round(h1_25_rev),"2H25 rev",round(h2_25_rev))
# --- forecasts
fc = {
 2026:dict(rev=48400, op=2800, ni=2080, fcf=1300),
 2027:dict(rev=53500, op=3300, ni=2450, fcf=1600),
 2028:dict(rev=58500, op=3800, ni=2830, fcf=1900),
 2029:dict(rev=63500, op=4350, ni=3250, fcf=2250),
 2030:dict(rev=68500, op=4900, ni=3650, fcf=2600),
 2031:dict(rev=73500, op=5500, ni=4100, fcf=2900),
}
for y,d in fc.items():
    d['eps']=d['ni']*1e8/SH; d['opm']=d['op']/d['rev']*100
    print(y, d['rev'], d['op'], round(d['opm'],2), d['ni'], round(d['eps']), "PER@336k", round(P/d['eps'],1))
# --- DCF (FCFF), net cash assumed 10,000억 (memory_unverified)
NC = 10000
def dcf(wacc,g,fcfs,nc=NC):
    pv=0
    for i,f in enumerate(fcfs,1): pv+=f/(1+wacc)**i
    tv=fcfs[-1]*(1+g)/(wacc-g); pv+=tv/(1+wacc)**len(fcfs)
    return pv, (pv+nc)*1e8/SH
fcfs=[fc[y]['fcf'] for y in range(2027,2032)]
for w,g in [(0.095,0.03),(0.09,0.035),(0.085,0.04),(0.10,0.03)]:
    ev,ps=dcf(w,g,fcfs); print("DCF wacc",w,"g",g,"EV",round(ev),"per share",round(ps))
# --- Reverse DCF: constant FCF growth over 2027-2036 (10y) from 2026 base 1300, then g=3%, wacc 9.5%
import math
def rev_dcf(growth,wacc=0.095,g=0.03,base=1300,years=10,nc=NC):
    fcfs=[base*(1+growth)**i for i in range(1,years+1)]
    return dcf(wacc,g,fcfs,nc)[1]
lo,hi=0.0,0.6
for _ in range(60):
    mid=(lo+hi)/2
    if rev_dcf(mid)<P: lo=mid
    else: hi=mid
print("implied 10y FCF CAGR @9.5%/3%:",round(mid*100,1))
for w in [0.085,0.09,0.10]:
    lo,hi=0,0.6
    for _ in range(60):
        m=(lo+hi)/2
        if rev_dcf(m,wacc=w)<P: lo=m
        else: hi=m
    print(" wacc",w,"implied CAGR",round(m*100,1))
# implied 2031 earnings for 10% CoE from P with ~0.6% yield -> required price 2031
req = P*(1.10**5) - 12550
print("required 2031-10 price for 10% TSR (ex cum div 12,550):", round(req))
for per in [20,25,30]:
    eps=req/per; ni=eps*SH/1e8
    print(" exit PER",per,"-> EPS",round(eps),"NI(억)",round(ni),"NI CAGR vs 2026E 2080:",round(((ni/2080)**(1/5)-1)*100,1),"%; rev needed @8% NIM:",round(ni/0.08),"(CAGR",round(((ni/0.08/48400)**(1/5)-1)*100,1),"%)")
# --- Scenario TSR
sc = {
 '1y':[('bear',25,198000,2000,0),('base',50,320000,2050,0),('bull',25,483000,2100,0)],
 '3y':[('bear',25,180000,6300,2),('base',50,372000,6800,0),('bull',25,630000,7300,0)],
 '5y':[('bear',25,180000,11000,2),('base',50,386000,12550,0),('bull',25,700000,14000,0)],
}
for h,rows in sc.items():
    ew=0
    for n,p,end,cash,dil in rows:
        tsr=(end+cash)/P-1; ew+=p/100*tsr
        print(h,n,p,end,cash,dil,"TSR",round(tsr*100,1))
    print(h,"prob-weighted TSR",round(ew*100,1))
# --- valuation blend
vals=[('DCF',195000,25),('peerPER',250000,30),('ownband',268000,25),('SOTP',255000,20)]
print("blend",sum(v*w for _,v,w in vals)/100)
# SOTP detail 2027E: ent IT OP 2500 x12 ; vehicle SW OP 800 x30 ; net cash 10000
print("SOTP",(2500*12+800*30+10000)*1e8/SH)
print("dps payout FY25", 1900*SH/1e8, "/1868 =", round(1900*SH/1e8/1868*100,1))
