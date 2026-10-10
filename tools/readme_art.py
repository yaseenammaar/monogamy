#!/usr/bin/env python3
"""Render Mori as self-animating SVGs (SMIL) for the README.

GitHub can't run the widget's JavaScript, so this ports Mori's pose maths
from widget/pet.html and bakes each mood's motion into the SVG itself.
Writes assets/mori-<mood>.svg and assets/mori-shapes.svg.
"""

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

# Same poses as POSES in widget/pet.html.
POSES = {
    "blob":  dict(cx=60, top=36, w=76, hemW=46, hemY=104, hemAmp=1.5, hemCurve=8, bulge=7, rot0=0,
                  hoodX=60, hoodY=68, hoodRx=21, hoodRy=21, faceX=60, faceY=70, faceRx=17, faceRy=17, faceS=.92,
                  haloX=60, haloY=21, haloRx=13, haloRy=3.4, wingDX=32, wingY=66, wingS=.8, wingR=-12,
                  scX=101, scY1=46, scY2=108, shadowRx=26),
    "ghost": dict(cx=60, top=18, w=36, hemW=36, hemY=108, hemAmp=5, hemCurve=0, bulge=0, rot0=0,
                  hoodX=60, hoodY=40, hoodRx=13, hoodRy=13, faceX=60, faceY=42, faceRx=10.5, faceRy=10, faceS=.57,
                  haloX=60, haloY=10, haloRx=11, haloRy=3, wingDX=14, wingY=46, wingS=.85, wingR=18,
                  scX=88, scY1=22, scY2=116, shadowRx=16),
    "chibi": dict(cx=60, top=20, w=68, hemW=46, hemY=114, hemAmp=4, hemCurve=0, bulge=-9, rot0=0,
                  hoodX=60, hoodY=57, hoodRx=26, hoodRy=26, faceX=60, faceY=59, faceRx=22, faceRy=22, faceS=1.19,
                  haloX=60, haloY=12, haloRx=15, haloRy=3.8, wingDX=17, wingY=92, wingS=.75, wingR=-5,
                  scX=91, scY1=70, scY2=118, shadowRx=22),
    "bean":  dict(cx=60, top=30, w=58, hemW=52, hemY=100, hemAmp=1, hemCurve=9, bulge=5, rot0=-8,
                  hoodX=58, hoodY=62, hoodRx=20, hoodRy=18, faceX=58, faceY=64, faceRx=16.5, faceRy=15, faceS=.89,
                  haloX=56, haloY=18, haloRx=13, haloRy=3.4, wingDX=26, wingY=64, wingS=.78, wingR=-8,
                  scX=99, scY1=42, scY2=110, shadowRx=24),
}

INK, CLOAK, HOOD, FACE, WING, GOLD = "#1e1830", "#4a3d73", "#2c2445", "#f6f1ea", "#d3cce6", "#e6c26a"
WING_D = "M0,0 C-12,-12 -24,-8 -27,3 C-18,3 -10,8 -1,16 Z"
EASE = "0.45 0 0.55 1"


