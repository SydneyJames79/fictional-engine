P=82900
sh_out=10127626
cb_remaining_shares=406500   # 252억/61,988
sh_dil=sh_out+cb_remaining_shares
print("diluted shares",sh_dil, "dilution %",round(cb_remaining_shares/sh_out*100,2))
mcap=P*sh_out/1e8
print("mcap 억",round(mcap,1))

# forecasts (억원)
fc={2026:(3700,640,500,450),2027:(4000,760,600,700),2028:(2300,280,230,150),2029:(2600,340,280,230),2030:(2800,380,310,270),2031:(3000,420,340,300)}
for y,(r,o,n,f) in fc.items():
    print(y,"rev",r,"op",o,"opm",round(o/r*100,1),"ni",n,"eps",round(n*1e8/sh_dil),"fcf",f)

# DCF
ke=0.115; g=0.02
t0=0.2
pv=0
for i,y in enumerate(range(2026,2032)):
    f=fc[y][3]; t=t0+i
    pv+=f/(1+ke)**t
tv=fc[2031][3]*(1+g)/(ke-g)
pv_tv=tv/(1+ke)**(t0+5)
print("PV explicit",round(pv-pv_tv if False else pv,0),"TV",round(tv),"PV TV",round(pv_tv),"total",round(pv+pv_tv))
for nc in (0,500,1000,1500):
    ev=pv+pv_tv+nc
    print(" net cash",nc,"equity",round(ev),"per share",round(ev*1e8/sh_dil))

# normalized multiple
ni_norm=340
for mult in (12,14,16):
    for nc in (0,500):
        v=ni_norm*mult+nc
        print("norm NI",ni_norm,"x",mult,"nc",nc,"->",round(v),"per sh",round(v*1e8/sh_dil))

# reverse DCF: required perpetual FCF
for nc in (0,1000,1500):
    req=(mcap-nc)*(ke-g)
    print("implied perpetual FCF (nc=%d)"%nc,round(req), "=> OP needed @78% conv",round(req/0.78), "rev @20% OPM",round(req/0.78/0.20))
# residual after 2026-27
pv2627=fc[2026][3]/(1+ke)**0.2+fc[2027][3]/(1+ke)**1.2
resid=mcap-pv2627
tv_needed=resid*(1+ke)**1.2
fcf2028_needed=tv_needed*(ke-g)
print("PV 26-27 FCF",round(pv2627),"residual",round(resid),"TV@end2027",round(tv_needed),"FCF2028+ needed perpetual",round(fcf2028_needed))

# scenario-weighted
sw=0.30*18000+0.45*50000+0.25*125000
print("scenario weighted",round(sw))
# peer
eps26=500e8/sh_dil; eps27=600e8/sh_dil
print("peer 11x avg eps",round((eps26+eps27)/2*11), "12.5x 2027 + nc500", round(eps27*12.5+500e8/sh_dil))
# weighted FV
fv=0.35*50000+0.25*38000+0.25*59000+0.15*57000
print("weighted FV",round(fv))

# scenarios TSR
sc={
 "1y":[("bear",25,42000,1000,0.0),("base",50,66000,1000,2.0),("bull",25,120000,1000,4.0)],
 "3y":[("bear",25,27000,2500,0.0),("base",50,52000,3000,4.0),("bull",25,118000,3500,4.0)],
 "5y":[("bear",25,21500,3500,0.0),("base",50,55000,5000,4.0),("bull",25,125000,7000,4.0)],
}
for h,rows in sc.items():
    w=0
    for n,p,e,c,d in rows:
        tsr=(e+c)/P-1
        w+=p/100*tsr
        print(h,n,p,e,c,d,"TSR %",round(tsr*100,1))
    print(h,"weighted TSR %",round(w*100,1))
