"""보고서 서술(narrative.json)을 만든다. 서술 속 수치는 산출 파일에서 직접 가져온다.

사용: python3 analysis/report/write_narrative.py
기존 narrative.json의 id_notes·disclaimer는 유지하고 나머지 키를 다시 쓴다. 부록은 report/appendix.html의 빈칸을 채워 만든다.
"""
import glob
import json
import os

import pandas as pd

AN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(AN, 'report', 'narrative.json')
O = os.path.join(AN, 'output')
r = pd.read_csv(f'{O}/final_ranks.csv', dtype={'code': str})
st = pd.read_csv(f'{O}/rank_stability.csv', dtype={'code': str})
sens = pd.read_csv(f'{O}/sens_runs.csv', dtype={'code': str})
br = pd.read_csv(f'{O}/final_branches.csv', dtype={'code': str})
pre = pd.read_csv(f'{O}/prelim_ranks.csv', dtype={'code': str})
risk = pd.read_csv(f'{AN}/data/risk_metrics_full_1021.csv', dtype={'code': str}).set_index('code')
SET = json.load(open(f'{O}/final_settings.json'))
JF = json.load(open(f'{AN}/data/aux/J_final_judge.json'))
J = {s['code']: s for s in JF['result']['stocks']}
RE = JF.get('rereview', {})  # 독립 검증(Q) 뒤 재심사한 종목(merge_judge.py가 기록)
J0F = f'{AN}/data/aux/J0_final_judge_1차.json'
J0 = {s['code']: s for s in json.load(open(J0F))['result']['stocks']} if os.path.exists(J0F) else J
I = {}
for f_ in sorted(glob.glob(f'{AN}/data/aux/I_cross-exam_*.json')):
    d_ = json.load(open(f_))['result']
    I[d_['code']] = d_
Q = json.load(open(f'{AN}/data/aux/Q_independent_verification.json'))['result']
Q2F = f'{AN}/data/aux/Q2_re-verification.json'
Q2 = json.load(open(Q2F))['result'] if os.path.exists(Q2F) else None  # 조치 뒤 좁은 재검증
NAME = dict(zip(r.code, r.name))
CODE = {v: k for k, v in NAME.items()}
RF = {'h1': 0.03688, 'h3': 0.03822, 'h5': 0.03965}
HL = {'h1': '1년', 'h3': '3년', 'h5': '5년'}
D0 = {'h1': 0.15, 'h3': 0.08, 'h5': 0.06}


def R(c, h):
    return r[(r.code == c) & (r.h == h)].iloc[0]


def S(c, h):
    return st[(st.code == c) & (st.h == h)].iloc[0]


def pc(x, d=1, signed=True):
    s = f'{x*100:+.{d}f}%' if signed else f'{x*100:.{d}f}%'
    return s.replace('+0.0%', '0.0%').replace('-0.0%', '0.0%').replace('-', '−')


def pp(x, d=1):
    return f'{x*100:+.{d}f}%p'.replace('-', '−')


def er(c, h):
    x = R(c, h)
    return x.exp_cum if h == 'h1' else x.exp_ann


def top(h, n=5):
    return list(r[r.h == h].sort_values('rank_bal').code[:n])


def bottom(h, n=5):
    return list(r[r.h == h].sort_values('rank_bal', ascending=False).code[:n])


def grp(c, h, m):
    g = br[(br.code == c) & (br.h == h) & (br.macro == m)]
    p0 = R(c, h).p0
    return (g.prob * (g.price + g['div'])).sum() / g.prob.sum() / p0 - 1


def fm(x):
    """배수 표기: 소수 둘째 자리, 셋째 자리가 있으면(1.005 등) 셋째 자리까지."""
    s = f'{x:.3f}'
    return s[:-1] if s.endswith('0') else s


def jm(c, src=None):
    a = (src or J)[c]['adjustments']
    return ', '.join(f"{HL[h]} {fm(a[h]['base_mult'])}/{fm(a[h]['bull_mult'])}/{fm(a[h]['bear_mult'])}" for h in ('h1', 'h3', 'h5')) + '(기준/낙관/비관)'


def rks(c):
    return '·'.join(f'{HL[h]} {int(R(c, h).rank_bal)}위' for h in ('h1', 'h3', 'h5'))


def bull_contrib(c, h):
    g = br[(br.code == c) & (br.h == h)]
    b = g[g.macro == '낙관']
    return (b.prob * b.tsr).sum(), (g.prob * g.tsr).sum() - (b.prob * b.tsr).sum()


def srank(run, c, h):
    m = sens[(sens.run == run) & (sens.code == c) & (sens.h == h)]
    return int(m.rank_bal.iloc[0]) if len(m) else None


def names(codes):
    return '·'.join(NAME[c] for c in codes)


def josa(word, a, b):
    """끝 글자에 받침이 있으면 a(이·은·이다), 없으면 b(가·는·다). 한글이 아닌 끝 글자는 받침 없음으로 본다."""
    ch = word[-1]
    return a if '가' <= ch <= '힣' and (ord(ch) - 0xAC00) % 28 else b


def li(items):
    return '<ul class="tight">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


n = json.load(open(P))

# ---------- 재심사 서술 ----------
REJ_NOTE = {
    '005380': f'재심사는 1차 사실검증의 대미투자특별법 통과를 반영해, 비관 그룹 안에서 관세 25%를 전제한 비중을 약 3분의 1로 낮춘 만큼 비관 배수를 올렸다. '
              f'기준·낙관 배수와 전문가 가중({J["005380"]["w_spec"]:.2f})은 관세와 무관해 그대로 두었다. ',
    '012330': '재심사는 같은 사실을 현대차 지분법이익과 A/S 부품 수출 경로로 반영해 비관 배수를 현대차의 절반 정도만 올렸다. 3·5년의 지배구조 개편 꼬리에 따른 하향은 관세와 별개라 유지했다. ',
    '010690': '재심사는 고객사의 관세비용 분담 요구 경로를 반영해 비관 배수를 올렸다. 비관의 주동인인 차환·레버리지 위험은 관세와 무관해 그대로 두었다. ',
    '005930': '재심사는 1차 사실검증이 짚은 다년 보상용 자사주 매입(보도상 약 80조원)이 회사 정의 FCF에 잡히지 않을 수 있다는 점을, 분석가가 이를 빠뜨렸을 확률(약 3분의 1)만큼 '
              '3·5년 기준과 5년 낙관에 1%p씩 더 반영했다. 2026년 말 순현금 정의가 분석가마다 달라(254조원 대 200조원, 주당 약 8,300원) 이 차이는 사실 오류가 아닌 추정 기준 차이로 보고 '
              '전문가 가중 0.5의 평균에 맡겼다. ',
}
REJ = {c: f'이 배수는 독립 검증 뒤 재심사에서 정했고, 1차 심사의 배수는 {jm(c, J0)}였다. {REJ_NOTE.get(c, "")}' for c in RE}
TARIFF = [c for c in ('005380', '012330', '010690', '307950', '370090') if c in RE]

# ---------- 공통 통계 ----------
stat = {}
for h in ('h1', 'h3', 'h5'):
    g = r[r.h == h]
    stat[h] = {'excess': list(g[g.excess_vs_index_ann > 0].sort_values('rank_bal').code), 'ploss50': int((g.p_loss > 0.5).sum()), 'med_neg': int((g.median_cum < 0).sum()),
               'below_rf': int((g.exp_ann < RF[h]).sum()), 'ploss_min': g.p_loss.min(), 'ploss_max': g.p_loss.max(),
               'stab': st[st.h == h].stability.value_counts().to_dict()}
conf_cnt = pd.Series([s['final_confidence'] for s in J.values()]).value_counts().to_dict()
NTOT = len(r)
NST = NTOT // 3
SS_N = int(r.same_side_fix.sum())

n['standfirst'] = ('2026-10-21 종가를 기준으로 26개 종목의 1·3·5년 기대 총주주수익률(배당 포함, 이하 TSR)을 추정해 순위를 매겼다. '
                   '총괄을 뺀 역할별 에이전트 108개가 종목 식별·거시·산업 분석·포렌식·가치평가·반대심문·사실검증·최종심사·독립 검증을 맡았고'
                   f'(독립 검증 뒤 최종심사 재심사 {len({v["run"] for v in RE.values()})}회{"와 재검증 1회" if Q2 else ""} 별도), 종목·기간마다 20만 개 경로의 몬테카를로로 수익률 분포를 만들었다.')