def f(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def lerp(a, b, t):
    return a + (b - a) * t


def body_path(c):
    """Port of bodyPath() in widget/pet.html: 24 points, closed Catmull-Rom."""
    r, hy = c["w"] / 2, c["top"] + c["w"] / 2
    R, L, p = c["cx"] + c["hemW"] / 2, c["cx"] - c["hemW"] / 2, []
    for i in range(9):
        a = math.pi * (1 + i / 8)
        p.append((c["cx"] + r * math.cos(a), hy + r * math.sin(a)))
    for i in range(1, 4):
        t = i / 4
        p.append((lerp(c["cx"] + r, R, t) + c["bulge"] * math.sin(math.pi * t), lerp(hy, c["hemY"], t)))
    for i in range(9):
        u = i / 8
        p.append((lerp(R, L, u), c["hemY"] + c["hemCurve"] * math.sin(math.pi * u) + (c["hemAmp"] if i % 2 else 0)))
    for i in range(1, 4):
        t = i / 4
        p.append((lerp(L, c["cx"] - r, t) - c["bulge"] * math.sin(math.pi * t), lerp(c["hemY"], hy, t)))
    n = len(p)
    d = "M%s,%s" % (f(p[0][0]), f(p[0][1]))
    for i in range(n):
        p0, a, b, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        d += "C%s,%s %s,%s %s,%s" % (f(a[0] + (b[0] - p0[0]) / 6), f(a[1] + (b[1] - p0[1]) / 6),
                                     f(b[0] - (p3[0] - a[0]) / 6), f(b[1] - (p3[1] - a[1]) / 6), f(b[0]), f(b[1]))
    return d + "Z"


def loop(attr, values, dur, key_times=None, splines=None, kind=None):
    """One SMIL <animate>/<animateTransform>, repeating forever."""
    tag = "animateTransform" if kind else "animate"
    extra = ' type="%s"' % kind if kind else ""
    if key_times:
        extra += ' keyTimes="%s" calcMode="spline" keySplines="%s"' % (";".join("%.4g" % t for t in key_times), ";".join(splines))
    return '<%s attributeName="%s"%s values="%s" dur="%gs" repeatCount="indefinite"/>' % (tag, attr, extra, ";".join(values), dur)


def smooth(attr, values, dur, kind=None):
    """Ease between each value."""
    n = len(values) - 1
    return loop(attr, values, dur, [i / n for i in range(n + 1)], [EASE] * n, kind)


def features(mood):
    eyes = {
        "dots": '<g fill="%s"><circle cx="-7" cy="-.5" r="2.5"/><circle cx="7" cy="-.5" r="2.5"/></g>' % INK,
        "arcs": '<path d="M-10,.5 Q-7,-3.5 -4,.5M4,.5 Q7,-3.5 10,.5"/>',
        "shut": '<path d="M-10,0 L-4,0M4,0 L10,0"/>',
    }
    brows = {"angry": '<path d="M-11,-6.5 L-4,-4M11,-6.5 L4,-4"/>', "worried": '<path d="M-11,-4 L-4,-6.5M11,-4 L4,-6.5"/>'}
    eye = {"happy": "arcs", "sleepy": "shut"}.get(mood, "dots")
    mouth = '<path d="M-2.5,8 Q0,6 2.5,8"/>' if mood in ("angry", "worried") else '<path d="M-2.5,6.5 Q0,8.5 2.5,6.5"/>'
    blink = loop("transform", ["1 1", "1 1", "1 .1", "1 1"], 4.5, [0, .94, .97, 1], ["0 0 1 1"] * 3, "scale")
    eye_svg = eyes[eye] if eye != "dots" else "<g>%s%s</g>" % (blink, eyes["dots"])
    return ('<g fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round">%s%s%s</g>'
            % (INK, eye_svg, brows.get(mood, ""), mouth))


def wing(c, side, flap):
    x = c["cx"] + side * c["wingDX"]
    mirror = "" if side < 0 else " scale(-1 1)"
    return ('<g transform="translate(%s %s)%s"><g>%s<path d="%s" transform="scale(%s)" fill="%s"/></g></g>'
            % (f(x), f(c["wingY"]), mirror, flap, WING_D, f(c["wingS"]), WING))


def character(c, mood, flap_dur):
    r = c["wingR"]
    flap = smooth("transform", [f(r - 4), f(r + 6), f(r - 4)], flap_dur, "rotate")
    length = c["scY2"] - c["scY1"]
    return "".join([
        '<g transform="rotate(%s 60 72)">' % f(c["rot0"]),
        wing(c, -1, flap), wing(c, 1, flap),
        '<g transform="translate(%s %s)"><line y2="%s" stroke="#8d84a6" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M0,0 Q11,-4 16,7 Q8,2 0,5 Z" fill="#c9c1dd"/></g>' % (f(c["scX"]), f(c["scY1"]), f(length)),
        '<path d="%s" fill="%s"/>' % (body_path(c), CLOAK),
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(c["hoodX"]), f(c["hoodY"]), f(c["hoodRx"]), f(c["hoodRy"]), HOOD),
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(c["faceX"]), f(c["faceY"]), f(c["faceRx"]), f(c["faceRy"]), FACE),
        '<g transform="translate(%s %s) scale(%s)">%s</g>' % (f(c["faceX"]), f(c["faceY"]), f(c["faceS"]), features(mood)),
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
        % (f(c["haloX"]), f(c["haloY"]), f(c["haloRx"]), f(c["haloRy"]), GOLD),
        "</g>",
    ])


def svg(inner, shadow_rx, shadow_anim=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 130" width="120" height="130">'
            '<ellipse cx="60" cy="123" rx="%s" ry="3.5" fill="#000" opacity=".14">%s</ellipse>%s</svg>\n'
            % (f(shadow_rx), shadow_anim, inner))


# Each mood: pose, body motion, wing flap speed.
MOODS = {
    "focused": ("chibi", lambda: smooth("transform", ["0 0", "0 -3", "0 0"], 3.4, "translate"), 1.6),
    "happy":   ("chibi", lambda: loop("transform", ["0 0", "0 -9", "0 0"], .9, [0, .4, 1],
                                      ["0.2 0.7 0.4 1", "0.6 0 0.8 0.3"], "translate"), .45),
    "angry":   ("chibi", lambda: loop("transform", ["-1.6 0", "1.6 0", "-1.6 0"], .16, [0, .5, 1],
                                      ["0 0 1 1"] * 2, "translate"), 1.2),
    "worried": ("chibi", lambda: smooth("transform", ["-3 60 118", "3 60 118", "-3 60 118"], 2.6, "rotate"), 2),
    "sleepy":  ("blob", None, 4),
}


