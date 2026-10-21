#!/usr/bin/env python3
"""Generate dualsense.svg — a top-view illustration of the PS5 DualSense controller.

Usage:
    python3 scripts/build_dualsense.py [OUT.svg]           write the SVG (default: dualsense.svg)
    python3 scripts/build_dualsense.py [OUT.svg] --check   exit 1 if OUT.svg is out of date

Standard library only. The output is deterministic, so the committed SVG can be
checked against this script.

All geometry is in millimetres (1 SVG user unit = 1 mm). The controller's
bounding box is x 0..160, y 0..105; the axis of symmetry is x = 80, and every
symmetric outline is built from its left half and mirrored.

Proportions follow Sony's published size (160 mm wide; 160 x 106 mm seen from
above) and positions measured from the PromptFont "DualSense" glyph (U+2441,
SIL OFL), whose aspect ratio matches that envelope. The glyph was only
measured, not copied. Light comes from the top of the picture throughout.
"""
import argparse
import math
import re
import sys

X0 = 80.0          # axis of symmetry
ID_PREFIX = "ds-"  # every id in the output gets this prefix, so the SVG can be inlined in HTML


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


def mirror_anchors(anchors, reverse=True):
    """Mirror anchors about the axis.

    With reverse=True the order and direction of travel are reversed too, so a
    left half traced downwards becomes the right half traced upwards.
    """
    out = []
    for a in (reversed(anchors) if reverse else anchors):
        x, y, ai, ao, hi, ho = _norm(a)
        if reverse:
            out.append((mx(x), y, -ao, -ai, ho, hi))
        else:
            out.append((mx(x), y, 180 - ai, 180 - ao, hi, ho))
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
            if turn <= 0:
                raise ValueError(f"corner {i}: the polygon must be convex and clockwise on screen")
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
            if R < 0:
                raise ValueError(f"offset {d} turns corner {i} (radius {r}) inside out")
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
        for _ in range(2):  # a second lap covers ranges that wrap past the start
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


def use(ref, **attrs):
    """Draw a shape kept once in <defs>; fill, stroke, transform and filter come from here."""
    return f'<use href="#{ref}"{fmt_attrs(attrs)}/>'


# ----------------------------------------------------------------------------
# minimal SVG path parser (to place the PlayStation logo in absolute coordinates)
# ----------------------------------------------------------------------------
_PATH_TOKEN = re.compile(r"([A-Za-z])|(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)|([\s,]+)")


def parse_path(d):
    """Parse M/L/H/V/C/S/Z path data (absolute or relative) into absolute segments."""
    toks, pos = [], 0
    for m in _PATH_TOKEN.finditer(d):
        if m.start() != pos:
            break
        pos = m.end()
        if m.group(1):
            if m.group(1) not in "MmLlHhVvCcSsZz":
                raise ValueError(f"unsupported path command {m.group(1)!r}")
            toks.append(m.group(1))
        elif m.group(2):
            toks.append(float(m.group(2)))
    if pos != len(d):
        raise ValueError(f"cannot parse path data at {d[pos:pos + 12]!r}")

    i, cmd = 0, None
    cur = start = (0.0, 0.0)
    prev_c2 = None
    out = []

    def num():
        nonlocal i
        if i >= len(toks) or isinstance(toks[i], str):
            raise ValueError(f"path command {cmd!r} is missing a number")
        i += 1
        return toks[i - 1]

    while i < len(toks):
        if isinstance(toks[i], str):
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cur, prev_c2 = start, None
                continue
        elif cmd is None:
            raise ValueError("path data must start with a command")
        rel = cmd.islower()
        ox, oy = cur if rel else (0.0, 0.0)
        op = cmd.upper()
        if op == "M":
            cur = start = (ox + num(), oy + num())
            out.append(("M", cur))
            cmd, prev_c2 = ("l" if rel else "L"), None
        elif op == "L":
            cur = (ox + num(), oy + num())
            out.append(("L", cur))
            prev_c2 = None
        elif op == "H":
            v = num()
            cur = ((cur[0] + v) if rel else v, cur[1])
            out.append(("L", cur))
            prev_c2 = None
        elif op == "V":
            v = num()
            cur = (cur[0], (cur[1] + v) if rel else v)
            out.append(("L", cur))
            prev_c2 = None
        elif op in "CS":
            if op == "C":
                c1 = (ox + num(), oy + num())
            else:
                c1 = (2 * cur[0] - prev_c2[0], 2 * cur[1] - prev_c2[1]) if prev_c2 else cur
            c2 = (ox + num(), oy + num())
            cur = (ox + num(), oy + num())
            out.append(("C", c1, c2, cur))
            prev_c2 = c2
        else:  # Z with numbers after it
            raise ValueError("numbers after a closepath command")
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
            xs.append(cur[0])
            ys.append(cur[1])
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
# Fitted to the glyph to within ~0.1 mm, except a slightly rounder grip tip.
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
    (4.10, 98.0, 63.1, 4.3, 3.9),
    (16.4, 105.0, 0, 6.0, 3.4),
    (22.75, 102.45, -58, 2.6, 3.6),
    (27.69, 92.0, -67.7, 3.8, 3.8),
    (31.71, 82.0, -63.4, 3.6, 3.0),
    (37.38, 74.0, -44.6, 3.0, 2.6),
    (44.5, 69.5, -18.7, 2.4, 3.2),
    (55.0, 68.01, -0.6, 3.6, 8),
    (80.0, 68.0, 0, 8, 8),
]
OUTLINE = sym_closed(OUTLINE_L)
TOP_EDGE = (spline(OUTLINE_L[:4], closed=False) + " "
            + spline(mirror_anchors(OUTLINE_L[:4], reverse=False), closed=False))

