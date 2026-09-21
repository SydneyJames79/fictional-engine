# -*- coding: utf-8 -*-
"""8부 민감도: 가정 충격별 순위 이동. 충격은 시나리오 사다리에 곱셈으로 적용."""
import numpy as np, copy, json
from engine import Stock, HorizonSpec, simulate, metrics, NSIM, SEED
from priors import SECTOR_LAMBDA, prior_log_mult
from rank import build_table
import inputs as IN

EXPORTERS = {"memory_large","semi_equip","semi_material","auto_oem","auto_parts","bio_cdmo","bio_holdco"}
LONGDUR   = {"fabless_new","bio_smallcap","space_satcom","rf_defense","display_equip","industrial_ess"}
DILUTERS  = {"퓨런티어","케이엠더블유","사피엔반도체","서진시스템","엘앤씨바이오","에이치브이엠","한중엔시에스","라온텍"}
CUSTCONC  = {"한미반도체","와이씨","한중엔시에스","서진시스템","바이오다인","HPSP","인텔리안테크"}

def shock(name, sec, T, h, S):
    p_be,p_ba,p_bu, m_be,m_ba,m_bu, c_be,c_ba,c_bu, q = h
    def scale(a=1.0,b=1.0,c=1.0): 
        return (p_be,p_ba,p_bu, m_be*a, m_ba*b, m_bu*c, c_be,c_ba,c_bu, q)
    if S=="FX+10%(원화약세)":   return scale(1.04,1.06,1.06) if sec in EXPORTERS else scale(0.98,0.98,0.98)
    if S=="무위험금리+100bp":   return scale(0.95,0.92,0.90) if sec not in LONGDUR else scale(0.93,0.88,0.85)
    if S=="최종멀티플-20%":     return scale(1.0,0.80,0.80) if T==5 else h
    if S=="AI캐펙스 역성장":
        if sec in {"memory_large","semi_equip","semi_material"}:
            return (min(p_be+0.10,0.95), p_ba, max(p_bu-0.10,0.0), m_be*0.85, m_ba*0.85, m_bu*0.85, c_be,c_ba,c_bu, q)
        return h
    if S=="자동차 관세 악화":   return scale(0.85,0.90,0.90) if sec in {"auto_oem","auto_parts","auto_software"} else h
    if S=="바이오 성공확률↓":
        if sec in {"bio_smallcap","bio_holdco"}:
            d=min(0.08,p_bu); return (p_be+d, p_ba, p_bu-d, m_be, m_ba, m_bu*0.85, c_be,c_ba,c_bu, min(q+0.05,1.0))
        return h
    if S=="추가 희석 20%":      return scale(0.83,0.83,0.83) if name in DILUTERS else h
    if S=="핵심고객 이탈":      return scale(0.78,0.88,0.90) if name in CUSTCONC else h
    return h

SCEN = ["기준(반대심문 반영)","FX+10%(원화약세)","무위험금리+100bp","최종멀티플-20%","AI캐펙스 역성장",
        "자동차 관세 악화","바이오 성공확률↓","추가 희석 20%","핵심고객 이탈"]

def run(S):
    rng = np.random.default_rng(SEED)
    Z = {T: rng.standard_normal(NSIM) for T in (1,3,5)}
    idx={}
    for nm,(p0,hs,lam,sg) in IN.INDEX.items():
        st=Stock("IDX",nm,"-","index",p0,lam,"H",sg); st.horizons={T:HorizonSpec(*h[:3],*h[3:6],*h[6:9],h[9]) for T,h in hs.items()}
        idx[nm]={T:metrics(simulate(st,T,np.log(1.07**T),rng,Z[T]),T,IN.RF[T]) for T in (1,3,5)}
    res=[]
    for (nm,code,mkt,sec,p0,pdate,conf,lam_o,floor,sh,hs) in IN.UNIVERSE:
        st=Stock(code,nm,mkt,sec,p0,lam_o if lam_o is not None else SECTOR_LAMBDA[sec],conf,floor,sh)
        st.horizons={T:HorizonSpec(*shock(nm,sec,T,h,S)[:3],*shock(nm,sec,T,h,S)[3:6],
                                   *shock(nm,sec,T,h,S)[6:9],shock(nm,sec,T,h,S)[9]) for T,h in hs.items()}
        b="KOSPI" if mkt=="KOSPI" else "KOSDAQ"
        m={T:metrics(simulate(st,T,prior_log_mult(sec,T),rng,Z[T]),T,IN.RF[T],idx[b][T]["e_ann"]) for T in (1,3,5)}
        res.append(dict(name=nm,code=code,market=mkt,sector=sec,p0=p0,pdate=pdate,conf=conf,m=m,why={},drift=""))
    for T in (1,3,5): build_table(res,T)
    return {r["name"]: {T: r["score"][T]["rank_bal"] for T in (1,3,5)} for r in res}, res

base, base_res = run(SCEN[0])
tab = {s: run(s)[0] for s in SCEN[1:]}

print("### 8부 민감도 — 5년 균형형 종합순위 변동 (기준 대비 ±칸)\n")
hdr = "| 종목 | 기준 |" + "".join(f" {s} |" for s in SCEN[1:])
print(hdr); print("|---|---:|" + "---:|"*len(SCEN[1:]))
inst={}
for nm in base:
    b5 = base[nm][5]; cells=[]; mx=0
    for s in SCEN[1:]:
        d = tab[s][nm][5]-b5; mx=max(mx,abs(d))
        cells.append(f"{tab[s][nm][5]} ({d:+d})" if d else f"{tab[s][nm][5]} (–)")
    inst[nm]=mx
    print(f"| {nm} | {b5} |" + "".join(f" {c} |" for c in cells))
print("\n### 순위 불안정 종목 (어떤 단일 충격에도 5년 종합순위가 4칸 이상 이동)")
for nm,v in sorted(inst.items(), key=lambda x:-x[1]):
    if v>=4: print(f"  - {nm}: 최대 {v}칸 이동")
json.dump({"base":{k:{str(t):v for t,v in d.items()} for k,d in base.items()},
           "scen":{s:{k:{str(t):v for t,v in d.items()} for k,d in tab[s].items()} for s in SCEN[1:]}},
          open("sens.json","w"), ensure_ascii=False)

print("\n\n### 4부 순위 이동표 (공격형/방어형 포함)")
print("| 종목(코드) | 1년 | 3년 | 5년 | 공격형5y | 방어형5y | 최대 스윙 |")
print("|---|---:|---:|---:|---:|---:|---:|")
for r in sorted(base_res, key=lambda r: r["score"][5]["rank_bal"]):
    s1,s3,s5 = r["score"][1],r["score"][3],r["score"][5]
    sw = max(abs(s["rank_agg"]-s["rank_def"]) for s in (s1,s3,s5))
    print(f"| {r['name']}({r['code']}) | {s1['rank_bal']} | {s3['rank_bal']} | {s5['rank_bal']} | "
          f"{s5['rank_agg']} | {s5['rank_def']} | {sw} |")
