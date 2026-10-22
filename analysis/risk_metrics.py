"""KRX 일별 데이터(FinanceData/marcap)로 26개 종목의 역사적 위험지표를 계산한다.

- 일간수익률: KRX 기준가 대비 등락률(ChangesRatio). 액면분할·무상증자는 기준가에 반영되므로 별도 보정이 필요 없다.
  현금배당락은 반영되지 않는다(변동성 추정에는 영향이 미미).
- 시장지수 대용치: 시장별(KOSPI, KOSDAQ) 전 종목의 전일 시가총액 가중 평균 일간수익률.
"""
import sys
import numpy as np
import pandas as pd

SRC = sys.argv[1]
OUT = sys.argv[2]

CODES = {'000660':'SK하이닉스','005930':'삼성전자','207940':'삼성바이오로직스','0126Z0':'삼성에피스홀딩스',
 '005380':'현대차','012330':'현대모비스','307950':'현대오토에버','295310':'에이치브이엠','452430':'사피엔반도체',
 '418420':'라온텍','370090':'퓨런티어','010690':'화신','290650':'엘앤씨바이오','314930':'바이오다인',
 '171090':'선익시스템','178320':'서진시스템','007660':'이수페타시스','107640':'한중엔시에스','218410':'RFHIC',
 '189300':'인텔리안테크','099320':'쎄트렉아이','403870':'HPSP','032500':'케이엠더블유','098460':'고영',
 '232140':'와이씨','042700':'한미반도체'}

df = pd.read_parquet(SRC)
df = df.sort_values(['Code', 'Date']).reset_index(drop=True)
df['ret'] = df['ChangesRatio'] / 100.0
df['mkt'] = np.where(df['Market'].str.startswith('KOSDAQ'), 'KOSDAQ', np.where(df['Market'] == 'KOSPI', 'KOSPI', 'OTHER'))
df['prev_cap'] = df.groupby('Code')['Marcap'].shift(1)

idx = {}
for m in ['KOSPI', 'KOSDAQ']:
    x = df[(df.mkt == m) & df.prev_cap.notna() & (df.ret.abs() < 0.35)]
    g = x.groupby('Date').apply(lambda t: np.average(t.ret, weights=t.prev_cap), include_groups=False)
    idx[m] = g
idx = pd.DataFrame(idx).sort_index()
idx.to_csv(OUT + '_index_proxy.csv')

last_date = df.Date.max()
rows = []
for code, name in CODES.items():
    s = df[df.Code == code].set_index('Date').sort_index()
    r = s['ret']
    mkt = 'KOSDAQ' if s['mkt'].iloc[-1] == 'KOSDAQ' else 'KOSPI'
    out = {'code': code, 'name': name, 'market': s['Market'].iloc[-1], 'first_date': s.index.min().date(),
           'n_days': len(s), 'close': s['Close'].iloc[-1], 'date': s.index.max().date(),
           'shares': int(s['Stocks'].iloc[-1]), 'mcap_krw_bn': s['Marcap'].iloc[-1] / 1e9}
    for lbl, n in [('1y', 250), ('3y', 750)]:
        rr = r.iloc[-n:] if len(r) >= 60 else r
        out[f'vol_{lbl}'] = rr.std() * np.sqrt(250)
        out[f'downdev_{lbl}'] = np.sqrt((np.minimum(rr, 0) ** 2).mean()) * np.sqrt(250)
        m = idx[mkt].reindex(rr.index).fillna(0)
        cov = np.cov(rr, m)
        out[f'beta_{lbl}_{mkt}'] = cov[0, 1] / cov[1, 1]
        if mkt == 'KOSDAQ':
            k = idx['KOSPI'].reindex(rr.index).fillna(0)
            out[f'beta_{lbl}_KOSPI'] = np.cov(rr, k)[0, 1] / k.var()
    # 수익률 지수(가격, 배당 제외)로 낙폭 계산
    lvl = (1 + r.fillna(0)).cumprod()
    dd = lvl / lvl.cummax() - 1
    out['mdd_full'] = dd.min()
    out['mdd_full_trough'] = dd.idxmin().date()
    l1 = lvl.iloc[-250:]
    out['mdd_1y'] = (l1 / l1.cummax() - 1).min()
    out['dd_from_52w_high'] = lvl.iloc[-1] / l1.max() - 1
    out['high_52w'] = s['High'].iloc[-250:].max()
    out['low_52w'] = s['Low'].iloc[-250:].min()
    for lbl, n in [('ret_1m', 21), ('ret_3m', 63), ('ret_6m', 126), ('ret_1y', 250)]:
        out[lbl] = lvl.iloc[-1] / lvl.iloc[-n - 1] - 1 if len(lvl) > n else np.nan
    ytd = lvl[lvl.index < '2026-01-01']
    out['ret_ytd'] = lvl.iloc[-1] / ytd.iloc[-1] - 1 if len(ytd) else np.nan
    out['adv20_krw_bn'] = s['Amount'].iloc[-20:].mean() / 1e9
    out['adv60_krw_bn'] = s['Amount'].iloc[-60:].mean() / 1e9
    out['adv250_krw_bn'] = s['Amount'].iloc[-250:].mean() / 1e9
    # 하루 ±10% 이상 움직인 날의 비율(갭·급락 위험의 대용치)
    out['pct_days_abs_gt10'] = (r.iloc[-250:].abs() > 0.10).mean()
    out['worst_day_1y'] = r.iloc[-250:].min()
    # 연간 수익률(가격) 이력
    yr = lvl.groupby(lvl.index.year).last()
    prev = yr.shift(1)
    first = lvl.groupby(lvl.index.year).first()
    for y in range(2021, 2027):
        if y in yr.index and (y - 1) in yr.index:
            out[f'ret_{y}'] = yr[y] / yr[y - 1] - 1
    # 주식수 변화 이력(마지막 6회)
    sc = s['Stocks']
    ch = sc[sc != sc.shift(1)]
    out['share_changes'] = '; '.join(f'{d.date()}:{v:,}' for d, v in ch.iloc[-6:].items())
    rows.append(out)

res = pd.DataFrame(rows)
res.to_csv(OUT + '.csv', index=False)
for m in ['KOSPI', 'KOSDAQ']:
    lv = (1 + idx[m].fillna(0)).cumprod()
    print(m, 'proxy vol1y=%.3f' % (idx[m].iloc[-250:].std() * np.sqrt(250)),
          'ret_1y=%.3f' % (lv.iloc[-1] / lv.iloc[-251] - 1), 'ytd=%.3f' % (lv.iloc[-1] / lv[lv.index < '2026-01-01'].iloc[-1] - 1),
          'mdd_1y=%.3f' % ((lv.iloc[-250:] / lv.iloc[-250:].cummax()) - 1).min(),
          'dd_from_high=%.3f' % (lv.iloc[-1] / lv.iloc[-250:].max() - 1))
print('last date', last_date.date())
