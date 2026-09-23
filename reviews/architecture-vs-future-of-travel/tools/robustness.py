"""S = sum(w_i * d_i). d: +는 작품 A(건축) 쪽, -는 작품 B(여행의 미래) 쪽. 'U'는 [-2,+2] 구간으로 처리."""
from fractions import Fraction as F
import sys, json
AX = ['A', 'B', 'C', 'D', 'E', 'F']
BASE = [F(2,10)]*4 + [F(1,10)]*2
def settings():
    yield '1 기본', BASE
    yield '2 균등', [F(1,6)]*6
    for i, ax in enumerate(AX):
        rest = sum(w for j, w in enumerate(BASE) if j != i)
        yield f'3 {ax}축 제거', [F(0) if j == i else w / rest for j, w in enumerate(BASE)]
    for i, ax in enumerate(AX):
        rest = sum(w for j, w in enumerate(BASE) if j != i)
        yield f'4 {ax}축 40%', [F(4,10) if j == i else w / rest * F(6,10) for j, w in enumerate(BASE)]
def score(ws, d):
    fixed = sum(w * x for w, x in zip(ws, d) if x != 'U')
    uw = sum(w for w, x in zip(ws, d) if x == 'U')
    return fixed - 2*uw, fixed + 2*uw
def verdict(lo, hi):
    if lo > 0: return 'A 우세 유지' if True else ''
    if hi < 0: return 'B 우세'
    if lo == hi == 0: return '동률'
    return '미결정(0 포함)'
def run(d, label):
    rows = []
    for name, ws in settings():
        assert sum(ws) == 1, name
        lo, hi = score(ws, d)
        v = 'A 쪽' if lo > 0 else 'B 쪽' if hi < 0 else ('동률' if lo == hi == 0 else '미결정(범위가 0 포함)')
        rows.append((name, ' '.join(f'{float(w):.3f}' for w in ws), float(lo), float(hi), v))
    print(f'## {label}  d = {d}')
    print('| 설정 | 가중치(A..F) | S 하한 | S 상한 | 방향 |')
    print('|---|---|---|---|---|')
    for r in rows:
        s = f'{r[2]:+.3f}' if r[2] == r[3] else f'{r[2]:+.3f}'
        print(f'| {r[0]} | {r[1]} | {r[2]:+.3f} | {r[3]:+.3f} | {r[4]} |')
    print()
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        label, vec = arg.split('=')
        d = [x if x == 'U' else int(x) for x in vec.split(',')]
        run(d, label)
