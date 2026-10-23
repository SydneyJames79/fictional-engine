"""최종 보고서(HTML)를 만든다.

사용: python3 analysis/report/build_report.py <출력.html> [stage]
입력
- output/{stage}_ranks.csv, {stage}_branches.csv, {stage}_settings.json (stage 기본값 final)
- output/rank_stability.csv, output/sens_runs.csv (있으면)
- data/aux/*.json (B·C·G·H·I·V·J·S), data/stocks/*.json, data/risk_metrics_full_1021.csv
- report/narrative.json: 사람이 쓴 서술(핵심 결론, 상위 종목 상세, 하위·고위험, 의견차, 민감도, 최종 판단, 비고, 체크리스트)
표·차트는 데이터에서 직접 만들고, 서술은 narrative.json에서 가져온다.
"""
import html
import json
import math
import os
import sys

import pandas as pd

AN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AN)
from workflows.build_stock_script import NAMES, SECTOR  # noqa: E402

OUT_HTML = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AN, 'report', 'report.html')
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'final'
O = os.path.join(AN, 'output')
H_LABEL = {'h1': '1년', 'h3': '3년', 'h5': '5년'}
H_END = {'h1': '2027-10-22', 'h3': '2029-10-22', 'h5': '2031-10-22'}

rk = pd.read_csv(f'{O}/{STAGE}_ranks.csv', dtype={'code': str})
br = pd.read_csv(f'{O}/{STAGE}_branches.csv', dtype={'code': str})
st_settings = json.load(open(f'{O}/{STAGE}_settings.json'))
stab = pd.read_csv(f'{O}/rank_stability.csv', dtype={'code': str}) if os.path.exists(f'{O}/rank_stability.csv') else None
sens = pd.read_csv(f'{O}/sens_runs.csv', dtype={'code': str}) if os.path.exists(f'{O}/sens_runs.csv') else None
risk = pd.read_csv(f'{AN}/data/risk_metrics_full_1021.csv', dtype={'code': str}).set_index('code')
macro = json.load(open(f'{AN}/data/macro.json'))['synth']
NARR = json.load(open(f'{AN}/report/narrative.json')) if os.path.exists(f'{AN}/report/narrative.json') else {}
AUX = f'{AN}/data/aux'


def aux(prefix):
    return {f: json.load(open(os.path.join(AUX, f)))['result'] for f in sorted(os.listdir(AUX)) if f.startswith(prefix)}


J = {}
for r in aux('J_').values():
    for s in r.get('stocks', []):
        J[s['code']] = s
J_GLOBAL = next(iter(aux('J_').values()), {})
I = {r['code']: r for r in aux('I_').values()}
V = {r['code']: r for r in aux('V_').values()}
G = {s['code']: s for s in next(iter(aux('G_risk_review').values()))['stocks']}
HB = next(iter(aux('H_base_rates').values()))
B = {}
for r in aux('B_verify').values():
    for s in r['stocks']:
        B[s['code']] = s
B2 = {s['code']: s for s in next(iter(aux('B2_price_update').values()))['stocks']}
STOCK = {c: json.load(open(f'{AN}/data/stocks/{c}.json')) for c in NAMES if os.path.exists(f'{AN}/data/stocks/{c}.json')}


def esc(s):
    return html.escape(str(s if s is not None else ''))