# Touchpad: trapezoid wider at the top (glyph: 67.4 mm at the top edge, 13.3° sides,
# bottom edge at y 35.6 with ~10.5 mm corners), top edge following the shell's front arc.
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
CHANNEL = 2.0            # touchpad edge -> white shell edge; the light bar sits in it
LB_IN, LB_OUT = 0.2, 1.8    # light-bar strip, as offsets from the pad edge

# The white shell's inner edge (left): runs beside the pad, rounds the junction
# below the pad's corner, then sweeps down the inside of the grip to its tip.
_L = math.hypot(*_TP_LEFT_DIR)
_NX, _NY = -_TP_LEFT_DIR[1] / _L, _TP_LEFT_DIR[0] / _L  # outward normal of the pad's left edge


def shell_edge_x(y):
    """x of the pad's left edge offset outward by CHANNEL, at height y."""
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
    (15.10, 100.0, 111.8, 5.0, 1.8),
    (13.9, 104.3, 98, 1.6, 1.5),   # meets the tip squarely, so the black band ends round
    (13.7, 108.0, 92, 1.5, 2),
]
SHELL_EDGES = (spline(SHELL_EDGE_L, closed=False) + " "
               + spline(mirror_anchors(SHELL_EDGE_L), closed=False))
# Black core = everything inboard of the shell edges (clipped to the silhouette later).
CORE = (spline(SHELL_EDGE_L, closed=False)
        + f" L{pt(13.7, 112)} L{pt(mx(13.7), 112)} L{pt(mx(13.7), 108)} "
        + spline(mirror_anchors(SHELL_EDGE_L), closed=False, move=False)
        + " Z")

# Components. Centres were measured on the glyph; sizes come from the reviewed
# drawing, because the glyph enlarges buttons for legibility.
DPAD_C = (29.35, 30.25)      # glyph: (29.4, 30.2), arms reach 14.6 mm from the centre
FACE_C = (mx(29.35), 30.25)  # mirror of the D-pad (glyph: 130.8, 30.26)
FACE_OFF = 11.0              # glyph: 11.07 mm from the cluster centre to each button
FACE_R = 5.45                # glyph caps are Ø12.9; drawn Ø10.9
STICK_L = (54.5, 52.6)       # glyph: (54.52, 52.6) and its mirror, 51 mm apart
STICK_R = (mx(54.5), 52.6)
STICK_WELL = 11.8            # glyph ring outer radius
STICK_CAP = 9.7
# Centre column, top to bottom: player LEDs, speaker grille, PS button, mute button
# (order from Sony's parts list; spacing chosen so each gap is about 2 mm).
LED_Y = 37.9
LED_STEP = 2.6
GRILLE_C = (80.0, 41.0)
PS_C = (80.0, 48.6)
PS_W = 10.4
MUTE_C = (80.0, 56.6)
MUTE_W, MUTE_H = 7.2, 2.4
CREATE_C = (41.7, 12.6)      # glyph: (41.69, 12.56)
CREATE_W, CREATE_H = 3.2, 7.6
CREATE_TILT = 14.0           # degrees; the top of the Create button leans outward, like the light bar


# ----------------------------------------------------------------------------
# palette
# ----------------------------------------------------------------------------
PALETTE = dict(
    shell_hi="#FCFCFB", shell="#F2F2F0", shell_mid="#E6E7E8", shell_lo="#D2D4D8",
    shell_shade="#8B9098",
    pad_hi="#FAFAF9", pad="#EEEEEC", pad_lo="#DCDDDE",
    core_hi="#36373A", core="#242527", core_lo="#141415",   # neutral black trim
    sheen="#76777B",
    gap="#0B0C0E", gap_clear_top="#B4B9C0", gap_clear="#5A5F67",
    sym="#878C94",           # face-button symbols, seen through the clear caps
    light="#2F6FFF", light_mid="#5A94FF", light_hi="#A9C9FF",
)
C = PALETTE


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
    if _DEFS.get(fid, markup) != markup:
        raise ValueError(f"definition {fid!r} registered twice with different content")
    _DEFS[fid] = markup
    return f"url(#{fid})"


def _tag(v):
    return n(v).replace(".", "_")


