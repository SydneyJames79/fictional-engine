# HPSP independent generalist calc
price=48400; shares_issued=82_300_000; treasury=900_000; sh=shares_issued-treasury
mcap=price*shares_issued/1e8  # eok
print("mcap(eok, incl treasury)=%.0f, mcap ex-treasury=%.0f"%(mcap, price*sh/1e8))
net_cash_assumed=2000  # memory_unverified assumption
ev=price*sh/1e8-net_cash_assumed
print("EV assumed=%.0f"%ev)

# --- Reverse DCF: find revenue CAGR 2026-2031 s.t. PV = EV ---
def dcf(rev26, g, opm, coe, tg, fcf_conv=0.90, tax=0.22, years=5):
    pv=0; rev=rev26
    for t in range(1,years+1):
        rev*= (1+g)
        fcf = rev*opm*(1-tax)*fcf_conv
        pv += fcf/((1+coe)**t)
    tv = fcf*(1+tg)/(coe-tg)
    pv += tv/((1+coe)**years)
    return pv, rev, fcf
for coe in (0.095,0.105):
    for opm in (0.50,0.55):
        lo,hi=0.0,0.6
        for _ in range(60):
            mid=(lo+hi)/2
            pv,_,_=dcf(2200,mid,opm,coe,0.03)
            if pv<ev: lo=mid
            else: hi=mid
        pv,rev31,fcf31=dcf(2200,mid,opm,coe,0.03)
        print("coe=%.3f opm=%.2f -> implied rev CAGR 26-31 = %.1f%%, rev2031=%.0f, fcf2031=%.0f"%(coe,opm,mid*100,rev31,fcf31))

# --- My base DCF ---
fcf={2027:1100,2028:1050,2029:1120,2030:1160,2031:1200}
for coe,tg in ((0.105,0.03),(0.095,0.035),(0.10,0.03)):
    pv=sum(v/((1+coe)**(y-2026)) for y,v in fcf.items())
    tv=fcf[2031]*(1+tg)/(coe-tg); pvtv=tv/((1+coe)**5)
    eq=pv+pvtv+net_cash_assumed
    print("DCF coe=%.3f tg=%.3f: PV fcf=%.0f PV tv=%.0f equity=%.0f per share=%.0f"%(coe,tg,pv,pvtv,eq,eq*1e8/sh))

# --- EPS ---
ni={2026:1000,2027:1170,2028:1090,2029:1210,2031:1270}
for y,v in ni.items(): print(y,"EPS=%.0f"%(v*1e8/sh))
print("normalized NI 1080 -> EPS %.0f"%(1080e8/sh))
print("P/E on my 2026E: %.1f ; on 2027E: %.1f"%(price/(1000e8/sh), price/(1170e8/sh)))
print("P/E on consensus 2026E (OP1266->NI~1080): %.1f"%(price/(1080e8/sh)))

# --- valuation weights ---
vals=[(21000,0.25),(35800,0.30),(40200,0.25),(43100,0.20)]
print("weighted FV=%.0f"%sum(v*w for v,w in vals))

# --- scenarios ---
sc={ '1y':[('bear',28000,500,25),('base',45000,600,50),('bull',68000,700,25)],
     '3y':[('bear',22000,1350,25),('base',45000,1950,50),('bull',80000,2700,25)],
     '5y':[('bear',17000,2050,25),('base',43000,3500,50),('bull',92000,5500,25)]}
for h,l in sc.items():
    exp=0
    for n,p,c,pr in l:
        tsr=(p+c)/price-1
        exp+=pr/100*tsr
        print(h,n,"TSR=%.1f%%"%(tsr*100))
    print(h,"prob-weighted TSR=%.1f%%"%(exp*100))