def pct(x, signed=True, d=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 'N/A'
    v = x * 100
    s = f'{v:+.{d}f}%' if signed else f'{v:.{d}f}%'
    return s.replace('+-', '-').replace('-0.0%', '0.0%').replace('+0.0%', '0.0%')


def cls(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ''
    return 'up' if x > 0.0005 else ('down' if x < -0.0005 else '')


def tsr_td(x, d=1):
    return f'<td class="{cls(x)}">{pct(x, True, d)}</td>'


def krw(x):
    return f'{x:,.0f}'


def conf_pill(c):
    k = {'높음': 'hi', '보통': 'mid', '낮음': 'lo'}.get(c, '')
    return f'<span class="pill {k}">{esc(c or "N/A")}</span>'


def stab_pill(s):
    k = {'안정': 'hi', '주의': 'mid', '불안정': 'lo'}.get(s, '')
    return f'<span class="pill {k}">{esc(s or "N/A")}</span>'


def nice_bounds(lo, hi, step):
    return math.floor(lo / step) * step, math.ceil(hi / step) * step


# ---------- 차트 ----------
def strip_svg(p10, med, mean, p90, lo, hi, w=150, h=20):
    """P10~P90 막대, 중앙값 세로선, 기대값 점. 같은 기간 안에서는 같은 눈금을 쓴다."""
    sx = lambda v: 4 + (min(max(v, lo), hi) - lo) / (hi - lo) * (w - 8)
    z = sx(0)
    t = (f'P10 {pct(p10)} · 중앙값 {pct(med)} · 기대값 {pct(mean)} · P90 {pct(p90)}')
    return (f'<svg class="strip" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(t)}"><title>{esc(t)}</title>'
            f'<line x1="{z:.1f}" y1="2" x2="{z:.1f}" y2="{h-2}" class="zero"/>'
            f'<rect x="{sx(p10):.1f}" y="{h/2-3:.1f}" width="{max(sx(p90)-sx(p10),1):.1f}" height="6" rx="3" class="rng"/>'
            f'<line x1="{sx(med):.1f}" y1="{h/2-6:.1f}" x2="{sx(med):.1f}" y2="{h/2+6:.1f}" class="med"/>'
            f'<circle cx="{sx(mean):.1f}" cy="{h/2:.1f}" r="4" class="mean"/></svg>')


def strip_scale(lo, hi, step, w=150):
    """분포 막대 머리글 눈금. 양 끝 글자는 안쪽으로 정렬해 잘리지 않게 한다."""
    sx = lambda v: 4 + (v - lo) / (hi - lo) * (w - 8)
    fmt = lambda t: '0%' if abs(t) < 1e-9 else f'{t*100:+.0f}%'
    lab = f'<text x="1" y="10" text-anchor="start">{fmt(lo)}</text><text x="{w-1}" y="10" text-anchor="end">{fmt(hi)}</text>'
    if lo < 0 < hi and sx(0) - 1 > 34 and (w - 1) - sx(0) > 34:
        lab += f'<text x="{sx(0):.1f}" y="10" text-anchor="middle">0%</text>'
    return f'<svg class="strip-scale" viewBox="0 0 {w} 12" width="{w}" height="12" aria-hidden="true">{lab}</svg>'


def text_w(t, size=12):
    return sum(size if ord(ch) > 0x3000 else size * 0.6 for ch in t)


def scatter_svg(g, key):
    """x = CVaR10(하위 10% 평균 누적 TSR), y = 기대 TSR(1년 누적, 3·5년 연환산). 균형 상위 5는 강조."""
    W, H, L, R, T, Bm = 640, 380, 64, 18, 16, 46
    ycol = 'exp_cum' if key == 'h1' else 'exp_ann'
    xs, ys = g['cvar10'], g[ycol]
    x0, x1 = nice_bounds(xs.min() - 0.02, min(xs.max() + 0.02, 0.0), 0.1)
    x0 = max(x0, -1.0)
    ystep = 0.05 if key == 'h1' else 0.02
    y0, y1 = nice_bounds(min(ys.min(), 0) - ystep / 2, ys.max() + ystep / 2, ystep)
    sx = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)
    sy = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - Bm)
    out = [f'<svg viewBox="0 0 {W} {H}" class="scatter" role="img" aria-label="{H_LABEL[key]} 기대수익과 CVaR10 산점도">']
    k = 0
    while True:
        yv = y0 + k * ystep
        if yv > y1 + 1e-9:
            break
        out.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(yv):.1f}" y2="{sy(yv):.1f}" class="grid"/>'
                   f'<text x="{L-6}" y="{sy(yv)+4:.1f}" text-anchor="end" class="tick">{yv*100:.0f}%</text>')
        k += 1
    k = 0
    while True:
        xv = x0 + k * 0.1
        if xv > x1 + 1e-9:
            break
        out.append(f'<line y1="{T}" y2="{H-Bm}" x1="{sx(xv):.1f}" x2="{sx(xv):.1f}" class="grid"/>'
                   f'<text x="{sx(xv):.1f}" y="{H-Bm+16}" text-anchor="middle" class="tick">{xv*100:.0f}%</text>')
        k += 1
    if y0 < 0 < y1:
        out.append(f'<line x1="{L}" x2="{W-R}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" class="axis"/>')
    out.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-8}" text-anchor="middle" class="axlab">CVaR10: 하위 10% 경로의 평균 누적 TSR (오른쪽일수록 꼬리 손실이 작음)</text>')
    out.append(f'<text transform="translate(14,{(T+H-Bm)/2:.1f}) rotate(-90)" text-anchor="middle" class="axlab">기대 TSR{" (누적)" if key=="h1" else " (연환산)"}</text>')
    top = g.sort_values('rank_bal').head(5)
    rest = g[~g.code.isin(top.code)]
    for _, r in rest.iterrows():
        t = f"{r['name']} · 균형 {int(r.rank_bal)}위 · 기대 {pct(r[ycol])} · CVaR10 {pct(r.cvar10)}"
        out.append(f'<g class="pt"><title>{esc(t)}</title><circle cx="{sx(r.cvar10):.1f}" cy="{sy(r[ycol]):.1f}" r="5" class="dot-mute"/></g>')
    boxes = [(sx(r.cvar10) - 6, sy(r[ycol]) - 6, sx(r.cvar10) + 6, sy(r[ycol]) + 6) for _, r in top.iterrows()]
    hit = lambda b, o: not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3])
    for _, r in top.sort_values(ycol, ascending=False).iterrows():
        cx, cy = sx(r.cvar10), sy(r[ycol])
        lab = f"{int(r.rank_bal)}. {r['name']}"
        tw = text_w(lab)
        t = f"{r['name']} · 균형 {int(r.rank_bal)}위 · 기대 {pct(r[ycol])} · CVaR10 {pct(r.cvar10)}"
        cands = [(8, -8, 'start'), (8, 16, 'start'), (-8, -8, 'end'), (-8, 16, 'end'), (8, -22, 'start'), (-8, -22, 'end'), (8, 30, 'start'), (-8, 30, 'end')]
        chosen, lead = None, False
        for dx, dy, anc in cands:
            x_a = cx + dx
            bx = (x_a, cy + dy - 12, x_a + tw, cy + dy + 3) if anc == 'start' else (x_a - tw, cy + dy - 12, x_a, cy + dy + 3)
            if bx[0] < L or bx[2] > W - R or bx[1] < T:
                continue
            if any(hit(bx, o) for o in boxes):
                continue
            chosen = (x_a, cy + dy, anc, bx)
            lead = abs(dy) > 16
            break
        if chosen is None:
            x_a = cx + 8 if cx + 8 + tw < W - R else cx - 8
            anc = 'start' if x_a > cx else 'end'
            chosen = (x_a, cy - 8, anc, (0, 0, 0, 0))
        x_a, y_a, anc, bx = chosen
        boxes.append(bx)
        leader = f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x_a:.1f}" y2="{y_a-4:.1f}" class="leader"/>' if lead else ''
        out.append(f'<g class="pt"><title>{esc(t)}</title>{leader}<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.5" class="dot-hi"/>'
                   f'<text x="{x_a:.1f}" y="{y_a:.1f}" text-anchor="{anc}" class="lab">{esc(lab)}</text></g>')
    out.append('</svg>')
    return ''.join(out)


