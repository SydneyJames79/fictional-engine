price=48400; sh=81_400_000; net_cash=2000
ev=price*sh/1e8-net_cash
# 10-year reverse DCF: growth g1 for 2027-2031, fades linearly to 3% by 2036, OPM given, tax 22%, fcf conv 0.9
def dcf10(rev26,g1,opm,coe,tg=0.03):
    pv=0; rev=rev26
    for t in range(1,11):
        g = g1 if t<=5 else g1 + (tg-g1)*(t-5)/5
        rev*=(1+g)
        fcf=rev*opm*0.78*0.9
        pv+=fcf/(1+coe)**t
    pv+= fcf*(1+tg)/(coe-tg)/(1+coe)**10
    return pv,rev
for coe in (0.095,0.105):
    for opm in (0.45,0.55):
        lo,hi=0,0.6
        for _ in range(60):
            m=(lo+hi)/2
            if dcf10(2200,m,opm,coe)[0]<ev: lo=m
            else: hi=m
        pv,rev36=dcf10(2200,m,opm,coe)
        rev31=2200*(1+m)**5
        print("10y frame coe=%.3f opm=%.2f -> 2027-31 CAGR %.1f%% rev2031=%.0f rev2036=%.0f"%(coe,opm,m*100,rev31,rev36))
# implied 2028 EPS at various forward PEs
for pe in (25,30):
    eps=price/pe; ni=eps*sh/1e8; op=ni/0.85; rev=op/0.55
    print("fwd P/E %d -> 2028E EPS %.0f NI %.0f OP %.0f rev(55%%OPM) %.0f ; CAGR25-28 %.1f%%"%(pe,eps,ni,op,rev,((rev/1730)**(1/3)-1)*100))
