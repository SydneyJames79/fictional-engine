#!/usr/bin/env python3
"""Generates dualsense.svg — a straight-on front view of the white PS5 DualSense wireless controller.

Coordinate system: 10 units = 1 mm. The controller spans x 0..1600 (160 mm) and y 0..1060 (106 mm:
trigger tips at the top, grip ends at the bottom). Mirror axis x = 800. Light comes from the top-left.
Geometry was calibrated against an orthographic projection of a 3D model plus published measurements.
"""
import sys, os, base64, argparse, math
sys.path.insert(0, os.path.dirname(__file__))
from svgkit import *

CX = 800
VB = (-8, -8, 1616, 1076)

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
SYMBOL = '#7d7d85'
LIGHTBAR = '#4d9dff'
LIGHTBAR_CORE = '#d6ecff'


def build(args):
    doc = Doc(VB, 'PlayStation 5 DualSense wireless controller',
              'Straight-on front view of a white Sony PS5 DualSense wireless controller: white two-tone shell with a black inner section, touch pad with light bar, two analog sticks, directional buttons, triangle, circle, cross and square buttons, PS button, mute button, create and options buttons, L1/R1 bumpers and L2/R2 triggers.')

    if args.ref:
        with open(args.ref, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        rx, ry, rw, rh = [float(v) for v in args.ref_rect.split(',')]
        doc.add(f'<image href="data:image/png;base64,{b64}" x="{n(rx)}" y="{n(ry)}" width="{n(rw)}" height="{n(rh)}" preserveAspectRatio="none" opacity="{args.ref_opacity}"/>')

    # ======================================================= defs
    D = doc.add_def
    D(rad('g-shell', 800, 260, 1150, [(0, SHELL_HI), (0.35, '#f6f6f8'), (0.7, SHELL), (1, SHELL_LO)]))
    D('<filter id="f-blur36" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="36"/></filter>')
    D(lin('g-trigger', 0, 0, 0, 130, [(0, '#3b3b41'), (0.35, '#232327'), (1, '#0f0f11')]))
    D(lin('g-bumper', 0, 40, 0, 120, [(0, '#3a3a40'), (0.5, '#222226'), (1, '#0e0e10')]))
    D(lin('g-frame', 0, 300, 0, 1060, [(0, FRAME_HI), (0.3, FRAME), (1, FRAME_LO)]))
    D(lin('g-pad', 0, 50, 0, 390, [(0, '#fafafb'), (1, '#ececef')]))
    D(rad('g-cap-rim', 0.35, 0.3, 0.75, [(0, '#3d3d43'), (0.6, '#232327'), (1, '#111113')], units='objectBoundingBox'))
    D(rad('g-cap-dish', 0.62, 0.66, 0.7, [(0, '#2e2e33'), (0.55, '#1f1f23'), (1, '#0e0e10')], units='objectBoundingBox'))
    D(rad('g-well', 0.5, 0.5, 0.5, [(0, '#0a0a0b'), (0.8, '#0c0c0e'), (0.93, '#2a2a2f'), (1, '#3a3a40')], units='objectBoundingBox'))
    D(lin('g-cap-face', 0, 0, 0, 1, [(0, '#f7f7f9'), (1, '#dcdde2')], units='objectBoundingBox'))
    D(lin('g-cap-ring', 0, 0, 0, 1, [(0, '#8b8c94'), (0.5, '#b9bac2'), (1, '#6f7078')], units='objectBoundingBox'))
    D(rad('g-cap-gloss', 0.38, 0.28, 0.72, [(0, '#ffffff', 0.95), (0.45, '#ffffff', 0.2), (1, '#ffffff', 0)], units='objectBoundingBox'))
    D(lin('g-ps', 0, 0, 0, 1, [(0, '#3b3b41'), (1, '#1b1b1f')], units='objectBoundingBox'))
    D(lin('g-mute', 0, 0, 0, 1, [(0, '#2f2f35'), (1, '#121214')], units='objectBoundingBox'))
    D(lin('g-create', 0, 0, 0, 1, [(0, '#f5f5f7'), (1, '#d3d4da')], units='objectBoundingBox'))
    D('<filter id="f-blur24" x="-15%" y="-15%" width="130%" height="130%"><feGaussianBlur stdDeviation="24"/></filter>')
    D('<filter id="f-blur12" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="12"/></filter>')
    D('<filter id="f-blur6" x="-25%" y="-25%" width="150%" height="150%"><feGaussianBlur stdDeviation="6"/></filter>')
    D('<filter id="f-blur3" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>')
    D('<filter id="f-blur1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.2"/></filter>')

    # ======================================================= main silhouette (left half)
    body = Path()
    body.M((CX, 25))
    body.C((700, 26), (600, 32), (500, 44))        # top edge to the touch-pad corner
    body.C((445, 51), (385, 64), (325, 80))        # shoulder top (under the bumper)
    body.C((265, 94), (215, 104), (190, 122))      # shoulder corner
    body.C((168, 140), (152, 160), (135, 190))     # into the outer side
    body.C((92, 275), (40, 410), (12, 560))        # outer side, upper
    body.C((1, 660), (0, 780), (3, 900))           # outer side, lower
    body.C((7, 975), (22, 1040), (90, 1055))       # grip end, outer corner
    body.C((130, 1063), (185, 1060), (215, 1042))  # grip end
    body.C((245, 1015), (292, 920), (335, 830))    # inner grip edge
    body.C((365, 765), (385, 725), (420, 706))     # into the crotch
    body.C((445, 696), (470, 696), (520, 697))
    body.C((600, 698), (700, 698), (CX, 698))      # bottom centre
    body_full = symmetric_path(body, CX)
    D(f'<clipPath id="clip-body"><path d="{body_full.d()}"/></clipPath>')

    # ======================================================= touch pad outline (left half)
    pad = Path()
    pad.M((CX, 50))
    pad.C((690, 50), (580, 52), (507, 56))
    pad.C((492, 57), (484, 64), (485, 80))
    pad.C((489, 150), (503, 250), (520, 325))
    pad.C((526, 352), (536, 376), (562, 383))
    pad.C((582, 388), (690, 391), (CX, 391))
    pad_full = symmetric_path(pad, CX)

    # ======================================================= black inner section (left half)
    frame = Path()
    frame.M((CX, 376))
    frame.C((700, 376), (610, 376), (578, 372))      # along the touch pad's lower edge
    frame.C((548, 368), (535, 356), (526, 340))      # pad's lower corner
    frame.C((516, 322), (507, 300), (499, 282))      # rising beside the light bar
    frame.C((440, 400), (330, 620), (235, 830))      # diagonal boundary with the white wing
    frame.C((205, 905), (175, 985), (150, 1052))     # tapering strip reaches the grip end
    frame.C((172, 1056), (196, 1054), (215, 1042))   # (shared with the silhouette from here on)
    frame.C((245, 1015), (292, 920), (335, 830))
    frame.C((365, 765), (385, 725), (420, 706))
    frame.C((445, 696), (470, 696), (520, 697))
    frame.C((600, 698), (700, 698), (CX, 698))
    frame_full = symmetric_path(frame, CX)
    D(f'<clipPath id="clip-frame"><path d="{frame_full.d()}"/></clipPath>')
    # the visible boundary (white wing edge), reused for shadow/highlight lines
    wing_edge = Path().M((499, 282)).C((440, 400), (330, 620), (235, 830)).C((205, 905), (175, 985), (150, 1052))

    # ======================================================= triggers and bumpers
    trig = Path()
    trig.M((190, 175)).C((188, 110), (192, 46), (222, 22)).C((246, 6), (300, 2), (336, 4)).C((376, 6), (404, 16), (416, 42)).C((424, 66), (426, 120), (426, 175)).Z()
    bump = Path()
    bump.M((194, 104)).C((214, 84), (256, 72), (310, 66)).C((360, 60), (406, 60), (428, 68)).C((438, 72), (440, 90), (430, 96))
    bump.C((392, 92), (344, 96), (272, 118)).C((250, 124), (226, 134), (214, 146)).C((206, 154), (192, 150), (192, 136)).C((192, 124), (192, 112), (194, 104)).Z()
    doc.comment('L2 / R2 triggers (behind the shell) and L1 / R1 bumpers — black on the white model')
    doc.add('<g id="triggers">')
    for side, mirror in (('l', False), ('r', True)):
        t = mirror_path(trig, CX) if mirror else trig
        doc.add(f'<path id="trigger-{side}2" d="{t.d()}" fill="url(#g-trigger)" stroke="#000" stroke-width="2" stroke-linejoin="round"/>', 2)
        # highlight along the trigger's top edge (lit from the top-left)
        hl = Path().M((228, 34)).C((250, 16), (298, 10), (336, 10)).C((372, 10), (398, 18), (410, 40))
        if mirror:
            hl = mirror_path(hl, CX)
        doc.add(f'<path d="{hl.d()}" fill="none" stroke="#9c9da6" stroke-width="4" opacity="{0.6 if not mirror else 0.45}" stroke-linecap="round" filter="url(#f-blur1)"/>', 2)
    doc.add('</g>')

    # ======================================================= white shell
    doc.comment('White top shell')
    doc.add('<g id="shell">')
    doc.add(f'<path id="shell-body" d="{body_full.d()}" fill="url(#g-shell)"/>', 2)
    doc.add('<g clip-path="url(#clip-body)">', 2)
    # rolled-edge shading along the outline
    doc.add(f'<path d="{body_full.d()}" fill="none" stroke="#8d8f99" stroke-width="44" opacity="0.5" filter="url(#f-blur24)"/>', 3)
    # highlight just inside the top edge
    doc.add('<path d="M160,120 C330,60 560,30 800,28 C1040,30 1270,60 1440,120" fill="none" stroke="#fff" stroke-width="26" opacity="0.9" filter="url(#f-blur12)"/>', 3)
    for mirror in (False, True):
        # soft ridge of light along each convex grip
        ridge = Path().M((250, 520)).C((210, 640), (170, 800), (135, 980))
        shade = Path().M((420, 560)).C((330, 700), (250, 860), (205, 1000))
        if mirror:
            ridge = mirror_path(ridge, CX); shade = mirror_path(shade, CX)
        doc.add(f'<path d="{ridge.d()}" fill="none" stroke="#fff" stroke-width="90" stroke-linecap="round" opacity="0.85" filter="url(#f-blur36)"/>', 3)
        # the wing surface falls away toward the black section
        doc.add(f'<path d="{shade.d()}" fill="none" stroke="#a3a5af" stroke-width="70" stroke-linecap="round" opacity="0.35" filter="url(#f-blur36)"/>', 3)
        dx = 300 if not mirror else 1300
        doc.add(f'<ellipse cx="{dx}" cy="330" rx="170" ry="140" fill="#fff" opacity="0.6" filter="url(#f-blur36)"/>', 3)
    doc.add('</g>', 2)
    doc.add(f'<path d="{body_full.d()}" fill="none" stroke="{SHELL_EDGE}" stroke-width="2.5" stroke-linejoin="round"/>', 2)
    # USB-C slot on the top edge
    doc.add('<rect id="usb-c" x="750" y="31" width="100" height="11" rx="5.5" fill="#55565e"/>', 2)
    doc.add('<rect x="754" y="33" width="92" height="7" rx="3.5" fill="#1e1e22"/>', 2)
    doc.add('</g>')

    doc.add('<g id="bumpers">')
    for side, mirror in (('l', False), ('r', True)):
        b = mirror_path(bump, CX) if mirror else bump
        doc.add(f'<path id="bumper-{side}1" d="{b.d()}" fill="url(#g-bumper)" stroke="#000" stroke-width="2" stroke-linejoin="round"/>', 2)
        # lit top edge of the bumper band (separates it from the trigger behind)
        hl = Path().M((204, 106)).C((240, 86), (290, 74), (340, 70)).C((375, 67), (410, 68), (428, 74))
        if mirror:
            hl = mirror_path(hl, CX)
        doc.add(f'<path d="{hl.d()}" fill="none" stroke="#b9bac2" stroke-width="3.5" opacity="{0.8 if not mirror else 0.6}" stroke-linecap="round" filter="url(#f-blur1)"/>', 2)
    doc.add('</g>')

    # ======================================================= black inner section
    doc.comment('Black inner section (sticks, PS button, mute button, inner grip strips)')
    doc.add('<g id="inner-section">')
    doc.add(f'<path id="inner-section-body" d="{frame_full.d()}" fill="url(#g-frame)"/>', 2)
    doc.add('<g clip-path="url(#clip-frame)">', 2)
    for cx in (546, 1054):
        doc.add(f'<circle cx="{cx}" cy="540" r="150" fill="#4a4a52" opacity="0.55" filter="url(#f-blur24)"/>', 3)
    doc.add('<rect x="690" y="372" width="220" height="330" fill="#3a3a41" opacity="0.5" filter="url(#f-blur24)"/>', 3)
    # highlight band just below the touch pad (the step down from the pad)
    doc.add('<path d="M540,380 L1060,380" stroke="#5a5a62" stroke-width="10" opacity="0.7" filter="url(#f-blur6)"/>', 3)
    for mirror in (False, True):
        p = mirror_path(wing_edge, CX) if mirror else wing_edge
        doc.add(f'<path d="{p.d()}" fill="none" stroke="#000" stroke-width="16" opacity="0.6" filter="url(#f-blur6)" transform="translate({-4 if not mirror else 4},6)"/>', 3)
        # rounded inner edge of the grip catches a little light
        ge = Path().M((222, 1036)).C((250, 1010), (292, 920), (335, 830)).C((365, 765), (385, 725), (420, 706))
        if mirror:
            ge = mirror_path(ge, CX)
        doc.add(f'<path d="{ge.d()}" fill="none" stroke="#4e4e56" stroke-width="7" opacity="0.8" filter="url(#f-blur3)"/>', 3)
    doc.add('</g>', 2)
    for mirror in (False, True):
        p = mirror_path(wing_edge, CX) if mirror else wing_edge
        doc.add(f'<path d="{p.d()}" fill="none" stroke="{SEAM}" stroke-width="1.5" opacity="0.85"/>', 2)
    doc.add('</g>')

    # ======================================================= touch pad with light bar
    doc.comment('Touch pad (white, glossy) with the light bar strips along its sides')
    # light bar: a tapered crescent hugging the pad's side, hairline at the top, wider at the bottom
    lb = Path()
    lb.M((484, 66)).C((478, 80), (476, 110), (478, 150)).C((483, 230), (496, 300), (512, 352)).C((516, 366), (524, 377), (540, 386))
    lb.C((552, 392), (560, 388), (556, 378)).C((540, 360), (526, 330), (518, 300)).C((506, 250), (494, 160), (492, 90)).C((492, 80), (490, 66), (484, 66)).Z()
    doc.add('<g id="touchpad">')
    doc.add(f'<path d="{pad_full.d()}" fill="none" stroke="#6f717c" stroke-width="10" opacity="0.35" filter="url(#f-blur6)"/>', 2)
    for side, mirror in (('l', False), ('r', True)):
        p = mirror_path(lb, CX) if mirror else lb
        doc.add(f'<path d="{p.d()}" fill="{LIGHTBAR}" opacity="0.5" filter="url(#f-blur12)"/>', 2)
        doc.add(f'<path id="lightbar-{side}" d="{p.d()}" fill="{LIGHTBAR}"/>', 2)
        core = Path().M((486, 90)).C((490, 180), (500, 270), (516, 330)).C((522, 352), (530, 368), (544, 380))
        if mirror:
            core = mirror_path(core, CX)
        doc.add(f'<path d="{core.d()}" fill="none" stroke="{LIGHTBAR_CORE}" stroke-width="3.5" stroke-linecap="round" opacity="0.9"/>', 2)
    doc.add(f'<path id="touchpad-surface" d="{pad_full.d()}" fill="url(#g-pad)" stroke="{PAD_EDGE}" stroke-width="2"/>', 2)
    doc.add('<path d="M520,70 C640,62 760,60 800,60 C840,60 960,62 1080,70 C1060,120 1040,160 1030,200 C900,185 700,185 570,200 C560,160 540,120 520,70 Z" fill="#fff" opacity="0.55" filter="url(#f-blur24)"/>', 2)
    doc.add('</g>')

    # ======================================================= player LEDs and speaker holes
    doc.add('<g id="player-indicator">')
    for i, x in enumerate((743, 772, 800, 828, 857)):
        if i == 2:
            doc.add(f'<circle cx="{x}" cy="421" r="14" fill="#9fd4ff" opacity="0.7" filter="url(#f-blur6)"/>', 2)
            doc.add(f'<circle cx="{x}" cy="421" r="8" fill="#eaf6ff"/>', 2)
        else:
            doc.add(f'<circle cx="{x}" cy="421" r="8" fill="#0b0b0c"/>', 2)
            doc.add(f'<circle cx="{x}" cy="421" r="8" fill="none" stroke="#3b3b42" stroke-width="1.2"/>', 2)
    doc.add('</g>')
    doc.add('<g id="speaker">')
    for x in (757, 786, 814, 843):
        doc.add(f'<circle cx="{x}" cy="447" r="8" fill="#0b0b0c"/>', 2)
        doc.add(f'<circle cx="{x}" cy="447" r="8" fill="none" stroke="#3b3b42" stroke-width="1.2"/>', 2)
    doc.add('</g>')

    # ======================================================= PS button, mute button, headset jack
    doc.add(ps_button(CX, 524), 1)
    doc.add(mute_button(CX, 622), 1)
    doc.add('<g id="headset-jack">')
    doc.add('<path d="M778,699 C778,690 786,686 800,686 C814,686 822,690 822,699 Z" fill="#0a0a0b"/>', 2)
    doc.add('<path d="M782,699 C782,693 790,690 800,690 C810,690 818,693 818,699 Z" fill="#1f1f23"/>', 2)
    doc.add('</g>')

    # ======================================================= sticks, d-pad, face buttons, create/options
    for side, cx in (('l', 546), ('r', 1054)):
        doc.add(stick(side, cx, 540), 1)
    doc.add(dpad(300, 320), 1)
    doc.add(face_buttons(1299, 320), 1)
    doc.add(small_button('create', 426, 144, -12), 1)
    doc.add(small_button('options', 1174, 144, 12), 1)
    doc.add(create_icon(414, 94), 1)
    doc.add(options_icon(1186, 94), 1)
    return doc.render()


# ----------------------------------------------------------------------------------------------
PS_LOGO_D = ("M8.984 2.596v17.547l3.915 1.261V6.688c0-.69.304-1.151.794-.991.636.18.76.814.76 1.505v5.875c2.441 1.193 "
             "4.362-.002 4.362-3.152 0-3.237-1.126-4.675-4.438-5.827-1.307-.448-3.728-1.186-5.39-1.502zm4.656 16.241l6.296-2.275"
             "c.715-.258.826-.625.246-.818-.586-.192-1.637-.139-2.357.123l-4.205 1.5V14.98l.24-.085s1.201-.42 2.913-.615c1.696-.18 "
             "3.785.03 5.437.661 1.848.601 2.04 1.472 1.576 2.072-.465.6-1.622 1.036-1.622 1.036l-8.544 3.107V18.86zM1.807 18.6"
             "c-1.9-.545-2.214-1.668-1.352-2.32.801-.586 2.16-1.052 2.16-1.052l5.615-2.013v2.313L4.205 17c-.705.271-.825.632-.239.826"
             ".586.195 1.637.15 2.343-.12L8.247 17v2.074c-.12.03-.256.044-.39.073-1.939.331-3.996.196-6.038-.479z")

def ps_button(cx, cy):
    """PS button: the PlayStation logo in relief (logo path CC0 from Simple Icons, 24x24 box)."""
    s = 4.6
    tx, ty = cx - 12 * s, cy - 12 * s
    out = ['<g id="ps-button">']
    out.append(f'  <g transform="translate({n(tx)},{n(ty)}) scale({n(s)})">')
    out.append(f'    <path d="{PS_LOGO_D}" fill="#000" opacity="0.55" transform="translate(0.25,0.55)" filter="url(#f-blur1)"/>')
    out.append(f'    <path d="{PS_LOGO_D}" fill="url(#g-ps)" stroke="#0a0a0b" stroke-width="0.25"/>')
    out.append(f'    <path d="{PS_LOGO_D}" fill="none" stroke="#5a5a62" stroke-width="0.22" transform="translate(-0.12,-0.18)" opacity="0.8"/>')
    out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def mute_button(cx, cy):
    w, h = 90, 28
    out = ['<g id="mute-button">']
    out.append(f'  <rect x="{n(cx-w/2)}" y="{n(cy-h/2+3)}" width="{w}" height="{h}" rx="{h/2}" fill="#000" opacity="0.6" filter="url(#f-blur1)"/>')
    out.append(f'  <rect x="{n(cx-w/2)}" y="{n(cy-h/2)}" width="{w}" height="{h}" rx="{h/2}" fill="url(#g-mute)" stroke="#0a0a0b" stroke-width="1.5"/>')
    out.append(f'  <rect x="{n(cx-w/2+6)}" y="{n(cy-h/2+2)}" width="{w-12}" height="6" rx="3" fill="#fff" opacity="0.14"/>')
    gx, gy = cx, cy + 36
    out.append(f'  <g id="mute-icon" transform="translate({n(gx)},{n(gy)})" fill="none" stroke="#9a9aa2" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">')
    out.append('    <rect x="-4.5" y="-12" width="9" height="15" rx="4.5"/>')
    out.append('    <path d="M-9,-2 C-9,5 -4,9 0,9 C4,9 9,5 9,-2 M0,9 L0,14 M-5,14 L5,14 M-11,-13 L11,11"/>')
    out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def stick(side, cx, cy):
    well_r = 116
    cap_r = 94
    dish_r = 76
    out = [f'<g id="stick-{side}">']
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r+3}" fill="#000" opacity="0.5" filter="url(#f-blur3)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r}" fill="url(#g-well)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{well_r-2}" fill="none" stroke="#000" stroke-width="3" opacity="0.7"/>')
    out.append(f'  <circle cx="{cx+5}" cy="{cy+8}" r="{cap_r+2}" fill="#000" opacity="0.7" filter="url(#f-blur3)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{cap_r}" fill="url(#g-cap-rim)" stroke="#08080a" stroke-width="2"/>')
    ticks = []
    for i in range(72):
        a = i * 5
        p1 = polar(cx, cy, dish_r + 3, a)
        p2 = polar(cx, cy, cap_r - 3, a)
        ticks.append(f'M{pt(p1)}L{pt(p2)}')
    out.append(f'  <path d="{"".join(ticks)}" stroke="#4a4a52" stroke-width="1.6" stroke-linecap="round" fill="none" opacity="0.75"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{cap_r-4}" fill="none" stroke="#fff" stroke-width="3" opacity="0.18" stroke-dasharray="{n(math.pi*(cap_r-4)*0.45)} {n(math.pi*(cap_r-4)*1.55)}" transform="rotate(205 {cx} {cy})" filter="url(#f-blur1)"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{dish_r}" fill="url(#g-cap-dish)" stroke="#0a0a0c" stroke-width="2"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="{dish_r-3}" fill="none" stroke="#fff" stroke-width="2.5" opacity="0.14" stroke-dasharray="{n(math.pi*(dish_r-3)*0.4)} {n(math.pi*(dish_r-3)*1.6)}" transform="rotate(20 {cx} {cy})" filter="url(#f-blur1)"/>')
    out.append('</g>')
    return '\n  '.join(out)