# ---------- 섹션 ----------
def narr(key, default='<p class="note">서술 작성 중</p>'):
    v = NARR.get(key)
    if v is None:
        return default
    return ''.join(v) if isinstance(v, list) else v


def sec(id_, title, body, lead=''):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    return f'<section id="{id_}"><h2>{title}</h2>{lead_html}{body}</section>'


def table(head, rows, cls_=''):
    th = ''.join(f'<th class="{c}">{h}</th>' for h, c in head)
    return f'<div class="tbl-wrap"><table class="{cls_}"><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def part1():
    rows = []
    for key in ('h1', 'h3', 'h5'):
        g = rk[rk.h == key].sort_values('rank_bal').head(5)
        for _, r in g.iterrows():
            e = r.exp_cum if key == 'h1' else r.exp_ann
            sb = stab[(stab.code == r.code) & (stab.h == key)].stability.iloc[0] if stab is not None and len(stab[(stab.code == r.code) & (stab.h == key)]) else None
            rows.append(f'<tr><td class="l">{H_LABEL[key]}</td><td>{int(r.rank_bal)}</td><td class="l stick">{esc(r["name"])}</td>'
                        f'{tsr_td(e)}<td>{r.sortino:.2f}</td>{tsr_td(r.cvar10)}<td>{pct(r.p_loss, False, 0)}</td>'
                        f'<td>{conf_pill(J.get(r.code, {}).get("final_confidence"))}</td><td>{stab_pill(sb)}</td></tr>')
    t = table([('기간', 'l'), ('균형 순위', ''), ('종목', 'l stick'), ('기대 TSR', ''), ('Sortino', ''), ('CVaR10', ''), ('손실확률', ''), ('신뢰도', ''), ('순위 안정성', '')], rows)
    return sec('p1', '1부. 핵심 결론', narr('core') + '<h3>기간별 균형형 상위 5</h3>' + t +
               '<p class="note">기대 TSR은 1년은 누적, 3·5년은 연환산이다. 손실확률은 기간 말 누적 TSR이 0 미만일 확률이다. 모든 확률은 모형 추정치이며 확정된 사실이 아니다.</p>')


def part2():
    rows = []
    notes = NARR.get('id_notes', {})
    for c, n in NAMES.items():
        r = risk.loc[c]
        b = B.get(c, {})
        c22 = B2.get(c, {}).get('close_1022')
        sp = STOCK.get(c, {})
        srch = '/'.join(str((sp.get(k) or {}).get('searches', '-')) for k in ('spec', 'gen', 'foren'))
        rows.append(f'<tr><td class="l">{c}</td><td class="l stick">{esc(n)}</td><td class="l">{esc(r["market"])}</td><td class="l">{esc(SECTOR[c])}</td>'
                    f'<td>{krw(r["close"])}</td><td>{krw(c22) if c22 else "확인 불가"}</td><td>{float(r["mcap_krw_bn"])/1000:,.1f}</td>'
                    f'<td>{float(r["adv60_krw_bn"]):,.1f}</td><td>{int(r["shares"]):,}</td><td>{esc(str(r["first_date"])[:10])}</td>'
                    f'<td>{srch}</td><td class="wrap">{esc(notes.get(c, ""))}</td></tr>')
    head = [('코드', 'l'), ('종목', 'l stick'), ('시장', 'l'), ('분류', 'l'), ('10/21 종가(원)', ''), ('10/22 종가(원)', ''), ('시총(조원)', ''),
            ('60일 평균 거래대금(십억원)', ''), ('상장주식수', ''), ('데이터 시작일', ''), ('검색 D/G/E', ''), ('비고', 'l')]
    return sec('p2', '2부. 식별표', table(head, rows) +
               '<p class="note">기준가는 2026-10-21 KRX 공식 종가(FinanceData/marcap 일별 자료)다. 10/22 종가는 장 마감 보도로 확인된 종목만 적었다. 시총·주식수는 10/21 상장주식수 기준이다. '
               '데이터 시작일은 이 분석에 쓴 일별 자료의 첫 거래일(2020-01-02 이후)이다. 검색 D/G/E는 산업 전문가·일반 분석가·포렌식 에이전트가 쓴 웹검색 횟수다.</p>',
               narr('id_lead', ''))


