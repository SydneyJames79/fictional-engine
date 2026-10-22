P=346000
sh_now=89820585
mcap=P*sh_now/1e8
print("mcap 억원", round(mcap))
# share count path (cancel 1.552M by Sep-2027, ~1M/yr buyback-cancel after)
shares={2026:90.3e6,2027:88.3e6,2028:87.2e6,2029:86.2e6,2031:84.4e6}
ni={2026:39500,2027:42500,2028:44500,2029:46000,2031:48000}
for y in shares: print(y,"EPS",round(ni[y]*1e8/shares[y]))
# DCF
wacc=0.097; g=0.015
fcff={2027:24000,2028:26500,2029:28000,2030:29000,2031:30000}
pv=0
for i,(y,f) in enumerate(fcff.items(),1):
    pv+=f/(1+wacc)**i
tv=fcff[2031]*(1+g)/(wacc-g)/(1+wacc)**5
ev=pv+tv
print("PV ops",round(pv),"PV TV",round(tv),"EV",round(ev))
netcash=50000
eq=ev+netcash
print("DCF/share",round(eq*1e8/88.3e6))
# SOTP
core=6*35600; hmc=75000; cash=0.8*50000
print("SOTP core",core,"hmc",hmc,"cash",cash,"total",core+hmc+cash,"per share",round((core+hmc+cash)*1e8/88.3e6))
# normalized
print("norm PER", 44000*7.5)
# reverse: FCF yield
ev_mkt=mcap-netcash
print("EV mkt",round(ev_mkt),"FCF yield 2027E",round(24000/ev_mkt*100,2),"implied g",round((wacc-24000/ev_mkt)*100,2))
core_ev=ev_mkt-hmc
print("core EV",round(core_ev),"core FCF yield",round((24000-5500)/core_ev*100,2),"implied g core",round((wacc-(24000-5500)/core_ev)*100,2))
# required EPS 2031 for 9.7% return
req_price=P*(1+wacc)**5-45000
print("req price 2031",round(req_price),"EPS@7x",round(req_price/7),"EPS@9x",round(req_price/9))
# current multiples
print("PER 26E",round(P/(ni[2026]*1e8/shares[2026]),2),"PER 27E",round(P/(ni[2027]*1e8/shares[2027]),2))
# scenarios
sc=[("1y bear",255000,6500),("1y base",370000,7000),("1y bull",475000,7500),
    ("3y bear",264000,19500),("3y base",410000,22500),("3y bull",560000,25500),
    ("5y bear",270000,32500),("5y base",420000,40000),("5y bull",640000,46500)]
for n,e,c in sc: print(n,round(((e+c)/P-1)*100,1))
for h,(b,ba,bu) in {"1y":(-24.4,9.0,39.5),"3y":(-18.1,25.0,69.2),"5y":(-12.6,32.9,98.4)}.items():
    print(h,"weighted",round(0.25*b+0.5*ba+0.25*bu,1))