def mood_svg(mood):
    pose, motion, flap = MOODS[mood]
    c = POSES[pose]
    char = character(c, mood, flap)
    if mood == "sleepy":  # slow breathing, squashing from the floor up
        breathe = smooth("transform", ["1 1", "1.04 .96", "1 1"], 5, "scale")
        return svg('<g transform="translate(60 118)"><g>%s<g transform="translate(-60 -118)">%s</g></g></g>'
                   % (breathe, char), c["shadowRx"])
    shadow = smooth("rx", [f(c["shadowRx"]), f(c["shadowRx"] * .86), f(c["shadowRx"])], 3.4) if mood == "focused" else ""
    return svg("<g>%s%s</g>" % (motion(), char), c["shadowRx"], shadow)


def shapes_svg():
    """Morph chibi → bean → ghost → blob → chibi, holding each pose."""
    order = ["chibi", "bean", "ghost", "blob", "chibi"]
    hold, move = 1.1, .6
    total = (hold + move) * 4
    times, seq, t = [0], [order[0]], 0
    for nxt in order[1:]:
        t += hold
        times.append(t / total); seq.append(seq[-1])
        t += move
        times.append(t / total); seq.append(nxt)
    times[-1] = 1
    splines = ["0 0 1 1" if i % 2 == 0 else "0.4 0 0.2 1" for i in range(len(seq) - 1)]

    def anim(attr, fn, kind=None):
        return loop(attr, [fn(POSES[p]) for p in seq], total, times, splines, kind)

    def ell(prefix, fill, extra=""):
        return '<ellipse fill="%s"%s>%s</ellipse>' % (fill, extra, "".join(
            anim(a, lambda c, k=prefix + k: f(c[k])) for a, k in (("cx", "X"), ("cy", "Y"), ("rx", "Rx"), ("ry", "Ry"))))

    def wing_m(side):
        mirror = '<g transform="scale(-1 1)">' if side > 0 else "<g>"
        return ("<g>%s%s<g>%s<path d=\"%s\" fill=\"%s\">%s</path></g></g></g>" % (
            anim("transform", lambda c: "%s %s" % (f(c["cx"] + side * c["wingDX"]), f(c["wingY"])), "translate"),
            mirror,
            anim("transform", lambda c: f(c["wingR"]), "rotate"),
            WING_D, WING, anim("transform", lambda c: f(c["wingS"]), "scale")))

    blink = loop("transform", ["1 1", "1 1", "1 .1", "1 1"], 4.5, [0, .94, .97, 1], ["0 0 1 1"] * 3, "scale")
    face_parts = ('<g fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round">'
                  '<g>%s<g fill="%s" stroke="none"><circle cx="-7" cy="-.5" r="2.5"/><circle cx="7" cy="-.5" r="2.5"/></g></g>'
                  '<path d="M-2.5,6.5 Q0,8.5 2.5,6.5"/></g>' % (INK, blink, INK))
    char = "".join([
        "<g>%s" % anim("transform", lambda c: "%s 60 72" % f(c["rot0"]), "rotate"),
        wing_m(-1), wing_m(1),
        "<g>%s<line stroke=\"#8d84a6\" stroke-width=\"2.4\" stroke-linecap=\"round\">%s</line>"
        "<path d=\"M0,0 Q11,-4 16,7 Q8,2 0,5 Z\" fill=\"#c9c1dd\"/></g>" % (
            anim("transform", lambda c: "%s %s" % (f(c["scX"]), f(c["scY1"])), "translate"),
            anim("y2", lambda c: f(c["scY2"] - c["scY1"]))),
        '<path fill="%s">%s</path>' % (CLOAK, anim("d", body_path)),
        ell("hood", HOOD), ell("face", FACE),
        "<g>%s<g>%s%s</g></g>" % (anim("transform", lambda c: "%s %s" % (f(c["faceX"]), f(c["faceY"])), "translate"),
                                  anim("transform", lambda c: f(c["faceS"]), "scale"), face_parts),
        ell("halo", "none", ' stroke="%s" stroke-width="2.4"' % GOLD),
        "</g>",
    ])
    floaty = smooth("transform", ["0 0", "0 -3", "0 0"], 3.4, "translate")
    return svg("<g>%s%s</g>" % (floaty, char), 22, anim("rx", lambda c: f(c["shadowRx"])))


def main():
    os.makedirs(OUT, exist_ok=True)
    for mood in MOODS:
        with open(os.path.join(OUT, "mori-%s.svg" % mood), "w") as fh:
            fh.write(mood_svg(mood))
    with open(os.path.join(OUT, "mori-shapes.svg"), "w") as fh:
        fh.write(shapes_svg())
    print("wrote", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