def blur(sd, region=None):
    """url() of a Gaussian blur filter (sRGB, so every renderer agrees)."""
    if region:
        x, y, w, h = REGIONS[region]
        fid = f"blur-{_tag(sd)}-{region}"
        box = f'filterUnits="userSpaceOnUse" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'
    else:
        fid = f"blur-{_tag(sd)}"
        box = 'x="-50%" y="-50%" width="200%" height="200%"'
    return _define(fid, f'<filter id="{fid}" {box} color-interpolation-filters="sRGB">'
                        f'<feGaussianBlur stdDeviation="{n(sd)}"/></filter>')


def soft(cx, cy, rx, ry, color, alpha, rot=0):
    """Soft-edged elliptical highlight or shade, drawn with a radial gradient (no filter)."""
    gid = f"soft-{color.lstrip('#').lower()}-{_tag(alpha)}"
    _define(gid, f'''<radialGradient id="{gid}">
      <stop offset="0" stop-color="{color}" stop-opacity="{n(alpha)}"/>
      <stop offset=".45" stop-color="{color}" stop-opacity="{n(alpha * .72)}"/>
      <stop offset=".78" stop-color="{color}" stop-opacity="{n(alpha * .22)}"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>''')
    tr = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="url(#{gid})"{tr}/>'


def _world_up_gradient(gid, rot, stops):
    """Linear gradient for a key drawn rotated by `rot`, lit from the top of the picture."""
    a = math.radians(rot)
    ux, uy = -math.sin(a), -math.cos(a)  # world (0, -1) expressed in the key's frame
    v = f'x1="{n(.5 + ux / 2)}" y1="{n(.5 + uy / 2)}" x2="{n(.5 - ux / 2)}" y2="{n(.5 - uy / 2)}"'
    return _define(gid, f'<linearGradient id="{gid}" {v}>{stops}</linearGradient>')


def ps_logo_path():
    segs = parse_path(PS_LOGO)
    x0, y0, x1, y1 = bbox_of(segs)
    s = PS_W / (x1 - x0)
    return transform_path(segs, s, PS_C[0] - (x0 + x1) / 2 * s, PS_C[1] - (y0 + y1) / 2 * s)


PS_D = ps_logo_path()


def _dpad_key():
    """The 'up' D-pad key in local coordinates (D-pad centre at 0,0), pointing at the centre."""
    hw, tip, R = 4.95, 2.6, 14.6
    sh = -(tip + hw)            # where the 45° tip edges meet the sides
    return RoundedPoly(
        [(-hw, -R + 0.45), (0, -R - 0.25), (hw, -R + 0.45), (hw, sh), (0, -tip), (-hw, sh)],
        [2.0, 18.0, 2.0, 1.0, 1.0, 1.0],
    )


DPAD_KEY = _dpad_key()


