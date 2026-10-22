# 인텔리안테크 밸류에이션 검산 (단위: 억원, 원)
P=58200; SH_TOT=10737497; SH_TR=509534; SH_EX=SH_TOT-SH_TR
MCAP=P*SH_TOT/1e8; ND=1254; EV=MCAP+ND
print(f"ex-treasury shares {SH_EX:,}  mcap {MCAP:.0f}  EV {EV:.0f}")
# ---- 기준 전망 ----
# year: rev, op, da, capex, dWC, net_int, shares(M)
f={2026:(3850,230,160,240,150,70,10.30),
   2027:(4400,350,170,150,130,60,10.35),
   2028:(4950,440,180,150,135,55,10.40),
   2029:(5450,510,185,160,125,45,10.45),
   2030:(5980,560,190,170,120,38,10.50),
   2031:(6500,600,195,175,115,30,10.55)}
t=0.22
print("year rev op opm nopat fcf ni eps")
fcf={}
for y,(r,op,da,cx,dwc,ni_,sh) in f.items():
    nopat=op*(1-t); fc=nopat+da-cx-dwc; fcf[y]=fc
    if y==2026: ni=182+ (op-77-35)*(1-t)  # 1H 실적 182 + 2H
    else: ni=(op-ni_)*(1-t)
    print(y,r,op,f"{op/r*100:.1f}%",f"{nopat:.0f}",f"{fc:.0f}",f"{ni:.0f}",f"{ni*1e8/(sh*1e6):.0f}")
# ---- DCF (기준: 2026년말 기준 가치, 2027~31 FCF + TV) ----
def dcf(wacc,g,fcfs,nd,sh):
    pv=sum(fcfs[i]/(1+wacc)**(i+1) for i in range(len(fcfs)))
    tv=fcfs[-1]*(1+g)/(wacc-g); pvtv=tv/(1+wacc)**len(fcfs)
    ev=pv+pvtv; eq=ev-nd
    return ev,eq,eq*1e8/(sh*1e6),pv,pvtv
base_f=[fcf[y] for y in range(2027,2032)]
for w,g in [(0.095,0.025),(0.09,0.03),(0.10,0.02)]:
    ev,eq,ps,pv,pvtv=dcf(w,g,base_f,1250,10.35)
    print(f"DCF wacc{w} g{g}: EV {ev:.0f} eq {eq:.0f} /sh {ps:.0f} (pv {pv:.0f} tv {pvtv:.0f})")
# ---- Reverse DCF: 시장 EV 7,503 정당화 FCF 경로 ----
# FCF 2027 시작값 s, 연 성장 gr 로 2031까지, 이후 g=2.5%
import itertools
w,g=0.095,0.025
for s,gr in [(200,0.30),(220,0.28),(250,0.25),(180,0.35),(300,0.20)]:
    fs=[s*(1+gr)**i for i in range(5)]
    ev,eq,ps,pv,pvtv=dcf(w,g,fs,1250,10.35)
    print(f"revDCF s{s} gr{gr}: FCF2031 {fs[-1]:.0f} EV {ev:.0f} /sh {ps:.0f}")
# 목표 EV 7503에 맞는 2031 FCF (성장 경로 비례 스케일)
target=EV
scale_f=[fcf[y] for y in range(2027,2032)]
lo,hi=0.5,5
for _ in range(60):
    m=(lo+hi)/2; fs=[x*m for x in scale_f]
    ev,_,_,_,_=dcf(w,g,fs,1250,10.35)
    if ev<target: lo=m
    else: hi=m
fs=[x*m for x in scale_f]
print(f"implied scale {m:.2f}: FCF2027 {fs[0]:.0f} ... FCF2031 {fs[-1]:.0f}; implied 2031 FCF margin on 6500 = {fs[-1]/6500*100:.1f}%")
# 필요 영업이익률: FCF2031 = OP(1-t)+DA-capex-dWC => OP = (FCF - DA + capex + dWC)/(1-t)
op_req=(fs[-1]-195+175+115)/(1-t)
print(f"required OP 2031 at rev 6500: {op_req:.0f} => OPM {op_req/6500*100:.1f}%;  at rev 8000: OPM {op_req/8000*100:.1f}% (rev CAGR 26-31 {((8000/3850)**(1/5)-1)*100:.1f}%)")
# ---- 멀티플 ----
print("P/E 26E(보고)",P/(275*1e8/10.30e6),"P/E 27E",P/(226*1e8/10.35e6),"P/E 28E",P/(300*1e8/10.40e6))
print("EV/Sales 26E",EV/3850,"EV/EBITDA 26E",EV/(230+160),"EV/EBITDA 27E",EV/(350+170))
bps26=(2662+275-21)*1e8/SH_EX; print("BPS26E",f"{bps26:.0f}","PBR now",P/bps26)
# ---- 밸류에이션 방법별 ----
v_dcf=dcf(0.095,0.025,base_f,1250,10.35)[2]
v_evebitda=(11*520-1200)*1e8/10.35e6
norm_eps=(4300*0.07-50)*(1-t)*1e8/10.35e6
v_pe=norm_eps*25
v_pbr=bps26*2.1
v_evs=0.25*((0.9*4000-1300)*1e8/10.35e6)+0.5*((1.4*4400-1200)*1e8/10.35e6)+0.25*((2.4*4900-1100)*1e8/10.35e6)
print(f"DCF {v_dcf:.0f} EV/EBITDA {v_evebitda:.0f} normEPS {norm_eps:.0f} PE {v_pe:.0f} PBR {v_pbr:.0f} EVS {v_evs:.0f}")
wts=[0.30,0.20,0.20,0.10,0.20]; vals=[v_dcf,v_evebitda,v_pe,v_pbr,v_evs]
print("weighted FV",sum(a*b for a,b in zip(wts,vals)))
# ---- 시나리오 TSR ----
sc=[("1y bear",30000,200,0),("1y base",56000,250,1),("1y bull",95000,250,1),
    ("3y bear",24000,600,15),("3y base",66000,900,2.5),("3y bull",135000,1500,2),
    ("5y bear",22000,1000,20),("5y base",70000,1900,5),("5y bull",150000,3000,3)]
pr={"bear":25,"base":50,"bull":25}
for h in ["1y","3y","5y"]:
    ew=0
    for n,px,cash,dil in sc:
        if n.startswith(h):
            tsr=(px+cash)/P-1; ew+=pr[n.split()[1]]/100*tsr
            print(f"{n}: end {px} cash {cash} dil {dil}% TSR {tsr*100:.1f}%")
    print(f"  {h} prob-weighted TSR {ew*100:.1f}%")
