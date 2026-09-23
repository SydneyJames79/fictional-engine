import re, sys
def ref_A(prefix):
    lines = [l for l in open('source_A.txt', encoding='utf-8').read().split('\n')]
    out = []; n = 0
    for l in lines:
        if l.strip() == '':
            out.append('')
            continue
        sents = re.split(r'(?<=\.)\s+', l)
        if len(sents) == 1:
            out.append(f'[{prefix}{n}] {l}')
        else:
            for i, s in enumerate(sents, 1):
                out.append(f'[{prefix}{n}.{i}] {s}')
        n += 1
    return '\n'.join(out).rstrip('\n')
def ref_B(prefix):
    lines = open('source_B.txt', encoding='utf-8').read().split('\n')
    out = []; n = 0
    for l in lines:
        if l.strip() == '':
            out.append('')
            continue
        out.append(f'[{prefix}{n}] {l}')
        n += 1
    return '\n'.join(out).rstrip('\n')
if __name__ == '__main__':
    which, prefix = sys.argv[1], sys.argv[2]
    print(ref_A(prefix) if which == 'A' else ref_B(prefix))