def static_defs():
    """Shapes drawn more than once (used via <use>), clip paths and named gradients."""
    return [
        # shared shapes
        f'<path id="outline" d="{OUTLINE}"/>',
        f'<path id="core-shape" d="{CORE}"/>',
        f'<path id="shell-edges" d="{SHELL_EDGES}"/>',
        f'<path id="top-edge" d="{TOP_EDGE}"/>',
        f'<path id="pad-shape" d="{TP.path(0)}"/>',
        f'<path id="ps-logo" d="{PS_D}"/>',
        f'<path id="dpad-key" d="{DPAD_KEY.path(0)}"/>',
        f'<path id="dpad-gap" d="{DPAD_KEY.path(0.22)}"/>',
        f'<path id="dpad-bevel" d="{DPAD_KEY.path(-0.55)}"/>',
        '<clipPath id="clip-body"><use href="#outline"/></clipPath>',
        '<clipPath id="clip-core"><use href="#core-shape"/></clipPath>',
        '<clipPath id="clip-pad"><use href="#pad-shape"/></clipPath>',
        '<clipPath id="clip-ps"><use href="#ps-logo"/></clipPath>',
        # below the touchpad: lets the black trim's outer edge be redrawn dark without touching the pad
        '<clipPath id="clip-low"><rect x="-10" y="38" width="180" height="80"/></clipPath>',
        # edge falloff that follows the light: faint along the front edge, strong at the grip ends
        f'''<linearGradient id="g-edge" x1="0" y1="0" x2="0" y2="105" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['shell_shade']}" stop-opacity=".15"/>
      <stop offset=".25" stop-color="{C['shell_shade']}" stop-opacity=".75"/>
      <stop offset="1" stop-color="{C['shell_shade']}"/>
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
        '''<linearGradient id="g-pad-rim" x1="0" y1="2" x2="0" y2="36" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>
      <stop offset=".5" stop-color="#FFFFFF" stop-opacity=".35"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>''',
        # hairline gaps round the clear keys: lit from above, in shadow below
        f'''<linearGradient id="g-gap" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{C['gap_clear_top']}"/>
      <stop offset="1" stop-color="{C['gap_clear']}"/>
    </linearGradient>''',
        # face buttons: clear caps over a white backing
        '''<radialGradient id="g-face" cx=".5" cy=".4" r=".62">
      <stop offset="0" stop-color="#F6F7F8"/>
      <stop offset=".6" stop-color="#E4E7EB"/>
      <stop offset=".88" stop-color="#CACFD5"/>
      <stop offset="1" stop-color="#B6BCC4"/>
    </radialGradient>''',
        '''<radialGradient id="g-face-caustic" cx=".5" cy=".86" r=".5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".5"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>''',
        '''<linearGradient id="g-cap-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"/>
      <stop offset=".4" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset=".6" stop-color="#959BA4" stop-opacity="0"/>
      <stop offset="1" stop-color="#959BA4" stop-opacity=".4"/>
    </linearGradient>''',
        # black parts
        '''<linearGradient id="g-l1" x1="0" y1="0" x2="0" y2="7" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#454649"/>
      <stop offset=".3" stop-color="#28292B"/>
      <stop offset="1" stop-color="#121213"/>
    </linearGradient>''',
        '''<linearGradient id="g-key" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#414245"/>
      <stop offset=".45" stop-color="#27282A"/>
      <stop offset="1" stop-color="#151516"/>
    </linearGradient>''',
        '''<linearGradient id="g-top-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#C5C7CB" stop-opacity=".8"/>
      <stop offset=".3" stop-color="#7C7E82" stop-opacity=".25"/>
      <stop offset=".55" stop-color="#7C7E82" stop-opacity="0"/>
    </linearGradient>''',
        '''<radialGradient id="g-dish" cx=".5" cy=".66" r=".6">
      <stop offset="0" stop-color="#38393C"/>
      <stop offset=".55" stop-color="#212224"/>
      <stop offset="1" stop-color="#0E0E0F"/>
    </radialGradient>''',
        '''<linearGradient id="g-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3E3F42"/>
      <stop offset=".4" stop-color="#252628"/>
      <stop offset="1" stop-color="#0F0F10"/>
    </linearGradient>''',
        '''<radialGradient id="g-well" cx=".5" cy=".5" r=".5">
      <stop offset=".74" stop-color="#040404"/>
      <stop offset=".93" stop-color="#0E0E0F"/>
      <stop offset="1" stop-color="#2B2C2E"/>
    </radialGradient>''',
        # the lip of a stick opening catches the light on its lower side
        '''<linearGradient id="g-lip" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1C1C1E"/>
      <stop offset=".55" stop-color="#2F3032"/>
      <stop offset="1" stop-color="#5A5B5F"/>
    </linearGradient>''',
        '''<linearGradient id="g-ps" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#404145"/>
      <stop offset=".45" stop-color="#1D1D1F"/>
      <stop offset="1" stop-color="#0F0F10"/>
    </linearGradient>''',
        '''<linearGradient id="g-mute" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#303134"/>
      <stop offset=".5" stop-color="#242527"/>
      <stop offset="1" stop-color="#19191B"/>
    </linearGradient>''',
    ]


# ----------------------------------------------------------------------------
# builders — each returns one top-level group of the drawing
# ----------------------------------------------------------------------------
def shadow():
    """Soft shadow under the controller plus a tighter contact shadow."""
    return f'''<g id="drop-shadow">
    {use("outline", transform="translate(0 2.6)", fill="#000", opacity=".2", filter=blur(3, "canvas"))}
    {use("outline", transform="translate(0 .9)", fill="#000", opacity=".3", filter=blur(.8, "canvas"))}
  </g>'''


def shoulders():
    """L1 bumper and a sliver of the L2 trigger behind it, seen from above."""
    # Slim bands that follow the shell's top edge; the lower parts tuck under the shell.
    l2 = spline([
        (41.0, 5.2, -95, 1, 1.2),
        (40.1, 2.05, -140, 1.0, 1.0),
        (37.9, 0.55, 186, 1.2, 1.8),
        (33.0, 0.35, 177, 2.4, 2.8),
        (25.4, 1.85, 166, 2.8, 2.0),
        (20.4, 3.85, 150, 1.6, 1.2),
        (18.3, 7.2, 112, 1.2, 1.0),
        (18.6, 10.0, 20, 1.5, 5),
        (30.0, 7.4, -8, 6, 6),
    ])
    l2_hi = spline([
        (38.6, 0.85, 187, 1, 1.6),
        (33.0, 0.62, 177, 2.2, 2.8),
        (25.5, 2.1, 166, 2.8, 2.0),
        (21.2, 3.85, 150, 1.4, 1),
    ], closed=False)
    l1 = spline([
        (41.0, 5.2, -95, 1, 1.2),
        (40.1, 2.4, -140, 1.0, 1.0),
        (38.0, 1.15, 186, 1.2, 1.8),
        (33.0, 1.0, 177, 2.2, 2.8),
        (25.5, 2.45, 166, 2.8, 2.0),
        (20.6, 4.15, 150, 1.6, 1.2),
        (18.3, 7.2, 112, 1.2, 1.0),
        (18.6, 10.0, 20, 1.5, 5),
        (30.0, 7.4, -8, 6, 6),
        (41.0, 5.2, -14, 4, 1),
    ])
    l1_hi = spline([
        (38.0, 1.5, 186, 1, 1.5),
        (33.0, 1.38, 177, 2.0, 2.6),
        (25.6, 2.8, 166, 2.6, 1.8),
        (21.3, 4.3, 150, 1.4, 1),
    ], closed=False)
    parts = []
    for side, tr in (("left", ""), ("right", f' transform="translate({n(2 * X0)} 0) scale(-1 1)"')):
        parts.append(f'''<g id="shoulder-{side}"{tr}>
      {path(l2, fill="#0D0D0E")}
      {path(l2_hi, fill="none", stroke="#4B4C50", stroke_width=".25", stroke_linecap="round", opacity=".65")}
      {path(l1, fill="url(#g-l1)")}
      {path(l1_hi, fill="none", stroke="#A0A2A6", stroke_width=".45", stroke_linecap="round", opacity=".3",
            filter=blur(.12))}
    </g>''')
    return ('<g id="shoulder-buttons">\n    <!-- per side: L2 trigger sliver + top highlight, L1 bumper + satin highlight -->\n    '
            + "\n    ".join(parts) + "\n  </g>")


