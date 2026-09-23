import re
T = {'A': '「건축」', 'B': '「여행의 미래」'}
def conv_judge(src, mapping, name):
    t = open(src, encoding='utf-8').read()
    t = re.sub(r'^# judge\.md', f'# {name}', t, flags=re.M)
    t = re.sub(r'\n도구 사용:.*', '', t)
    t = re.sub(r'[PQ](「[^」]+」)', r'\1', t)
    t = re.sub(r'(?<![A-Za-z])([PQ])(?=\d)', lambda m: mapping[m.group(1)], t)
    t = re.sub(r'(?<![A-Za-z])([PQ])(?![A-Za-z0-9])', lambda m: T[mapping[m.group(1)]], t)
    t = re.sub(r'\*\*([A-F]) ', r'**축\1 ', t)
    t = re.sub(r'\s*\*\*d=[^*]+\*\*', '', t)
    t = re.sub(r' d=[+-]?\d\*\*', '**', t)
    t = re.sub(r'\n±2는 주지 않았다[^\n]*\n', '\n', t)
    t = re.sub(r'\*\*잠정 판정\**:?\**[^\n]*\n', '[조정자 삭제: 잠정 종합 판정과 수치]\n', t)
    t = re.sub(r'\n\*\*(좌우 근거|근거\[가치\]:)\*\*:?\n(\d\.[^\n]*\n)+', '\n[조정자 삭제: 종합 판정을 좌우한 근거 목록]\n', t)
    return t
def conv_reading(src, letter):
    t = open(src, encoding='utf-8').read()
    t = re.sub(r'\n도구 사용:.*', '', t)
    t = re.sub(r'(?<![A-Za-z])L(?=\d)', letter, t)
    return t
open('inputs/phase2/report_X.md','w',encoding='utf-8').write(conv_judge('judge_2.md', {'P':'B','Q':'A'}, '비교 보고서 X'))
open('inputs/phase2/report_Y.md','w',encoding='utf-8').write(conv_judge('judge_1.md', {'P':'A','Q':'B'}, '비교 보고서 Y'))
open('inputs/phase2/reading_A_anon.md','w',encoding='utf-8').write(conv_reading('reading_A.md','A'))
open('inputs/phase2/reading_B_anon.md','w',encoding='utf-8').write(conv_reading('reading_B.md','B'))
