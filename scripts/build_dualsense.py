#!/usr/bin/env python3
"""Generate dualsense.svg — a top-view illustration of the PS5 DualSense controller.

Usage: python3 build_dualsense.py [out.svg]   (standard library only)

All geometry is in millimetres (1 SVG user unit = 1 mm). The controller's
bounding box is x 0..160, y 0..105; the axis of symmetry is x = 80, and every
symmetric outline is built from its left half and mirrored.

Proportions follow Sony's published size (160 mm wide; 160 x 106 mm seen from
above) and positions measured from the PromptFont "DualSense" glyph (U+2441,
SIL OFL), whose aspect ratio matches that envelope. The glyph was only
measured, not copied. Light comes from the top of the picture throughout.
"""
import math
import re
import sys

X0 = 80.0  # axis of symmetry


# ----------------------------------------------------------------------------
# number / path helpers
# ----------------------------------------------------------------------------
def n(v):
    s = f"{v:.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pt(x, y):
    return f"{n(x)} {n(y)}"


def mx(x):
    return 2 * X0 - x


def rad(a):
    return math.radians(a)


def _norm(a):
    return a if len(a) == 6 else (a[0], a[1], a[2], a[2], a[3], a[4])


def spline(anchors, closed=True, move=True):
    """Cubic Bézier path through anchors.

    anchor = (x, y, angle, h_in, h_out) or (x, y, angle_in, angle_out, h_in, h_out);
    angles in degrees, SVG orientation (0 = +x, 90 = +y / down).
    """
    A = [_norm(a) for a in anchors]
    d = [f"M{pt(A[0][0], A[0][1])}"] if move else []
    pairs = list(zip(A, A[1:]))
    if closed:
        pairs.append((A[-1], A[0]))
    for (x1, y1, _, ao1, _, ho1), (x2, y2, ai2, _, hi2, _) in pairs:
        c1 = (x1 + ho1 * math.cos(rad(ao1)), y1 + ho1 * math.sin(rad(ao1)))
        c2 = (x2 - hi2 * math.cos(rad(ai2)), y2 - hi2 * math.sin(rad(ai2)))
        d.append(f"C{pt(*c1)} {pt(*c2)} {pt(x2, y2)}")
    if closed:
        d.append("Z")
    return " ".join(d)


def mirror_anchors(left):
    """Mirror anchors about the axis and reverse their order (and direction)."""
    out = []
    for a in reversed(left):
        x, y, ai, ao, hi, ho = _norm(a)
        out.append((mx(x), y, -ao, -ai, ho, hi))
    return out


def sym_closed(left):
    """Closed symmetric path from left-half anchors that start and end on the axis."""
    right = mirror_anchors(left)
    return spline(left + right[1:-1], closed=True)


class RoundedPoly:
    """Convex polygon (clockwise on screen) with circular-arc corners; offsettable."""

    def __init__(self, verts, radii):
        self.v = verts
        self.r = radii
        k = len(verts)
        self.corners = []
        for i in range(k):
            p0, p1, p2 = verts[i - 1], verts[i], verts[(i + 1) % k]
            u = self._unit(p0, p1)
            w = self._unit(p1, p2)
            turn = math.atan2(u[0] * w[1] - u[1] * w[0], u[0] * w[0] + u[1] * w[1])
            r = radii[i]
            t = r * math.tan(turn / 2)
            a = (p1[0] - u[0] * t, p1[1] - u[1] * t)
            nin = (-u[1], u[0])  # inward normal (clockwise on screen)
            c = (a[0] + nin[0] * r, a[1] + nin[1] * r)
            self.corners.append((c, r, (u[1], -u[0]), (w[1], -w[0]), turn))
        for i in range(k):
            t_here = self.r[i] * math.tan(self.corners[i][4] / 2)
            t_next = self.r[(i + 1) % k] * math.tan(self.corners[(i + 1) % k][4] / 2)
            if t_here + t_next > math.dist(verts[i], verts[(i + 1) % k]) + 1e-9:
                raise ValueError(f"fillets overlap on edge {i}->{(i + 1) % k}")

    @staticmethod
    def _unit(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        return (dx / L, dy / L)

    def segments(self, d=0.0):
        """Boundary offset outward by d, as ('A', c, R, a0, a1) / ('L', p0, p1)."""
        segs = []
        k = len(self.corners)
        for i in range(k):
            c, r, ni, no, turn = self.corners[i]
            R = r + d
            a0 = math.atan2(ni[1], ni[0])
            segs.append(("A", c, R, a0, a0 + turn))
            c2, r2, ni2, _, _ = self.corners[(i + 1) % k]
            p0 = (c[0] + no[0] * R, c[1] + no[1] * R)
            p1 = (c2[0] + ni2[0] * (r2 + d), c2[1] + ni2[1] * (r2 + d))
            segs.append(("L", p0, p1))
        return segs

    @staticmethod
    def _seg_len(s):
        return s[2] * (s[4] - s[3]) if s[0] == "A" else math.dist(s[1], s[2])

    def path(self, d=0.0):
        out = []
        for s in self.segments(d):
            if s[0] == "A":
                _, c, R, a0, a1 = s
                p0 = (c[0] + R * math.cos(a0), c[1] + R * math.sin(a0))
                p1 = (c[0] + R * math.cos(a1), c[1] + R * math.sin(a1))
                if not out:
                    out.append(f"M{pt(*p0)}")
                out.append(f"A{n(R)} {n(R)} 0 0 1 {pt(*p1)}")
            else:
                out.append(f"L{pt(*s[2])}")
        out.append("Z")
        return " ".join(out)

    def walk(self, d, s0, s1):
        """Open sub-path along the offset boundary, arc length s0..s1 (may wrap)."""
        segs = self.segments(d)
        total = sum(self._seg_len(s) for s in segs)
        if s1 < s0:
            s1 += total
        out = []
        pos = 0.0
        for lap in (0, 1):
            for s in segs:
                L = self._seg_len(s)
                lo, hi = max(s0, pos), min(s1, pos + L)
                if hi > lo and L > 0:
                    t0, t1 = (lo - pos) / L, (hi - pos) / L
                    if s[0] == "A":
                        _, c, R, a0, a1 = s
                        b0, b1 = a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1
                        p0 = (c[0] + R * math.cos(b0), c[1] + R * math.sin(b0))
                        p1 = (c[0] + R * math.cos(b1), c[1] + R * math.sin(b1))
                        if not out:
                            out.append(f"M{pt(*p0)}")
                        out.append(f"A{n(R)} {n(R)} 0 0 1 {pt(*p1)}")
                    else:
                        (xa, ya), (xb, yb) = s[1], s[2]
                        p0 = (xa + (xb - xa) * t0, ya + (yb - ya) * t0)
                        p1 = (xa + (xb - xa) * t1, ya + (yb - ya) * t1)
                        if not out:
                            out.append(f"M{pt(*p0)}")
                        out.append(f"L{pt(*p1)}")
                pos += L
        return " ".join(out)

    def marks(self, d=0.0):
        """Arc-length position of the start of every segment (A0, L0, A1, L1, ...)."""
        pos, acc = [], 0.0
        for s in self.segments(d):
            pos.append(acc)
            acc += self._seg_len(s)
        pos.append(acc)
        return pos


def capsule_path(cx, cy, w, h):
    """Stadium shape centred on (cx, cy); the long axis is vertical when h > w."""
    r = min(w, h) / 2
    x, y = cx - w / 2, cy - h / 2
    if h >= w:
        return (f"M{pt(x, y + r)}A{n(r)} {n(r)} 0 0 1 {pt(x + w, y + r)}V{n(y + h - r)}"
                f"A{n(r)} {n(r)} 0 0 1 {pt(x, y + h - r)}Z")
    return (f"M{pt(x + r, y)}H{n(x + w - r)}A{n(r)} {n(r)} 0 0 1 {pt(x + w - r, y + h)}"
            f"H{n(x + r)}A{n(r)} {n(r)} 0 0 1 {pt(x + r, y)}Z")


def fmt_attrs(attrs):
    return "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())


def circle(cx, cy, r, **attrs):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{fmt_attrs(attrs)}/>'


def ellipse(cx, cy, rx, ry, **attrs):
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}"{fmt_attrs(attrs)}/>'


