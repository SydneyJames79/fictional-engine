"""보고서의 큰따옴표 인용을 원문과 대조한다. ' / '는 행 경계로 보고 조각별로 확인한다."""
import re, sys, glob
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
src = norm(open('source_A.txt', encoding='utf-8').read() + '\n' + open('source_B.txt', encoding='utf-8').read())
crit = norm(open('criteria.md', encoding='utf-8').read())
files = sys.argv[1:]
total = 0
for f in files:
    t = open(f, encoding='utf-8').read()
    qs = re.findall(r'"([^"\n]+)"', t)
    miss = []
    for q in qs:
        total += 1
        parts = [norm(p) for p in re.split(r'\s*/\s*', q) if p.strip()]
        if not all(p in src or p in crit for p in parts):
            miss.append(q)
    print(f'{f}: {len(qs)} quotes; unmatched: {miss}')
print('total quotes checked:', total)
