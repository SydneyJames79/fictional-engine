"""보정 워크플로(H 베이스레이트, G 위험 검토, 10/22 종가 갱신) 스크립트를 생성한다."""
import json
import sys
import pandas as pd
sys.path.insert(0, '/home/user/fictional-engine/analysis')
from pipeline import forward_sigma
from build_stock_script import NAMES, SECTOR  # noqa: E402

SCR = '/tmp/claude-0/-home-user-fictional-engine/53597674-b69d-5832-baad-c5e925f14216/scratchpad/kr'
risk = pd.read_csv(f'{SCR}/risk_metrics_full.csv', dtype={'code': str}).set_index('code')
uni, rk = [], []
for c, n in NAMES.items():
    r = risk.loc[c]
    uni.append({'code': c, 'name': n, 'market': r['market'], 'mcap': f"{r['mcap_krw_bn']:,.0f}", 'sector': SECTOR[c], 'close': f"{r['close']:,.0f}"})
    s1, slr = forward_sigma(r.to_dict())
    rk.append(f"{c} {n}: vol 1y {r.vol_1y:.0%}, 3y {r.vol_3y:.0%}, full {r.vol_full:.0%}, 2020-24 {r.vol_2020_2024 if pd.notna(r.vol_2020_2024) else float('nan'):.0%}, "
              f"beta1y {r.beta_1y_KOSPI:.2f}, beta3y {r.beta_3y_KOSPI:.2f}, MDD since 2020 {r.mdd_full:.0%}, ADV60 {r.adv60_krw_bn:,.1f}bn KRW, "
              f"days |ret|>10% (1y) {r.pct_days_abs_gt10:.1%}, first trading date {r.first_date} -> default sigma_1y {s1:.0%}, sigma_LR {slr:.0%}")
t = open('/home/user/fictional-engine/analysis/workflows/later_template.js').read()
t = t.replace('__UNIVERSE__', json.dumps(uni, ensure_ascii=False)).replace('__RISK__', json.dumps('\n'.join(rk), ensure_ascii=False))
open(sys.argv[1], 'w').write(t)
print('wrote', sys.argv[1], len(t))
