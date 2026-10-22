P=335000; SH=24883049; MC=P*SH/1e8
print("mktcap(억)",round(MC))
# Forecasts (holdco consolidated, 억)
fc={2026:dict(rev=18370,subop=3840,ppa=1120,fin=600,ni=3050,fcf=3000),
    2027:dict(rev=20100,subop=4220,ppa=1120,fin=600,ni=None,fcf=3200),
    2028:dict(rev=21900,subop=4380,ppa=1120,fin=600,ni=None,fcf=3300),
    2029:dict(rev=24500,subop=5390,ppa=1120,fin=650,ni=None,fcf=3900),
    2030:dict(rev=26800,subop=6030,ppa=1000,fin=700,ni=None,fcf=4500),
    2031:dict(rev=29000,subop=6670,ppa=900,fin=700,ni=None,fcf=5100)}
for y,d in fc.items():
    d['hop']=d['subop']-d['ppa']
    if d['ni'] is None: d['ni']=round((d['hop']+d['fin'])*0.78+0.24*d['ppa'],-1)
    d['eps']=round(d['ni']*1e8/SH)
    print(y,d, "PER@335k", round(P/d['eps'],1))
# DCF
def dcf(wacc,g,netcash,fcfs):
    pv=sum(f/(1+wacc)**(i+1) for i,f in enumerate(fcfs))
    tv=fcfs[-1]*(1+g)/(wacc-g); pvtv=tv/(1+wacc)**len(fcfs)
    ev=pv+pvtv; eq=ev+netcash
    return round(ev),round(pvtv),round(eq*1e8/SH)
fcfs=[fc[y]['fcf'] for y in [2027,2028,2029,2030,2031]]
for w,g,nc in [(0.095,0.02,8000),(0.09,0.025,8000),(0.105,0.01,8000),(0.095,0.02,3000),(0.095,0.02,13000)]:
    print("DCF",w,g,nc,dcf(w,g,nc,fcfs))
# Reverse DCF: scale factor k s.t. equity value = market cap
import math
def eqv(k,w=0.095,g=0.02,nc=8000):
    return dcf(w,g,nc,[f*k for f in fcfs])[2]
lo,hi=0.5,3
for _ in range(60):
    m=(lo+hi)/2
    if eqv(m)<P: lo=m
    else: hi=m
k=(lo+hi)/2; print("reverse k",round(k,3),"FCF2031 req",round(fcfs[-1]*k),"=> rev2031 @20% FCF margin",round(fcfs[-1]*k/0.2), "CAGR from 16720", round(((fcfs[-1]*k/0.2)/16720)**(1/6)-1,4))
# required EPS 2031 to earn 9.5% with exit PER
for pe in [18,22,25]:
    req=P*1.095**5/pe; print("exit PER",pe,"req EPS2031",round(req),"CAGR vs 2026E",round((req/fc[2026]['eps'])**(1/5)-1,4))
# SOTP
core=[3200,3300,3500,3700,3800]
cev,cpv,_=dcf(0.095,0.015,0,core); print("core EV",cev)
# SB27 rNPV
r=0.11; cfs={2029:-50,2030:750,2031:1250,2032:1625,2033:1750}
npv=sum(v/(1+r)**(y-2026) for y,v in cfs.items()); tv=1750*0.95/(r+0.05)/(1+r)**7
sb27=(npv+tv)*0.65; print("SB27 rNPV",round(sb27))
adc=2000; nc=8000
sotp=cev+sb27+adc+nc; print("SOTP eq",round(sotp),"per share",round(sotp*1e8/SH))
# PER comps
for pe in [18,22,25,28]: print("PER",pe,"x 2027E EPS",round(pe*fc[2027]['eps']))
# Scenarios
sc=[("1y","bear",25,198000,0,0),("1y","base",50,317000,1500,0),("1y","bull",25,465000,2000,0),
    ("3y","bear",25,172000,3000,3),("3y","base",50,357000,6000,0),("3y","bull",25,624000,8000,0),
    ("5y","bear",25,130000,6000,5),("5y","base",50,390000,12500,0),("5y","bull",25,792000,18000,0)]
agg={}
for h,n,p,ep,cash,dil in sc:
    tsr=(ep+cash)/P-1; print(h,n,p,ep,cash,dil,"TSR",round(tsr*100,1))
    agg[h]=agg.get(h,0)+p/100*tsr
print({k:round(v*100,1) for k,v in agg.items()})
# scenario-weighted PV (3y)
ev3=0.25*(172000+3000)+0.5*(357000+6000)+0.25*(624000+8000); print("3y EV",ev3,"PV@10%",round(ev3/1.1**3))
