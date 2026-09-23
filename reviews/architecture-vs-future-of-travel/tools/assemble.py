import sys
r = lambda p: open(p, encoding='utf-8').read().rstrip('\n')
srcA = r('source_A.txt')
def block_A(label, ref):
    return (f"## {label}\n\n### 원문 (배치 그대로)\n\n```text\n{srcA}\n```\n\n"
            f"### 참고용 번호 사본 (산문 문단을 문장 단위로 나눈 참조용 사본이며 원문 배치가 아님)\n\n```text\n{r(ref)}\n```")
def block_B(label, ref):
    return (f"## {label}\n\n### 원문 (참고용 행 번호만 덧붙임; 빈 줄과 행갈이는 원문 그대로)\n\n```text\n{r(ref)}\n```")
common = r('inputs/rules_common.md'); crit = r('criteria.md')
P = {}
P['R_A'] = '\n\n'.join([r('inputs/task_reader.md'), common, '# 작품 원문', block_A('작품', 'inputs/ref_RA.txt')])
P['R_B'] = '\n\n'.join([r('inputs/task_reader.md'), common, '# 작품 원문', block_B('작품', 'inputs/ref_RB.txt')])
P['J_1'] = '\n\n'.join([r('inputs/task_judge.md'), common, '# 고정 평가 규약\n\n' + crit, '# 작품 원문',
                        block_A('작품 P (먼저 제시)', 'inputs/ref_J1_P.txt'), block_B('작품 Q (나중 제시)', 'inputs/ref_J1_Q.txt')])
P['J_2'] = '\n\n'.join([r('inputs/task_judge.md'), common, '# 고정 평가 규약\n\n' + crit, '# 작품 원문',
                        block_B('작품 P (먼저 제시)', 'inputs/ref_J2_P.txt'), block_A('작품 Q (나중 제시)', 'inputs/ref_J2_Q.txt')])
for k, v in P.items():
    open(f'inputs/prompt_{k}.md', 'w', encoding='utf-8').write(v + '\n')
    print(k, len(v))