def body():
    """White shell with its form shading, then the black core trim."""
    return f'''<g id="body" clip-path="url(#clip-body)">
    <!-- white shell -->
    {use("outline", fill="url(#g-shell)")}
    <g id="shell-shading">
      {use("outline", fill="none", stroke="url(#g-edge)", stroke_width="9", opacity=".36", filter=blur(3, "body"))}
      {use("outline", fill="none", stroke="#6E737B", stroke_width="1.8", opacity=".3", filter=blur(.8, "body"))}
      {soft(24, 33, 26, 30, "#FFFFFF", .7)}
      {soft(mx(24), 33, 26, 30, "#FFFFFF", .7)}
      <!-- grips: a lit crown, shade toward the black trim, darker toward the tips -->
      {soft(13.5, 72, 8.5, 25, "#FFFFFF", .5, -17)}
      {soft(mx(13.5), 72, 8.5, 25, "#FFFFFF", .5, 17)}
      {soft(23.5, 84, 4.5, 21, "#8E949C", .28, -20)}
      {soft(mx(23.5), 84, 4.5, 21, "#8E949C", .28, 20)}
      {soft(12, 100, 17, 12, "#8E949C", .38)}
      {soft(mx(12), 100, 17, 12, "#8E949C", .38)}
      <!-- the shell rolls down into the seam beside the core -->
      {use("shell-edges", fill="none", stroke="#8F959E", stroke_width="1.5", opacity=".4", filter=blur(.4, "body"))}
    </g>
    <!-- black core: the centre section and the inner halves of the grips -->
    <g id="core">
      {use("core-shape", fill="url(#g-core)")}
      <g clip-path="url(#clip-core)">
        {use("core-shape", fill="none", stroke="#000", stroke_width="2.2", opacity=".5", filter=blur(.8, "core"))}
        {soft(80, 50, 44, 22, C['sheen'], .24)}
        {soft(31, 79, 8.5, 27, "#95979B", .26, 21)}
        {soft(mx(31), 79, 8.5, 27, "#95979B", .26, -21)}
        {use("outline", fill="none", stroke="#000", stroke_width="5", opacity=".45", filter=blur(1.5, "core"))}
        {use("shell-edges", fill="none", stroke="#8F9195", stroke_width=".8", opacity=".22", filter=blur(.4, "core"))}
        <!-- soft rim where the black edges roll away (keeps the body readable on dark backgrounds) -->
        {use("outline", fill="none", stroke="#717276", stroke_width="1.1", opacity=".48", filter=blur(.4, "core"))}
      </g>
      {use("shell-edges", fill="none", stroke="#050505", stroke_width=".22")}
    </g>
  </g>
  <g id="outline-stroke">
    {use("outline", fill="none", stroke="#8C9198", stroke_width=".25", opacity=".55")}
    <!-- a light outline would halo the black trim on dark backgrounds, so redraw its edge dark -->
    <g clip-path="url(#clip-low)"><g clip-path="url(#clip-core)">
      {use("outline", fill="none", stroke="#0D0D0E", stroke_width=".3")}
    </g></g>
  </g>'''


