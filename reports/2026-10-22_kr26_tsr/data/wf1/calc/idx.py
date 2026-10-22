# scenario midpoints (annualized %), probabilities 25/50/25 for all horizons
P = [0.25, 0.50, 0.25]
S = {
 "KOSPI": {1: [-21.5, 10.0, 27.5], 3: [-5.5, 8.0, 17.0], 5: [-2.5, 7.5, 14.5]},
 "KOSDAQ": {1: [-30.0, 5.0, 32.5], 3: [-7.5, 6.0, 18.0], 5: [-3.5, 5.5, 13.0]},
}
base = {"KOSPI": 5533.77, "KOSDAQ": 764.10}
for idx, hs in S.items():
    for h, mids in hs.items():
        cums = [((1+m/100)**h - 1)*100 for m in mids]
        wcum = sum(p*c for p, c in zip(P, cums))
        wann = ((1+wcum/100)**(1/h) - 1)*100
        lvl = base[idx]*(1+wcum/100)
        print(f"{idx} {h}y: scen cum={[round(c,1) for c in cums]} -> E[cum]={wcum:.1f}% E[ann]={wann:.1f}% level~{lvl:,.0f}")
# scenario level ranges for KOSPI 1y
k = 5533.77
for lo, hi, tag in [(-28,-15,"1y bear"),(5,15,"1y base"),(20,35,"1y bull")]:
    print(tag, round(k*(1+lo/100)), round(k*(1+hi/100)))
for lo, hi, tag, h in [(-8,-3,"3y bear",3),(6,10,"3y base",3),(14,20,"3y bull",3),(-5,0,"5y bear",5),(6,9,"5y base",5),(12,17,"5y bull",5)]:
    print(tag, "cum", round(((1+lo/100)**h-1)*100,1), round(((1+hi/100)**h-1)*100,1), "level", round(k*(1+lo/100)**h), round(k*(1+hi/100)**h))
kd = 764.10
for lo, hi, tag in [(-35,-25,"KD 1y bear"),(0,10,"KD 1y base"),(25,40,"KD 1y bull")]:
    print(tag, round(kd*(1+lo/100)), round(kd*(1+hi/100)))
print("KOSPI drawdown from 7384.56:", round((5533.77/7384.56-1)*100,1))
