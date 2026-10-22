P0 = 1294000
shares_now = 730492365
cancel = 24070000
sh_post = shares_now - cancel   # 706,422,365
mcap = P0*shares_now/1e8
print("mcap(억)", round(mcap), "post-cancel shares", sh_post)

# ---- Base forecasts (억원) ----
# OP, tax-adj NI ratio 0.79 (recurring)
F = {
 2026: dict(rev=3441000, op=2651000, ni_rep=2540000, ni_rec=2060000, sh=718e6, fcf=1450000),
 2027: dict(rev=4600000, op=3300000, ni=round(3300000*0.79), sh=695e6, fcf=2000000),
 2028: dict(rev=3700000, op=1450000, ni=round(1450000*0.79), sh=677e6, fcf=900000),
 2029: dict(rev=4100000, op=1850000, ni=round(1850000*0.79), sh=662e6, fcf=1150000),
 2030: dict(rev=4350000, op=1900000, ni=round(1900000*0.79), sh=648e6, fcf=1150000),
 2031: dict(rev=4200000, op=1720000, ni=round(1720000*0.79), sh=635e6, fcf=1050000),
}
for y,d in F.items():
    ni = d.get('ni', d.get('ni_rep'))
    eps = ni*1e8/d['sh']
    extra = ''
    if 'ni_rec' in d:
        extra = f" rec_NI={d['ni_rec']} rec_EPS={d['ni_rec']*1e8/d['sh']:,.0f}"
    print(y, "rev",d['rev'],"op",d['op'],"OPM %.1f%%"%(100*d['op']/d['rev']),"NI",ni,"EPS %.0f"%eps, "FCF",d['fcf'], extra)

# normalized (mid-cycle 2028-2031 avg)
nrev = sum(F[y]['rev'] for y in (2028,2029,2030,2031))/4
nop  = sum(F[y]['op'] for y in (2028,2029,2030,2031))/4
nni = nop*0.79; nsh=660e6
print("normalized rev %.0f op %.0f OPM %.1f NI %.0f EPS %.0f"%(nrev,nop,100*nop/nrev,nni,nni*1e8/nsh))

# ---- DCF ----
net_cash_now = 1100000  # 억, est. 2026-10-22 (88조 gross 2Q + 3Q FCF ~50 + ADR 40 - buyback 40 - debt ~25)
def dcf(wacc, g, tfcf=970000, verbose=True):
    pv = 400000/(1+wacc)**0.19  # 4Q26 remaining FCF
    flows = {2027:2000000,2028:900000,2029:1150000,2030:1150000,2031:1050000}
    for i,(y,f) in enumerate(flows.items(), start=1):
        pv += f/(1+wacc)**(i-0.3)   # ~mid-year from 10/22/26
    tv = tfcf*(1+g)/(wacc-g)
    pvtv = tv/(1+wacc)**4.7
    ev = pv+pvtv
    eq = ev+net_cash_now
    ps = eq*1e8/sh_post
    if verbose: print(f"DCF wacc={wacc} g={g}: PV FCF {pv:,.0f} PV TV {pvtv:,.0f} EV {ev:,.0f} Eq {eq:,.0f} => {ps:,.0f}/sh")
    return ps, pv
base_dcf, pvf = dcf(0.115, 0.015)
dcf(0.11,0.015); dcf(0.12,0.01); dcf(0.125,0.0)

# ---- Reverse DCF: what terminal FCF does market imply ----
wacc=0.115; g=0.015
ev_mkt = mcap - net_cash_now
resid = ev_mkt - pvf
tv_implied = resid*(1+wacc)**4.7
tfcf_implied = tv_implied*(wacc-g)/(1+g)
print(f"Reverse DCF: EV mkt {ev_mkt:,.0f}, PV of base FCF 4Q26-2031 {pvf:,.0f}, residual {resid:,.0f}, implied TV2031 {tv_implied:,.0f}, implied terminal FCF {tfcf_implied:,.0f}, implied terminal OP ~{tfcf_implied/0.79/0.75:,.0f}")
# alt: if market disbelieves 2027-31 too: constant FCF F such that PV(F, 5y)+TV(F)= EV
import math
def pv_const(Fc):
    pv = 400000/(1+wacc)**0.19
    for i in range(1,6): pv += Fc/(1+wacc)**(i-0.3)
    pv += Fc*(1+g)/(wacc-g)/(1+wacc)**4.7
    return pv
lo,hi=0,5e6
for _ in range(60):
    mid=(lo+hi)/2
    if pv_const(mid)>ev_mkt: hi=mid
    else: lo=mid
print(f"Implied constant FCF 2027-perp: {mid:,.0f} -> OP ~{mid/0.79/0.75:,.0f}")

# ---- Multiples ----
nc_ps = 1550000*1e8/sh_post  # YE26E net cash/share
print("YE26E net cash/share %.0f"%nc_ps)
A = 196000*8.5 + 0.5*nc_ps
C = (F[2028]['ni']*1e8/F[2028]['sh'])*7 + 0.5*nc_ps
print("A normalized PER:", round(A), "C trough PER:", round(C), "B DCF:", round(base_dcf))
fv = 0.35*A+0.35*base_dcf+0.30*C
print("weighted FV", round(fv))
print("PER on 2026 rec EPS %.1f, on 2027E %.1f, on 2028E %.1f, on normalized %.1f"%(P0/(2060000*1e8/718e6), P0/(F[2027]['ni']*1e8/F[2027]['sh']), P0/(F[2028]['ni']*1e8/F[2028]['sh']), P0/196000))

# ---- Scenarios TSR ----
sc = {
 '1y': [('bear',25,800000,38000),('base',50,1300000,75000),('bull',25,2050000,98000)],
 '3y': [('bear',25,600000,65000),('base',50,1550000,166000),('bull',25,2600000,240000)],
 '5y': [('bear',25,620000,90000),('base',50,1750000,236000),('bull',25,2900000,380000)],
}
for h,rows in sc.items():
    w=0
    for n,p,ep,cash in rows:
        tsr=((ep+cash)/P0-1)*100
        w+=p*tsr/100
        print(h,n,p,ep,cash,"TSR %.1f%%"%tsr)
    print(h,"prob-weighted TSR %.1f%%"%w)
