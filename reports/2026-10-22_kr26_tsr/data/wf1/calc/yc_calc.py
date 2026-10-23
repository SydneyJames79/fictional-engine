# 와이씨(232140) 검산 스크립트
price=12900; shares=82045350; tsy=100000; sh_out=shares-tsy
mcap=price*shares/1e8; cash=1720; debt=0
ev=mcap-cash+debt
print(f"mcap={mcap:.0f}억 EV={ev:.0f}억 cash/share={cash*1e8/sh_out:.0f}원")

# forecasts (억원)
fc={2026:(2950,470,405),2027:(3500,620,530),2028:(2600,290,275),2029:(3500,560,485),2031:(3900,600,530)}
for y,(r,op,ni) in fc.items():
    print(y, f"OPM={op/r*100:.1f}% NIM={ni/r*100:.1f}% EPS={ni*1e8/sh_out:.0f} PER={price/(ni*1e8/sh_out):.1f}x EV/OP={ev/op:.1f}x")

# normalized
nrev,nopm=3300,0.13; nop=nrev*nopm; nni=nop*0.78+45; print(f"norm OP={nop:.0f} NI={nni:.0f} EPS={nni*1e8/sh_out:.0f} PER={price/(nni*1e8/sh_out):.1f}x")

# DCF
wacc,g=0.115,0.02
fcff={2027:394,2028:376,2029:307,2030:440,2031:458}
pv=30+sum(v/(1+wacc)**(y-2026) for y,v in fcff.items())
tv_norm=305*(1+g)/(wacc-g); tv_2031=458*(1+g)/(wacc-g)
for nm,tv in (("norm",tv_norm),("2031",tv_2031)):
    eq=pv+tv/(1+wacc)**5+cash
    print(f"DCF({nm}) EV_ops={pv+tv/(1+wacc)**5:.0f} equity={eq:.0f} /sh={eq*1e8/sh_out:.0f}")
# sensitivity
for w,gg in ((0.10,0.025),(0.125,0.015)):
    pv2=30+sum(v/(1+w)**(y-2026) for y,v in fcff.items()); tv=380*(1+gg)/(w-gg)
    eq=pv2+tv/(1+w)**5+cash; print(f"DCF wacc={w} g={gg} /sh={eq*1e8/sh_out:.0f}")

# implied perpetual growth from 2027 FCFF 394 (EV basis)
g_imp=(ev*wacc-394)/(ev+394); print(f"implied g from 2027 FCFF={g_imp*100:.2f}%")
print(f"required steady FCFF={ev*(wacc-g):.0f}억 -> OP≈{ev*(wacc-g)/0.78:.0f}억")

# valuation weights
meth=[("DCF",7000,30),("norm PE",8000,25),("peer PE 2027E",11650,25),("hist band",9700,20)]
print("weighted FV=", sum(v*w for _,v,w in meth)/100)

# scenarios TSR
sc={
 "1y":[("bear",25,6500,0,0),("base",50,11000,0,0),("bull",25,19000,0,0)],
 "3y":[("bear",25,5400,0,2),("base",50,11500,100,0),("bull",25,21000,200,0)],
 "5y":[("bear",25,4700,0,3),("base",50,10250,260,1),("bull",25,21800,500,1)],
}
for h,rows in sc.items():
    e=0
    for n,p,ep,cc,d in rows:
        tsr=(ep+cc)/price-1; e+=p/100*tsr
        print(h,n,p,ep,cc,d,f"TSR={tsr*100:.1f}%")
    print(h,"expected",f"{e*100:.1f}%", "prob sum", sum(r[1] for r in rows))