def touchpad():
    """Touchpad, the light bars beside it, and the rim light along the front edge."""
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
    left = (TP.walk(lb_mid, mm[9] - (mm[9] - mm[8]) * wrap, mm[10])
            + f" L{pt(top_l[0] - 3 * ux, top_l[1] - 3 * uy)}")
    right = (f"M{pt(top_r[0] + 3 * ux, top_r[1] - 3 * uy)} L"
             + TP.walk(lb_mid, mm[5], mm[6] + (mm[7] - mm[6]) * wrap)[1:])
    both = left + " " + right
    return f'''<g id="touchpad-and-light-bar" clip-path="url(#clip-body)">
    <!-- seam round the pad -->
    {path(TP.path(0.3), fill=C['gap'])}
    <!-- light bars: wide bloom, inner glow, a softly edged strip, a bright core -->
    <g id="light-bar" fill="none" stroke-linecap="round">
      {path(both, stroke=C['light'], stroke_width="7", opacity=".08", filter=blur(3, "lightbar"))}
      {path(both, stroke=C['light'], stroke_width="3.2", opacity=".32", filter=blur(1.2, "lightbar"))}
      {path(both, stroke=C['light_mid'], stroke_width=n(lb_w), filter=blur(.12, "lightbar"))}
      {path(both, stroke=C['light_hi'], stroke_width=".5", opacity=".5", filter=blur(.12, "lightbar"))}
    </g>
    <!-- pad surface -->
    {use("pad-shape", fill="#000", opacity=".45", transform="translate(0 .3)", filter=blur(.4))}
    {use("pad-shape", fill="url(#g-pad)")}
    <g clip-path="url(#clip-pad)">
      {use("pad-shape", fill="none", stroke="#9DA2AA", stroke_width="1.6", opacity=".34", filter=blur(.8))}
      {soft(80, 10, 34, 13, "#FFFFFF", .7)}
      {path(both, fill="none", stroke=C['light'], stroke_width="3", opacity=".2", filter=blur(1.5, "lightbar"))}
      {path(TP.path(-0.35), fill="none", stroke="url(#g-pad-rim)", stroke_width=".4")}
    </g>
    {use("pad-shape", fill="none", stroke="#7D828A", stroke_width=".2")}
    <!-- rim light along the whole front edge, over the pad and the shell -->
    {use("top-edge", fill="none", stroke="#FFFFFF", stroke_width=".9", opacity=".9", transform="translate(0 .5)",
         filter=blur(.2))}
  </g>'''


