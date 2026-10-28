price = 191200; shares = 95.312e6; mcap = price*shares/1e8
fc = {
 2026: dict(rev=7300, op=3350, ni=2750, fcf=2300),
 2027: dict(rev=8800, op=3870, ni=3150, fcf=2800),
 2028: dict(rev=7300, op=2770, ni=2330, fcf=2300),
 2029: dict(rev=9000, op=3600, ni=2980, fcf=2750),
 2030: dict(rev=11500, op=4600, ni=3780, fcf=3300),
 2031: dict(rev=11000, op=4180, ni=3500, fcf=3200),
}
for y,d in fc.items():
    print(y, "OPM %.1f%%"%(d['op']/d['rev']*100), "NI/OP %.2f"%(d['ni']/d['op']), "EPS", round(d['ni']*1e8/shares), "FCF", d['fcf'])
avg_ni = sum(d['ni'] for d in fc.values())/6; avg_op = sum(d['op'] for d in fc.values())/6; avg_rev=sum(d['rev'] for d in fc.values())/6
print("mid-cycle avg rev %.0f op %.0f ni %.0f eps %.0f"%(avg_rev, avg_op, avg_ni, avg_ni*1e8/shares))

def dcf(wacc, g_term, fade_g, net_cash, years_fade=5):
    pv = fc[2026]['fcf']*0.2/((1+wacc)**0.1)
    for y in range(2027, 2032):
        t = y-2026-0.2+0.5
        pv += fc[y]['fcf']/((1+wacc)**t)
    f = fc[2031]['fcf']; last_t=t
    for i in range(1, years_fade+1):
        f *= (1+fade_g); last_t = 2031+i-2026-0.2+0.5
        pv += f/((1+wacc)**last_t)
    tv = f*(1+g_term)/(wacc-g_term); pv_tv = tv/((1+wacc)**last_t)
    ev = pv+pv_tv; eq = ev+net_cash
    return ev, eq, eq*1e8/shares, pv_tv/ev
for wacc in (0.095, 0.105, 0.115):
    for fg in (0.05, 0.08):
        ev, eq, ps, tvs = dcf(wacc, 0.03, fg, 3000)
        print(f"DCF wacc={wacc:.1%} fade={fg:.0%}: EV {ev:.0f} eq {eq:.0f} /sh {ps:,.0f} TV {tvs:.0%}")

# blend
dcf_v = 52000; norm_v = 100000; peer_v = 125600; evs_v = 127800
blend = 0.30*dcf_v+0.25*norm_v+0.25*peer_v+0.20*evs_v
print("blend", round(blend))
# EV/Sales scenario
w = 0.25*8+0.5*13+0.25*20
print("weighted EV/S", w, "->", round((8800*w+3000)*1e8/shares))
print("norm: 2900 x 32 + 3000 ->", round((2900*32+3000)*1e8/shares))
eps27=fc[2027]['ni']*1e8/shares
print("peer 2027E EPS", round(eps27), "x38", round(eps27*38), "x45", round(eps27*45))

scen = {
 '1y': [('bear',25, 85000, 1200), ('base',50,150000,1500), ('bull',25,275000,1800)],
 '3y': [('bear',30, 60000, 3000), ('base',45,125000,4800), ('bull',25,250000,6500)],
 '5y': [('bear',30, 50000, 5000), ('base',45,110000,8500), ('bull',25,250000,12000)],
}
for h,lst in scen.items():
    ew=0; ps=0
    for n,p,endp,cash in lst:
        tsr=(endp+cash)/price-1; ew+=p/100*(endp+cash); ps+=p
        print(h,n,p,endp,cash,"TSR %.1f%%"%(tsr*100))
    print(h,"prob sum",ps,"E[end]",round(ew),"E[TSR] %.1f%%"%((ew/price-1)*100))
# implied
for req in (0.10,):
    for per in (30,):
        ni = mcap*(1+req)**5/per
        print(f"req {req:.0%} exit PER {per}: 2031 NI {ni:,.0f} OP {ni/0.78:,.0f} rev@44% {ni/0.78/0.44:,.0f} CAGR {((ni/0.78/0.44)/7300)**0.2-1:.1%}")
# 2028 implied at 47x (BofA) 
print("mcap/47 =", round(mcap/47), "억 NI 2028 needed at 47x today -> rev@44%OPM", round(mcap/47/0.78/0.44))
