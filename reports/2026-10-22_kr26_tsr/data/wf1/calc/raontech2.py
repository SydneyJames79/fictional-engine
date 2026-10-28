P0=3250; sharesM=30.700933
mcap=P0*sharesM/100   # 억원
nd=60                 # assumed net debt (CB 150 debt - est cash ~90), memory-based assumption
EV=mcap+nd
print("mcap", round(mcap,1), "EV", round(EV,1), "EV/S FY25", round(EV/87.46,1), "EV/S 2027E", round(EV/130,1))
r=0.15; g=0.03
fcf_path={2026:-72,2027:-48,2028:-22,2029:-3,2030:12}
pv_int=sum(v/(1+r)**(y-2025.8) for y,v in fcf_path.items())
tv_pv_needed=EV-pv_int
tv_2031=tv_pv_needed*(1+r)**(2031-2025.8)
fcf2031=tv_2031*(r-g)/(1+g)
print("PV interim", round(pv_int,1), "needed TV2031", round(tv_2031), "needed FCF2031", round(fcf2031))
for opm in (0.15,0.20,0.25):
    op=fcf2031/0.85; rev=op/opm
    print("OPM %.0f%% -> OP %.0f, rev %.0f, CAGR25-31 %.1f%%"%(opm*100,op,rev,((rev/87.46)**(1/6)-1)*100))
# exit multiple: PER 20x on 2031 NI, discount 15% 5y, dilution to 40M shares
ni_needed=(P0*40/100)*(1.15**5)/20
print("NI2031 needed (PER20, 40M sh, 15%):", round(ni_needed), "rev @12% NPM", round(ni_needed/0.12), "CAGR", round(((ni_needed/0.12/87.46)**(1/6)-1)*100,1))
# sensitivity r=12%
r=0.12
pv_int=sum(v/(1+r)**(y-2025.8) for y,v in fcf_path.items())
tv_2031=(EV-pv_int)*(1+r)**(2031-2025.8); fcf2031=tv_2031*(r-g)/(1+g)
print("r=12%: needed FCF2031", round(fcf2031), "rev@15%OPM", round(fcf2031/0.85/0.15))
# fair value weighting
m1=1608; m2=2250; m3=849
w=(0.40,0.35,0.25)
fv=w[0]*m1+w[1]*m2+w[2]*m3
print("weighted FV", round(fv))