def part3():
    body = []
    for key in ('h1', 'h3', 'h5'):
        g = rk[rk.h == key].sort_values('rank_bal')
        lo, hi = nice_bounds(g.p10.min(), g.p90.max(), 0.25)
        rows = []
        for _, r in g.iterrows():
            sb = None
            if stab is not None:
                m = stab[(stab.code == r.code) & (stab.h == key)]
                sb = m.stability.iloc[0] if len(m) else None
            ann = '' if key == 'h1' else f'<td class="{cls(r.exp_ann)}">{pct(r.exp_ann)}</td>'
            rows.append(f'<tr><td>{int(r.rank_bal)}</td><td class="l stick">{esc(r["name"])}</td>{tsr_td(r.exp_cum)}{ann}'
                        f'<td class="viz">{strip_svg(r.p10, r.median_cum, r.exp_cum, r.p90, lo, hi)}</td>'
                        f'{tsr_td(r.median_cum)}{tsr_td(r.p10)}{tsr_td(r.p90)}<td>{pct(r.p_loss, False)}</td><td>{pct(r.p_loss30, False)}</td>'
                        f'{tsr_td(r.cvar10)}<td>{r.sortino:.2f}</td>{tsr_td(r.excess_vs_index_ann)}'
                        f'<td>{int(r.rank_er)}</td><td>{int(r.rank_ra)}</td><td>{int(r.rank_agg)}</td><td>{int(r.rank_def)}</td>'
                        f'<td>{conf_pill(J.get(r.code, {}).get("final_confidence"))}</td><td>{stab_pill(sb)}</td></tr>')
        head = [('균형', ''), ('종목', 'l stick'), ('기대 TSR(누적)', '')] + ([] if key == 'h1' else [('기대(연)', '')]) + \
               [(f'분포 {strip_scale(lo, hi, 0.25)}', 'viz'), ('중앙값', ''), ('P10', ''), ('P90', ''), ('손실확률', ''), ('−30% 이하', ''), ('CVaR10', ''),
                ('Sortino', ''), ('지수 대비(연)', ''), ('기대 순위', ''), ('위험조정 순위', ''), ('공격형', ''), ('방어형', ''), ('신뢰도', ''), ('안정성', '')]
        idx = macro['index_expected_pct']
        idx_txt = (f"KOSPI {idx['kospi']['h1_cum']:.1f}%, KOSDAQ {idx['kosdaq']['h1_cum']:.1f}%" if key == 'h1' else
                   f"KOSPI 연 {idx['kospi'][key + '_ann']:.1f}%, KOSDAQ 연 {idx['kosdaq'][key + '_ann']:.1f}%")
        body.append(f'<h3 id="p3-{key}">{H_LABEL[key]} (2026-10-21 → {H_END[key]})</h3>'
                    f'<p class="note">지수 기대 TSR {idx_txt}. 무위험수익률 {st_settings["rf"][key]*100:.3f}%. 분포 막대는 P10~P90, 세로선은 중앙값, 점은 기대값이다(누적 기준).</p>'
                    + table(head, rows, 'rank') +
                    f'<figure>{scatter_svg(g, key)}<figcaption>{H_LABEL[key]}: 기대 TSR과 CVaR10. 진하게 표시한 점은 균형형 상위 5종목이고, 나머지 점에 커서를 올리면 종목명이 보인다. 같은 값은 위 표에 모두 있다.</figcaption></figure>')
    return sec('p3', '3부. 기간별 전체 순위표', ''.join(body) + narr('rank_notes', ''),
               '균형형 점수 = 기대 TSR 백분위 60% + Forward Sortino 백분위 25% + CVaR10 백분위 15%. 1년 기대 순위는 누적, 3·5년은 연환산 기대 TSR 기준이다. 위험조정 순위는 Sortino 순이고 동률이면 CVaR10, 손실확률, 영구손실 위험 점수 순으로 가른다.')