def path(d, **attrs):
    return f'<path d="{d}"{fmt_attrs(attrs)}/>'


# ----------------------------------------------------------------------------
# minimal SVG path parser (to place the PlayStation logo in absolute coordinates)
# ----------------------------------------------------------------------------
def parse_path(d):
    toks = re.findall(r"[MmLlHhVvCcSsZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    i, cmd = 0, None
    cur = start = (0.0, 0.0)
    prev_c2 = None
    out = []

    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cur, prev_c2 = start, None
                continue
        rel = cmd.islower()
        ox, oy = cur if rel else (0.0, 0.0)
        C = cmd.upper()
        if C == "M":
            cur = start = (ox + num(), oy + num())
            out.append(("M", cur))
            cmd, prev_c2 = ("l" if rel else "L"), None
        elif C == "L":
            cur = (ox + num(), oy + num())
            out.append(("L", cur))
            prev_c2 = None
        elif C == "H":
            v = num()
            cur = ((cur[0] + v) if rel else v, cur[1])
            out.append(("L", cur))
            prev_c2 = None
        elif C == "V":
            v = num()
            cur = (cur[0], (cur[1] + v) if rel else v)
            out.append(("L", cur))
            prev_c2 = None
        elif C in "CS":
            if C == "C":
                c1 = (ox + num(), oy + num())
            else:
                c1 = (2 * cur[0] - prev_c2[0], 2 * cur[1] - prev_c2[1]) if prev_c2 else cur
            c2 = (ox + num(), oy + num())
            cur = (ox + num(), oy + num())
            out.append(("C", c1, c2, cur))
            prev_c2 = c2
    return out


def transform_path(segs, s, tx, ty):
    def T(p):
        return pt(p[0] * s + tx, p[1] * s + ty)

    d = []
    for g in segs:
        if g[0] == "M":
            d.append(f"M{T(g[1])}")
        elif g[0] == "L":
            d.append(f"L{T(g[1])}")
        elif g[0] == "C":
            d.append(f"C{T(g[1])} {T(g[2])} {T(g[3])}")
        else:
            d.append("Z")
    return " ".join(d)


def bbox_of(segs):
    xs, ys, cur = [], [], (0.0, 0.0)
    for g in segs:
        if g[0] in ("M", "L"):
            cur = g[1]
            xs.append(cur[0]); ys.append(cur[1])
        elif g[0] == "C":
            p0, c1, c2, p3 = cur, g[1], g[2], g[3]
            for k in range(41):
                t = k / 40
                m = 1 - t
                xs.append(m**3 * p0[0] + 3 * m * m * t * c1[0] + 3 * m * t * t * c2[0] + t**3 * p3[0])
                ys.append(m**3 * p0[1] + 3 * m * m * t * c1[1] + 3 * m * t * t * c2[1] + t**3 * p3[1])
            cur = p3
    return min(xs), min(ys), max(xs), max(ys)


# PlayStation logo (Simple Icons, CC0) — the PS button is moulded in this shape.
PS_LOGO = ("M8.984 2.596v17.547l3.915 1.261V6.688c0-.69.304-1.151.794-.991.636.18.76.814.76 1.505v5.875"
           "c2.441 1.193 4.362-.002 4.362-3.152 0-3.237-1.126-4.675-4.438-5.827-1.307-.448-3.728-1.186-5.39-1.502z"
           "m4.656 16.241l6.296-2.275c.715-.258.826-.625.246-.818-.586-.192-1.637-.139-2.357.123l-4.205 1.5V14.98"
           "l.24-.085s1.201-.42 2.913-.615c1.696-.18 3.785.03 5.437.661 1.848.601 2.04 1.472 1.576 2.072-.465.6"
           "-1.622 1.036-1.622 1.036l-8.544 3.107V18.86zM1.807 18.6c-1.9-.545-2.214-1.668-1.352-2.32.801-.586 2.16"
           "-1.052 2.16-1.052l5.615-2.013v2.313L4.205 17c-.705.271-.825.632-.239.826.586.195 1.637.15 2.343-.12"
           "L8.247 17v2.074c-.12.03-.256.044-.39.073-1.939.331-3.996.196-6.038-.479z")


# ----------------------------------------------------------------------------
# geometry (mm)
# ----------------------------------------------------------------------------
# Outer silhouette, left half: top centre -> shoulder -> flank -> grip tip -> crotch -> bottom centre.
OUTLINE_L = [
    (80.0, 1.30, 180, 12, 12),
    (50.0, 3.10, 173.2, 10, 7),
    (30.0, 5.84, 170.4, 7, 4.5),
    (17.7, 8.22, 167.4, 4.2, 1.35),
    (15.05, 11.35, 112.5, 1.45, 3.0),
    (11.46, 20.0, 111.6, 3.0, 6.5),
    (4.93, 40.0, 105.3, 7, 7),
    (0.60, 60.0, 97.2, 6.5, 3.4),
    (0.0, 70.0, 90, 3.4, 5),
    (0.78, 85.0, 83.2, 5, 4.3),
    (4.10, 98.0, 63.1, 4.3, 4.6),
    (18.6, 104.95, 1.5, 7.6, 1.8),
    (22.94, 102.0, -64, 2.2, 3.8),
    (27.69, 92.0, -67.7, 3.8, 3.8),
    (31.71, 82.0, -63.4, 3.6, 3.0),
    (37.38, 74.0, -44.6, 3.0, 2.6),
    (44.5, 69.5, -18.7, 2.4, 3.2),
    (55.0, 68.01, -0.6, 3.6, 8),
    (80.0, 68.0, 0, 8, 8),
]
OUTLINE = sym_closed(OUTLINE_L)

# Touchpad: trapezoid wider at the top, top edge following the shell's front arc.
_TP_LEFT_DIR = (5.44, 23.0)          # direction of the pad's left edge (13.3° off vertical)
_TP_SLOPE = _TP_LEFT_DIR[0] / _TP_LEFT_DIR[1]


def tp_left_x(y):
    return 46.43 + _TP_SLOPE * (y - 5.0)


TP_TOP = 3.99
TP_BOT = 35.6
TP = RoundedPoly(
    [(tp_left_x(TP_TOP), TP_TOP), (X0, -0.72), (mx(tp_left_x(TP_TOP)), TP_TOP),
     (mx(tp_left_x(TP_BOT)), TP_BOT), (tp_left_x(TP_BOT), TP_BOT)],
    [1.6, 210, 1.6, 10.5, 10.5],  # the top arc's crown sits on the silhouette (y = 1.3)
)
CHANNEL = 2.0            # touchpad edge -> white shell edge
LB_IN, LB_OUT = 0.2, 1.8    # light-bar strip, as offsets from the pad edge

# The white shell's inner edge (left): runs beside the pad, rounds the junction
# below the pad's corner, then sweeps down the inside of the grip to its tip.
_L = math.hypot(*_TP_LEFT_DIR)
_NX, _NY = -_TP_LEFT_DIR[1] / _L, _TP_LEFT_DIR[0] / _L  # outward normal of the pad's left edge


def shell_edge_x(y):
    # x of the pad's left edge offset outward by CHANNEL, at height y
    y0 = y - _NY * CHANNEL
    return tp_left_x(y0) + _NX * CHANNEL


_A_EDGE = math.degrees(math.atan2(_TP_LEFT_DIR[1], _TP_LEFT_DIR[0]))  # ~76.7°
SHELL_EDGE_L = [
    (shell_edge_x(-2.0), -2.0, _A_EDGE, 3, 9),
    (shell_edge_x(26.6), 26.6, _A_EDGE, 9, 1.5),
    (49.96, 30.4, 98, 1.6, 2.0),
    (45.25, 37.6, 127.5, 3.0, 5.0),
    (36.32, 50.0, 123.6, 5.0, 6.0),
    (28.38, 65.0, 113.3, 6.0, 6.5),
    (20.57, 85.0, 110.3, 6.8, 5.2),
    (15.10, 100.0, 111.8, 5.0, 2.4),
    (12.20, 108.0, 112, 2.6, 2),
]
# Black core = everything inboard of the shell edges (clipped to the silhouette later).
CORE = (spline(SHELL_EDGE_L, closed=False)
        + f" L{pt(12.2, 112)} L{pt(mx(12.2), 112)} L{pt(mx(12.2), 108)} "
        + spline(mirror_anchors(SHELL_EDGE_L), closed=False, move=False)
        + " Z")

# Components
DPAD_C = (29.35, 30.25)
FACE_C = (mx(29.35), 30.25)
FACE_OFF = 11.0
FACE_R = 5.45
STICK_L = (54.5, 52.6)
STICK_R = (mx(54.5), 52.6)
STICK_WELL = 11.8
STICK_CAP = 9.7
# Centre column, top to bottom: player LEDs, speaker grille, PS button, mute button.
LED_Y = 37.9
LED_STEP = 2.6
GRILLE_C = (80.0, 41.0)
PS_C = (80.0, 48.6)
PS_W = 10.4
MUTE_C = (80.0, 56.6)
MUTE_W, MUTE_H = 7.2, 2.4
CREATE_C = (41.7, 12.6)
CREATE_W, CREATE_H = 3.2, 7.6
CREATE_TILT = 14.0       # degrees; the top of the Create button leans outward, like the light bar


# ----------------------------------------------------------------------------
# palette
# ----------------------------------------------------------------------------
C = dict(
    shell_hi="#FCFCFB", shell="#F2F2F0", shell_mid="#E6E7E8", shell_lo="#D2D4D8",
    shell_shade="#8B9098",
    pad_hi="#FAFAF9", pad="#EEEEEC", pad_lo="#DCDDDE",
    core_hi="#35383E", core="#232529", core_lo="#131417",
    gap="#0B0C0E", gap_clear="#4E525A",
    sym="#878C94",          # face-button symbols, seen through the clear caps
    light="#2F6FFF", light_mid="#5A94FF", light_hi="#A9C9FF",
)


# ----------------------------------------------------------------------------
# shared definitions — filters and soft gradients are registered on first use
# ----------------------------------------------------------------------------
_DEFS = {}

# User-space filter regions (mm) for large or thin shapes. Small shapes use their
# bounding box. Tight regions keep the blur cost down in CPU renderers.
REGIONS = {
    "canvas": (-10, -8, 180, 124),
    "body": (-6, -5, 172, 116),
    "core": (10, -4, 140, 112),
    "lightbar": (34, -4, 92, 46),
}


def _define(fid, markup):
    _DEFS.setdefault(fid, markup)
    return f"url(#{fid})"


def blur(sd, region=None):
    """url() of a Gaussian blur filter (sRGB, so every renderer agrees)."""
    tag = n(sd).replace(".", "")
    if region:
        x, y, w, h = REGIONS[region]
        fid = f"blur{tag}-{region}"
        box = f'filterUnits="userSpaceOnUse" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'
    else:
        fid = f"blur{tag}"
        box = 'x="-50%" y="-50%" width="200%" height="200%"'
    return _define(fid, f'<filter id="{fid}" {box} color-interpolation-filters="sRGB">'
                        f'<feGaussianBlur stdDeviation="{n(sd)}"/></filter>')


def soft(cx, cy, rx, ry, color, alpha, rot=0):
    """Soft-edged elliptical highlight or shade, drawn with a radial gradient (no filter)."""
    gid = f"soft-{color.lstrip('#').lower()}-{n(alpha).replace('.', '')}"
    _define(gid, f'''<radialGradient id="{gid}">
      <stop offset="0" stop-color="{color}" stop-opacity="{n(alpha)}"/>
      <stop offset=".45" stop-color="{color}" stop-opacity="{n(alpha * .72)}"/>
      <stop offset=".78" stop-color="{color}" stop-opacity="{n(alpha * .22)}"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>''')
    tr = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="url(#{gid})"{tr}/>'


def ps_logo_path():
    segs = parse_path(PS_LOGO)
    x0, y0, x1, y1 = bbox_of(segs)
    s = PS_W / (x1 - x0)
    return transform_path(segs, s, PS_C[0] - (x0 + x1) / 2 * s, PS_C[1] - (y0 + y1) / 2 * s)


PS_D = ps_logo_path()
TOP_EDGE = spline(OUTLINE_L[:4], closed=False) + " " + spline(
    [(mx(a[0]), a[1], 180 - a[2], a[3], a[4]) for a in OUTLINE_L[:4]], closed=False)
SHELL_EDGES = (spline(SHELL_EDGE_L, closed=False) + " "
               + spline(mirror_anchors(SHELL_EDGE_L), closed=False))


def static_defs():
    return [
        f'<clipPath id="clip-body"><path d="{OUTLINE}"/></clipPath>',
        f'<clipPath id="clip-core"><path d="{CORE}"/></clipPath>',
        f'<clipPath id="clip-pad"><path d="{TP.path(0)}"/></clipPath>',
        f'<clipPath id="clip-ps"><path d="{PS_D}"/></clipPath>',
        # below the touchpad: lets the black trim's outer edge be redrawn dark without touching the pad
        '<clipPath id="clip-low"><rect x="-10" y="38" width="180" height="80"/></clipPath>',
        # edge falloff that follows the light: faint along the front edge, strong at the grip ends
        f'''<linearGradient id="g-edge" x1="0" y1="0" x2="0" y2="105" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['shell_shade']}" stop-opacity=".15"/>
      <stop offset=".25" stop-color="{C['shell_shade']}" stop-opacity=".75"/>
      <stop offset="1" stop-color="{C['shell_shade']}"/>
    </linearGradient>''',
        '''<linearGradient id="g-pad-rim" x1="0" y1="2" x2="0" y2="36" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>
      <stop offset=".5" stop-color="#FFFFFF" stop-opacity=".35"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>''',
        '''<linearGradient id="g-cap-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/>
      <stop offset=".4" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset=".6" stop-color="#959BA4" stop-opacity="0"/>
      <stop offset="1" stop-color="#959BA4" stop-opacity=".75"/>
    </linearGradient>''',
        f'''<linearGradient id="g-gap" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#8A8F97"/>
      <stop offset="1" stop-color="{C['gap_clear']}"/>
    </linearGradient>''',
        '''<linearGradient id="g-lip" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1B1C20"/>
      <stop offset=".55" stop-color="#2E3035"/>
      <stop offset="1" stop-color="#585C64"/>
    </linearGradient>''',
        f'''<linearGradient id="g-shell" x1="0" y1="2" x2="0" y2="105" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['shell_hi']}"/>
      <stop offset=".38" stop-color="{C['shell']}"/>
      <stop offset=".7" stop-color="{C['shell_mid']}"/>
      <stop offset="1" stop-color="{C['shell_lo']}"/>
    </linearGradient>''',
        f'''<linearGradient id="g-core" x1="0" y1="30" x2="0" y2="105" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['core_hi']}"/>
      <stop offset=".3" stop-color="{C['core']}"/>
      <stop offset="1" stop-color="{C['core_lo']}"/>
    </linearGradient>''',
        f'''<linearGradient id="g-pad" x1="0" y1="2" x2="0" y2="36" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['pad_hi']}"/>
      <stop offset=".55" stop-color="{C['pad']}"/>
      <stop offset="1" stop-color="{C['pad_lo']}"/>
    </linearGradient>''',
        '''<linearGradient id="g-l1" x1="0" y1="0" x2="0" y2="7" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#43464D"/>
      <stop offset=".3" stop-color="#26282D"/>
      <stop offset="1" stop-color="#111214"/>
    </linearGradient>''',
        '''<linearGradient id="g-key" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3F4249"/>
      <stop offset=".45" stop-color="#25272C"/>
      <stop offset="1" stop-color="#141519"/>
    </linearGradient>''',
        '''<linearGradient id="g-top-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#C3C7CE" stop-opacity=".8"/>
      <stop offset=".3" stop-color="#7A7E86" stop-opacity=".25"/>
      <stop offset=".55" stop-color="#7A7E86" stop-opacity="0"/>
    </linearGradient>''',
        # face buttons: clear caps over a white backing
        '''<radialGradient id="g-face" cx=".5" cy=".4" r=".62">
      <stop offset="0" stop-color="#F6F7F8"/>
      <stop offset=".6" stop-color="#E4E7EB"/>
      <stop offset=".88" stop-color="#CED3D9"/>
      <stop offset="1" stop-color="#B7BDC5"/>
    </radialGradient>''',
        '''<radialGradient id="g-face-caustic" cx=".5" cy=".86" r=".5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".75"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>''',
        '''<radialGradient id="g-dish" cx=".5" cy=".66" r=".6">
      <stop offset="0" stop-color="#36383E"/>
      <stop offset=".55" stop-color="#202125"/>
      <stop offset="1" stop-color="#0D0E10"/>
    </radialGradient>''',
        '''<linearGradient id="g-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#585B63"/>
      <stop offset=".4" stop-color="#2B2D32"/>
      <stop offset="1" stop-color="#0F1012"/>
    </linearGradient>''',
        '''<radialGradient id="g-well" cx=".5" cy=".5" r=".5">
      <stop offset=".74" stop-color="#040405"/>
      <stop offset=".93" stop-color="#0D0E10"/>
      <stop offset="1" stop-color="#2A2C31"/>
    </radialGradient>''',
        '''<linearGradient id="g-ps" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3E4148"/>
      <stop offset=".45" stop-color="#1C1D21"/>
      <stop offset="1" stop-color="#0E0F11"/>
    </linearGradient>''',
        '''<linearGradient id="g-mute" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2E3035"/>
      <stop offset=".5" stop-color="#232428"/>
      <stop offset="1" stop-color="#18191C"/>
    </linearGradient>''',
    ]


# ----------------------------------------------------------------------------
# builders
# ----------------------------------------------------------------------------
def shadow():
    return f'''<g id="drop-shadow">
    {path(OUTLINE, transform="translate(0 2.6)", fill="#000", opacity=".2", filter=blur(3, "canvas"))}
    {path(OUTLINE, transform="translate(0 .9)", fill="#000", opacity=".3", filter=blur(.8, "canvas"))}
  </g>'''


def shoulders():
    """L1 bumper (and a sliver of the L2 trigger behind it), seen from above."""
    # The visible top contours follow the measured silhouette; the lower parts tuck under the shell.
    l2 = spline([
        (41.6, 5.0, -100, 1, 1.8),
        (40.4, 1.2, -140, 1.2, 1.2),
        (37.4, -0.15, 187, 1.4, 2.0),
        (32.5, -0.75, 180, 2.6, 3.0),
        (24.4, 0.4, 162, 3.0, 2.4),
        (19.4, 3.1, 143, 1.8, 1.4),
        (16.8, 6.9, 112, 1.4, 1.2),
        (17.3, 10.4, 20, 2, 5),
        (30.0, 7.6, -8, 6, 6),
        (41.6, 5.0, -14, 4, 1),
    ])
    l2_hi = spline([
        (38.6, 0.0, 190, 1, 1.6),
        (32.5, -0.45, 180, 2.2, 2.8),
        (24.6, 0.7, 162, 2.8, 2.0),
        (20.0, 3.2, 143, 1.4, 1),
    ], closed=False)
    l1 = spline([
        (40.9, 5.2, -95, 1, 1.2),
        (39.9, 2.0, -150, 1.0, 1.0),
        (37.5, 0.85, 187, 1.2, 1.6),
        (32.5, 0.32, 180, 2.2, 2.8),
        (25.0, 1.35, 163, 2.8, 2.0),
        (20.4, 3.75, 145, 1.6, 1.2),
        (18.0, 7.0, 112, 1.2, 1.2),
        (18.4, 10.0, 20, 1.5, 5),
        (30.0, 7.2, -8, 6, 6),
        (40.9, 5.2, -14, 4, 1),
    ])
    l1_hi = spline([
        (37.6, 1.2, 187, 1, 1.5),
        (32.5, 0.72, 180, 2.0, 2.6),
        (25.0, 1.75, 163, 2.6, 1.8),
        (21.0, 3.9, 145, 1.4, 1),
    ], closed=False)
    parts = []
    for flip in (False, True):
        tr = f' transform="translate({n(2 * X0)} 0) scale(-1 1)"' if flip else ""
        parts.append(f'''<g{tr}>
      {path(l2, fill="#0C0D0F")}
      {path(l2_hi, fill="none", stroke="#55585F", stroke_width=".6", stroke_linecap="round", opacity=".35", filter=blur(.2))}
      {path(l1, fill="url(#g-l1)")}
      {path(l1, fill="none", stroke="#000", stroke_width=".2", opacity=".8")}
      {path(l1_hi, fill="none", stroke="#9DA1A9", stroke_width=".7", stroke_linecap="round", opacity=".35", filter=blur(.2))}
    </g>''')
    return '<g id="shoulder-buttons">\n    ' + "\n    ".join(parts) + "\n  </g>"


def body():
    return f'''<g id="body" clip-path="url(#clip-body)">
    <!-- white shell -->
    {path(OUTLINE, fill="url(#g-shell)")}
    <g id="shell-shading">
      {path(OUTLINE, fill="none", stroke="url(#g-edge)", stroke_width="9", opacity=".36", filter=blur(3, "body"))}
      {path(OUTLINE, fill="none", stroke="#6E737B", stroke_width="1.8", opacity=".3", filter=blur(.8, "body"))}
      {soft(24, 33, 26, 30, "#FFFFFF", .7)}
      {soft(mx(24), 33, 26, 30, "#FFFFFF", .7)}
      {soft(13.5, 72, 8.5, 25, "#FFFFFF", .42, -17)}
      {soft(mx(13.5), 72, 8.5, 25, "#FFFFFF", .42, 17)}
      {soft(12, 100, 17, 12, "#8E949C", .38)}
      {soft(mx(12), 100, 17, 12, "#8E949C", .38)}
      <!-- the shell rolls down into the seam beside the core -->
      {path(SHELL_EDGES, fill="none", stroke="#8F959E", stroke_width="1.5", opacity=".4", filter=blur(.4, "body"))}
    </g>
    <!-- black core: the centre section and the inner halves of the grips -->
    <g id="core">
      {path(CORE, fill="url(#g-core)")}
      <g clip-path="url(#clip-core)">
        {path(CORE, fill="none", stroke="#000", stroke_width="2.2", opacity=".5", filter=blur(.8, "core"))}
        {soft(80, 50, 44, 22, "#70757F", .24)}
        {soft(31, 79, 8.5, 27, "#9096A0", .26, 21)}
        {soft(mx(31), 79, 8.5, 27, "#9096A0", .26, -21)}
        {path(OUTLINE, fill="none", stroke="#000", stroke_width="5", opacity=".45", filter=blur(1.5, "core"))}
        {path(SHELL_EDGES, fill="none", stroke="#8D929B", stroke_width=".8", opacity=".22", filter=blur(.4, "core"))}
        <!-- rim light where the black edges roll away (keeps the body readable on dark backgrounds) -->
        {path(OUTLINE, fill="none", stroke="#6C717B", stroke_width="1", opacity=".3", filter=blur(.35, "core"))}
      </g>
      {path(SHELL_EDGES, fill="none", stroke="#050506", stroke_width=".24")}
    </g>
  </g>
  {path(OUTLINE, fill="none", stroke="#868B93", stroke_width=".28", opacity=".85")}
  <!-- a light outline would halo the black trim on dark backgrounds, so redraw its edge dark -->
  <g clip-path="url(#clip-low)"><g clip-path="url(#clip-core)">
    {path(OUTLINE, fill="none", stroke="#0D0E11", stroke_width=".3")}
  </g></g>'''


def touchpad():
    lb_mid = (LB_IN + LB_OUT) / 2
    lb_w = LB_OUT - LB_IN
    mm = TP.marks(lb_mid)
    # segment order: A0 TL, L, A1 TC, L, A2 TR, L, A3 BR, L, A4 BL, L (left edge, going up)
    wrap = 0.42  # fraction of the lower corner arc that the light bar follows
    # Each strip hooks part-way round a lower corner, runs up the pad's side and carries on
    # past the shell's top edge (the body clip trims it there).
    ux, uy = _TP_LEFT_DIR[0] / _L, _TP_LEFT_DIR[1] / _L  # unit vector down the left edge
    top_l = TP.segments(lb_mid)[9][2]       # where the left edge meets the top-left corner arc
    top_r = (mx(top_l[0]), top_l[1])
    left = TP.walk(lb_mid, mm[9] - (mm[9] - mm[8]) * wrap, mm[10]) + f" L{pt(top_l[0] - 3 * ux, top_l[1] - 3 * uy)}"
    right = (f"M{pt(top_r[0] + 3 * ux, top_r[1] - 3 * uy)} L"
             + TP.walk(lb_mid, mm[5], mm[6] + (mm[7] - mm[6]) * wrap)[1:])
    both = left + " " + right
    pad = TP.path(0)
    return f'''<g id="touchpad-and-light-bar" clip-path="url(#clip-body)">
    <!-- gap round the pad, and the channels that hold the light bars -->
    {path(TP.path(0.42), fill=C['gap'])}
    {path(both, fill="none", stroke=C['gap'], stroke_width=n(CHANNEL - 0.15), stroke_linecap="round")}
    <g id="light-bar" fill="none" stroke-linecap="round">
      {path(both, stroke=C['light'], stroke_width="7", opacity=".08", filter=blur(3, "lightbar"))}
      {path(both, stroke=C['light'], stroke_width="3.2", opacity=".32", filter=blur(1.2, "lightbar"))}
      {path(both, stroke=C['light_mid'], stroke_width=n(lb_w))}
      {path(both, stroke=C['light_hi'], stroke_width=".5", opacity=".75")}
    </g>
    <!-- pad surface -->
    {path(pad, fill="#000", opacity=".45", transform="translate(0 .3)", filter=blur(.4))}
    {path(pad, fill="url(#g-pad)")}
    <g clip-path="url(#clip-pad)">
      {path(pad, fill="none", stroke="#9DA2AA", stroke_width="1.6", opacity=".34", filter=blur(.8))}
      {soft(80, 10, 34, 13, "#FFFFFF", .7)}
      {path(both, fill="none", stroke=C['light'], stroke_width="3", opacity=".2", filter=blur(1.5, "lightbar"))}
      {path(TP.path(-0.35), fill="none", stroke="url(#g-pad-rim)", stroke_width=".4")}
    </g>
    {path(pad, fill="none", stroke="#7D828A", stroke_width=".22")}
    <!-- rim light along the whole front edge, over the pad and the shell -->
    {path(TOP_EDGE, fill="none", stroke="#FFFFFF", stroke_width=".9", opacity=".9", transform="translate(0 .5)", filter=blur(.2))}
  </g>'''


def _world_up_gradient(gid, rot, stops):
    """Linear gradient for a key drawn rotated by `rot`, lit from the top of the picture."""
    a = math.radians(rot)
    ux, uy = -math.sin(a), -math.cos(a)  # world (0, -1) expressed in the key's frame
    v = f'x1="{n(.5 + ux / 2)}" y1="{n(.5 + uy / 2)}" x2="{n(.5 - ux / 2)}" y2="{n(.5 - uy / 2)}"'
    return _define(gid, f'<linearGradient id="{gid}" {v}>{stops}</linearGradient>')


def dpad():
    """Four clear keys over a white backing, each a "house" pointing at the centre."""
    cx, cy = DPAD_C
    hw, tip, R = 4.95, 2.6, 14.6
    sh = -(tip + hw)            # where the 45° tip edges meet the sides
    up = RoundedPoly(
        [(-hw, -R + 0.45), (0, -R - 0.25), (hw, -R + 0.45), (hw, sh), (0, -tip), (-hw, sh)],
        [2.0, 18.0, 2.0, 1.0, 1.0, 1.0],
    )
    key, gap, bevel = up.path(0), up.path(0.3), up.path(-0.55)
    casts, gaps, shadows, keys = [], [], [], []
    for rot in (0, 90, 180, 270):
        place = f"translate({n(cx)} {n(cy)}) rotate({rot})"
        spec = _world_up_gradient(f"g-dpad-spec-{rot}", rot,
                                  '<stop offset=".02" stop-color="#FFFFFF" stop-opacity="0"/>'
                                  '<stop offset=".05" stop-color="#FFFFFF" stop-opacity=".28"/>'
                                  '<stop offset=".1" stop-color="#FFFFFF" stop-opacity=".1"/>'
                                  '<stop offset=".16" stop-color="#FFFFFF" stop-opacity="0"/>')
        fill = _world_up_gradient(f"g-dpad-{rot}", rot,
                                  '<stop offset="0" stop-color="#F7F8F9"/><stop offset=".5" stop-color="#E3E6EA"/>'
                                  '<stop offset="1" stop-color="#C6CBD2"/>')
        caustic = _world_up_gradient(f"g-dpad-caustic-{rot}", rot,
                                     '<stop offset=".5" stop-color="#FFFFFF" stop-opacity="0"/>'
                                     '<stop offset=".92" stop-color="#FFFFFF" stop-opacity=".6"/>'
                                     '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>')
        rim = _world_up_gradient(f"g-dpad-rim-{rot}", rot,
                                 '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/>'
                                 '<stop offset=".35" stop-color="#FFFFFF" stop-opacity=".2"/>'
                                 '<stop offset=".6" stop-color="#FFFFFF" stop-opacity="0"/>')
        casts.append(path(gap, transform=f"translate({n(cx)} {n(cy + 0.8)}) rotate({rot})"))
        gap_fill = _world_up_gradient(f"g-gap-{rot}", rot,
                                      f'<stop offset="0" stop-color="#8A8F97"/><stop offset="1" stop-color="{C["gap_clear"]}"/>')
        gaps.append(path(gap, fill=gap_fill, transform=place))
        shadows.append(path(key, transform=f"translate({n(cx)} {n(cy + 0.3)}) rotate({rot})"))
        keys.append(f'''<g transform="{place}">
        {path(key, fill=fill)}
        {path(key, fill=caustic)}
        {path(key, fill=spec)}
        {path(bevel, fill="none", stroke="#FFFFFF", stroke_width=".3", opacity=".4")}
        {path(key, fill="none", stroke=rim, stroke_width=".26")}
      </g>''')
    return (f'<g id="d-pad">\n      <g fill="#000" opacity=".2" filter="{blur(.8)}">' + "".join(casts) + "</g>\n      "
            + "\n      ".join(gaps)
            + f'\n      <g fill="#000" opacity=".16" filter="{blur(.45)}">' + "".join(shadows) + "</g>\n      "
            + "\n      ".join(keys) + "\n  </g>")


def face_buttons():
    """Clear caps over a white backing; the grey symbols sit under the clear top."""
    cx, cy = FACE_C
    o, r = FACE_OFF, FACE_R
    k = r / 5.0  # symbol scale relative to a 10 mm button
    sw = n(0.45 * k)
    pos = {"triangle": (cx, cy - o), "circle": (cx + o, cy), "cross": (cx, cy + o), "square": (cx - o, cy)}
    out = []
    for name, (x, y) in pos.items():
        if name == "triangle":
            R3 = 2.7 * k
            p = [(x + R3 * math.cos(rad(a)), y + 0.25 * k + R3 * math.sin(rad(a))) for a in (-90, 30, 150)]
            glyph = f'<path d="M{pt(*p[0])}L{pt(*p[1])}L{pt(*p[2])}Z" stroke-linejoin="miter"/>'
        elif name == "circle":
            glyph = circle(x, y, 2.25 * k)
        elif name == "cross":
            a = 1.85 * k
            glyph = (f'<path d="M{pt(x - a, y - a)}L{pt(x + a, y + a)}M{pt(x + a, y - a)}L{pt(x - a, y + a)}"'
                     ' stroke-linecap="butt"/>')
        else:
            s_ = 1.8 * k
            glyph = f'<rect x="{n(x - s_)}" y="{n(y - s_)}" width="{n(2 * s_)}" height="{n(2 * s_)}" stroke-linejoin="miter"/>'
        out.append(f'''<g id="btn-{name}">
      {circle(x, y, r, fill="url(#g-face)")}
      {circle(x, y, r, fill="url(#g-face-caustic)")}
      <g fill="none" stroke="#FFFFFF" stroke-width="{sw}" opacity=".55" transform="translate(0 .16)"
         filter="{blur(.15)}">{glyph}</g>
      <g fill="none" stroke="{C['sym']}" stroke-width="{sw}">{glyph}</g>
      {soft(x, y - r * 0.5, r * 0.62, r * 0.3, "#FFFFFF", .45)}
      {ellipse(x, y - r * 0.775, r * 0.433, r * 0.092, fill="#FFFFFF", opacity=".55", filter=blur(.2))}
      {circle(x, y, r - 0.16, fill="none", stroke="url(#g-cap-rim)", stroke_width=".3")}
    </g>''')
    casts = "".join(circle(x, y + 0.8, r + 0.75) for x, y in pos.values())
    gaps = "".join(circle(x, y, r + 0.3) for x, y in pos.values())
    shadows = "".join(circle(x, y + 0.35, r) for x, y in pos.values())
    return (f'<g id="face-buttons">\n    <g fill="#000" opacity=".2" filter="{blur(.8)}">{casts}</g>\n    '
            f'<g fill="url(#g-gap)">{gaps}</g>\n    '
            f'<g fill="#000" opacity=".16" filter="{blur(.45)}">{shadows}</g>\n    '
            + "\n    ".join(out) + "\n  </g>")


def stick(cx, cy, side):
    rw, rc = STICK_WELL, STICK_CAP
    dish = rc * 0.74
    ring_r = (rc + dish) / 2 + 0.15
    dash = 2 * math.pi * ring_r / 110
    knurl = dict(fill="none", stroke="#08080A", stroke_width=n(rc - dish - 0.5),
                 stroke_dasharray=f"{n(dash * 0.42)} {n(dash * 0.58)}", opacity=".38")
    return f'''<g id="stick-{side}">
      {circle(cx, cy, rw + 0.5, fill="none", stroke="url(#g-lip)", stroke_width=".55")}
      {circle(cx, cy, rw, fill="url(#g-well)")}
      {circle(cx, cy, rc, fill="url(#g-rim)")}
      {circle(cx, cy, ring_r, **knurl)}
      {circle(cx, cy, rc - 0.22, fill="none", stroke="url(#g-top-rim)", stroke_width=".3")}
      {circle(cx, cy, dish + 0.4, fill="#40434A")}
      {circle(cx, cy, dish, fill="url(#g-dish)")}
      {soft(cx, cy - dish * 0.45, dish * 0.95, dish * 0.6, "#000000", .42)}
      {soft(cx, cy + dish * 0.8, dish * 0.62, dish * 0.2, "#9AA0AA", .18)}
      {soft(cx, cy - rc * 0.84, rc * 0.62, rc * 0.16, "#FFFFFF", .16)}
    </g>'''


def sticks():
    shadows = "".join(circle(x, y + 1.0, STICK_CAP + 0.5) for x, y in (STICK_L, STICK_R))
    return (f'<g id="analog-sticks">\n    <g fill="#000" opacity=".65" filter="{blur(.8)}">{shadows}</g>\n    '
            + stick(*STICK_L, "left") + "\n    " + stick(*STICK_R, "right") + "\n  </g>")


def ps_button():
    x, y = PS_C
    return f'''<g id="ps-button">
    {path(PS_D, fill="none", stroke="#050506", stroke_width=".7", stroke_linejoin="round")}
    {path(PS_D, fill="#000", opacity=".6", transform="translate(0 .35)", filter=blur(.25))}
    {path(PS_D, fill="url(#g-ps)")}
    <g clip-path="url(#clip-ps)">
      {soft(x, y - 3.2, 6.5, 3.2, "#FFFFFF", .13)}
    </g>
    {path(PS_D, fill="none", stroke="url(#g-top-rim)", stroke_width=".3")}
  </g>'''


def mute_button():
    x, y = MUTE_C
    w, h = MUTE_W, MUTE_H
    return f'''<g id="mute-button">
    {path(capsule_path(x, y, w + 0.6, h + 0.6), fill="#060607")}
    {path(capsule_path(x, y, w, h), fill="url(#g-mute)")}
    {path(capsule_path(x, y - 0.3, w - 1.4, h - 1.5), fill="#FFFFFF", opacity=".06")}
    {path(capsule_path(x, y, w, h), fill="none", stroke="#474A50", stroke_width=".18")}
  </g>'''


def speaker_grille():
    """Built-in speaker: a small lens-shaped field of holes above the PS button."""
    cx, cy = GRILLE_C
    pitch, row_h, r_hole = 1.1, 0.95, 0.28
    a, b = 4.6, 1.6  # half-extent of the lens-shaped envelope
    lips, holes = [], []
    for row in (-1, 0, 1):
        off = 0.0 if row else pitch / 2
        for i in range(-5, 6):
            hx, hy = off + i * pitch, row * row_h
            if (hx / a) ** 2 + (hy / b) ** 2 <= 1.0:
                lips.append(circle(cx + hx, cy + hy + 0.07, r_hole + 0.05))
                holes.append(circle(cx + hx, cy + hy, r_hole))
    return f'''<g id="speaker-grille">
    <g fill="#4A4D54" opacity=".4">{"".join(lips)}</g>
    <g fill="#030304">{"".join(holes)}</g>
  </g>'''


def player_leds():
    out = []
    for k in range(-2, 3):
        x = X0 + k * LED_STEP
        led = capsule_path(x, LED_Y, 1.4, 0.45)  # each LED shows as a short dash
        if k == 0:  # player 1: only the centre LED is lit
            out.append(soft(x, LED_Y, 3.0, 1.9, "#FFFFFF", .5))
            out.append(path(led, fill="#FFFFFF"))
        else:
            out.append(path(led, fill="#000", opacity=".12"))  # unlit: barely visible
    return '<g id="player-leds">\n    ' + "\n    ".join(out) + "\n  </g>"


def small_buttons():
    out = []
    for side in ("create", "options"):
        if side == "create":
            x, y, rot = CREATE_C[0], CREATE_C[1], -CREATE_TILT
        else:
            x, y, rot = mx(CREATE_C[0]), CREATE_C[1], CREATE_TILT
        w, h = CREATE_W, CREATE_H
        cap = capsule_path(0, 0, w, h)
        if side == "options":
            # "≡" printed on the shell above the button
            icon = "".join(f'<path d="M-1.3 {n(-h / 2 - dy)}H1.3"/>' for dy in (1.5, 2.25, 3.0))
        else:
            # Create: three short rays fanning out above the button
            fx, fy = 0.0, -h / 2 + 0.6
            rays = []
            for ang in (-132, -90, -48):
                c, s = math.cos(rad(ang)), math.sin(rad(ang))
                rays.append(f"M{pt(fx + 1.8 * c, fy + 1.8 * s)}L{pt(fx + 3.6 * c, fy + 3.6 * s)}")
            icon = f'<path d="{"".join(rays)}"/>'
        out.append(f'''<g id="btn-{side}" transform="translate({n(x)} {n(y)}) rotate({n(rot)})">
      {path(capsule_path(0, 0, w + 0.6, h + 0.6), fill="#000", opacity=".2",
            transform=f"rotate({n(-rot)}) translate(0 .6) rotate({n(rot)})", filter=blur(.4))}
      {path(capsule_path(0, 0, w + 0.6, h + 0.6), fill=C['gap'])}
      {path(cap, fill="url(#g-key)")}
      {path(capsule_path(0, -h / 2 + 1.0, w - 0.4, 0.8), fill="#FFFFFF", opacity=".22", filter=blur(.2))}
      {path(capsule_path(0, 0, w - 0.2, h - 0.2), fill="none", stroke="url(#g-top-rim)", stroke_width=".26")}
      <g fill="none" stroke="#9EA2A9" stroke-width=".38" stroke-linecap="round">{icon}</g>
    </g>''')
    return '<g id="create-options">\n    ' + "\n    ".join(out) + "\n  </g>"


def build():
    _DEFS.clear()
    layers = [shadow(), shoulders(), body(), touchpad(), dpad(), face_buttons(), sticks(),
              speaker_grille(), ps_button(), mute_button(), player_leds(), small_buttons()]
    defs = static_defs() + list(_DEFS.values())
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- PS5 DualSense wireless controller, top view. 1 unit = 1 mm.',
        '     Generated by scripts/build_dualsense.py; edit the script, not this file.',
        '     PS button outline: PlayStation logo path from Simple Icons (CC0).',
        '     PlayStation, DualSense and the PS logo are trademarks of Sony Interactive Entertainment. -->',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -8 180 124" width="900" height="620"'
        ' role="img" aria-labelledby="title desc">',
        '  <title id="title">DualSense wireless controller (PS5)</title>',
        '  <desc id="desc">Top view illustration of the Sony PlayStation 5 DualSense wireless controller'
        ' in the white two-tone design.</desc>',
        '  <defs>\n    ' + "\n    ".join(defs) + '\n  </defs>',
    ] + ['  ' + layer for layer in layers] + ['</svg>']
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dualsense.svg"
    with open(out, "w") as fh:
        fh.write(build())
    print("wrote", out)
