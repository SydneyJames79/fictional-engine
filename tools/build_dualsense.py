#!/usr/bin/env python3
"""Generates dualsense.svg — a straight-on front view of the white PS5 DualSense wireless controller.

Coordinate system: 10 units = 1 mm. The controller spans x 0..1600 (160 mm) and y 0..1060 (106 mm:
trigger tips at the top, grip ends at the bottom). Mirror axis x = 800. Light comes from the top-left.
Geometry was calibrated against published dimensions and an orthographic projection of a 3D model.
All ids carry the prefix "ds-" so the file can be inlined next to other SVGs without collisions.
"""
import sys, os, base64, argparse, math
sys.path.insert(0, os.path.dirname(__file__))
from svgkit import *

CX = 800
VB = (-8, -8, 1616, 1076)
P = 'ds-'                      # id prefix

# ---------------- palette ----------------
SHELL_HI = '#ffffff'
SHELL = '#f4f4f6'
SHELL_LO = '#dfe0e5'
SHELL_EDGE = '#b4b6bf'
SEAM = '#9a9ca6'
FRAME_HI = '#3a3a40'
FRAME = '#222226'
FRAME_LO = '#141416'
PAD_EDGE = '#c9cad1'
SYMBOL = '#75757d'
LIGHTBAR = '#4d9dff'
LIGHTBAR_CORE = '#cfe6ff'
DARK_EDGE = '#3a3a40'          # outline for black parts (keeps them visible on dark backgrounds)


def arc(cx, cy, r, a0, a1):
    """Path data for a circular arc from angle a0 to a1 (degrees, clockwise on screen)."""
    p0, p1 = polar(cx, cy, r, a0), polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'M{pt(p0)} A{n(r)},{n(r)} 0 {large},1 {pt(p1)}'