# ---------- 1부 ----------
t1, t3, t5 = top('h1'), top('h3'), top('h5')
big4 = ['012330', '000660', '005380', '005930']
h35_ok = all(S(c, h).stability != '불안정' for h in ('h3', 'h5') for c in top(h))
unst35 = list(dict.fromkeys(c for h in ('h3', 'h5') for c in top(h) if S(c, h).stability == '불안정'))
lead = (('3·5년 상위 순위는 비교적 견고하지만 ' if h35_ok else '3·5년 상위 순위도 일부는 가정에 따라 바뀌고, ') +
        (f'1년은 {NAME[t1[0]]} 1위를 빼면 순위가 불안정하고, ' if S(t1[0], 'h1').stability != '불안정' else '1년 순위는 불안정하고, ') + '절대 수준의 매력은 낮다.')
if all(set(top(h, 4)) == set(big4) for h in ('h1', 'h3', 'h5')):
    big_txt = '대형 4종목(현대모비스·SK하이닉스·현대차·삼성전자)이 세 기간 모두 균형형 1~4위다. '
elif all(set(top(h, 4)) == set(big4) for h in ('h3', 'h5')):
    big_txt = '대형 4종목(현대모비스·SK하이닉스·현대차·삼성전자)은 3·5년 균형형 1~4위다. '
else:
    big_txt = ''
fifth = (f'3·5년 5위는 모두 {NAME[t3[4]]}{josa(NAME[t3[4]], "이다", "다")}. ' if t3[4] == t5[4]
         else f'3년 5위는 {NAME[t3[4]]}, 5년 5위는 {NAME[t5[4]]}{josa(NAME[t5[4]], "이다", "다")}. ')
mid17 = list(r[r.h == 'h1'].sort_values('rank_bal').code[1:7])
pt17 = [S(c, 'h1').p_top5 for c in mid17]


def ex_list(h):
    return ', '.join(f'{NAME[c]}(연 {pp(R(c, h).excess_vs_index_ann)})' for c in stat[h]['excess'])


def ex_sent(h):
    ex = stat[h]['excess']
    if not ex:
        return f'{HL[h]}에는 지수 기대를 넘는 종목이 없다.'
    small = all(R(c, h).excess_vs_index_ann < S(c, h).tau for c in ex)
    return f'{HL[h]}에 지수 기대를 넘는 종목은 {ex_list(h)}{"뿐이다" if len(ex) == 1 else "다"}.' + (' 그 차이는 추정오차보다 작다.' if small else '')


def stab_list(h, codes):
    s = ', '.join(f'{NAME[c]} {S(c, h).stability}' for c in codes)
    return s + josa(S(codes[-1], h).stability, '이다', '다')


_s35 = {S(c, h).stability for h, cs in (('h3', t3), ('h5', t5)) for c in cs}
stab35 = (f'3·5년 상위 5는 모두 \'{next(iter(_s35))}\' 판정이다' if len(_s35) == 1
          else f'3년 상위 5의 판정은 {stab_list("h3", t3)}. 5년은 {stab_list("h5", t5)}')
rob = ('가중 프로필, 거시 확률, 전문가 가중, 축소 강도, 변동성 가정을 바꾸거나 추정오차를 넣어도 이 종목들의 순위는 크게 흔들리지 않는다. ' if h35_ok
       else f'{names(unst35)}{josa(NAME[unst35[-1]], "은", "는")} 가정이나 추정오차에 따라 순위가 크게 움직일 수 있다. ')
p1 = S(t1[0], 'h1')
pl = stat['h1']
core = [
    f'<p><b>{lead}</b> {big_txt}{fifth}그러나 1년 기대 TSR이 지수 기대(KOSPI 8.5%, KOSDAQ 6.0%)를 넘는 종목은 '
    + ('하나도 없다.' if not pl['excess'] else names(pl['excess']) + '뿐이다.') + '</p>',
    li([
        '<b>1년 균형형 상위 5</b>: ' + ', '.join(f'{NAME[c]}({pc(er(c, "h1"))})' for c in t1) + '. 괄호는 1년 기대 TSR이다.',
        '<b>3년 상위 5</b>: ' + ', '.join(f'{NAME[c]}(연 {pc(er(c, "h3"))})' for c in t3) + '.',
        '<b>5년 상위 5</b>: ' + ', '.join(f'{NAME[c]}(연 {pc(er(c, "h5"))})' for c in t5) + '.',
        f'<b>견고성</b>: {stab35}. {rob}'
        f'1년은 {NAME[t1[0]]} 1위가 {p1.stability}(상위 5 확률 {p1.p_top5*100:.0f}%)이고, 2~7위({names(mid17)})의 상위 5 확률은 '
        f'{min(pt17)*100:.0f}~{max(pt17)*100:.0f}%로 서로 자리를 바꿀 수 있다.',
        f'<b>지수 대비</b>: {ex_sent("h3")} {ex_sent("h5")} 기대 TSR이 같은 기간 국고채 수익률보다 낮은 종목이 1년 {stat["h1"]["below_rf"]}개, '
        f'3년 {stat["h3"]["below_rf"]}개, 5년 {stat["h5"]["below_rf"]}개다.',
        f'<b>분포의 비대칭</b>: 1년 손실확률은 {"26종목 모두" if pl["ploss50"] == NST else str(pl["ploss50"]) + "종목에서"} 50%를 넘고'
        f'({pc(pl["ploss_min"], signed=False)}~{pc(pl["ploss_max"], signed=False)}), 중앙값도 {"모두" if pl["med_neg"] == NST else str(pl["med_neg"]) + "종목에서"} 음수다. '
        f'기대값을 플러스로 만드는 것은 확률 20%의 낙관 그룹과 소수의 큰 상승 경로다. 예를 들어 현대차의 1년 기대값에서 낙관 그룹 기여(약 {bull_contrib("005380", "h1")[0]*100:.1f}%p)를 빼면 '
        f'약 {pp(bull_contrib("005380", "h1")[1])}다.',
        '<b>대형주가 위에 있는 이유</b>: 변동성이 상대적으로 낮아 Sortino·CVaR가 낫고, 두 분석가의 기대가 지수 근처로 모인다. 베이스레이트(H)도 대형 메모리·자동차 버킷에는 중립에 가까운 알파(−0.5%~+0.5%)를 준다. '
        '반대로 중소형 성장·테마주는 두 분석가 모두 현재가가 아직 실현되지 않은 이익을 반영했다고 봤다. 2026년 급등락 뒤의 베이스레이트(마니아 이후 3년 중앙값 약 −37%, H 원자료의 정수값)도 음의 알파를 준다.',
        f'<b>하위권</b>: 1년 {names(bottom("h1"))}, 3년 {names(bottom("h3"))}, 5년 {names(bottom("h5"))}.',
        '<b>판단을 바꿀 사건</b>: 10/28 발표된 SK하이닉스 3Q26 실적과 추가 환원(아래 상자, 순위에 반영하지 않음), 10월 말 현대차·현대모비스·삼성전자 3Q26 실적, 11/16 다수 종목 3분기보고서 기한, '
        '11/24 현대모비스 임시주총과 매수청구, 2027년 1월 삼성전자 잔여 환원 결정, 미국 자동차 관세(15% 유지 또는 25% 재부과).',
        f'<b>신뢰도</b>: 최종심사 기준 보통 {conf_cnt.get("보통", 0)}종목, 낮음 {conf_cnt.get("낮음", 0)}종목, 높음 {conf_cnt.get("높음", 0)}종목이다. '
        '공시 원문을 직접 열람하지 못했고, 대부분 종목의 3Q26 실적이 아직 나오지 않았다.',
    ]),
]
n['core'] = core

# ---------- 3부 ----------
n['rank_notes'] = ('<p class="note">읽는 법: 기대 TSR은 분기 확률가중 평균이라 분포가 오른쪽으로 길면 중앙값보다 훨씬 크다. 분포 막대에서 점(기대값)이 세로선(중앙값)보다 오른쪽에 있는 것이 그 표시다. '
                   'Sortino가 음수인 종목은 기대 TSR이 무위험수익률보다 낮다는 뜻이다. 신뢰도는 최종심사(J)가 매긴 등급이고, 안정성은 8부의 판정이다.</p>')

