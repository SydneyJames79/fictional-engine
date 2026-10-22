# 고영 밸류에이션 계산
price=33200
shares_now=68.2e6; treasury=2.042463e6
sh_ex=shares_now-treasury
print("ex-treasury shares(M)",sh_ex/1e6)
sh_dil=sh_ex+0.866909e6   # 자사주 처분 완료 가정
print("diluted shares(M)",sh_dil/1e6)
mcap=price*sh_dil/1e8
print("mkt cap(억)",round(mcap))
netcash=2000  # 가정(memory_unverified, 하향조정)
ev=mcap-netcash
print("EV(억) w/ netcash 2000:",round(ev))

def dcf(fcfs, wacc, g, netcash, shares):
    pv=sum(f/(1+wacc)**(i+1) for i,f in enumerate(fcfs))
    tv=fcfs[-1]*(1+g)/(wacc-g)/(1+wacc)**len(fcfs)
    eq=pv+tv+netcash
    return pv,tv,eq,eq*1e8/shares

# base FCF 2027~2031
base=[520,450,490,540,620]
for w,g in [(0.10,0.03),(0.095,0.03),(0.105,0.025),(0.09,0.03)]:
    pv,tv,eq,ps=dcf(base,w,g,netcash,sh_dil)
    print(f"DCF wacc{w} g{g}: pv{pv:.0f} tv{tv:.0f} eq{eq:.0f} per share {ps:.0f}")

# reverse DCF: FCF 2026=440, grows at cagr for 5 yrs, then g
import math
def rev(cagr,w,g):
    f=[440*(1+cagr)**i for i in range(1,6)]
    pv,tv,eq,ps=dcf(f,w,g,netcash,sh_dil)
    return ps,f[-1]
for w,g in [(0.10,0.03),(0.09,0.03)]:
    lo,hi=0.0,0.6
    for _ in range(60):
        mid=(lo+hi)/2
        ps,f31=rev(mid,w,g)
        if ps<price: lo=mid
        else: hi=mid
    ps,f31=rev(mid,w,g)
    print(f"reverse DCF wacc{w} g{g}: implied FCF CAGR {mid*100:.1f}%, 2031 FCF {f31:.0f}억")

# implied exit
for exit_pe in [25,30]:
    p31=price*1.10**5
    eps=p31/exit_pe
    ni=eps*65.4e6/1e8
    print(f"exit PE {exit_pe}: 2031 price {p31:.0f}, EPS {eps:.0f}, NI {ni:.0f}억, OP@20%OPM rev {(ni-80)/0.8/0.20:.0f}억, CAGR {(((ni-80)/0.8/0.20)/3350)**(1/5)-1:.3f}")

# scenario TSR
sc={
 "1y":[("bear",25,17000,170),("base",50,28000,170),("bull",25,42000,170)],
 "3y":[("bear",25,13000,800),("base",50,28000,1000),("bull",25,45000,1300)],
 "5y":[("bear",25,12000,1200),("base",50,28000,1700),("bull",25,58000,2500)],
}
for h,l in sc.items():
    ew=0
    for n,p,ep,c in l:
        t=(ep+c)/price-1
        ew+=p/100*t
        print(h,n,p,ep,c,f"TSR {t*100:.1f}%")
    print(h,"weighted",f"{ew*100:.1f}%")
# scenario-weighted valuation (3y) discounted
w3=0.25*(13000+800)+0.5*(28000+1000)+0.25*(45000+1300)
print("3y weighted value",w3, "disc 10.5%",w3/1.105**3)
# fair value weights
fv=[(13600,0.20),(20600,0.30),(23800,0.25),(25600,0.10),(w3/1.105**3,0.15)]
print("FV mid",sum(a*b for a,b in fv))
# EPS
for y,ni,sh in [(2026,550,66.5),(2027,590,67.0),(2028,495,66.6),(2029,560,66.2),(2031,700,65.4)]:
    print(y,"EPS",round(ni*1e8/(sh*1e6)))
print("PER on price: 2026E",price/827,"2027E",price/881)
