"""Tiny SVG authoring kit: number formatting, path building with mirroring, defs registry."""
from __future__ import annotations
import math

PREC = 2

def n(v):
    """Compact number formatting."""
    if isinstance(v, int):
        return str(v)
    s = f"{v:.{PREC}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    if s == '-0':
        s = '0'
    return s

def pt(p):
    return f"{n(p[0])},{n(p[1])}"

class Path:
    """Absolute-coordinate path builder. Segments are stored so the path can be mirrored."""
    def __init__(self):
        self.segs = []  # ('M',(x,y)) | ('L',(x,y)) | ('C',c1,c2,p) | ('Q',c,p) | ('A',rx,ry,rot,laf,sf,p) | ('Z',)
    def M(self, p): self.segs.append(('M', tuple(p))); return self
    def L(self, p): self.segs.append(('L', tuple(p))); return self
    def C(self, c1, c2, p): self.segs.append(('C', tuple(c1), tuple(c2), tuple(p))); return self
    def Q(self, c, p): self.segs.append(('Q', tuple(c), tuple(p))); return self
    def A(self, rx, ry, rot, laf, sf, p): self.segs.append(('A', rx, ry, rot, laf, sf, tuple(p))); return self
    def Z(self): self.segs.append(('Z',)); return self
    def d(self):
        out = []
        for s in self.segs:
            k = s[0]
            if k in ('M', 'L'):
                out.append(f"{k}{pt(s[1])}")
            elif k == 'C':
                out.append(f"C{pt(s[1])} {pt(s[2])} {pt(s[3])}")
            elif k == 'Q':
                out.append(f"Q{pt(s[1])} {pt(s[2])}")
            elif k == 'A':
                out.append(f"A{n(s[1])},{n(s[2])} {n(s[3])} {s[4]},{s[5]} {pt(s[6])}")
            elif k == 'Z':
                out.append('Z')
        return ' '.join(out)
    def end(self):
        for s in reversed(self.segs):
            if s[0] in ('M', 'L'): return s[1]
            if s[0] == 'C': return s[3]
            if s[0] == 'Q': return s[2]
            if s[0] == 'A': return s[6]
        return None

def mirror_x(p, cx):
    return (2 * cx - p[0], p[1])

def mirrored_continuation(segs, cx):
    """Given an open polyline/curve chain (segments after an initial M) that ends at the mirror axis,
    return the segments that continue the path along the mirrored chain back to the start (reversed order),
    so that chain + mirrored_continuation(chain) forms a closed symmetric outline."""
    # Build list of (start, seg) pairs
    pts = []
    cur = None
    chain = []
    for s in segs:
        k = s[0]
        if k == 'M':
            cur = s[1]; continue
        if k == 'L':
            chain.append((cur, s)); cur = s[1]
        elif k == 'C':
            chain.append((cur, s)); cur = s[3]
        elif k == 'Q':
            chain.append((cur, s)); cur = s[2]
        elif k == 'A':
            chain.append((cur, s)); cur = s[6]
    out = []
    for start, s in reversed(chain):
        k = s[0]
        if k == 'L':
            out.append(('L', mirror_x(start, cx)))
        elif k == 'C':
            out.append(('C', mirror_x(s[2], cx), mirror_x(s[1], cx), mirror_x(start, cx)))
        elif k == 'Q':
            out.append(('Q', mirror_x(s[1], cx), mirror_x(start, cx)))
        elif k == 'A':
            # mirrored arc reverses direction twice (mirror flips sweep, reversal flips it again) -> same sweep flag
            out.append(('A', s[1], s[2], -s[3], s[4], s[5], mirror_x(start, cx)))
    return out

def symmetric_path(left: Path, cx) -> Path:
    """left: path from a point ON the axis, around the left side, back to a point ON the axis."""
    full = Path()
    full.segs = list(left.segs) + mirrored_continuation(left.segs, cx) + [('Z',)]
    return full

def mirror_path(p: Path, cx) -> Path:
    """Mirror a whole path about x=cx (keeps segment order, flips sweep flags of arcs)."""
    out = Path()
    for s in p.segs:
        k = s[0]
        if k in ('M', 'L'):
            out.segs.append((k, mirror_x(s[1], cx)))
        elif k == 'C':
            out.segs.append(('C', mirror_x(s[1], cx), mirror_x(s[2], cx), mirror_x(s[3], cx)))
        elif k == 'Q':
            out.segs.append(('Q', mirror_x(s[1], cx), mirror_x(s[2], cx)))
        elif k == 'A':
            out.segs.append(('A', s[1], s[2], -s[3], s[4], 1 - s[5], mirror_x(s[6], cx)))
        elif k == 'Z':
            out.segs.append(('Z',))
    return out

def rounded_rect_path(x, y, w, h, r):
    p = Path()
    p.M((x + r, y)).L((x + w - r, y)).A(r, r, 0, 0, 1, (x + w, y + r)).L((x + w, y + h - r)).A(r, r, 0, 0, 1, (x + w - r, y + h))
    p.L((x + r, y + h)).A(r, r, 0, 0, 1, (x, y + h - r)).L((x, y + r)).A(r, r, 0, 0, 1, (x + r, y)).Z()
    return p

def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

class Doc:
    def __init__(self, vb, title, desc):
        self.vb = vb
        self.title = title
        self.desc = desc
        self.defs = []
        self.body = []
        self._ids = set()
    def add_def(self, s):
        self.defs.append(s)
    def add(self, s, indent=1):
        self.body.append(('  ' * indent) + s)
    def comment(self, s, indent=1):
        self.body.append(('  ' * indent) + f"<!-- {s} -->")
    def render(self):
        x, y, w, h = self.vb
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'viewBox="{n(x)} {n(y)} {n(w)} {n(h)}" width="{n(w)}" height="{n(h)}" role="img" aria-labelledby="title desc">\n'
                f'  <title id="title">{self.title}</title>\n'
                f'  <desc id="desc">{self.desc}</desc>\n')
        defs = '  <defs>\n' + '\n'.join('    ' + d for d in self.defs) + '\n  </defs>\n'
        return head + defs + '\n'.join(self.body) + '\n</svg>\n'

def lin(id_, x1, y1, x2, y2, stops, units='userSpaceOnUse', extra=''):
    st = ''.join(f'<stop offset="{n(o)}" stop-color="{c}"' + (f' stop-opacity="{n(a)}"' if a is not None else '') + '/>' for o, c, a in [(s[0], s[1], s[2] if len(s) > 2 else None) for s in stops])
    return f'<linearGradient id="{id_}" gradientUnits="{units}" x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}"{extra}>{st}</linearGradient>'

def rad(id_, cx, cy, r, stops, fx=None, fy=None, units='userSpaceOnUse', extra=''):
    st = ''.join(f'<stop offset="{n(o)}" stop-color="{c}"' + (f' stop-opacity="{n(a)}"' if a is not None else '') + '/>' for o, c, a in [(s[0], s[1], s[2] if len(s) > 2 else None) for s in stops])
    f = (f' fx="{n(fx)}"' if fx is not None else '') + (f' fy="{n(fy)}"' if fy is not None else '')
    return f'<radialGradient id="{id_}" gradientUnits="{units}" cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{f}{extra}>{st}</radialGradient>'