# ---------- 4부 ----------
piv = r.pivot_table(index='code', columns='h', values='rank_bal')
down = piv.assign(d=piv.h5 - piv.h1).sort_values('d', ascending=False)
upm = piv.assign(d=piv.h1 - piv.h5).sort_values('d', ascending=False)
dn3 = list(down.index[:3])
up3 = list(upm.index[:2])
big_all = all(set(top(h, 4)) == set(big4) for h in ('h1', 'h3', 'h5'))
n['rank_change'] = ('<p>' + '기간이 길어질수록 크게 밀리는 종목은 ' + ', '.join(f'{NAME[c]}({int(piv.loc[c, "h1"])}위 → {int(piv.loc[c, "h5"])}위)' for c in dn3) + josa(NAME[dn3[-1]], '이다. ', '다. ') +
                    '1년에는 수주·테마 기대와 사전값 비중이 기대값을 받쳐 준다. 그러나 기간이 길어지면 희석과 현금 소진이 쌓이고, 소형 적자주·통신장비 버킷의 음의 베이스레이트가 누적된다. '
                    '반대로 ' + ', '.join(f'{NAME[c]}({int(piv.loc[c, "h1"])}위 → {int(piv.loc[c, "h5"])}위)' for c in up3) + josa(NAME[up3[-1]], '은', '는') + ' 단기 이익 정체와 디레이팅을 지나 장기 이익이 반영되면서 올라간다. '
                    + ('대형 4종목은 세 기간 모두 1~4위를 지킨다.' if big_all else '') + '</p>')


# ---------- 5부 ----------
def spec_gen(c, h):
    x = R(c, h)
    return x.e_spec_ann, x.e_gen_ann


def detail(c, thesis, risks, review):
    return {'thesis': thesis, 'risks': risks, 'review': review, 'monitor': J[c]['key_monitoring']}


TOPS = list(dict.fromkeys(t1 + t3 + t5))
es, eg = spec_gen('012330', 'h1')
OTH = [c for c in TOPS if c != '012330']
td = {}
td['012330'] = detail('012330',
    f'<p>이익의 대부분은 현대차·기아 차량 보유대수에 연동된 A/S 부문에서 나온다(1H26 A/S 영업이익이 전사의 약 106%). 순현금, 현대차 지분, 2025~27년 총주주환원율 30% 이상 정책이 하방을 받친다. '
    f'두 분석가는 로봇(보스턴다이나믹스) 가치를 거의 인정하지 않고도 1년 {pc(es)}·{pc(eg)}의 기대(반대심문 조정 반영, 축소 전)를 냈다. '
    f'상위권의 핵심은 얕은 하방이다. 1년 비관 그룹의 확률가중 TSR이 {pc(grp("012330", "h1", "비관"))}로, 다른 상위 종목({pc(min(grp(c, "h1", "비관") for c in OTH))}~{pc(max(grp(c, "h1", "비관") for c in OTH))})보다 손실 폭이 작다.</p>',
    f'<p>원화가 1,320원 수준으로 강해지면 A/S 마진이 정점에서 내려올 수 있다. 미국 관세가 25%로 돌아가면 모듈 적자와 현대차 지분법이익이 함께 줄어든다. '
    f'램프 사업 물적분할은 매수청구 한도(2,300억원)를 넘으면 무산될 수 있다. 순현금 추정이 6조·7조·8조원으로 엇갈리는데, 2조원 차이가 시총의 약 6%라 순위를 바꿀 수 있다. '
    f'1년 기대값의 상당 부분(낙관 그룹 기여 약 {bull_contrib("012330", "h1")[0]*100:.1f}%p)이 낙관 그룹에서 나온다.</p>',
    '<p>반대심문(I)은 1년 기대값이 낙관 꼬리에 기댄다며 기준 0.97·낙관 0.95배 하향을 제안했다. 사실검증(V)은 실적·자사주·환원 정책을 모두 확인했고, 램프 분할이 분석에서 빠졌다고 지적했다. '
    f'최종심사(J)는 램프 분할, 기보유 자사주 소각의 환원율 산입 문제, 3Q26 하회 신호, 지배구조 개편 꼬리를 반영했다. "밴드 상단 배수" 같은 일반론은 축소 단계에 맡겼다. '
    f'채택한 배수는 {jm("012330")}다. {REJ.get("012330", "")}최종 신뢰도는 {J["012330"]["final_confidence"]}이다.</p>')

es, eg = spec_gen('005380', 'h1')
bc5380 = bull_contrib('005380', 'h1')
td['005380'] = detail('005380',
    '<p>P/B 0.7배대, 최소 주당배당 1만원(10/21 종가 기준 배당수익률 약 3.2%), 총주주환원율 35% 정책이 바닥을 받친다. '
    '1차 사실검증은 대미투자특별법이 2026-03-12 국회 본회의를 통과했다는 것을 보도(한국경제·아주경제 2026-03-12)로 확인했다. 그래서 관세 25% 재부과는 기본 경로보다 꼬리위험에 가깝다. '
    '이 결과는 검증 재실행 때 파일이 덮어써져 1차 심사에 빠졌다가, 독립 검증(Q) 뒤 복원돼 재심사에 반영됐다. 2차 검증은 232조 자동차 관세 15% 적용(2026-08 기준)을 확인했다. 미국 관보 기준 현행 세율은 확인하지 못했다. '
    f'기대수익은 지수를 밑돈다(1년 {pc(R("005380", "h1").exp_cum)}로 지수 대비 {pp(R("005380", "h1").excess_vs_index_ann)}, 5년 연 {pc(R("005380", "h5").exp_ann)}로 {pp(R("005380", "h5").excess_vs_index_ann)}).</p>',
    '<p>매출이 늘어도 영업이익이 줄고 있다(FY25 −19.5%, 1Q26 −30.8%, 2Q26 −20.8%). 3Q26 추정치는 직전 컨센서스보다 약 20% 낮아졌고 2026년 영업이익률 가이던스(6.3~7.3%)는 미달이 유력하다. '
    f'로봇 재평가의 전제인 보스턴다이나믹스 상장은 공식 계획이 없다. 1년 기대값에서 낙관 그룹 기여(약 {bc5380[0]*100:.1f}%p)를 빼면 '
    f'{"약 " + pp(bc5380[1]) + "로 음수다" if bc5380[1] < 0 else "약 " + pp(bc5380[1]) + "다"}.</p>',
    f'<p>I는 기준 0.93~0.97배, 낙관 0.92~0.94배 하향을 제안했다. J는 일반 분석가 기준 분기의 내부 모순(자기 2027E EPS의 9.7배로, 본인이 제시한 중앙 배수 7배와 어긋남)을 전문가 가중 {J["005380"]["w_spec"]:.2f}로 처리했다. '
    f'그리고 낙관 그룹의 로봇 분기 비중을 낮췄다. 채택한 배수는 {jm("005380")}다. {REJ.get("005380", "")}우선주 3종을 주당가치 분모에서 어떻게 다뤘는지는 확인하지 못했다. '
    f'최종 신뢰도는 {J["005380"]["final_confidence"]}이다.</p>')

td['000660'] = detail('000660',
    '<p>두 분석가 모두 시장이 이익 정점(2Q26 영업이익률 76%) 뒤의 정상화를 이미 크게 할인하고 있다고 봤다(2027E P/E 약 3배, 역DCF상 영구 영업이익 60~100조원. 10/20 종가 기준 분석가 추정이며 10/21 기준가는 약 6% 높다). '
    '순현금, FCF 50% 이상 환원 정책, 40조원으로 취득한 자사주 23,693,272주의 소각 예정이 3·5년 기대를 끌어올린다. '
    f'5년 기대 TSR(연 {pc(R("000660", "h5").exp_ann)})은 '
    + ('26종목 중 유일하게 지수 기대를 넘는다.' if stat['h5']['excess'] == ['000660'] else ('지수 기대를 넘는다.' if '000660' in stat['h5']['excess'] else '지수 기대에 못 미친다.')) + '</p>',
    '<p>기준 경로는 역대 가장 완만한 하강(2029년 저점 영업이익 125~170조원)과 2030년 이후 영업이익률 35~45%를 전제한다. '
    'HBM4 점유율(카운터포인트 기준 54%)과 삼성의 추격, 장기공급계약의 가격상한, 1Q27 범용 D램 계약가 상승률 둔화(+3~8%, 트렌드포스)가 하향 위험이다. '
    f'1년 변동성이 커서 1년 중앙값은 {pc(R("000660", "h1").median_cum)}다. 메모리 가격과 AI 설비투자가 기준보다 20% 낮은 스트레스에서는 1년 순위가 {srank("shock_memory_ai_capex_down", "000660", "h1")}위까지 내려간다.</p>',
    '<p>I는 강세론의 핵심은 타당하다고 보면서 기준 0.95~0.98배, 낙관 0.96배의 소폭 하향을 권고했다. V는 핵심 사실을 확인했고, 분석가 서술부의 수익률이 10/20 종가 기준이라는 점을 짚었다. 순위에는 10/21 기준 구조화 가격만 썼다. '
    f'J는 HBM 점유율, 가격상한, 계약가 둔화, 2029 저점에 P/B 1.5배를 두는 공통 프레임 불일치만 반영했다. 채택한 배수는 {jm("000660")}다. '
    f'전문가의 5년 주식수 −26.6% 가정이 정책 근거를 넘는다고 보아 전문가 가중은 {J["000660"]["w_spec"]:.2f}로 낮췄다. 최종 신뢰도는 {J["000660"]["final_confidence"]}이다.</p>')