def part4():
    piv = rk.pivot_table(index=['code', 'name'], columns='h', values=['rank_bal', 'rank_er', 'rank_ra']).reset_index()
    piv.columns = ['_'.join([x for x in col if x]) for col in piv.columns]
    piv = piv.sort_values('rank_bal_h5')
    rows = []
    for _, r in piv.iterrows():
        d15 = int(r.rank_bal_h1 - r.rank_bal_h5)
        arrow = f'<span class="up">▲{d15}</span>' if d15 > 0 else (f'<span class="down">▼{-d15}</span>' if d15 < 0 else '–')
        rows.append(f'<tr><td class="l stick">{esc(r["name"])}</td><td>{int(r.rank_bal_h1)}</td><td>{int(r.rank_bal_h3)}</td><td>{int(r.rank_bal_h5)}</td><td>{arrow}</td>'
                    f'<td>{int(r.rank_er_h1)}</td><td>{int(r.rank_er_h3)}</td><td>{int(r.rank_er_h5)}</td>'
                    f'<td>{int(r.rank_ra_h1)}</td><td>{int(r.rank_ra_h3)}</td><td>{int(r.rank_ra_h5)}</td></tr>')
    head = [('종목', 'l stick'), ('균형 1년', ''), ('균형 3년', ''), ('균형 5년', ''), ('1→5년', ''), ('기대 1년', ''), ('기대 3년', ''), ('기대 5년', ''),
            ('위험조정 1년', ''), ('위험조정 3년', ''), ('위험조정 5년', '')]
    return sec('p4', '4부. 순위 변화표', table(head, rows) + narr('rank_change', ''),
               '5년 균형 순위 순으로 정렬했다. 1→5년 열의 ▲는 5년 순위가 1년보다 높다는 뜻이다.')


def scen_table(c):
    rows = []
    for key in ('h1', 'h3', 'h5'):
        g = br[(br.code == c) & (br.h == key)]
        p0 = float(risk.loc[c, 'close'])
        cells = []
        for m in ('기준', '낙관', '비관'):
            t = g[g.macro == m]
            p = t.prob.sum()
            tsr = ((t.prob * (t.price + t['div'])).sum() / p / p0 - 1) if p > 0 else float('nan')
            cells.append(f'<td>{p*100:.0f}%</td>{tsr_td(tsr)}')
        rows.append(f'<tr><td class="l">{H_LABEL[key]}</td>{"".join(cells)}</tr>')
    head = [('기간', 'l'), ('기준 확률', ''), ('기준 TSR', ''), ('낙관 확률', ''), ('낙관 TSR', ''), ('비관 확률', ''), ('비관 TSR', '')]
    return table(head, rows, 'compact')


def branch_list(c, key, n=6):
    g = br[(br.code == c) & (br.h == key)].sort_values('prob', ascending=False).head(n)
    items = []
    for _, r in g.iterrows():
        nm = r.branch.split(':', 1)[-1]
        who = {'spec': '전문가', 'gen': '일반', 'cross': '반대심문'}.get(r.branch.split(':', 1)[0], '')
        items.append(f'<li>[{r.macro}·{who}] {esc(nm)} — 확률 {r.prob*100:.1f}%, TSR {pct(r.tsr)}</li>')
    return '<ul class="tight">' + ''.join(items) + '</ul>'


def part5():
    tops = []
    for key in ('h1', 'h3', 'h5'):
        for c in rk[rk.h == key].sort_values('rank_bal').head(5).code:
            if c not in tops:
                tops.append(c)
    det = NARR.get('top_detail', {})
    cards = []
    for c in tops:
        rr = rk[rk.code == c].set_index('h')
        ranks = ' · '.join(f'{H_LABEL[k]} {int(rr.loc[k, "rank_bal"])}위' for k in ('h1', 'h3', 'h5'))
        d = det.get(c, {})
        j = J.get(c, {})
        mon = d.get('monitor') or j.get('key_monitoring') or []
        cards.append(f'<article class="card stock" id="d-{c}"><h3>{esc(NAMES[c])} <span class="code">{c}</span></h3>'
                     f'<p class="note">균형형 순위: {ranks} · 최종 신뢰도 {conf_pill(j.get("final_confidence"))}</p>'
                     f'{scen_table(c)}'
                     f'<h4>핵심 논리</h4><div>{d.get("thesis", "<p class=note>작성 중</p>")}</div>'
                     f'<h4>무엇이 틀릴 수 있나</h4><div>{d.get("risks", "")}</div>'
                     f'<h4>반대심문·검증·최종심사</h4><div>{d.get("review", "")}</div>'
                     f'<h4>확인할 사건</h4><ul class="tight">{"".join(f"<li>{esc(x)}</li>" for x in mon)}</ul>'
                     f'<details><summary>5년 주요 분기(확률 상위)</summary>{branch_list(c, "h5")}</details></article>')
    return sec('p5', '5부. 상위 종목 상세', narr('top_lead', '') + '<div class="cards">' + ''.join(cards) + '</div>',
               '세 기간 중 한 번이라도 균형형 상위 5에 든 종목이다. 시나리오 표의 확률은 무조건부(합 100%)이고 TSR은 그룹 안 확률가중 평균(축소 후)이다.')


