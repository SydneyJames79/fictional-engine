P0 = 1361000
sh = 48.56e6  # post-rights shares

def tsr(end, cash): return (end + cash) / P0 * 100 - 100

h = {
 "1y": [(25, 940000, 0), (50, 1400000, 0), (25, 1800000, 1000)],
 "3y": [(25, 830000, 0), (50, 1560000, 6000), (25, 2180000, 10000)],
 "5y": [(25, 740000, 3000), (50, 1670000, 22000), (25, 2550000, 42000)],
}
for k, rows in h.items():
    e = 0
    for p, end, cash in rows:
        t = tsr(end, cash); e += p/100*t
        print(k, p, end, cash, round(t, 2))
    print(k, "E[TSR] =", round(e, 2), "\n")

# EPS from NI (억원) / shares
for yr, ni in [("2026E",17000),("2027E",20100),("2028E",22800),("2029E",25350),("2030E",27400),("2031E",29500)]:
    print(yr, "EPS", round(ni*1e8/sh))

# margins / growth
rev = {"2025A":45570,"2026E":55300,"2027E":68000,"2028E":76000,"2029E":84500,"2030E":92500,"2031E":101000}
op  = {"2025A":20692,"2026E":24200,"2027E":27000,"2028E":30400,"2029E":33800,"2030E":36500,"2031E":39400}
prev=None
for y in rev:
    g = (rev[y]/rev[prev]-1)*100 if prev else None
    print(y, "OPM", round(op[y]/rev[y]*100,1), "growth", None if g is None else round(g,1))
    prev=y
print("CAGR 26-31", round(((101000/55300)**(1/5)-1)*100,2))
print("EPS CAGR 26-31", round(((60750/35000)**(1/5)-1)*100,2))

# valuation weights
fv = 0.35*970000 + 0.30*1242000 + 0.15*1377000 + 0.20*1150000
print("FV mid", round(fv))
print("EV/EBITDA check", round((33300*20+3000)*1e8/sh))
print("PER 2027E", round(41400*30))
# current multiples
for y,eps in [("2026E",35000),("2027E",41400),("2028E",46950)]:
    print(y, "PER at P0", round(P0/eps,1))
mcap = P0*sh/1e8
print("mcap 억원", round(mcap), "EV/EBITDA27", round((mcap-3000)/33300,1))
# DCF quick
fcff = [11500,14800,21500,25000,28000]
for w in (0.085, 0.09):
    f = fcff[:] 
    for i in range(5): f.append(f[-1]*1.07)
    pv = sum(x/(1+w)**(i+1) for i,x in enumerate(f))
    tv = f[-1]*1.03/(w-0.03)/(1+w)**10
    ev = pv+tv
    print("WACC", w, "EV", round(ev), "per share", round((ev+3000)*1e8/sh))
# expected dilution check
print("3y exp dilution", 0.25*8+0.75*4.9, "5y", 0.25*12+0.75*4.9)
# 5y required price at 9%
print("req 5y price", round(P0*1.09**5 - 22000))