h5g = r[r.h == 'h5']
td['005930'] = detail('005930',
    '<p>3Q26 잠정 영업이익 107.4조원, 2026년 환원 90~110조원 계획, 2Q26 말 순현금 약 168조원이 사실검증으로 확인됐다. '
    '두 분석가는 2028년 이익이 컨센서스보다 36~39% 낮을 것으로 보면서도, 현 주가가 함의한 영구 FCF(연 약 100조원. 10/20 종가 기준 분석가 추정이며 10/21 기준가는 약 6% 높다)보다 기준 경로가 높다고 판단했다. '
    f'5년 중앙값({pc(R("005930", "h5").median_cum)})은 26종목 중 {"가장 높고" if R("005930", "h5").median_cum >= h5g.median_cum.max() - 1e-12 else "상위권이고"}'
    f'(양수는 {names(list(h5g[h5g.median_cum > 0].sort_values("median_cum", ascending=False).code)) or "없음"}), '
    f'5년 손실확률({pc(R("005930", "h5").p_loss, signed=False)})은 26종목 중 {"가장 낮다" if R("005930", "h5").p_loss <= h5g.p_loss.min() + 1e-12 else "낮은 편이다"}.</p>',
    '<p>HBM에서 SK하이닉스에 뒤처져(엔비디아 루빈 HBM4 물량의 약 2/3가 SK하이닉스에 배정됐다는 보도) 범용 메모리 노출이 크다. '
    '반대심문은 과거 메모리 정점 뒤의 깊은 이익 감소 사례를 들어 정상화가 기준 경로보다 깊고 길 수 있다고 봤다. 최종심사는 이 논거를 일반론(정상이익 기저율)으로 보아 채택하지 않고 축소 단계에 맡겼다. '
    '이 논거의 가격 근거 일부(DDR5 소매가 약 6배, 마이크론 전망)는 기술 블로그 인용이다. '
    '15조원 자사주는 소각이 아닌 임직원 보상용이고, 1차 사실검증은 보상용 매입이 다년·대규모(보도상 80조원 규모)일 수 있다고 지적했다. 2027~29년 환원 정책은 아직 정해지지 않았다.</p>',
    '<p>I는 3년 기준 0.95배, 5년 기준 0.92배·낙관 0.95배를 제안하고 3Q26 배당 처리 확인을 요구했다. 코디네이터가 확인한 결과 두 분석가 모두 3Q26 배당(기준일 9/30)을 이미 뺐다. '
    f'J는 2029년 하강기 P/B 불일치와 보상용 자사주 처리의 불확실성을 반영했다. 채택한 배수는 {jm("005930")}다. {REJ.get("005930", "")}'
    'V는 분석가의 2026년 말 순현금 가정에 30조원 배당과 15조원 보상용 매입이 빠졌는지 확인하라고 권고했다. 이 부분은 확인하지 못했고, 빠졌다면 주당가치가 약 3% 과대다. '
    f'최종 신뢰도는 {J["005930"]["final_confidence"]}이다.</p>')

es, eg = spec_gen('189300', 'h1')
x_ = R('189300', 'h1')
shr_txt = (f'나온 순위다. 분석가 신뢰도가 낮아 축소 가중치가 {x_.shrink_w:.2f}에 그쳐 사전값 쪽 비중({1 - x_.shrink_w:.2f})이 더 크다' if x_.shrink_w < 0.5
           else f'나온 순위다(축소 가중 {x_.shrink_w:.2f})')
td['189300'] = detail('189300',
    '<p>위성통신 지상단(게이트웨이·사용자 단말·해상 안테나) 전문 업체다. 2025년 말 수주잔고가 매출의 약 1.34배로 추정된다(사실검증, 증권사 리포트 인용). '
    f'1년 {int(x_.rank_bal)}위는 두 분석가의 기대가 엇갈린 상태(전문가 {pc(es)}, 일반 {pc(eg)}, 반대심문 조정 반영)에서 {shr_txt}. '
    f'균형 순위는 {rks("189300")}다.</p>',
    '<p>영업현금흐름이 적자이고(FY25 −182억원) 매출채권이 매출보다 빨리 늘었다. Starlink·Amazon이 단말과 지상국을 내재화하면서 제3자 시장이 좁아지고 있고, 상위 3개 고객이 매출의 50%를 넘는다. '
    f'원화 강세는 마진에 불리하다. 1년 기대값에서 낙관 그룹 기여는 약 {bull_contrib("189300", "h1")[0]*100:.1f}%p다.</p>',
    '<p>I는 정체·비관 분기의 출구배수가 성공 분기보다 높은 내부 모순을 지적해 3·5년을 낮추자고 했다. V는 누락된 배당(주당 200원)과 자기주식을 뺀 분모를 상향 요인으로 짚었다. '
    f'J는 둘을 절반씩 반영했다. 채택한 배수는 {jm("189300")}다. '
    f'최종 신뢰도는 {J["189300"]["final_confidence"]}이다. 1년 판정은 \'{S("189300", "h1").stability}\'이고 상위 5 확률은 {S("189300", "h1").p_top5*100:.0f}%다.</p>')

td['010690'] = detail('010690',
    '<p>현대차·기아의 섀시·차체 1차 협력사이고 P/B는 약 0.43배다. 미국 조지아(HMGMA)·인도 공장의 램프업과 배터리 케이스 매출이 회복 경로를 이끈다. '
    f'균형 순위는 {rks("010690")}이고, 판정은 3년 \'{S("010690", "h3").stability}\'·5년 \'{S("010690", "h5").stability}\'{josa(S("010690", "h5").stability, "이다", "다")}(상위 5 확률 3년 {S("010690", "h3").p_top5*100:.0f}%, 5년 {S("010690", "h5").p_top5*100:.0f}%).</p>',
    '<p>순차입(2025년 말 약 4,780억원, 집계 사이트 기준·미검증)이 시가총액의 약 2배이고, 차입의 57%가 1년 안에 만기라는 집계도 있다(미검증). FCF는 3년 연속 적자이고 2Q26 영업이익률은 1.2%였다. '
    '현대차·기아의 관세 비용 분담 요구가 납품 단가 압력이 될 수 있다. 지수 강세장에서 소외된 이력(2025년 KOSPI 대용지수 +75.8%, 화신 +21.5%)이 있어 낙관 그룹 가정이 과할 수 있다. '
    f'1년 기대값에서 낙관 그룹 기여(약 {bull_contrib("010690", "h1")[0]*100:.1f}%p)를 빼면 약 {pp(bull_contrib("010690", "h1")[1])}다.</p>',
    '<p>I는 1년 기준 0.95배·낙관 0.90배 등 중간~강한 하향을 제안했다. J는 기준 분기의 디레버리징 가정이 실제 순차입 증가와 충돌하는 점, 지수 상승이 주가에 잘 전이되지 않은 점만 반영했다. '
    f'채택한 배수는 {jm("010690")}다. 비테마 시기 PER 4배 논거는 축소에 맡겼다. {REJ.get("010690", "")}'
    f'순차입이 ±500억원 달라지면 주당가치가 약 ±20% 움직여 최종 신뢰도는 {J["010690"]["final_confidence"]}이다.</p>')
