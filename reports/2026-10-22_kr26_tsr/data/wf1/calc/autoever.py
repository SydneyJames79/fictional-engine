P=336000; SH=27423982; MC=P*SH/1e8
print("mktcap bn", round(MC,1))
# quarterly backout
q25={'1Q':9357/1.123,'2Q':12507.4/1.20,'3Q':10543}
q25['4Q']=42521-sum(q25.values())
o25={'1Q':212/0.793,'2Q':905/1.113,'3Q':708}
o25['4Q']=2553-sum(o25.values())
print("2025 rev q", {k:round(v) for k,v in q25.items()})
print("2025 op q", {k:round(v) for k,v in o25.items()}, "4Q OPM", round(o25['4Q']/q25['4Q']*100,2))
# EPS
for y,ni in [(2025,1868),(2026,2000),(2027,2400),(2028,2780),(2029,3120),(2031,3750)]:
    print(y,"EPS",round(ni*1e8/SH), "PER@336k", round(P/(ni*1e8/SH),1))
# Reverse DCF: FCF 2026E 1600, Ke 10%, g_term 2.5%, 10-yr growth g, net cash assumption
def pv(g,ke=0.10,gt=0.025,fcf0=1600,netcash=8000,n=10):
    v=0; f=fcf0
    for t in range(1,n+1):
        f=f*(1+g); v+=f/(1+ke)**t
    tv=f*(1+gt)/(ke-gt)/(1+ke)**n
    return v+tv+netcash
import math
for nc in [0,8000,12000]:
    lo,hi=0.0,0.6
    for _ in range(60):
        m=(lo+hi)/2
        if pv(m,netcash=nc)<MC: lo=m
        else: hi=m
    print("implied 10y FCF CAGR netcash",nc,"->",round(lo*100,1),"%")
# implied growth w/ exit PER 25x in 2031, Ke 10%
for per in [20,25,30]:
    req_ni=MC*(1.10**5)/per
    print("exit PER",per,"req 2031 NI",round(req_ni),"NI CAGR 25-31",round(((req_ni/1868)**(1/6)-1)*100,1),"%; rev@5% NIm",round(req_ni/0.05),"CAGR",round(((req_ni/0.05/42521)**(1/6)-1)*100,1),"; rev@7% NIm",round(req_ni/0.07),"CAGR",round(((req_ni/0.07/42521)**(1/6)-1)*100,1))
# DCF base
def dcf(ke,gt,netcash,fcfs=[2000,2400,2750,3100,3400,3570,3750,3935,4130]):
    v=sum(f/(1+ke)**(t+1) for t,f in enumerate(fcfs))
    tv=fcfs[-1]*(1+gt)/(ke-gt)/(1+ke)**len(fcfs)
    return v+tv+netcash, (v+tv+netcash)*1e8/SH
for ke,gt,nc in [(0.10,0.025,8000),(0.09,0.025,8000),(0.10,0.03,10000),(0.095,0.025,8000),(0.11,0.02,6000)]:
    eq,ps=dcf(ke,gt,nc); print("DCF ke",ke,"g",gt,"nc",nc,"->",round(eq),"bn,",round(ps),"KRW/sh")
# scenarios
sc=[("1y bear",190000,2100),("1y base",305000,2100),("1y bull",490000,2100),
    ("3y bear",171000,7200),("3y base",325000,7200),("3y bull",570000,7200),
    ("5y bear",150000,13600),("5y base",320000,13600),("5y bull",610000,13600)]
for n,e,c in sc: print(n, round(((e+c)/P-1)*100,1))
w=[.25,.5,.25]
for h in ["1y","3y","5y"]:
    vals=[((e+c)/P-1)*100 for n,e,c in sc if n.startswith(h)]
    print(h,"prob-weighted TSR",round(sum(a*b for a,b in zip(w,vals)),1))
# SOTP
ent=2150*18; veh=260*40; nc=8000; opt=10000
print("SOTP", ent+veh+nc, (ent+veh+nc)*1e8/SH, "w/ option", (ent+veh+nc+opt)*1e8/SH)
print("payout", 1900*SH/1e8, 1900*SH/1e8/1868)