def dpad_arm():
    """One directional button pointing UP, centred at x=0, tip toward the origin (local units)."""
    return ("M-46,-90 C-46,-122 -38,-137 -16,-138 L16,-138 C38,-137 46,-122 46,-90 "
            "L46,-62 C46,-54 43,-48 37,-43 L11,-25 C5,-21 -5,-21 -11,-25 L-37,-43 C-43,-48 -46,-54 -46,-62 Z")

def dpad(cx, cy):
    out = ['<g id="dpad">']
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="19" fill="#c9cad1"/>')
    out.append(f'  <circle cx="{cx}" cy="{cy}" r="19" fill="none" stroke="#9c9ea8" stroke-width="1.5"/>')
    out.append(f'  <circle cx="{cx+2}" cy="{cy+3}" r="13" fill="#b5b7bf" opacity="0.7" filter="url(#f-blur1)"/>')
    d = dpad_arm()
    for name, ang in (('up', 0), ('right', 90), ('down', 180), ('left', 270)):
        out.append(f'  <g id="dpad-{name}" transform="translate({cx},{cy}) rotate({ang})">')
        a = math.radians(-ang)
        ox, oy = 3 * math.cos(a) + 5 * math.sin(a), -3 * math.sin(a) + 5 * math.cos(a)
        out.append(f'    <path d="{d}" fill="#000" opacity="0.28" transform="translate({n(ox)},{n(oy)})" filter="url(#f-blur3)"/>')
        out.append(f'    <path d="{d}" fill="url(#g-cap-face)" stroke="#a9abb3" stroke-width="1.6" stroke-linejoin="round"/>')
        # small direction mark near the outer end
        out.append(f'    <path d="M-9,-100 L0,-114 L9,-100 Z" fill="{SYMBOL}" opacity="0.75"/>')
        out.append(f'    <path d="{d}" fill="url(#g-cap-gloss)" opacity="0.65"/>')
        out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def face_buttons(cx, cy):
    r = 50
    off = 118
    out = ['<g id="face-buttons">']
    btns = (('triangle', cx, cy - off), ('circle', cx + off, cy), ('cross', cx, cy + off), ('square', cx - off, cy))
    for name, x, y in btns:
        out.append(f'  <g id="btn-{name}">')
        out.append(f'    <circle cx="{n(x+3)}" cy="{n(y+5)}" r="{r+1}" fill="#000" opacity="0.3" filter="url(#f-blur3)"/>')
        # clear cap: dark refracting rim, lighter disc inside
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="url(#g-cap-ring)"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r-6}" fill="url(#g-cap-face)"/>')
        sw = 5.5
        if name == 'triangle':
            k = 23
            p = f'M{n(x)},{n(y-k)} L{n(x+k*0.92)},{n(y+k*0.58)} L{n(x-k*0.92)},{n(y+k*0.58)} Z'
            out.append(f'    <path d="{p}" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linejoin="round"/>')
        elif name == 'circle':
            out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="20" fill="none" stroke="{SYMBOL}" stroke-width="{sw}"/>')
        elif name == 'cross':
            k = 16.5
            out.append(f'    <path d="M{n(x-k)},{n(y-k)} L{n(x+k)},{n(y+k)} M{n(x+k)},{n(y-k)} L{n(x-k)},{n(y+k)}" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linecap="round"/>')
        else:
            k = 17.5
            out.append(f'    <rect x="{n(x-k)}" y="{n(y-k)}" width="{n(2*k)}" height="{n(2*k)}" rx="2" fill="none" stroke="{SYMBOL}" stroke-width="{sw}" stroke-linejoin="round"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r-1}" fill="url(#g-cap-gloss)" opacity="0.8"/>')
        out.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="none" stroke="#5f6068" stroke-width="1.2" opacity="0.8"/>')
        out.append('  </g>')
    out.append('</g>')
    return '\n  '.join(out)


def small_button(name, cx, cy, angle):
    w, h = 38, 78
    out = [f'<g id="{name}-button" transform="translate({cx},{cy}) rotate({angle})">']
    out.append(f'  <rect x="{n(-w/2+2)}" y="{n(-h/2+4)}" width="{w}" height="{h}" rx="{w/2}" fill="#000" opacity="0.28" filter="url(#f-blur3)"/>')
    out.append(f'  <rect x="{n(-w/2)}" y="{n(-h/2)}" width="{w}" height="{h}" rx="{w/2}" fill="url(#g-create)" stroke="#a9abb3" stroke-width="1.6"/>')
    out.append(f'  <rect x="{n(-w/2+6)}" y="{n(-h/2+5)}" width="{w-12}" height="{h*0.42}" rx="{(w-12)/2}" fill="#fff" opacity="0.7"/>')
    out.append('</g>')
    return '\n  '.join(out)


def create_icon(cx, cy):
    out = [f'<g id="create-icon" transform="translate({cx},{cy})" fill="none" stroke="{SYMBOL}" stroke-width="3.2" stroke-linecap="round">']
    out.append('  <path d="M0,-20 L0,-2 M-16,-15 L-6,-1 M16,-15 L6,-1"/>')
    out.append('</g>')
    return '\n  '.join(out)


def options_icon(cx, cy):
    out = [f'<g id="options-icon" transform="translate({cx},{cy})" fill="none" stroke="{SYMBOL}" stroke-width="3.2" stroke-linecap="round">']
    out.append('  <path d="M-11,-16 L11,-16 M-11,-8 L11,-8 M-11,0 L11,0"/>')
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