td['000660']['monitor'] = [m + ' (60조원은 환원 규모다. 반대심문 원문은 1Q27 범용 D램 계약가 상승률 +5% 이상도 철회 조건으로 둔다)' if '60조' in m else m
                           for m in J['000660']['key_monitoring']]
missing = [c for c in TOPS if c not in td]
if missing:
    print('경고: 상위 종목 상세 서술 없음', [NAME[c] for c in missing])
n['top_detail'] = td
n['top_lead'] = (f'<p>{len(TOPS)}종목 모두 기대값이 확률 20%의 낙관 그룹에 크게 기댄다. 그래서 각 종목의 "무엇이 틀릴 수 있나"와 "확인할 사건"이 순위보다 중요한 정보다. '
                 '분석가 기대(전문가·일반)는 최종심사가 채택한 반대심문 조정을 반영한 축소 전 값이다.</p>')

# ---------- 6부 ----------
HB = json.load(open(f'{AN}/data/aux/H_base_rates.json'))['result']['priors']
cal = []
for b in HB:
    mem = [c for c in NAME if any(c in m for m in b['members'])]
    v = r[(r.h == 'h5') & (r.code.isin(mem))].p_loss50.mean()
    cal.append((b['bucket'].split(' ')[0], v, b['prob_perm_loss_gt50_5y_pct'] / 100))
above = [x for x in cal if x[1] > x[2]]
gap_min = min(cal, key=lambda x: x[1] - x[2])
CAL_ALL = len(above) == len(cal)
CAL_TXT = (f'{len(cal)}개 버킷 모두 베이스레이트보다 높고' if CAL_ALL else f'{len(cal)}개 버킷 중 {len(above)}개에서 베이스레이트보다 높고') + \
          f', 차이가 가장 작은 것은 {gap_min[0]}({pc(gap_min[1], signed=False)} 대 {gap_min[2]*100:.0f}%)다'
_vb = sens[(sens.run == 'base') & (sens.h == 'h5')].set_index('code').rank_bal
_vl = sens[(sens.run == 'vol_low') & (sens.h == 'h5')].set_index('code').rank_bal
VOL_MAXD = int((_vb - _vl).abs().max())
h5 = r[r.h == 'h5'].sort_values('p_loss30', ascending=False)
tail2 = list(h5.code[:2])
BOT = list(dict.fromkeys(bottom('h1') + bottom('h3') + bottom('h5')))
BOT_DETAIL = {
    '290650': f'엘앤씨바이오({rks("290650")}): 리투오 단일 제품 의존, ECM 스킨부스터 규제 강화 움직임(10/13 국정감사, "최소 조작" 재검토), 약 100개 경쟁 제품. '
              '주주배정 유상증자 370만주와 1:1 무상증자가 진행 중이다. 최종심사는 유증 대금이 주당가치에 가산됐는지 확인하지 못했고, 빠졌다면 약 7% 과소평가일 수 있다고 적었다.',
    '007660': f'이수페타시스({rks("007660")}): 원화 강세에 따른 2027E 영업이익 감소, 구글 TPU 공급사 다변화 위험, 반복된 주주배정 증자 이력.',
    '232140': f'와이씨({rks("232140")}): 삼성전자 단일 고객, 2027년 메모리 장비 수주 정점 뒤 2029년 저점이라는 공통 프레임, 연결 이익의 상당 부분이 비지배지분 몫.',
    '107640': f'한중엔시에스({rks("107640")}): 삼성SDI 단일 고객, 메자닌·종류주 전환 오버행(약 9.8%), 차입으로 짓는 미국 공장.',
    '042700': f'한미반도체({rks("042700")}): 두 분석가가 모두 3년 손실을 예상한다(같은 방향 불일치 보정 뒤 연 {pc(R("042700", "h3").exp_ann)}).',
    '032500': f'케이엠더블유({rks("032500")}): 2021년 이후 연속 영업적자, 추가 CB, 미국 통신장비 수요 시점의 불확실성. 5년 기대는 연 {pc(R("032500", "h5").exp_ann)}다.',
    '418420': f'라온텍({rks("418420")}): 법인세비용차감전손실 관리종목 요건, 코스닥 시가총액 상장유지 기준 상향(2027-07 300억원), CB 풋 상환 부담.',
}
n['bottom'] = '<h3>하위권의 공통점</h3>' + li(
    [f'하위권({", ".join(NAME[c] for c in BOT)}){josa(NAME[BOT[-1]], "은", "는")} 두 분석가가 모두 현재 주가가 정점 이익이나 아직 실현되지 않은 마진을 반영했다고 본 종목이 대부분이다.'] +
    [BOT_DETAIL[c] for c in BOT if c in BOT_DETAIL]) + \
    (f'<p>5년 −30% 이하 손실확률이 가장 높은 종목은 {NAME[tail2[0]]}({pc(R(tail2[0], "h5").p_loss30, signed=False)}){josa(NAME[tail2[0]], "과", "와")} '
     f'{NAME[tail2[1]]}({pc(R(tail2[1], "h5").p_loss30, signed=False)}){josa(NAME[tail2[1]], "이다", "다")}. '
     f'꼬리 확률 점검표에서 보듯 모형의 5년 −50% 이하 확률은 {CAL_TXT}. 변동성 가정을 15% 낮춰도 5년 균형 순위는 최대 {VOL_MAXD}계단만 바뀌어, 이 차이는 순위보다 손실확률·CVaR의 절대 수준에 영향을 준다.</p>')

# ---------- 7부 ----------
d1 = r[r.h == 'h1'].assign(diff=lambda x: (x.e_spec_ann - x.e_gen_ann).abs()).sort_values('diff', ascending=False).head(3)
_nf = r.assign(e_nofix=lambda x: x.shrink_w_raw * (1 + x.e_raw_cum) + (1 - x.shrink_w_raw) * (1 + x.prior_ann) ** x['T'] - 1)
_nf = _nf.assign(e_nofix_ann=lambda x: (1 + x.e_nofix) ** (1 / x['T']) - 1)
big_fix = _nf.loc[(_nf.exp_ann - _nf.e_nofix_ann).abs().idxmax()]
fixed = r[r.same_side_fix == 1].assign(g=lambda x: x.shrink_w - x.shrink_w_raw).sort_values('g', ascending=False).head(2)
damp = r.assign(base_w=lambda x: x.shrink_w_raw * (1 + (x.disagree_log_ann / x.h.map(D0)) ** 2))
damp = damp[damp.shrink_w < 0.95 * damp.base_w].sort_values('shrink_w')  # 보정 뒤에도 실효 가중이 기본 가중의 95% 미만


def adopt(c):
    """반대심문 제안 대비 최종심사 채택 비율(기준·낙관 배수의 하향 폭 기준). I가 하향을 제안한 칸만 센다.
    비관 배수는 재심사에서 관세 사실로 따로 정한 종목이 있어 비교에서 뺀다."""
    vals = []
    for h in ('h1', 'h3', 'h5'):
        for k in ('base_mult', 'bull_mult'):
            ip, jp = I[c]['adjustments'][h][k], J[c]['adjustments'][h][k]
            if ip < 0.995:
                vals.append(max(0.0, (1 - jp) / (1 - ip)))
    return (min(vals), max(vals)) if vals else None


