"""종목별 분석 워크플로 스크립트(JS)를 데이터와 함께 생성한다.

생성된 스크립트는 args={"codes": [...]}로 실행하며, 종목마다
D(산업 전문가+가치평가) → [독립 일반 분석가, E(회계·포렌식)]를 실행한다.
"""
import json
import sys

SCR = '/tmp/claude-0/-home-user-fictional-engine/53597674-b69d-5832-baad-c5e925f14216/scratchpad/kr'
AN = '/home/user/fictional-engine/analysis'
macro = json.load(open(f'{AN}/data/macro.json'))['synth']
ver = json.load(open(f'{AN}/data/verify_round1.json'))
foren = json.load(open(f'{AN}/data/forensic_round1.json'))
packs = json.load(open(f'{SCR}/datapacks.json'))

NAMES = {'000660': 'SK하이닉스', '005930': '삼성전자', '207940': '삼성바이오로직스', '0126Z0': '삼성에피스홀딩스',
         '005380': '현대차', '012330': '현대모비스', '307950': '현대오토에버', '295310': '에이치브이엠',
         '452430': '사피엔반도체', '418420': '라온텍', '370090': '퓨런티어', '010690': '화신',
         '290650': '엘앤씨바이오', '314930': '바이오다인', '171090': '선익시스템', '178320': '서진시스템',
         '007660': '이수페타시스', '107640': '한중엔시에스', '218410': 'RFHIC', '189300': '인텔리안테크',
         '099320': '쎄트렉아이', '403870': 'HPSP', '032500': '케이엠더블유', '098460': '고영',
         '232140': '와이씨', '042700': '한미반도체'}
SEMI = '반도체·AI하드웨어·디스플레이장비'
AUTO = '자동차·전장·SDV·부품'
BIO = '바이오의약품·의료기기·진단'
SPACE = '우주항공·위성통신·5G·6G'
ESS = 'ESS·산업재·특수소재'
SECTOR = {'000660': SEMI, '005930': SEMI, '042700': SEMI, '403870': SEMI, '232140': SEMI, '007660': SEMI,
          '098460': SEMI, '171090': SEMI, '452430': SEMI, '418420': SEMI,
          '295310': ESS, '178320': ESS, '107640': ESS,
          '005380': AUTO, '012330': AUTO, '307950': AUTO, '010690': AUTO, '370090': AUTO,
          '207940': BIO, '0126Z0': BIO, '290650': BIO, '314930': BIO,
          '218410': SPACE, '189300': SPACE, '099320': SPACE, '032500': SPACE}
GOOD_FORENSIC = {c for c, x in foren.items() if x['searches'] >= 10}


def bnote(c):
    s = ver.get(c)
    if not s:
        return '확인 불가(검증 에이전트 결과 없음)'
    tag = '[B 에이전트 검증, 웹검색 사용]' if s['searches_agent'] > 0 else '[B 에이전트 초안, 웹검색 불가 상태에서 작성 — 전부 미검증으로 취급]'
    parts = [tag, '법인명: ' + s['legal_name'], '상장 이력: ' + s['listing_history'],
             '거래정지·관리·투자경고 등: ' + s['halt_or_admin_issues'],
             '주식수: ' + s['shares_listed'] + ' / 자기주식: ' + s['treasury_shares'] + ' / 완전희석: ' + s['fully_diluted_shares'],
             '최근 보고서: ' + s['latest_reported_period'], '예정 이벤트: ' + s['upcoming_events'],
             '최근 종가(찾은 것): ' + '; '.join(f"{x['date']} {x['close_krw']:,.0f}원" for x in s['latest_closes_found']),
             '특이사항: ' + ' / '.join(s['data_flags'])]
    return ' | '.join(parts)[:2600]


def draft(c):
    x = foren.get(c)
    if not x or c in GOOD_FORENSIC:
        return ''
    r = x['result']
    keep = {k: r.get(k) for k in ['dilutive_instruments', 'share_count_changes_explained', 'shareholder_returns',
                                  'treasury_shares', 'ownership_overhang', 'governance', 'balance_sheet', 'red_flags']}
    return json.dumps(keep, ensure_ascii=False)[:4500]


DATA = {}
for c, n in NAMES.items():
    DATA[c] = {'code': c, 'name': n, 'sector': SECTOR[c], 'pack': packs[c], 'bnote': bnote(c),
               'forensic_redo': c not in GOOD_FORENSIC, 'draft': draft(c)}

GUIDE = {g['sector']: g['guidance'] for g in macro['sector_guidance']}
# 섹터 이름 정규화(C3 출력 표기와 맞춤)
def guide_for(sector):
    for k, v in GUIDE.items():
        if k.replace(' ', '').replace('/', '·')[:4] == sector.replace(' ', '')[:4]:
            return v
    for k, v in GUIDE.items():
        if sector[:2] in k:
            return v
    return ''
SECTOR_GUIDE = {s: guide_for(s) for s in [SEMI, AUTO, BIO, SPACE, ESS]}
for s, g in SECTOR_GUIDE.items():
    assert g, s

sc_lines = []
for sc in macro['scenarios']:
    k, q = sc['kospi_tsr_pct'], sc['kosdaq_tsr_pct']
    sc_lines.append(f"- {sc['name']} (확률 {sc['prob_pct']}%): KOSPI TSR 1년 {k['h1_cum']}% / 3년 연 {k['h3_ann']}% / 5년 연 {k['h5_ann']}%, "
                    f"KOSDAQ 1년 {q['h1_cum']}% / 3년 연 {q['h3_ann']}% / 5년 연 {q['h5_ann']}%")
MACRO = ('[공통 거시 프레임워크 — Agent C 산출물, 모든 분석가 필수 적용]\n' + macro['common_brief'] +
         '\n\n[시나리오별 지수 TSR]\n' + '\n'.join(sc_lines) +
         f"\n\n[무위험수익률(국고, 2026-10-21)] 1년 {macro['rf']['h1_pct']}%, 3년 {macro['rf']['h3_pct']}%, 5년 {macro['rf']['h5_pct']}%" +
         '\n\n[일관성 규칙]\n' + '\n'.join('- ' + r for r in macro['consistency_rules']))

template = open(f'{AN}/workflows/stock_template.js').read()
script = (template.replace('__DATA__', json.dumps(DATA, ensure_ascii=False))
          .replace('__MACRO__', json.dumps(MACRO, ensure_ascii=False))
          .replace('__GUIDE__', json.dumps(SECTOR_GUIDE, ensure_ascii=False)))
out = sys.argv[1]
open(out, 'w').write(script)
print('wrote', out, len(script), 'chars; forensic redo:', sorted(c for c in DATA if DATA[c]['forensic_redo']).__len__())