def build(args):
    doc = Doc(VB, 'PlayStation 5 DualSense wireless controller',
              'Straight-on front view of a white Sony PS5 DualSense wireless controller: white two-tone shell with a black inner section, touch pad with light bar, two analog sticks, directional buttons, triangle, circle, cross and square buttons, PS button, mute button, create and options buttons, L1/R1 bumpers and L2/R2 triggers.',
              id_prefix=P)

    if args.ref:
        with open(args.ref, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        rx, ry, rw, rh = [float(v) for v in args.ref_rect.split(',')]
        doc.add(f'<image href="data:image/png;base64,{b64}" x="{n(rx)}" y="{n(ry)}" width="{n(rw)}" height="{n(rh)}" preserveAspectRatio="none" opacity="{args.ref_opacity}"/>')

    # ======================================================= geometry (left halves, mirrored)
    body = Path()
    body.M((CX, 25))
    body.C((700, 26), (600, 32), (500, 44))        # top edge to the touch-pad corner
    body.C((455, 50), (370, 57), (300, 66))        # shoulder (the bumper sits on this edge)
    body.C((250, 74), (210, 84), (185, 95))        # shoulder corner
    body.C((165, 105), (150, 125), (140, 160))     # into the outer side
    body.C((110, 230), (45, 400), (12, 560))       # outer side, upper
    body.C((1, 660), (0, 780), (3, 900))           # outer side, lower
    body.C((7, 975), (22, 1040), (90, 1055))       # grip end, outer corner
    body.C((130, 1063), (185, 1060), (215, 1042))  # grip end
    body.C((245, 1015), (292, 920), (335, 830))    # inner grip edge
    body.C((365, 765), (385, 725), (420, 706))     # into the crotch
    body.C((445, 696), (470, 696), (520, 697))
    body.C((600, 698), (700, 698), (CX, 698))      # bottom centre
    body_full = symmetric_path(body, CX)

    pad = Path()
    pad.M((CX, 40))
    pad.C((690, 40), (580, 42), (507, 46))
    pad.C((492, 47), (484, 54), (485, 70))
    pad.C((489, 140), (503, 240), (520, 315))
    pad.C((526, 342), (536, 366), (562, 373))
    pad.C((582, 378), (690, 381), (CX, 381))
    pad_full = symmetric_path(pad, CX)

    # boundary between the white wing and the black section: a thin sliver beside the light bar,
    # then ~38 degrees under the pad corner, easing to ~27 degrees along the grip
    wing_edge = Path().M((503, 345)).C((497, 357), (491, 370), (487, 382)).C((455, 422), (423, 460), (391, 500))
    wing_edge.C((368, 530), (300, 680), (235, 830)).C((205, 905), (175, 985), (150, 1052))
    frame = Path()
    frame.M((CX, 370))
    frame.L((560, 370))
    frame.C((540, 370), (528, 364), (518, 356))
    frame.C((512, 352), (508, 349), (503, 345))
    for seg in wing_edge.segs[1:]:
        frame.segs.append(seg)
    frame.C((172, 1056), (196, 1054), (215, 1042))   # shared with the silhouette from here on
    frame.C((245, 1015), (292, 920), (335, 830))
    frame.C((365, 765), (385, 725), (420, 706))
    frame.C((445, 696), (470, 696), (520, 697))
    frame.C((600, 698), (700, 698), (CX, 698))
    frame_full = symmetric_path(frame, CX)

    trig = Path()
    trig.M((204, 110)).C((200, 60), (214, 18), (246, 8)).C((272, 0), (334, -2), (372, 4)).C((400, 9), (418, 24), (424, 46)).C((428, 62), (430, 86), (430, 110)).Z()
    bump = Path()
    bump.M((190, 72)).C((206, 50), (242, 34), (292, 28)).C((332, 23), (378, 24), (410, 32)).C((420, 36), (424, 46), (418, 52))
    bump.C((392, 54), (352, 57), (300, 65)).C((260, 72), (226, 83), (202, 94)).C((194, 96), (188, 88), (190, 72)).Z()

    lb = Path()   # light bar: tapered crescent hugging the pad's side
    lb.M((484, 56)).C((478, 70), (476, 100), (478, 140)).C((483, 220), (496, 290), (512, 342)).C((516, 356), (524, 367), (540, 376))
    lb.C((552, 382), (560, 378), (556, 368)).C((540, 350), (526, 320), (518, 290)).C((506, 240), (494, 150), (492, 80)).C((492, 70), (490, 56), (484, 56)).Z()
    lb_core = Path().M((486, 80)).C((490, 170), (500, 260), (516, 320)).C((522, 342), (530, 358), (544, 370))

    # ======================================================= defs
    D = doc.add_def
    D(f'<path id="{P}shell-outline" d="{body_full.d()}"/>')
    D(f'<path id="{P}inner-outline" d="{frame_full.d()}"/>')
    D(f'<path id="{P}pad-outline" d="{pad_full.d()}"/>')
    D(f'<clipPath id="{P}clip-shell"><use xlink:href="#{P}shell-outline"/></clipPath>')
    D(f'<clipPath id="{P}clip-inner"><use xlink:href="#{P}inner-outline"/></clipPath>')
    D(rad(f'{P}g-shell', 800, 260, 1150, [(0, SHELL_HI), (0.35, '#f6f6f8'), (0.7, SHELL), (1, SHELL_LO)]))
    D(lin(f'{P}g-trigger', 0, 0, 0, 110, [(0, '#44444b'), (0.4, '#232327'), (1, '#0f0f11')]))
    D(lin(f'{P}g-bumper', 0, 24, 0, 96, [(0, '#3d3d44'), (0.5, '#222226'), (1, '#0e0e10')]))
    D(lin(f'{P}g-inner', 0, 300, 0, 1060, [(0, FRAME_HI), (0.3, FRAME), (1, FRAME_LO)]))
    D(lin(f'{P}g-pad', 490, 40, 1110, 381, [(0, '#ffffff'), (0.55, '#f1f1f4'), (1, '#e3e4e9')]))
    D(rad(f'{P}g-stick-rim', 0.35, 0.3, 0.75, [(0, '#44444b'), (0.6, '#232327'), (1, '#0f0f11')], units='objectBoundingBox'))
    D(rad(f'{P}g-stick-dish', 0.66, 0.7, 0.72, [(0, '#3e3e45'), (0.55, '#202024'), (1, '#08080a')], units='objectBoundingBox'))
    D(rad(f'{P}g-stick-well', 0.42, 0.4, 0.62, [(0, '#060607'), (0.7, '#0b0b0d'), (0.92, '#30303a'), (1, '#45454d')], units='objectBoundingBox'))
    D(lin(f'{P}g-button-ring', 0, 0, 1, 1, [(0, '#d6d7dd'), (0.5, '#9d9ea6'), (1, '#6c6d75')], units='objectBoundingBox'))
    D(lin(f'{P}g-button-face', 0, 0, 0, 1, [(0, '#f8f8fa'), (1, '#dedfe4')], units='objectBoundingBox'))
    D(rad(f'{P}g-button-gloss', 0.38, 0.28, 0.72, [(0, '#ffffff', 0.95), (0.45, '#ffffff', 0.2), (1, '#ffffff', 0)], units='objectBoundingBox'))
    for ang in (0, 90, 180, 270):   # d-pad keys are rotated, so their gradients are counter-rotated
        D(lin(f'{P}g-key-face-{ang}', 0, 0, 0, 1, [(0, '#f8f8fa'), (1, '#dedfe4')], units='objectBoundingBox', extra=f' gradientTransform="rotate({-ang} 0.5 0.5)"'))
        D(rad(f'{P}g-key-gloss-{ang}', 0.5, 0.22, 0.75, [(0, '#ffffff', 0.9), (0.5, '#ffffff', 0.15), (1, '#ffffff', 0)], units='objectBoundingBox', extra=f' gradientTransform="rotate({-ang} 0.5 0.5)"'))
    D(lin(f'{P}g-ps', 0, 0, 0, 1, [(0, '#3b3b41'), (1, '#1b1b1f')], units='objectBoundingBox'))
    D(lin(f'{P}g-mute', 0, 0, 0, 1, [(0, '#2f2f35'), (1, '#121214')], units='objectBoundingBox'))
    D(lin(f'{P}g-pill', 0, 0, 0, 1, [(0, '#f5f5f7'), (1, '#d3d4da')], units='objectBoundingBox'))
    D(f'<filter id="{P}blur36" x="-200%" y="-100%" width="500%" height="300%"><feGaussianBlur stdDeviation="36"/></filter>')
    D(f'<filter id="{P}blur24" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="24"/></filter>')
    D(f'<filter id="{P}blur12" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="12"/></filter>')
    D(f'<filter id="{P}blur6" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>')
    D(f'<filter id="{P}blur3" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3"/></filter>')
    D(f'<filter id="{P}blur1" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.2"/></filter>')

    # ======================================================= triggers (behind the shell)
    doc.comment('L2 / R2 triggers (black; mostly hidden behind the bumpers)')
    doc.add(f'<g id="{P}triggers">')
    for side, mirror in (('l', False), ('r', True)):
        t = mirror_path(trig, CX) if mirror else trig
        hl = Path().M((250, 14)).C((280, 4), (330, 2), (372, 6)).C((395, 9), (410, 16), (420, 30))
        if mirror:
            hl = mirror_path(hl, CX)
        doc.add(f'<g id="{P}trigger-{side}2">', 2)
        doc.add(f'<path d="{t.d()}" fill="url(#{P}g-trigger)" stroke="{DARK_EDGE}" stroke-width="2" stroke-linejoin="round"/>', 3)
        doc.add(f'<path d="{hl.d()}" fill="none" stroke="#a0a1aa" stroke-width="3.5" opacity="{0.7 if not mirror else 0.5}" stroke-linecap="round" filter="url(#{P}blur1)"/>', 3)
        doc.add('</g>', 2)
    doc.add('</g>')

    # ======================================================= white shell
    doc.comment('White top shell')
    doc.add(f'<g id="{P}shell">')
    doc.add(f'<use id="{P}shell-body" xlink:href="#{P}shell-outline" fill="url(#{P}g-shell)"/>', 2)
    doc.add(f'<g id="{P}shell-shading" clip-path="url(#{P}clip-shell)">', 2)
    doc.add(f'<use xlink:href="#{P}shell-outline" fill="none" stroke="#8d8f99" stroke-width="44" opacity="0.5" filter="url(#{P}blur24)"/>', 3)
    doc.add(f'<path d="M160,120 C330,60 560,30 800,28 C1040,30 1270,60 1440,120" fill="none" stroke="#fff" stroke-width="26" opacity="0.9" filter="url(#{P}blur12)"/>', 3)
    for mirror in (False, True):
        ridge = Path().M((250, 520)).C((210, 640), (170, 800), (135, 980))
        shade = Path().M((420, 560)).C((330, 700), (250, 860), (205, 1000))
        if mirror:
            ridge = mirror_path(ridge, CX); shade = mirror_path(shade, CX)
        doc.add(f'<path d="{ridge.d()}" fill="none" stroke="#fff" stroke-width="90" stroke-linecap="round" opacity="0.85" filter="url(#{P}blur36)"/>', 3)
        doc.add(f'<path d="{shade.d()}" fill="none" stroke="#a3a5af" stroke-width="70" stroke-linecap="round" opacity="0.35" filter="url(#{P}blur36)"/>', 3)
        dx = 300 if not mirror else 1300
        doc.add(f'<ellipse cx="{dx}" cy="330" rx="170" ry="140" fill="#fff" opacity="0.6" filter="url(#{P}blur36)"/>', 3)
    doc.add('</g>', 2)
    doc.add(f'<use xlink:href="#{P}shell-outline" fill="none" stroke="{SHELL_EDGE}" stroke-width="2.5" stroke-linejoin="round"/>', 2)
    doc.add(f'<g id="{P}usb-c">', 2)
    doc.add('<rect x="750" y="31" width="100" height="11" rx="5.5" fill="#55565e"/>', 3)
    doc.add('<rect x="754" y="33" width="92" height="7" rx="3.5" fill="#1e1e22"/>', 3)
    doc.add('</g>', 2)
    doc.add('</g>')

    # ======================================================= bumpers (on the shoulder edge)
    doc.comment('L1 / R1 bumpers (black)')
    doc.add(f'<g id="{P}bumpers">')
    for side, mirror in (('l', False), ('r', True)):
        b = mirror_path(bump, CX) if mirror else bump
        hl = Path().M((204, 66)).C((236, 44), (280, 32), (320, 28)).C((360, 25), (395, 28), (414, 36))
        if mirror:
            hl = mirror_path(hl, CX)
        doc.add(f'<g id="{P}bumper-{side}1">', 2)
        doc.add(f'<path d="{b.d()}" fill="url(#{P}g-bumper)" stroke="{DARK_EDGE}" stroke-width="2" stroke-linejoin="round"/>', 3)
        doc.add(f'<path d="{hl.d()}" fill="none" stroke="#b9bac2" stroke-width="3.5" opacity="{0.8 if not mirror else 0.6}" stroke-linecap="round" filter="url(#{P}blur1)"/>', 3)
        doc.add('</g>', 2)
    doc.add('</g>')

    # ======================================================= black inner section
    doc.comment('Black inner section (sticks, PS button, mute button, inner grip strips)')
    doc.add(f'<g id="{P}inner-section">')
    doc.add(f'<use id="{P}inner-section-body" xlink:href="#{P}inner-outline" fill="url(#{P}g-inner)"/>', 2)
    doc.add(f'<g id="{P}inner-shading" clip-path="url(#{P}clip-inner)">', 2)
    for cx in (546, 1054):
        doc.add(f'<circle cx="{cx}" cy="540" r="150" fill="#4a4a52" opacity="0.55" filter="url(#{P}blur24)"/>', 3)
    doc.add(f'<rect x="690" y="370" width="220" height="330" fill="#3a3a41" opacity="0.5" filter="url(#{P}blur24)"/>', 3)
    doc.add(f'<path d="M540,374 L1060,374" stroke="#5a5a62" stroke-width="10" opacity="0.7" filter="url(#{P}blur6)"/>', 3)
    for mirror in (False, True):
        p = mirror_path(wing_edge, CX) if mirror else wing_edge
        doc.add(f'<path d="{p.d()}" fill="none" stroke="#000" stroke-width="16" opacity="0.6" filter="url(#{P}blur6)" transform="translate({-4 if not mirror else 4},6)"/>', 3)
        ge = Path().M((222, 1036)).C((250, 1010), (292, 920), (335, 830)).C((365, 765), (385, 725), (420, 706))
        if mirror:
            ge = mirror_path(ge, CX)
        doc.add(f'<path d="{ge.d()}" fill="none" stroke="#4e4e56" stroke-width="7" opacity="0.8" filter="url(#{P}blur3)"/>', 3)
    doc.add('</g>', 2)
    for mirror in (False, True):
        p = mirror_path(wing_edge, CX) if mirror else wing_edge
        doc.add(f'<path d="{p.d()}" fill="none" stroke="{SEAM}" stroke-width="1.5" opacity="0.85"/>', 2)
    doc.add('</g>')

    # ======================================================= touch pad with light bar
    doc.comment('Touch pad (white) with the light bar strips along its sides')
    doc.add(f'<g id="{P}touchpad">')
    doc.add(f'<use xlink:href="#{P}pad-outline" fill="none" stroke="#6f717c" stroke-width="10" opacity="0.35" filter="url(#{P}blur6)"/>', 2)
    for side, mirror in (('l', False), ('r', True)):
        p = mirror_path(lb, CX) if mirror else lb
        core = mirror_path(lb_core, CX) if mirror else lb_core
        doc.add(f'<g id="{P}lightbar-{side}">', 2)
        doc.add(f'<path d="{p.d()}" fill="{LIGHTBAR}" opacity="0.5" filter="url(#{P}blur12)"/>', 3)
        doc.add(f'<path d="{p.d()}" fill="{LIGHTBAR}"/>', 3)
        doc.add(f'<path d="{core.d()}" fill="none" stroke="{LIGHTBAR_CORE}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>', 3)
        doc.add('</g>', 2)
    doc.add(f'<use id="{P}touchpad-surface" xlink:href="#{P}pad-outline" fill="url(#{P}g-pad)" stroke="{PAD_EDGE}" stroke-width="2"/>', 2)
    doc.add('<path d="M512,50 C600,45 700,43 800,43 C900,43 1000,45 1088,50" fill="none" stroke="#b9bbc4" stroke-width="2" opacity="0.6"/>', 2)
    doc.add('</g>')

    # ======================================================= player LEDs and speaker holes
    doc.add(f'<g id="{P}player-indicator">')
    for i, x in enumerate((743, 772, 800, 828, 857)):
        if i == 2:
            doc.add(f'<circle cx="{x}" cy="411" r="16" fill="#9fd4ff" opacity="0.7" filter="url(#{P}blur6)"/>', 2)
            doc.add(f'<circle cx="{x}" cy="411" r="10" fill="#eaf6ff"/>', 2)
        else:
            doc.add(f'<circle cx="{x}" cy="411" r="10" fill="#0b0b0c"/>', 2)
            doc.add(f'<circle cx="{x}" cy="411" r="10" fill="none" stroke="#3b3b42" stroke-width="1.2"/>', 2)
    doc.add('</g>')
    doc.add(f'<g id="{P}speaker">')
    for x in (757, 786, 814, 843):
        doc.add(f'<circle cx="{x}" cy="437" r="10" fill="#0b0b0c"/>', 2)
        doc.add(f'<circle cx="{x}" cy="437" r="10" fill="none" stroke="#3b3b42" stroke-width="1.2"/>', 2)
    doc.add('</g>')

    # ======================================================= PS button, mute button, headset jack
    doc.add(ps_button(CX, 520), 1)
    doc.add(mute_button(CX, 616), 1)
    doc.add(f'<g id="{P}headset-jack"><rect x="783" y="691" width="34" height="8" rx="4" fill="#0a0a0b"/></g>')

    # ======================================================= sticks, d-pad, face buttons, create/options
    for side, cx in (('l', 546), ('r', 1054)):
        doc.add(stick(side, cx, 540), 1)
    doc.add(dpad(300, 320), 1)
    doc.add(face_buttons(1299, 320), 1)
    doc.add(small_button('create', 426, 144, -12, 414, 94), 1)
    doc.add(small_button('options', 1174, 144, 12, 1186, 94), 1)
    return doc.render()


# ----------------------------------------------------------------------------------------------
PS_LOGO_D = ("M8.984 2.596v17.547l3.915 1.261V6.688c0-.69.304-1.151.794-.991.636.18.76.814.76 1.505v5.875c2.441 1.193 "
             "4.362-.002 4.362-3.152 0-3.237-1.126-4.675-4.438-5.827-1.307-.448-3.728-1.186-5.39-1.502zm4.656 16.241l6.296-2.275"
             "c.715-.258.826-.625.246-.818-.586-.192-1.637-.139-2.357.123l-4.205 1.5V14.98l.24-.085s1.201-.42 2.913-.615c1.696-.18 "
             "3.785.03 5.437.661 1.848.601 2.04 1.472 1.576 2.072-.465.6-1.622 1.036-1.622 1.036l-8.544 3.107V18.86zM1.807 18.6"
             "c-1.9-.545-2.214-1.668-1.352-2.32.801-.586 2.16-1.052 2.16-1.052l5.615-2.013v2.313L4.205 17c-.705.271-.825.632-.239.826"
             ".586.195 1.637.15 2.343-.12L8.247 17v2.074c-.12.03-.256.044-.39.073-1.939.331-3.996.196-6.038-.479z")

def ps_button(cx, cy):
    """PS button: the PlayStation logo in relief (logo path CC0 from Simple Icons, 24x24 box, ~11 mm wide)."""
    s = 4.6
    tx, ty = cx - 12 * s, cy - 12 * s
    out = [f'<g id="{P}ps-button">']
    out.append(f'  <path id="{P}ps-logo" d="{PS_LOGO_D}" transform="translate({n(tx)},{n(ty)}) scale({n(s)})" fill="none"/>')
    out.append(f'  <use xlink:href="#{P}ps-logo" fill="#000" opacity="0.55" transform="translate(1.2,2.5)" filter="url(#{P}blur1)"/>')
    out.append(f'  <use xlink:href="#{P}ps-logo" fill="url(#{P}g-ps)" stroke="#0a0a0b" stroke-width="1.2"/>')
    out.append(f'  <use xlink:href="#{P}ps-logo" fill="none" stroke="#5a5a62" stroke-width="1" transform="translate(-0.6,-0.8)" opacity="0.8"/>')
    out.append('</g>')
    return '\n  '.join(out)


def mute_button(cx, cy):
    w, h = 90, 28
    out = [f'<g id="{P}mute-button">']
    out.append(f'  <rect x="{n(cx-w/2)}" y="{n(cy-h/2+3)}" width="{w}" height="{h}" rx="{h/2}" fill="#000" opacity="0.6" filter="url(#{P}blur1)"/>')
    out.append(f'  <rect x="{n(cx-w/2)}" y="{n(cy-h/2)}" width="{w}" height="{h}" rx="{h/2}" fill="url(#{P}g-mute)" stroke="#0a0a0b" stroke-width="1.5"/>')
    out.append(f'  <rect x="{n(cx-w/2+6)}" y="{n(cy-h/2+2)}" width="{w-12}" height="6" rx="3" fill="#fff" opacity="0.14"/>')
    gx, gy = cx, cy + 36
    out.append(f'  <g id="{P}mute-icon" transform="translate({n(gx)},{n(gy)})" fill="none" stroke="#9a9aa2" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">')
    out.append('    <rect x="-4.5" y="-12" width="9" height="15" rx="4.5"/>')
    out.append('    <path d="M-9,-2 C-9,5 -4,9 0,9 C4,9 9,5 9,-2 M0,9 L0,14 M-5,14 L5,14 M-11,-13 L11,11"/>')
    out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def stick(side, cx, cy):
    well_r = 116
    cap_r = 94
    dish_r = 66
    out = [f'<g id="{P}stick-{side}">']
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r+3}" fill="#000" opacity="0.5" filter="url(#{P}blur3)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r}" fill="url(#{P}g-stick-well)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r-2}" fill="none" stroke="#000" stroke-width="3" opacity="0.7"/>')
    out.append(f'  <circle cx="{cx+5}" cy="{cy+8}" r="{cap_r+2}" fill="#000" opacity="0.7" filter="url(#{P}blur3)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{cap_r}" fill="url(#{P}g-stick-rim)" stroke="#08080a" stroke-width="2"/>')
    lit, dark = [], []
    for i in range(72):
        a = i * 5
        p1 = polar(cx, cy, dish_r + 4, a)
        p2 = polar(cx, cy, cap_r - 3, a)
        (lit if 150 <= a < 330 else dark).append(f'M{pt(p1)}L{pt(p2)}')
    out.append(f'  <path d="{"".join(lit)}" stroke="#4a4a52" stroke-width="1.6" stroke-linecap="round" fill="none" opacity="0.85"/>')
    out.append(f'  <path d="{"".join(dark)}" stroke="#4a4a52" stroke-width="1.6" stroke-linecap="round" fill="none" opacity="0.4"/>')
    out.append(f'  <path d="{arc(cx, cy, cap_r-4, 195, 285)}" fill="none" stroke="#fff" stroke-width="3" opacity="0.2" stroke-linecap="round" filter="url(#{P}blur1)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{dish_r}" fill="url(#{P}g-stick-dish)" stroke="#0a0a0c" stroke-width="2"/>')
    out.append(f'  <path d="{arc(cx, cy, dish_r-3, 15, 100)}" fill="none" stroke="#fff" stroke-width="4" opacity="0.3" stroke-linecap="round" filter="url(#{P}blur1)"/>')
    out.append('</g>')
    return '\n  '.join(out)


