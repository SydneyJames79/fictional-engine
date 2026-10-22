sh=27423982
px=336000
mcap=px*sh/1e8
print("mcap 억원",round(mcap))
ni25=1868; eps25=ni25*1e8/sh
print("EPS FY25",round(eps25),"PER trailing",round(px/eps25,1))
# base forecasts
f={2026:(48000,2780,2100,1600),2027:(53300,3410,2560,2050),2028:(58600,3985,3000,2550),2029:(63900,4470,3370,3030),2030:(68500,4870,3670,3300),2031:(73200,5270,3980,3580)}
for y,(r,o,n,fc) in f.items():
    print(y,"OPM",round(o/r*100,2),"EPS",round(n*1e8/sh),"PER",round(px/(n*1e8/sh),1))
# DCF base
netcash=9000  # memory_unverified assumption
def dcf(fcfs,wacc,tg,start_disc=1.0):
    pv=0
    for i,fc in enumerate(fcfs):
        pv+=fc/(1+wacc)**(i+start_disc)
    tv=fcfs[-1]*(1+tg)/(wacc-tg)
    pv+=tv/(1+wacc)**(len(fcfs)-1+start_disc)
    return pv
base_fcf=[2050,2550,3030,3300,3580]
# extend 2032-2036 at 6% growth
ext=base_fcf+[base_fcf[-1]*1.06**k for k in range(1,6)]
for w,g in [(0.10,0.03),(0.095,0.03),(0.09,0.03),(0.095,0.035)]:
    ev=dcf(ext,w,g)+320  # 320 = 2026 residual FCF (2 months)
    print("DCF wacc",w,"tg",g,"EV",round(ev),"eq/share",round((ev+netcash)*1e8/sh))
# Reverse DCF: find 10y FCF CAGR from 2026 base 1600 such that EV = mcap-netcash
target=mcap-netcash
import math
def ev_for_g(g,w=0.095,tg=0.03):
    fc=[1600*(1+g)**k for k in range(1,11)]
    return dcf(fc,w,tg)+320
lo,hi=0.0,0.5
for _ in range(60):
    mid=(lo+hi)/2
    if ev_for_g(mid)<target: lo=mid
    else: hi=mid
print("target EV",round(target),"implied 10y FCF CAGR @9.5%/3%",round(mid*100,1))
lo,hi=0.0,0.5
for _ in range(60):
    mid=(lo+hi)/2
    if ev_for_g(mid,0.10,0.03)<target: lo=mid
    else: hi=mid
print("implied 10y FCF CAGR @10%/3%",round(mid*100,1))
# implied 2031 NI for 10%/yr return at exit PE
for pe in (20,22,25):
    need_mcap=mcap*1.10**5 - 14500*sh/1e8  # subtract cum dividends
    ni=need_mcap/pe
    print("exit PE",pe,"needed 2031 NI",round(ni),"CAGR from FY25",round(((ni/ni25)**(1/6)-1)*100,1))
# Scenario TSR
sc={
 "1y":[("bear",195000,1900),("base",310000,2100),("bull",540000,2300)],
 "3y":[("bear",152000,5800),("base",330000,7500),("bull",600000,8800)],
 "5y":[("bear",134000,9900),("base",340000,14500),("bull",680000,18100)],
}
for h,l in sc.items():
    wsum=0
    for n,p,d in l:
        t=(p+d)/px-1
        prob={"bear":0.25,"base":0.5,"bull":0.25}[n]
        wsum+=prob*t
        print(h,n,"TSR%",round(t*100,2))
    print(h,"weighted",round(wsum*100,2))
# valuation methods weighted
vm=[(215000,0.30),(252000,0.25),(205500,0.20),(276400,0.15),(237500,0.10)]
print("weighted FV",round(sum(v*w for v,w in vm)))
# SOTP
print("SOTP", round((44300*1.0+9000*2.5+9000)*1e8/sh))
print("PER at FV 235000 on 26E/27E", round(235000*sh/1e8/2100,1), round(235000*sh/1e8/2560,1))
print("DPS payout FY25",round(1900*sh/1e8/ni25*100,1))