ad4 = {c: adopt(c) for c in ('012330', '000660', '005380', '005930') if c in I and adopt(c)}
n_tail = sum(1 for s in J.values() for h in ('h1', 'h3', 'h5') if s['adjustments'][h].get('extra_tail_prob_pct', 0) > 0)
dil = {c: [f for role in v.values() for f in role.values() if f < 0.9999] for c, v in SET['dilution_fix'].items()}
dil = {c: v for c, v in dil.items() if v}
tariff_names = names(TARIFF)
n['disagreement'] = '<h3>무엇이 결과를 바꿨나</h3>' + li([
    '분석가 간 차이가 가장 큰 곳은 1년 ' + ', '.join(f'{x["name"]}(전문가 {pc(x.e_spec_ann)}, 일반 {pc(x.e_gen_ann)})' for _, x in d1.iterrows()) + josa(d1.iloc[-1]['name'], '이다. ', '다. ') +
    '차이가 크면 축소 가중치가 내려간다. 다만 두 분석가가 사전값의 같은 쪽에 있으면 같은 방향 보정으로 감쇠가 대부분 풀린다('
    + ', '.join(f'{x["name"]} {HL[x.h]} {x.shrink_w_raw:.2f}→{x.shrink_w:.2f}' for _, x in fixed.iterrows()) + f' 등 {NTOT}건 중 {SS_N}건). '
    + ('보정 뒤에도 감쇠가 남은 곳(실효 가중이 기본 가중의 95% 미만)은 ' + ', '.join(f'{x["name"]} {HL[x.h]}({x.shrink_w:.2f})' for _, x in damp.head(3).iterrows()) + f' 등 {len(damp)}건이다.' if len(damp) else ''),
    f'같은 방향 불일치 보정: 최종심사의 권고로, 두 분석가가 사전값의 같은 쪽에 있을 때 불일치 감쇠가 결과를 덜 극단적인 분석가 값이나 감쇠 없는 축소값 너머로 끌고 가지 못하게 했다. '
    f'영향이 가장 큰 곳은 {big_fix["name"]} {HL[big_fix.h]}{josa(HL[big_fix.h], "이다", "다")}(축소 가중 {big_fix.shrink_w_raw:.2f} → {big_fix.shrink_w:.2f}, 기대 연 {pc(big_fix.e_nofix_ann)} → {pc(big_fix.exp_ann)}). '
    '보정은 사전값 쪽으로 당기는 힘을 줄일 뿐이라, 두 분석가가 모두 사전값보다 낮게 본 종목의 기대는 오히려 낮아진다.',
    f'반대심문(I) {len(I)}건에서 제안된 하향 배수 가운데 최종심사는 사실 근거가 있는 부분만 채택했다. 기준·낙관 배수의 하향 폭으로 본 채택 비율은 '
    + ', '.join(f'{NAME[c]} {lo*100:.0f}~{hi*100:.0f}%' for c, (lo, hi) in ad4.items()) + '다. 삼성에피스홀딩스의 순차입 보정은 1·3년에 그대로 채택됐다. '
    + ('추가 꼬리 분기는 한 건도 채택되지 않았다. ' if n_tail == 0 else f'추가 꼬리 분기는 {n_tail}건 채택됐다. ')
    + '"배수가 높다", "성장이 기저율을 넘는다" 같은 일반론은 축소 단계와 겹치므로 채택하지 않았다.',
    '사실검증(V)이 결과를 바꾼 사실: 삼성에피스홀딩스의 순현금 가정 오류(증거는 순차입을 가리킴, 기준·낙관·비관 0.91~0.95배), 쎄트렉아이 기술유출 의혹의 경찰 불송치 종결(1년 비관 1.03배), '
    '현대모비스 램프 분할 누락, 인텔리안테크 배당 누락. '
    + (f'덮어써졌다가 복원된 1차 검증의 대미투자특별법 통과는 재심사에서 비관 분기에 관세 25%를 넣은 {len(TARIFF)}종목({tariff_names})의 비관 배수에 반영됐고, '
       '삼성전자의 다년 보상용 자사주 매입 가능성은 3·5년 배수에 반영됐다.' if RE else ''),
    '포렌식이 바꾼 사실: 선익시스템은 두 분석가가 자기주식을 뺀 유통주식 대신 상장주식 수를 분모로 쓴 것으로 보여, 그 차이의 절반을 반영해 1.03배로 올렸다.',
    ('희석 보정: 포렌식이 분석가보다 더 큰 신주 발행을 본 ' + names(list(dil)) + f'에 {min(min(v) for v in dil.values()):.2f}~{max(max(v) for v in dil.values()):.2f}배를 적용했다. ' if dil else '희석 보정은 적용된 종목이 없다. ')
    + 'SK하이닉스처럼 자사주 소각 가정만 다른 경우(전문가 5년 −26.6%, 포렌식 −9%)는 보정하지 않았다.',
])

# ---------- 8부 ----------
lines = []
for h in ('h1', 'h3', 'h5'):
    base = set(top(h))
    agg = set(r[r.h == h].sort_values('rank_agg').code[:5])
    dfn = set(r[r.h == h].sort_values('rank_def').code[:5])
    diff = (agg ^ base) | (dfn ^ base)
    lines.append(f'{HL[h]}: 공격형·방어형 가중으로 바꿔도 상위 5 구성은 ' + ('같다.' if not diff else '일부 바뀐다(' + names(sorted(diff)) + ').'))
mb = {h: [srank('macro_bear', c, h) for c in top(h)] for h in ('h1', 'h3', 'h5')}
lines.append('거시 비관 확률을 45%로 올리면 상위 5의 균형 순위는 1년 ' + ', '.join(f'{NAME[c]} {v}위' for c, v in zip(top('h1'), mb['h1'])) + '가 된다.')
mem = {c: srank('shock_memory_ai_capex_down', c, 'h1') for c in ('000660', '005930')}
tar = {c: srank('shock_auto_tariff_25pct', c, 'h1') for c in ('005380', '012330')}
lines.append(f'스트레스 충격은 업종 노출대로 순위를 흔든다. 메모리·AI capex가 20% 낮으면 1년 순위가 SK하이닉스 {mem["000660"]}위, 삼성전자 {mem["005930"]}위로 내려간다. '
             f'자동차 관세 25%에서는 현대차 {tar["005380"]}위, 현대모비스 {tar["012330"]}위가 된다.')
gap_med = {}
for h in ('h1', 'h3', 'h5'):
    g = r[(r.h == h) & (r.rank_bal.between(6, 20))]
    e = (g.exp_cum if h == 'h1' else g.exp_ann).sort_values()
    gap_med[h] = float(e.diff().dropna().median())
lines.append(f'순위 안정성 판정: 1년 안정 {stat["h1"]["stab"].get("안정", 0)}·주의 {stat["h1"]["stab"].get("주의", 0)}·불안정 {stat["h1"]["stab"].get("불안정", 0)}, '
             f'3년 {stat["h3"]["stab"].get("안정", 0)}·{stat["h3"]["stab"].get("주의", 0)}·{stat["h3"]["stab"].get("불안정", 0)}, '
             f'5년 {stat["h5"]["stab"].get("안정", 0)}·{stat["h5"]["stab"].get("주의", 0)}·{stat["h5"]["stab"].get("불안정", 0)}. '
             f'중위권(6~20위)은 기대수익을 크기순으로 늘어놓았을 때 이웃한 종목 간 차이가 작아(중앙값 1년 {gap_med["h1"]*100:.1f}%p, 3년 연 {gap_med["h3"]*100:.1f}%p, '
             f'5년 연 {gap_med["h5"]*100:.1f}%p) 순위 자체의 의미가 작다.')
n['sensitivity_lead'] = '<h3>요약</h3>' + li(lines)
n['sensitivity'] = ''

# ---------- 9부 ----------
def stab_short(h, codes):
    v = [S(c, h).stability for c in codes]
    return f'판정 모두 {v[0]}' if len(set(v)) == 1 else '판정 ' + ', '.join(v)


c_med = h5g.sort_values('median_cum', ascending=False).code.iloc[0]
c_pl = h5g.sort_values('p_loss').code.iloc[0]
def_txt = (f' {NAME[c_med]}{josa(NAME[c_med], "은", "는")} 5년 중앙값과 손실확률에서 가장 방어적이다.' if c_med == c_pl else
           f' 5년 중앙값은 {NAME[c_med]}, 손실확률은 {NAME[c_pl]}{josa(NAME[c_pl], "이", "가")} 가장 낫다.')