def dpad():
    """Four clear keys over a white backing, each a "house" pointing at the centre."""
    cx, cy = DPAD_C
    casts, gaps, shadows, keys = [], [], [], []
    for name, rot in (("up", 0), ("right", 90), ("down", 180), ("left", 270)):
        place = f"translate({n(cx)} {n(cy)}) rotate({rot})"
        fill = _world_up_gradient(f"g-dpad-{rot}", rot,
                                  '<stop offset="0" stop-color="#F7F8F9"/><stop offset=".5" stop-color="#DCE0E4"/>'
                                  '<stop offset="1" stop-color="#BCC2C9"/>')
        caustic = _world_up_gradient(f"g-dpad-caustic-{rot}", rot,
                                     '<stop offset=".5" stop-color="#FFFFFF" stop-opacity="0"/>'
                                     '<stop offset=".92" stop-color="#FFFFFF" stop-opacity=".5"/>'
                                     '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>')
        spec = _world_up_gradient(f"g-dpad-spec-{rot}", rot,
                                  '<stop offset=".02" stop-color="#FFFFFF" stop-opacity="0"/>'
                                  '<stop offset=".05" stop-color="#FFFFFF" stop-opacity=".2"/>'
                                  '<stop offset=".1" stop-color="#FFFFFF" stop-opacity=".1"/>'
                                  '<stop offset=".16" stop-color="#FFFFFF" stop-opacity="0"/>')
        rim = _world_up_gradient(f"g-dpad-rim-{rot}", rot,
                                 '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".7"/>'
                                 '<stop offset=".35" stop-color="#FFFFFF" stop-opacity=".15"/>'
                                 '<stop offset=".6" stop-color="#FFFFFF" stop-opacity="0"/>')
        gap = _world_up_gradient(f"g-gap-{rot}", rot,
                                 f'<stop offset="0" stop-color="{C["gap_clear_top"]}"/>'
                                 f'<stop offset="1" stop-color="{C["gap_clear"]}"/>')
        casts.append(use("dpad-gap", transform=f"translate({n(cx)} {n(cy + 0.8)}) rotate({rot})"))
        gaps.append(use("dpad-gap", fill=gap, transform=place))
        shadows.append(use("dpad-key", transform=f"translate({n(cx)} {n(cy + 0.3)}) rotate({rot})"))
        keys.append(f'''<g id="dpad-{name}" transform="{place}">
        {use("dpad-key", fill=fill)}
        {use("dpad-key", fill=caustic)}
        {use("dpad-key", fill=spec)}
        {use("dpad-bevel", fill="none", stroke="#FFFFFF", stroke_width=".3", opacity=".4")}
        {use("dpad-key", fill="none", stroke=rim, stroke_width=".26")}
      </g>''')
    return ('<g id="d-pad">\n      <!-- cast shadow, hairline gaps, contact shadow, then each key: '
            'base, caustic, specular edge, bevel, rim -->\n      '
            + f'<g fill="#000" opacity=".14" filter="{blur(.8)}">' + "".join(casts) + "</g>\n      "
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
            glyph = (f'<rect x="{n(x - s_)}" y="{n(y - s_)}" width="{n(2 * s_)}" height="{n(2 * s_)}"'
                     ' stroke-linejoin="miter"/>')
        out.append(f'''<g id="btn-{name}">
      {circle(x, y, r, fill="url(#g-face)")}
      {circle(x, y, r, fill="url(#g-face-caustic)")}
      <g fill="none" stroke="#FFFFFF" stroke-width="{sw}" opacity=".55" transform="translate(0 .16)"
         filter="{blur(.15)}">{glyph}</g>
      <g fill="none" stroke="{C['sym']}" stroke-width="{sw}">{glyph}</g>
      {soft(x, y - r * 0.5, r * 0.62, r * 0.3, "#FFFFFF", .32)}
      {ellipse(x, y - r * 0.775, r * 0.433, r * 0.092, fill="#FFFFFF", opacity=".35", filter=blur(.2))}
      {circle(x, y, r - 0.16, fill="none", stroke="url(#g-cap-rim)", stroke_width=".3")}
    </g>''')
    casts = "".join(circle(x, y + 0.8, r + 0.75) for x, y in pos.values())
    gaps = "".join(circle(x, y, r + 0.22) for x, y in pos.values())
    shadows = "".join(circle(x, y + 0.35, r) for x, y in pos.values())
    return ('<g id="face-buttons">\n    <!-- cast shadows, hairline gaps, contact shadows, then each cap: '
            'base, caustic, symbol (lit copy + grey), highlights, rim -->\n    '
            f'<g fill="#000" opacity=".14" filter="{blur(.8)}">{casts}</g>\n    '
            f'<g fill="url(#g-gap)">{gaps}</g>\n    '
            f'<g fill="#000" opacity=".16" filter="{blur(.45)}">{shadows}</g>\n    '
            + "\n    ".join(out) + "\n  </g>")


def stick(cx, cy, side):
    """One analog stick: opening with a lit lip, cap with a knurled rim and a concave dish."""
    rw, rc = STICK_WELL, STICK_CAP
    dish = rc * 0.74
    ring_r = float(n((rc + dish) / 2 + 0.15))  # the radius exactly as written to the file
    period = 2 * math.pi * ring_r / 110         # 110 ridges that close up without a seam
    knurl = dict(fill="none", stroke="#08080A", stroke_width=n(rc - dish - 0.5),
                 stroke_dasharray=f"{period * 0.42:.4f} {period * 0.58:.4f}", opacity=".45")
    return f'''<g id="stick-{side}">
      {circle(cx, cy, rw + 0.5, fill="none", stroke="url(#g-lip)", stroke_width=".55")}
      {circle(cx, cy, rw, fill="url(#g-well)")}
      {circle(cx, cy, rc, fill="url(#g-rim)")}
      {circle(cx, cy, ring_r, **knurl)}
      {circle(cx, cy, rc - 0.22, fill="none", stroke="url(#g-top-rim)", stroke_width=".3", opacity=".55")}
      {circle(cx, cy, dish + 0.4, fill="#333437")}
      {circle(cx, cy, dish, fill="url(#g-dish)")}
      {soft(cx, cy - dish * 0.45, dish * 0.95, dish * 0.6, "#000000", .42)}
      {soft(cx, cy + dish * 0.8, dish * 0.62, dish * 0.2, "#9C9EA2", .18)}
      {soft(cx, cy - rc * 0.84, rc * 0.62, rc * 0.16, "#FFFFFF", .16)}
    </g>'''


def sticks():
    return ('<g id="analog-sticks">\n    <!-- per stick: lip, opening, cap, knurling, cap rim, dish, dish shading -->\n    '
            + stick(*STICK_L, "left") + "\n    " + stick(*STICK_R, "right") + "\n  </g>")


def ps_button():
    """The PS button: a raised black key moulded in the shape of the PlayStation logo."""
    x, y = PS_C
    return f'''<g id="ps-button">
    {use("ps-logo", fill="none", stroke="#08080A", stroke_width=".35", stroke_linejoin="round")}
    {use("ps-logo", fill="#000", opacity=".6", transform="translate(0 .35)", filter=blur(.25))}
    {use("ps-logo", fill="url(#g-ps)")}
    <g clip-path="url(#clip-ps)">
      {soft(x, y - 3.2, 6.5, 3.2, "#FFFFFF", .13)}
    </g>
    {use("ps-logo", fill="none", stroke="url(#g-top-rim)", stroke_width=".25")}
  </g>'''


def mute_button():
    """Mute button: a slim dark bar (it glows orange only when the microphone is muted)."""
    x, y = MUTE_C
    w, h = MUTE_W, MUTE_H
    return f'''<g id="mute-button">
    {path(capsule_path(x, y, w + 0.6, h + 0.6), fill="#060607")}
    {path(capsule_path(x, y, w, h), fill="url(#g-mute)")}
    {path(capsule_path(x, y - 0.3, w - 1.4, h - 1.5), fill="#FFFFFF", opacity=".06")}
    {path(capsule_path(x, y, w, h), fill="none", stroke="#48494C", stroke_width=".18")}
  </g>'''


def speaker_grille():
    """Built-in speaker: a small lens-shaped field of holes above the PS button."""
    cx, cy = GRILLE_C
    pitch, row_h, r_hole = 1.1, 0.95, 0.26
    a, b = 4.6, 1.6  # half-extent of the lens-shaped envelope
    holes = []
    for row in (-1, 0, 1):
        off = 0.0 if row else pitch / 2
        for i in range(-5, 6):
            hx, hy = off + i * pitch, row * row_h
            if (hx / a) ** 2 + (hy / b) ** 2 <= 1.0:
                holes.append(circle(cx + hx, cy + hy, r_hole))
    return f'''<g id="speaker-grille" fill="#0B0B0C" opacity=".6">
    {"".join(holes)}
  </g>'''


def player_leds():
    """Five player-indicator LEDs; for player 1 only the centre one is lit."""
    out = []
    for k in range(-2, 3):
        x = X0 + k * LED_STEP
        led = capsule_path(x, LED_Y, 1.4, 0.45)  # each LED shows as a short dash
        if k == 0:
            out.append(soft(x, LED_Y, 2.0, 1.2, "#FFFFFF", .55))
            out.append(path(led, fill="#FFFFFF"))
        else:
            out.append(path(led, fill="#000", opacity=".05"))  # unlit: practically invisible
    return '<g id="player-leds">\n    ' + "\n    ".join(out) + "\n  </g>"


def small_buttons():
    """Create and Options: small black pills beside the light bars, icons printed above them."""
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
            icon = "".join(f'<path d="M-1.15 {n(-h / 2 - dy)}H1.15"/>' for dy in (1.45, 2.1, 2.75))
        else:
            # Create: three short rays fanning out above the button
            fx, fy = 0.0, -h / 2 + 0.6
            rays = []
            for ang in (-132, -90, -48):
                c, s = math.cos(rad(ang)), math.sin(rad(ang))
                rays.append(f"M{pt(fx + 1.85 * c, fy + 1.85 * s)}L{pt(fx + 3.35 * c, fy + 3.35 * s)}")
            icon = f'<path d="{"".join(rays)}"/>'
        out.append(f'''<g id="btn-{side}" transform="translate({n(x)} {n(y)}) rotate({n(rot)})">
      {path(capsule_path(0, 0, w + 0.6, h + 0.6), fill="#000", opacity=".2",
            transform=f"rotate({n(-rot)}) translate(0 .6) rotate({n(rot)})", filter=blur(.4))}
      {path(capsule_path(0, 0, w + 0.4, h + 0.4), fill=C['gap'])}
      {path(cap, fill="url(#g-key)")}
      {path(capsule_path(0, -h / 2 + 1.0, w - 0.4, 0.8), fill="#FFFFFF", opacity=".22", filter=blur(.2))}
      {path(capsule_path(0, 0, w - 0.2, h - 0.2), fill="none", stroke="url(#g-top-rim)", stroke_width=".26")}
      <g fill="none" stroke="#AEB2B8" stroke-width=".32" stroke-linecap="round">{icon}</g>
    </g>''')
    return '<g id="create-options">\n    ' + "\n    ".join(out) + "\n  </g>"


def _prefix_ids(svg, prefix):
    """Namespace every id and every reference to it."""
    svg = re.sub(r'(\sid=")', r"\1" + prefix, svg)
    svg = svg.replace("url(#", "url(#" + prefix).replace('href="#', 'href="#' + prefix)
    return svg


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
        ' role="img" aria-labelledby="title" aria-describedby="desc">',
        '  <title id="title">DualSense wireless controller (PS5)</title>',
        '  <desc id="desc">Top view illustration of the Sony PlayStation 5 DualSense wireless controller'
        ' in the white two-tone design.</desc>',
        '  <defs>\n    ' + "\n    ".join(defs) + '\n  </defs>',
    ] + ['  ' + layer for layer in layers] + ['</svg>']
    svg = "\n".join(parts) + "\n"
    svg = _prefix_ids(svg, ID_PREFIX)
    return svg.replace('aria-labelledby="title" aria-describedby="desc"',
                       f'aria-labelledby="{ID_PREFIX}title" aria-describedby="{ID_PREFIX}desc"')


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the DualSense top-view SVG illustration.")
    ap.add_argument("output", nargs="?", default="dualsense.svg", help="output file (default: dualsense.svg)")
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if the output file differs from a fresh build")
    args = ap.parse_args(argv)
    svg = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8", newline="") as fh:
                current = fh.read()
        except FileNotFoundError:
            current = None
        if current != svg:
            print(f"{args.output} is out of date; run without --check to regenerate it", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date")
        return 0
    with open(args.output, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