def part6():
    rows = []
    for key in ('h1', 'h3', 'h5'):
        g = rk[rk.h == key].sort_values('rank_bal', ascending=False).head(5)
        for _, r in g.iterrows():
            e = r.exp_cum if key == 'h1' else r.exp_ann
            rows.append(f'<tr><td class="l">{H_LABEL[key]}</td><td>{int(r.rank_bal)}</td><td class="l stick">{esc(r["name"])}</td>{tsr_td(e)}{tsr_td(r.median_cum)}'
                        f'<td>{pct(r.p_loss, False)}</td><td>{pct(r.p_loss30, False)}</td>{tsr_td(r.cvar10)}<td>{G.get(r.code, {}).get("perm_loss_risk_score", "N/A")}</td></tr>')
    head = [('기간', 'l'), ('균형 순위', ''), ('종목', 'l stick'), ('기대 TSR', ''), ('중앙값', ''), ('손실확률', ''), ('−30% 이하', ''), ('CVaR10', ''), ('영구손실 위험(1~5)', '')]
    hr = rk[rk.h == 'h5'].sort_values('p_loss30', ascending=False).head(8)
    rows2 = [f'<tr><td class="l stick">{esc(r["name"])}</td><td>{pct(r.p_loss30, False)}</td>{tsr_td(r.cvar10)}{tsr_td(r.median_cum)}{tsr_td(r.exp_ann)}'
             f'<td>{G.get(r.code, {}).get("perm_loss_risk_score", "N/A")}</td><td>{esc(G.get(r.code, {}).get("liquidity_risk", ""))}</td></tr>' for _, r in hr.iterrows()]
    head2 = [('종목', 'l stick'), ('5년 −30% 이하 확률', ''), ('5년 CVaR10', ''), ('5년 중앙값', ''), ('5년 기대(연)', ''), ('영구손실 위험', ''), ('유동성 위험', '')]
    # 모형의 5년 −50% 이하 확률과 베이스레이트(H) 버킷 기저율 비교
    g5 = rk[rk.h == 'h5'].set_index('code')
    rows3 = []
    for b in HB['priors']:
        mem = [c for c in NAMES if any(c in m for m in b['members'])]
        if not mem or 'p_loss50' not in g5.columns:
            continue
        vals = [float(g5.loc[c, 'p_loss50']) for c in mem if c in g5.index]
        names = ', '.join(NAMES[c] for c in mem)
        rows3.append(f'<tr><td class="l">{esc(b["bucket"])}</td><td class="l wrap">{esc(names)}</td><td>{b["prob_perm_loss_gt50_5y_pct"]:.0f}%</td>'
                     f'<td>{sum(vals)/len(vals)*100:.1f}%</td><td>{min(vals)*100:.1f}~{max(vals)*100:.1f}%</td></tr>')
    head3 = [('베이스레이트 버킷', 'l'), ('종목', 'l'), ('H 기저율(5년 −50% 초과 손실)', ''), ('모형 평균', ''), ('모형 범위', '')]
    calib = ('<h3>꼬리 확률 점검: 모형 대 베이스레이트</h3>' + table(head3, rows3) +
             '<p class="note">H 기저율은 버킷별 5년 영구손실(−50% 초과) 확률 추정치다. 모형 값은 5년 누적 TSR이 −50% 미만인 경로 비율이다. '
             '모형이 대체로 더 높게 나오는 까닭은 2026년 급등락으로 커진 변동성 가정 때문이며, 이 차이는 손실확률·CVaR를 보수적으로 만든다.</p>')
    return sec('p6', '6부. 하위·고위험 종목', '<h3>기간별 균형형 하위 5</h3>' + table(head, rows) + '<h3>5년 꼬리위험 상위</h3>' + table(head2, rows2) + calib + narr('bottom', ''))


