# L&C Bio valuation check (units: 억원, shares in millions, per-share KRW on pre-bonus-equivalent basis)
shares_prebonus_eq = 30.669704  # after rights issue (ex-rights priced), pre 1:1 bonus
price = 56700
mcap = price * shares_prebonus_eq / 10000 * 10000 / 10000  # 억원
mcap = price * shares_prebonus_eq * 1e6 / 1e8
net_cash = 1200  # assumption post rights issue & CB redemption
ev = mcap - net_cash
print(f"mcap={mcap:.0f} EV={ev:.0f}")

def dcf(fcfs, wacc, g2, g_term, years2=5):
    pv = 0; t = 0
    for f in fcfs:
        t += 1; pv += f / (1+wacc)**t
    last = fcfs[-1]
    for i in range(years2):
        t += 1; last *= (1+g2); pv += last/(1+wacc)**t
    tv = last*(1+g_term)/(wacc-g_term)
    pv += tv/(1+wacc)**t
    return pv

base = [-80, 80, 430, 480, 520]
for w in (0.095, 0.105, 0.115):
    for g2 in (0.05, 0.07, 0.09):
        ev_b = dcf(base, w, g2, 0.03)
        ps = (ev_b + net_cash) / shares_prebonus_eq * 1e8 / 1e6
        print(f"base wacc={w} g2={g2} EV={ev_b:.0f} per_share={ps:.0f}")

bull = [-50, 150, 600, 750, 900]
ev_bull = dcf(bull, 0.10, 0.10, 0.03)
print(f"bull EV={ev_bull:.0f} per_share={(ev_bull+net_cash)/shares_prebonus_eq*100:.0f}")

# reverse DCF: what 2031 FCF level (growing per path) justifies EV
import math
def implied(wacc, g2, g_term):
    # scale base path shape by factor k until PV == ev
    lo, hi = 0.1, 20
    for _ in range(60):
        k = (lo+hi)/2
        v = dcf([f*k for f in [0, 100, 300, 420, 520]], wacc, g2, g_term)
        if v < ev: lo = k
        else: hi = k
    return k*520
for w,g2 in ((0.105,0.07),(0.10,0.08),(0.095,0.10)):
    f31 = implied(w,g2,0.03)
    print(f"wacc={w} g2={g2}: implied 2031 FCF={f31:.0f} -> rev @14% FCF margin={f31/0.14:.0f}, CAGR vs 1520={(f31/0.14/1520)**0.2-1:.1%}")

# exit multiple approach: EV*(1.105^5) = EBIT2031 * 20
need_ebit = ev*1.105**5/20
print(f"exit 20x EBIT: EBIT2031={need_ebit:.0f}, rev@25%={need_ebit/0.25:.0f}, CAGR={(need_ebit/0.25/1520)**0.2-1:.1%}")

# scenarios
sc = {
 '1y bear':(28000,50),'1y base':(48000,50),'1y bull':(75000,50),
 '3y bear':(24000,150),'3y base':(45000,250),'3y bull':(93000,400),
 '5y bear':(18000,200),'5y base':(46000,750),'5y bull':(137000,1500)}
for k,(p,c) in sc.items():
    print(k, f"{(p+c)/price-1:+.1%}")
probs = {'1y':(0.30,0.45,0.25),'3y':(0.30,0.45,0.25),'5y':(0.30,0.45,0.25)}
for h,(pb,pm,pu) in probs.items():
    t = [ (sc[f'{h} {n}'][0]+sc[f'{h} {n}'][1])/price-1 for n in ('bear','base','bull')]
    print(h, 'weighted', f"{pb*t[0]+pm*t[1]+pu*t[2]:+.1%}")
# EPS
for y,ni,sh in (('2026',-70,30.67),('2027',400,30.67),('2028',470,31.3),('2029',520,31.3),('2031',580,31.9)):
    print(y, f"EPS={ni/sh*100:.0f}")
print("PER 2027E", price/(400/30.67*100), "PER 2028E", price/(470/31.3*100))
print("EV/Sales 26E", ev/1520, "EV/EBIT 26E", ev/320, "EV/EBIT 27E", ev/520)
# weighted fair value
fv = 0.30*24000+0.35*39000+0.20*45000+0.15*25000
print("fair mid", fv)
