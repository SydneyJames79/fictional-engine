P0=47550
sh_basic=26.3e6   # outstanding excl. treasury (est.)
sh_dil=28.5e6     # + CB mid 1.27M + EB 0.9M
print("mktcap(issued 26.5M) bn KRW:", P0*26.5e6/1e8)

# scenarios: (end, cash)
sc={ "1Y":{"bear":(27000,350),"base":(47000,450),"bull":(76000,500)},
     "3Y":{"bear":(21000,1000),"base":(54000,1650),"bull":(100000,2200)},
     "5Y":{"bear":(20000,1800),"base":(56000,3250),"bull":(110000,4000)}}
pr={"bear":.25,"base":.5,"bull":.25}
for h,d in sc.items():
    w=0
    for k,(e,c) in d.items():
        t=(e+c)/P0-1; w+=pr[k]*t
        print(h,k,f"TSR={t*100:.1f}%")
    print(h,"weighted",f"{w*100:.1f}%")

# DCF base
fcf={2027:350,2028:460,2029:540,2030:600,2031:660}
for wacc in (0.105,0.11):
    g=0.03
    pv=sum(v/(1+wacc)**(y-2026) for y,v in fcf.items())
    tv=fcf[2031]*(1+g)/(wacc-g)/(1+wacc)**5
    ev=pv+tv; eq=ev+300
    print(f"WACC {wacc}: PV FCF {pv:.0f} PV TV {tv:.0f} EV {ev:.0f} eq {eq:.0f} per share {eq*1e8/sh_dil:.0f}")

# reverse DCF: find constant growth g1 from FCF2027=350 over 2028-2031 s.t. PV=EV target
target=12600-300+0  # EV = mktcap - netcash(assumed +300)
target=12300
wacc=0.105;g=0.03
def pv_for(g1):
    f=350; pv=f/(1+wacc)
    for t in range(2,6):
        f*=1+g1; pv+=f/(1+wacc)**t
    return pv+f*(1+g)/(wacc-g)/(1+wacc)**5, f
lo,hi=0,1
for _ in range(60):
    m=(lo+hi)/2
    if pv_for(m)[0]<target: lo=m
    else: hi=m
pv,f31=pv_for(lo)
print(f"implied FCF growth 2028-31: {lo*100:.1f}%  FCF2031={f31:.0f}  implied rev2031 @14% FCF margin={f31/0.14:.0f}  CAGR rev 2026-31 from 2350: {((f31/0.14/2350)**(1/5)-1)*100:.1f}%")
# implied exit PER under base NI 2031=830 : FV of mktcap at Ke 11.5% 5y
fv=12600*1.115**5
print("implied 2031 exit PER on base NI 830:", fv/830, "on NI2032 880:", fv/880)
# EPS
for y,ni in [(2026,430),(2027,520),(2028,630),(2029,720),(2030,775),(2031,830),(2032,880)]:
    print(y, "EPS dil", round(ni*1e8/sh_dil))
# EV/Sales
evs=0.25*2.0*2850+0.5*3.5*2850+0.25*5.5*2850
print("EV/S weighted eq per share", (evs+300)*1e8/sh_dil)
print("PER 25x 2027E", 1825*25, "norm 22x", 2105*22)
print("fair mid weighted", 0.2*27000+0.3*45600+0.3*46300+0.2*37300)
print("scenario-implied PV 1Y", (0.25*27000+0.5*47000+0.25*76000)/1.115)
# dividend: 30% of separate NI
for y,sep in [(2026,330),(2027,400),(2028,480),(2029,560),(2030,620)]:
    print(y,"DPS est", round(sep*0.3*1e8/sh_basic))
