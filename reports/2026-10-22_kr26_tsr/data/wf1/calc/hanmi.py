# 한미반도체 valuation calc (억원, 원)
price = 191200
shares = 95.312e6
mcap = price*shares/1e8  # 억원
print("mcap 억원:", round(mcap))

# --- Base forecasts (억원) ---
fc = {
 2026: dict(rev=7300, op=3350, ni=2750, fcf=2300),
 2027: dict(rev=8800, op=3870, ni=3150, fcf=2800),
 2028: dict(rev=7300, op=2770, ni=2330, fcf=2300),
 2029: dict(rev=8600, op=3440, ni=2850, fcf=2600),
 2030: dict(rev=10500, op=4200, ni=3450, fcf=3000),
 2031: dict(rev=9800, op=3630, ni=3050, fcf=2800),
}
for y,d in fc.items():
    print(y, "OPM %.1f%%"%(d['op']/d['rev']*100), "EPS", round(d['ni']*1e8/shares))

def dcf(wacc, g_term, fade_g, net_cash, years_fade=5):
    # valuation date ~ end Oct 2026; treat 2026 FCF as 0.2 yr remaining -> include 20% of 2026 FCF
    pv = 0.0
    t = 0.2
    pv += fc[2026]['fcf']*0.2/((1+wacc)**0.1)
    for y in range(2027, 2032):
        t = y-2026-0.2+0.5  # mid-year
        pv += fc[y]['fcf']/((1+wacc)**t)
    f = fc[2031]['fcf']
    last_t = t
    for i in range(1, years_fade+1):
        f *= (1+fade_g)
        last_t = 2031+i-2026-0.2+0.5
        pv += f/((1+wacc)**last_t)
    tv = f*(1+g_term)/(wacc-g_term)
    pv_tv = tv/((1+wacc)**last_t)
    ev = pv+pv_tv
    eq = ev+net_cash
    return ev, eq, eq*1e8/shares, pv_tv/ev

for wacc in (0.10, 0.11, 0.12):
    for fg in (0.04, 0.06):
        ev, eq, ps, tvshare = dcf(wacc, 0.03, fg, 3000)
        print(f"DCF wacc={wacc:.0%} fade={fg:.0%}: EV {ev:.0f} eq {eq:.0f} per-share {ps:,.0f} TV share {tvshare:.0%}")

# --- Reverse DCF: constant FCF CAGR 2027-2036 from 2026 base s.t. equity = mcap ---
def rev_dcf(wacc, g_term, net_cash, base_fcf=2300, n=10):
    target = mcap - net_cash
    lo, hi = 0.0, 1.0
    for _ in range(100):
        g = (lo+hi)/2
        pv = 0; f = base_fcf
        for i in range(1, n+1):
            f *= (1+g)
            t = i-0.2+0.5-1+1  # approx
            pv += f/((1+wacc)**(i-0.7+0.5))
        tv = f*(1+g_term)/(wacc-g_term)
        pv += tv/((1+wacc)**(n-0.2))
        if pv < target: lo = g
        else: hi = g
    f = base_fcf*(1+g)**n
    return g, f
for wacc in (0.09, 0.10, 0.11):
    g, f = rev_dcf(wacc, 0.03, 3000)
    print(f"Reverse DCF wacc={wacc:.0%}: implied 10y FCF CAGR {g:.1%}, 2036 FCF {f:,.0f} 억 (vs 2026 2300)")

# --- Implied 2031 earnings for current price at exit PER & required return ---
for req in (0.09, 0.11):
    for per in (25, 35):
        ni = mcap*(1+req)**5/per
        print(f"req {req:.0%} exitPER {per}: 2031 NI needed {ni:,.0f}억 -> OP@44% {ni/0.78:,.0f} -> rev@44%OPM {ni/0.78/0.44:,.0f}억, CAGR vs 2026E 7300 {((ni/0.78/0.44)/7300)**(1/5)-1:.1%}")

# --- normalized multiples ---
norm_ni = 2800
for per in (28, 32, 36):
    print("Normalized NI 2800 x", per, "+ netcash 3000 ->", round((norm_ni*per+3000)*1e8/shares))
eps27 = fc[2027]['ni']*1e8/shares
for per in (32, 38, 45):
    print("2027E EPS", round(eps27), "x", per, "->", round(eps27*per))

# --- Scenarios TSR ---
scen = {
 '1y': [('bear',25, 85000, 1200), ('base',50,150000,1500), ('bull',25,275000,1800)],
 '3y': [('bear',30, 60000, 3000), ('base',45,125000,4500), ('bull',25,250000,6000)],
 '5y': [('bear',30, 50000, 5000), ('base',45,100000,8000), ('bull',25,250000,11000)],
}
for h, lst in scen.items():
    ew = 0
    for n,p,endp,cash in lst:
        tsr = (endp+cash)/price-1
        ew += p/100*(endp+cash)
        print(h, n, p, endp, cash, "TSR %.1f%%"%(tsr*100))
    print(h, "prob-weighted end value", round(ew), "E[TSR] %.1f%%"%((ew/price-1)*100))

# current multiples
print("PER 2026E", round(price/(fc[2026]['ni']*1e8/shares),1), "PER 2027E", round(price/eps27,1), "PER norm", round(price/(norm_ni*1e8/shares),1))
print("EV/Sales 2026E", round((mcap-3000)/7300,1), "EV/Sales 2027E", round((mcap-3000)/8800,1))
print("consensus 2026E OP 4015 -> NI ~", round(4015*0.8), "EPS", round(4015*0.8*1e8/shares), "PER", round(price/(4015*0.8*1e8/shares),1))
# BofA 500,000 = 2028E EPS x 47
print("BofA implied 2028E EPS", round(500000/47), "NI", round(500000/47*shares/1e8))
# DPS derived: 곽 회장 누적 배당 647.4억 / ~32M shares
print("derived DPS cum since 2024:", round(647.4e8/32.0e6))