def part7():
    rows = []
    for c, n in NAMES.items():
        g = rk[rk.code == c].set_index('h')
        if not len(g):
            continue
        cells = ''
        for key in ('h1', 'h3', 'h5'):
            r = g.loc[key]
            cells += f'{tsr_td(r.e_spec_ann)}{tsr_td(r.e_gen_ann)}<td>{r.disagree_log_ann*100:.1f}%p</td><td>{r.shrink_w:.2f}</td>'
        j = J.get(c, {})
        adj = j.get('adjustments', {})
        mult = []
        for key in ('h1', 'h3', 'h5'):
            a = adj.get(key)
            if a and (abs(a['base_mult'] - 1) > 1e-6 or abs(a['bull_mult'] - 1) > 1e-6 or abs(a['bear_mult'] - 1) > 1e-6 or a.get('extra_tail_prob_pct', 0) > 0):
                tail = f", 꼬리 {a['extra_tail_prob_pct']:.0f}%@{a['extra_tail_price_frac']:.2f}" if a.get('extra_tail_prob_pct', 0) > 0 else ''
                mult.append(f"{H_LABEL[key]} {a['base_mult']:.2f}/{a['bull_mult']:.2f}/{a['bear_mult']:.2f}{tail}")
        rows.append(f'<tr><td class="l stick">{esc(n)}</td>{cells}<td>{g.loc["h1"].w_spec:.2f}</td><td class="l">{"I" if c in I else ""}{"·V" if c in V else ""}</td>'
                    f'<td class="wrap">{esc("; ".join(mult) or "조정 없음")}</td></tr>')
    head = [('종목', 'l stick')]
    for key in ('h1', 'h3', 'h5'):
        lab = H_LABEL[key]
        head += [(f'{lab} 전문가', ''), (f'{lab} 일반', ''), (f'{lab} 차이', ''), (f'{lab} 축소 w', '')]
    head += [('전문가 가중', ''), ('검토', 'l'), ('채택한 조정(기준/낙관/비관 배수)', 'l')]
    return sec('p7', '7부. 의견차와 반대심문', table(head, rows) +
               '<p class="note">전문가·일반은 각 분석가 트리의 연환산 기대 TSR(축소 전, 1년은 누적)이다. 차이는 두 값의 로그 차이(연환산)다. 축소 w는 분석가 혼합값에 주는 가중치이고 나머지는 사전값(무위험 + 선행베타 × 지수 초과기대 + 베이스레이트 알파)으로 간다. '
               '검토 열의 I는 반대심문, V는 독립 사실검증을 받은 종목이다.</p>' + narr('disagreement', ''))


def part8():
    body = narr('sensitivity_lead', '')
    if sens is not None and stab is not None:
        label = {'macro_bear': '거시 비관 45%', 'macro_bull': '거시 낙관 35%', 'w_spec_lo': '전문가 가중 0.35', 'w_spec_hi': '전문가 가중 0.65', 'prior_heavy': '축소 2배', 'vol_low': '변동성 −15%',
                 'shock_krw_strong_10pct': '원화 10% 강세', 'shock_rates_up_100bp': '금리 +100bp', 'shock_exit_multiple_down_20pct': '출구배수 −20%',
                 'shock_memory_ai_capex_down': '메모리·AI capex −20%', 'shock_auto_tariff_25pct': '자동차 관세 25%', 'shock_bio_pos_down': '성공확률 −20%',
                 'shock_extra_dilution_5pct': '추가 희석 5%', 'shock_top_customer_loss': '최대 고객 이탈'}
        assump = ['macro_bear', 'macro_bull', 'w_spec_lo', 'w_spec_hi', 'prior_heavy', 'vol_low']
        shocks = [r for r in sens.run.unique() if r.startswith('shock_')]

        def cell(run, key, c, b0):
            m = sens[(sens.run == run) & (sens.h == key) & (sens.code == c)]
            if not len(m):
                return '<td>N/A</td>'
            v = int(m.rank_bal.iloc[0])
            dv = b0 - v
            k = 'up' if dv >= 3 else ('down' if dv <= -3 else '')
            return f'<td class="{k}">{v}</td>'
        for key in ('h1', 'h3', 'h5'):
            fin = rk[rk.h == key].set_index('code')
            order = fin.sort_values('rank_bal').index
            rows, rows2 = [], []
            for c in order:
                b0 = int(fin.loc[c, 'rank_bal'])
                srow = stab[(stab.code == c) & (stab.h == key)].iloc[0]
                cells = f'<td>{b0}</td><td>{int(fin.loc[c, "rank_agg"])}</td><td>{int(fin.loc[c, "rank_def"])}</td>' + ''.join(cell(r, key, c, b0) for r in assump)
                rows.append(f'<tr><td class="l stick">{esc(NAMES[c])}</td>{cells}<td>{int(srow.boot_p10)}~{int(srow.boot_p90)}</td>'
                            f'<td>{srow.p_top5*100:.0f}%</td><td>{stab_pill(srow.stability)}</td></tr>')
                rows2.append(f'<tr><td class="l stick">{esc(NAMES[c])}</td><td>{b0}</td>' + ''.join(cell(r, key, c, b0) for r in shocks) + '</tr>')
            head = [('종목', 'l stick'), ('균형', ''), ('공격형', ''), ('방어형', '')] + [(label[r], '') for r in assump] + [('추정오차 80% 구간', ''), ('상위5 확률', ''), ('판정', '')]
            head2 = [('종목', 'l stick'), ('기준', '')] + [(label.get(r, r), '') for r in shocks]
            body += (f'<h3>{H_LABEL[key]}</h3>' + table(head, rows, 'sens') +
                     f'<details><summary>{H_LABEL[key]} 스트레스 충격별 균형 순위 보기</summary>' + table(head2, rows2, 'sens') + '</details>')
        body += ('<p class="note">가정 변경 열은 그 가정만 바꿔 다시 계산한 균형형 순위다(같은 난수 시드, 6만 경로). 거시 비관은 기준·낙관·비관 확률을 45/10/45로, 거시 낙관은 45/35/20으로 바꾸고 사전값의 지수 기대도 같이 바꾼다. '
                 '축소 2배는 분석가 쪽 가중치를 절반으로 줄여 사전값 쪽으로 더 당긴 경우다. 변동성 −15%는 모든 종목의 목표 변동성을 15% 낮춘 경우로, 6부의 꼬리 확률 점검에서 모형 꼬리가 베이스레이트보다 두껍게 나온 점을 확인하려고 넣었다. 기준보다 3계단 이상 오르면 빨강, 3계단 이상 내리면 파랑으로 표시했다. '
                 '추정오차 구간은 기대수익에 두 가지 오차를 더해 4,000번 다시 순위를 매긴 결과의 10~90% 구간이다. 하나는 종목 고유 오차로, 전문가·일반 분석가 차이와 그 기간의 중앙값을 합쳐 축소 가중치와 최종 신뢰도에 비례해 키운다. '
                 '다른 하나는 사전값 오차로, 베이스레이트 버킷마다 연 1.5%p의 공통 충격을 사전값 비중만큼 준다. '
                 '판정 기준은 다음과 같다. 안정은 추정오차 구간 폭 4계단 이하이면서 가정 변경에 따른 순위 폭 3계단 이하다. 주의는 각각 9계단 이하, 6계단 이하다. 나머지는 불안정이다. '
                 '스트레스 충격(Agent S가 종목별 노출로 추정한 기간말 가치 변화)은 확률가중 시나리오가 아닌 가상 상황이라 판정에서 뺐다.</p>')
    return sec('p8', '8부. 민감도와 순위 안정성', body + narr('sensitivity', ''))