n['final'] = li([
    f'<b>1년</b>: {NAME[t1[0]]}{josa(NAME[t1[0]], "이", "가")} 1위다(판정 {p1.stability}, 상위 5 확률 {p1.p_top5*100:.0f}%). 2~7위는 추정오차를 넣으면 서로 자리를 바꿀 수 있다. '
    + ('모든 종목의 1년 기대 TSR이 지수 기대를 밑돌고' if not pl['excess'] else f'1년 기대 TSR이 지수 기대를 넘는 종목은 {names(pl["excess"])}뿐이고')
    + (' 손실확률이 50%를 넘는다.' if pl['ploss50'] == NST else f' {pl["ploss50"]}종목의 손실확률이 50%를 넘는다.'),
    f'<b>3년</b>: 상위 5는 {names(t3)}{josa(NAME[t3[-1]], "이다", "다")}({stab_short("h3", t3)}). {ex_sent("h3")}',
    f'<b>5년</b>: 상위 5는 {names(t5)}{josa(NAME[t5[-1]], "이다", "다")}({stab_short("h5", t5)}). {ex_sent("h5")}{def_txt}',
    '<b>하위권</b>: 두 분석가가 모두 현재가가 미실현 이익을 반영했다고 본 중소형 성장·테마주가 대부분이다. 하위권 판정은 1·3·5년에 걸쳐 대체로 일관된다.',
    '<b>판단을 바꿀 조건</b>: 삼성전자 2027년 1월 잔여 환원 75조원 이상과 소각 포함(상향), 보상용 자사주의 다년 매입 확인(삼성전자 3·5년 추가 하향), '
    f'미국 자동차 관세 25% 재부과 공고({tariff_names or "현대차·현대모비스·화신"} 하향, 재심사가 올린 비관 배수를 되돌림), 현대모비스 매수청구 한도 초과(분할 철회), 화신 3Q26 순차입 확정, '
    '1Q27 범용 D램 계약가가 전분기보다 낮아지는 경우(메모리 하향).',
    '<b>이 보고서가 하지 않는 것</b>: 개인의 위험선호와 재무상황을 모르므로 매수·매도 판단이나 투자비중을 제시하지 않는다. 순위는 같은 가정과 같은 방법으로 비교한 상대적 위치이며, 확률은 모두 모형 추정치다.',
])

# ---------- 체크리스트 ----------
qi = pd.Series([x['severity'] for x in Q['issues']]).value_counts().to_dict()
n['qc'] = [
    {'item': '26개 종목 식별(법인명·시장·상장 이력·거래 가능 여부)', 'status': '부분', 'note': '26종목 모두 식별했다. 15종목은 식별 단계에서 검색 한도로 독립 검색 없이 데이터셋과 내부 지식으로 점검했고, 분석 단계에서 웹검색으로 보완했다.'},
    {'item': '기준가·기간·무위험수익률을 전 종목에 같게 적용', 'status': '통과', 'note': '2026-10-21 KRX 종가, 종료일 2027/2029/2031-10-22, 국고 1·3·5년 3.688/3.822/3.965%.'},
    {'item': '시나리오 확률 합 100%, 거시 그룹 50/20/30', 'status': '통과', 'note': '156개 트리(26종목×3기간×2분석가) 모두 합이 맞아 비례 조정이 0건이었다. 독립 검증(Q)이 결합 후 분기 945개에서도 확인했다.'},
    {'item': '기대·중앙값·P10·P90·손실확률·−30% 손실확률·CVaR10·Sortino·지수 대비 초과·신뢰도 산출', 'status': '통과',
     'note': '종목·기간별 200,000 경로. 기대 TSR은 분기 확률가중 정확값이고(독립 검증 지적 반영), 나머지 분포 지표는 경로에서 계산했다. 신뢰도는 최종심사 등급.'},
    {'item': '축소를 한 번만 적용(이중 벌점 없음)', 'status': '통과',
     'note': f'사전값 축소는 종목·기간마다 한 번이다(Q 확인). 반대심문의 일반론은 채택하지 않게 했고, 같은 방향 불일치 보정({NTOT}건 중 {SS_N}건)으로 과도한 감쇠를 막았다.'},
    {'item': '균형형(60/25/15) 순위와 공격형·방어형 민감도', 'status': '통과', 'note': '3부·8부.'},
    {'item': '순위 불안정 표시', 'status': '통과', 'note': '가정 변경 8종(가중 프로필 2, 거시 확률 2, 전문가 가중 2, 축소 강도 1, 변동성 1)과 추정오차 부트스트랩 4,000회로 안정·주의·불안정을 판정했다. '
                                                    '축소 강도 실행이 같은 방향 보정에 막혀 효과가 없던 문제를 독립 검증 뒤 고쳐 다시 계산했다.'},
    {'item': '확률을 확정적 사실처럼 표현하지 않음', 'status': '통과', 'note': '모든 확률·기대값을 모형 추정치로 표기했다.'},
    {'item': '확인되지 않은 값은 "확인 불가" 또는 N/A', 'status': '부분',
     'note': '식별표의 10/22 종가 등. 종가인지 확인하지 못한 시세 페이지 값(현대모비스·와이씨 10/22)과 집계 사이트 수치(화신 순차입 등)에 (미검증)을 붙이지 않은 곳이 있었고, 독립 검증 뒤 표시했다.'},
    {'item': '익명 게시물·출처 불명 블로그·홍보성 콘텐츠·유튜브에 의존하지 않음', 'status': '부분',
     'note': '근거로 쓰지 않게 했다. 반대심문 근거 가운데 기술 블로그를 인용한 논거가 1건 있었고, 최종심사는 이를 일반론으로 보아 채택하지 않았다. 공시 원문 대신 2차 집계 사이트 수치를 쓴 곳과 AI 요약 페이지를 인용한 곳이 있고, 해당 값은 "미검증" 또는 "신뢰도 낮음"으로 표시했다.'},
    {'item': '유료 데이터베이스 접근을 가장하지 않음', 'status': '통과', 'note': '접근하지 않았고 그렇게 적었다.'},
    {'item': '매매 지시·투자비중을 제시하지 않음', 'status': '통과', 'note': '1부·9부에 명시.'},
    {'item': '수익률은 소수 첫째 자리', 'status': '통과', 'note': 'Sortino·축소 가중 등 비율은 소수 둘째 자리.'},
    {'item': '공시 원문(DART·KRX) 대조', 'status': '미흡', 'note': '실행 환경에서 직접 접속이 막혀 보도·요약을 통해서만 확인했다.'},
    {'item': '최신 실적 반영', 'status': '부분', 'note': '대부분 종목의 3Q26 실적이 분석 시점에 발표 전이었다. 분석 뒤 발표된 SK하이닉스 실적은 순위에 반영하지 않고 따로 적었다.'},
    {'item': '꼬리 확률의 베이스레이트 정합성', 'status': '부분',
     'note': f'모형의 5년 −50% 이하 확률이 {"모든" if CAL_ALL else "대부분"} 버킷에서 베이스레이트보다 높다. 순위 영향은 작다(변동성 −15% 시 최대 {VOL_MAXD}계단).'},
    {'item': '단계 간 결과 전달', 'status': '부분',
     'note': '워크플로 재개 때 사실검증 2건(현대차·삼성전자)이 다시 실행돼 1차 결과를 덮어썼고, 대미투자특별법 통과 등이 최종심사에 전달되지 않았다. '
             f'독립 검증(Q)이 찾아냈고, 1차 결과를 복원해 {len(RE)}종목({names(list(RE))})을 재심사했다. 같은 이유로 포렌식 3건도 두 번 실행됐는데 두 번째 결과를 모든 단계에서 일관되게 썼다.'},
    *([{'item': '재검증(Q2)', 'status': '통과',
        'note': f'Q 지적의 조치와 재심사 병합을 다시 대조했다. 핵심 조치는 모두 확인됐고, 남은 낮음 {len(Q2["issues"])}건도 조치했다(아래 표).'}] if Q2 else []),
    {'item': '독립 검증(Q)', 'status': '통과',
     'note': f'높음 {qi.get("높음", 0)}건·중간 {qi.get("중간", 0)}건·낮음 {qi.get("낮음", 0)}건을 지적받아 모두 조치했다(아래 표). 아래 Q 판정은 수정 전 보고서에 대한 것이다.'},
]


def st_cnt(h):
    return f'{stat[h]["stab"].get("안정", 0)}·{stat[h]["stab"].get("주의", 0)}·{stat[h]["stab"].get("불안정", 0)}'