def dpad_key():
    """One directional button pointing UP, centred at x=0, tip toward the origin (local units)."""
    return ("M-46,-90 C-46,-122 -38,-137 -16,-138 L16,-138 C38,-137 46,-122 46,-90 "
            "L46,-62 C46,-54 43,-48 37,-43 L11,-25 C5,-21 -5,-21 -11,-25 L-37,-43 C-43,-48 -46,-54 -46,-62 Z")

def dpad(cx, cy):
    out = [f'<g id="{P}dpad">']
    out.append(f'  <path id="{P}dpad-key" d="{dpad_key()}" fill="none"/>')
    # centre recess: white, with a soft inner shadow on its top-left
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="19" fill="#e4e5ea"/>')
    out.append(f'  <path d="{arc(cx, cy, 15, 150, 330)}" fill="none" stroke="#9c9ea8" stroke-width="7" opacity="0.6" filter="url(#{P}blur3)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="19" fill="none" stroke="#b0b2bb" stroke-width="1.5"/>')
    for name, ang in (('up', 0), ('right', 90), ('down', 180), ('left', 270)):
        out.append(f'  <g id="{P}dpad-{name}" transform="translate({cx},{cy}) rotate({ang})">')
        a = math.radians(ang)   # shadow offset (3,5) on screen, expressed in the key's rotated frame
        ox, oy = 3 * math.cos(a) + 5 * math.sin(a), -3 * math.sin(a) + 5 * math.cos(a)
        out.append(f'    <use xlink:href="#{P}dpad-key" fill="#000" opacity="0.28" transform="translate({n(ox)},{n(oy)})" filter="url(#{P}blur3)"/>')
        out.append(f'    <use xlink:href="#{P}dpad-key" fill="url(#{P}g-key-face-{ang})" stroke="#a9abb3" stroke-width="1.6" stroke-linejoin="round"/>')
        out.append(f'    <path d="M-9,-100 L0,-114 L9,-100 Z" fill="{SYMBOL}" opacity="0.7"/>')
        out.append(f'    <use xlink:href="#{P}dpad-key" fill="url(#{P}g-key-gloss-{ang})" opacity="0.6"/>')
        out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def face_buttons(cx, cy):
    r = 50
    off = 118
    out = [f'<g id="{P}face-buttons">']
    btns = (('triangle', cx, cy - off), ('circle', cx + off, cy), ('cross', cx, cy + off), ('square', cx - off, cy))
    for name, x, y in btns:
        out.append(f'  <g id="{P}btn-{name}">')
        out.append(f'    <circle cx="{n(x+3)}" cy="{n(y+5)}" r="{r+1}" fill="#000" opacity="0.3" filter="url(#{P}blur3)"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="url(#{P}g-button-ring)"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r-5}" fill="url(#{P}g-button-face)"/>')
        sw = 7
        if name == 'triangle':
            out.append(f'    <path d="M{n(x)},{n(y-24)} L{n(x+23)},{n(y+15)} L{n(x-23)},{n(y+15)} Z" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linejoin="round"/>')
        elif name == 'circle':
            out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="22" fill="none" stroke="{SYMBOL}" stroke-width="{sw}"/>')
        elif name == 'cross':
            k = 19
            out.append(f'    <path d="M{n(x-k)},{n(y-k)} L{n(x+k)},{n(y+k)} M{n(x+k)},{n(y-k)} L{n(x-k)},{n(y+k)}" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linecap="round"/>')
        else:
            k = 19
            out.append(f'    <rect x="{n(x-k)}" y="{n(y-k)}" width="{n(2*k)}" height="{n(2*k)}" rx="2.5" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linejoin="round"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r-1}" fill="url(#{P}g-button-gloss)" opacity="0.75"/>')
        out.append(f'    <ellipse cx="{n(x-17)}" cy="{n(y-26)}" rx="13" ry="6" transform="rotate(-35 {n(x-17)} {n(y-26)})" fill="#fff" opacity="0.85" filter="url(#{P}blur1)"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="none" stroke="#6a6b73" stroke-width="1.2" opacity="0.7"/>')
        out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def small_button(name, cx, cy, angle, ix, iy):
    """Create / Options: a slim tilted pill, with its glyph printed on the shell above it."""
    w, h = 34, 72
    out = [f'<g id="{P}{name}">']
    out.append(f'  <g id="{P}{name}-button" transform="translate({cx},{cy}) rotate({angle})">')
    out.append(f'    <rect x="{n(-w/2+2)}" y="{n(-h/2+4)}" width="{w}" height="{h}" rx="{w/2}" fill="#000" opacity="0.28" filter="url(#{P}blur3)"/>')
    out.append(f'    <rect x="{n(-w/2)}" y="{n(-h/2)}" width="{w}" height="{h}" rx="{w/2}" fill="url(#{P}g-pill)" stroke="#a9abb3" stroke-width="1.6"/>')
    out.append(f'    <rect x="{n(-w/2+6)}" y="{n(-h/2+5)}" width="{w-12}" height="{h*0.42}" rx="{(w-12)/2}" fill="#fff" opacity="0.45" filter="url(#{P}blur3)"/>')
    out.append('  </g>')
    out.append(f'  <g id="{P}{name}-icon" transform="translate({ix},{iy})" fill="none" stroke="{SYMBOL}" stroke-width="3.2" stroke-linecap="round">')
    if name == 'create':
        out.append('    <path d="M0,-20 L0,-4 M-13,-17 L-5,-6 M13,-17 L5,-6"/>')
    else:
        out.append('    <path d="M-11,-18 L11,-18 M-11,-10 L11,-10 M-11,-2 L11,-2"/>')
    out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--out', default='dualsense.svg')
    ap.add_argument('--ref', help='reference image to embed behind the drawing (debug)')
    ap.add_argument('--ref-rect', default='-50,-30,1700,1140')
    ap.add_argument('--ref-opacity', default='0.45')
    args = ap.parse_args()
    svg = build(args)
    with open(args.out, 'w') as f:
        f.write(svg)
    print(f'wrote {args.out} ({len(svg)} bytes)')