def part9():
    return sec('p9', '9부. 최종 판단', narr('final'))


def qc():
    items = NARR.get('qc', [])
    rows = ''.join(f'<tr><td class="l">{esc(x["item"])}</td><td>{esc(x["status"])}</td><td class="wrap">{esc(x.get("note", ""))}</td></tr>' for x in items)
    return sec('qc', '품질 체크리스트', table([('항목', 'l'), ('상태', ''), ('근거·비고', 'l')], rows))


def appendix():
    return sec('ax', '부록. 방법·자료·한계', narr('appendix'))


def masthead():
    idx = macro['index_expected_pct']
    meta = [('분석 기준일', '2026-10-22(KST)'), ('기준 주가', '2026-10-21 KRX 공식 종가'),
            ('기간 종료일', '1년 2027-10-22 · 3년 2029-10-22 · 5년 2031-10-22'),
            ('무위험수익률(국고, 10/21)', '1년 3.688% · 3년 3.822% · 5년 3.965%'),
            ('거시 시나리오', '기준 50% · 낙관 20% · 비관 30%'),
            ('지수 기대 TSR', f"KOSPI {idx['kospi']['h1_cum']:.1f}% / 연 {idx['kospi']['h3_ann']:.1f}% / 연 {idx['kospi']['h5_ann']:.1f}% · KOSDAQ {idx['kosdaq']['h1_cum']:.1f}% / 연 {idx['kosdaq']['h3_ann']:.1f}% / 연 {idx['kosdaq']['h5_ann']:.1f}%"),
            ('시뮬레이션', '종목·기간별 200,000 경로'), ('통화', '원화(KRW), 배당 포함 총수익')]
    dl = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in meta)
    toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in [('p1', '핵심 결론'), ('p2', '식별표'), ('p3', '기간별 전체 순위표'), ('p4', '순위 변화표'),
                                                                   ('p5', '상위 종목 상세'), ('p6', '하위·고위험 종목'), ('p7', '의견차와 반대심문'),
                                                                   ('p8', '민감도와 순위 안정성'), ('p9', '최종 판단'), ('qc', '품질 체크리스트'), ('ax', '부록')])
    return (f'<header class="masthead"><p class="eyebrow">멀티에이전트 리서치 · 기대 TSR 순위</p><h1>한국 26종목 1·3·5년 기대수익 순위</h1>'
            f'<p class="lead">{narr("standfirst", "")}</p><dl class="meta">{dl}</dl></header>'
            f'<nav class="toc" aria-label="목차"><ol>{toc}</ol></nav>'
            f'<p class="callout">{narr("disclaimer", "")}</p>')


def main():
    css = open(os.path.join(AN, 'report', 'style.css')).read()
    head = ('<title>26종목 기대수익 순위</title><meta name="claude:viewport-fit-sides" content="cover">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@600;700&display=swap">'
            f'<style>{css}</style>')
    body = (head + '<div class="page">' + masthead() + part1() + part2() + part3() + part4() + part5() + part6() + part7() + part8() + part9() + qc() + appendix() +
            '<footer class="note">생성: analysis/report/build_report.py · 데이터와 코드: 브랜치 ccr-12243598-y78irj의 analysis/ 폴더</footer></div>')
    open(OUT_HTML, 'w').write(body)
    print('wrote', OUT_HTML, len(body))


if __name__ == '__main__':
    main()