n['q_fixes'] = {
    '0': '원인은 재실행으로 덮어써진 1차 사실검증(V1) 파일이었다. V1(한국경제·아주경제 2026-03-12 보도 인용)을 복원해 근거를 남기고, 이를 최종심사에 넘겨 자동차 3종목을 재심사했다. '
         f'그 재심사의 권고에 따라 비관 분기에 관세 25%를 넣은 나머지 종목도 같은 기준으로 재심사했다(대상 {tariff_names}). 5부·7부 서술은 출처와 경위를 밝혀 고쳤다.',
    '1': f'축소 강도를 같은 방향 보정 뒤의 최종 축소 결과에 적용하도록 고치고 민감도를 다시 계산했다. 재계산 판정(안정·주의·불안정)은 1년 {st_cnt("h1")}, 3년 {st_cnt("h3")}, 5년 {st_cnt("h5")}이다.',
    '2': '기대 TSR을 분기 확률가중 정확값으로 바꾸고 기대 순위·Sortino·지수 대비·균형 순위를 모두 다시 계산했다. 경로는 분위수·손실확률·CVaR·하방편차에만 쓴다.',
    '3': '민감도 실행을 최종 계산과 같은 20만 경로·같은 시드로 다시 돌렸고, 색 표시 기준을 같은 실행의 기준 순위로 바꿨다.',
    '4': f'부록 C에 같은 방향 보정을 설명했고(적용 {SS_N}/{NTOT}건), 7부 문장을 실효 가중 기준으로 고쳤다. 수치는 데이터에서 직접 만든다.',
    '5': '5년 중앙값 서술을 데이터에서 직접 만들게 바꿨다(양수 종목을 모두 적음).',
    '6': '현대모비스·와이씨 10/22 종가에 (미검증)을 붙이고 표 주석을 고쳤다. 화신 순차입과 단기 만기 비중은 집계 사이트 기준·미검증으로 표시했다. 체크리스트 해당 항목을 부분으로 바꿨다.',
    '7': '수치에 보도 기준·미검증을 표시했다. 최종심사가 적은 조건을 그대로 옮기고 60조원이 환원 규모이며 반대심문 원문에 1Q27 계약가 조건도 있다는 점을 밝혔다. '
         '60조원에 기존 40조원 매입분이 포함되는지 확인하지 못해 "해당할 수 있다"로 고쳤다. 5부 확인할 사건에도 같은 설명을 붙였다.',
    '8': 'B2 출처와 별개인 마감 속보(stockhub.kr, 10/22)의 등락률 −5.49%와 대조했다(코디네이터 웹검색, data/aux/A_coordinator_checks.json에 기록). '
         '10/21 KRX 종가 1,294,000원(일별 자료)에 −5.49%를 적용하면 호가 단위로 1,223,000원 하나뿐이라 B2 값과 맞는다. 종가 숫자 자체는 검색 결과에서 보지 못했다. '
         '10/20 종가와 같은 것은 이틀 등락폭이 모두 71,000원이라서다. 순위 계산에는 쓰지 않는다.',
    '9': '두 서술에 10/20 종가 기준 분석가 추정이라는 점과 10/21 기준가가 약 6% 높다는 점을 적었다.',
    '10': '채택 비율을 배수 하향 폭 기준으로 데이터에서 계산해 종목별로 적었다(재심사 반영).',
    '11': '중위권 문장을 기대수익을 크기순으로 늘어놓았을 때 이웃한 종목 간 차이의 중앙값으로 바꿨다(데이터에서 계산).',
    '12': '기대값을 정확값으로 바꿔 표시값과 낙관 그룹 기여 계산이 같은 기준이 됐다.',
    '13': '버킷 비교 문장과 체크리스트를 데이터에서 만들게 바꿨다.',
    '14': '지수 대비 차이를 함께 적어 "지수를 밑돈다"로 고쳤다.',
    '15': '1부 첫 문장을 기간별 견고성 차이가 드러나게 바꾸고 판정 결과에서 직접 만들게 했다.',
    '16': '범위를 소수 첫째 자리로 고치고, −37%에 H 원자료 정수값임을 밝혔다. 1부 표 손실확률을 소수 첫째 자리로, 3부 지수 대비 단위를 %p로 바꿨다.',
    '17': '비고를 10/21 기준 시총 약 470억원, 60일 평균 거래대금 약 1.5억원으로 고치고, 식별표의 시총·거래대금 열을 억원 단위로 바꿨다.',
    '18': '조사를 끝 글자 받침에 맞춰 붙이도록 고쳤다.',
    '19': '머리말에 총괄을 뺀 108개라고 밝히고, 부록 B에 삼성전자 반대심문 6회, 재심사 횟수, 재개 때 다시 실행된 에이전트 5개를 적었다.',
    '20': '5부에 블로그 인용 사실과 최종심사의 미채택(일반론으로 보아 축소 단계에 맡김)을 적고, 체크리스트와 부록 A에 블로그 1건과 AI 요약 페이지 인용을 밝혔다.',
}

if Q2:
    n['q2_fixes'] = {
        '0': '5부 문장을 최종심사 파일의 근거대로 고쳤다(일반론으로 보아 축소 단계에 맡김). 블로그 인용은 사실로만 적었고, 체크리스트·부록 A·조치표 20번도 같이 고쳤다.',
        '1': '부록 B 주석을 서진시스템 1년 1.0%p가 가장 크고 나머지는 0.5%p 이내라고 고쳤다.',
        '2': f'감쇠가 남은 곳을 실효 가중이 기본 가중의 95% 미만인 곳으로 다시 셌다({len(damp)}건, 같은 방향 보정이 걸린 행 포함).',
        '3': '중위권 차이를 소수 첫째 자리로 적고, 체크리스트의 예외 설명을 지웠다.',
        '4': '코디네이터가 찾은 마감 속보의 제목·URL·대조 결과를 data/aux/A_coordinator_checks.json에 기록하고 조치표 8번을 고쳤다. 종가 숫자 자체는 확인하지 못했다는 점도 적었다.',
        '5': '상자와 5부 확인할 사건에 60조원이 환원 규모이고 반대심문 원문에는 1Q27 계약가 +5% 이상 조건도 있다는 점을 붙였다.',
    }

# ---------- 분석 이후 사건(순위에 반영하지 않음) ----------
n['post_events'] = ('<b>분석 이후 확인된 사건(순위에 반영하지 않음)</b>: SK하이닉스는 2026-10-28 3Q26 매출 104.6조원, 영업이익 83.3조원(컨센서스 약 77조원)과 '
                    '2026년 약 100조원 규모의 주주환원 계획(현금배당 30조원 이상, 자사주 매입·소각 60조원)을 발표했다고 보도됐다(CNBC·서울경제 2026-10-28, 보도 기준·미검증). '
                    '최종심사가 미리 적은 조건은 "영업이익 70조원 미만 또는 환원 40조원 미만이면 하향, 60조원 초과면 조정 철회"다. 60조원은 10-28 환원 규모이고, '
                    '이 조건의 출처인 반대심문 원문은 1Q27 범용 D램 계약가 상승률 +5% 이상도 철회 조건으로 둔다. 보도대로라면 하향 조건에는 해당하지 않는다. '
                    '환원 규모 조건에는 해당할 수 있지만, 발표된 매입·소각 60조원에 10/21에 끝난 40조원 매입분이 포함되는지는 확인하지 못했다. 계약가 조건은 2027년 초에야 알 수 있다. '
                    '이 보고서의 순위는 2026-10-21 가격과 10-22까지의 정보로 계산했고, 발표 뒤 주가도 크게 움직였다(미국 상장 ADR 장중 +11% 보도). '
                    '그래서 수치를 다시 계산하지 않았다. 다른 종목의 3Q26 실적도 반영하지 않았다.')

# ---------- 식별표 비고(퓨런티어: 10/21 기준 시총·거래대금) ----------
m_ = risk.loc['370090']
n['id_notes']['370090'] = (f'2022-02 상장. 10/21 시총 약 {round(float(m_.mcap_krw_bn) * 10, -1):,.0f}억원으로, 상향되는 코스닥 시총 상장유지 기준에 노출돼 있다. '
                           f'60일 평균 거래대금 약 {float(m_.adv60_krw_bn) * 10:.1f}억원.')

# ---------- 부록 ----------
ax = open(os.path.join(AN, 'report', 'appendix.html')).read()
ax = (ax.replace('{{SAME_SIDE}}', f'{SS_N}/{NTOT}건').replace('{{J_RUNS}}', str(len({v['run'] for v in RE.values()})))
        .replace('{{J_STOCKS}}', f'{len(RE)}종목({names(list(RE))})' if RE else '0종목')
        .replace('{{PLOSS1}}', '26종목 모두' if pl['ploss50'] == NST else f'{pl["ploss50"]}종목에서')
        .replace('{{Q2_NOTE}}', '(재검증 1회 별도)' if Q2 else '')
        .replace('{{Q2_WHAT}}', '. 재검증은 지적별 조치와 재심사 병합을 다시 대조' if Q2 else ''))
assert '{{' not in ax, '부록 빈칸이 남았다'
n['appendix'] = ax
json.dump(n, open(P, 'w'), ensure_ascii=False, indent=1)
print('wrote', P, list(n.keys()))
