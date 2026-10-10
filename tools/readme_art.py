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


def mori_parts(mood):
    """(shadow rx, shadow animation, animated body) for one mood, in a 120x130 box."""
    pose, motion, flap = MOODS[mood]
    c = POSES[pose]
    char = character(c, mood, flap)
    if mood == "sleepy":  # slow breathing, squashing from the floor up
        breathe = smooth("transform", ["1 1", "1.04 .96", "1 1"], 5, "scale")
        return c["shadowRx"], "", ('<g transform="translate(60 118)"><g>%s<g transform="translate(-60 -118)">%s</g></g></g>'
                                   % (breathe, char))
    shadow = smooth("rx", [f(c["shadowRx"]), f(c["shadowRx"] * .86), f(c["shadowRx"])], 3.4) if mood == "focused" else ""
    return c["shadowRx"], shadow, "<g>%s%s</g>" % (motion(), char)


def mood_svg(mood):
    rx, shadow_anim, body = mori_parts(mood)
    return svg(body, rx, shadow_anim)


def mori_at(mood, x, y, scale):
    """Mori (with her shadow) placed inside a bigger drawing."""
    rx, shadow_anim, body = mori_parts(mood)
    return ('<g transform="translate(%s %s) scale(%s)"><ellipse cx="60" cy="123" rx="%s" ry="3.5" fill="#1e1830" opacity=".14">%s</ellipse>%s</g>'
            % (f(x), f(y), scale, f(rx), shadow_anim, body))


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


# ---------------------------------------------------------------- explainer art
# Both drawings sit on their own light card so they read the same on
# GitHub's light and dark themes.

BG, CARD, LINE, TXT, MUTED = "#f6f4fa", "#ffffff", "#d9d3e6", "#1e1830", "#7d7593"
ACCENT, GREEN, RED, AMBER = "#6b55c4", "#2fa36b", "#d9546b", "#c38f1c"
TERM, TERM_TXT, TERM_MUTED = "#1e1830", "#f1eef7", "#9d95b3"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kt(*times):
    """keyTimes string, nudged so every value is strictly increasing."""
    out, prev = [], -1
    for t in times:
        t = max(0.0, min(1.0, t))
        if t <= prev:
            t = prev + 0.0005
        out.append(t)
        prev = t
    out[-1] = 1
    return ";".join("%.4f" % t for t in out)


def text(x, y, s, size=13, fill=TXT, weight=400, family=SANS, anchor="start", extra=""):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>'
            % (f(x), f(y), family, size, weight, fill, anchor, extra, esc(s)))


def node(x, y, w, h, title, subs=(), stroke=LINE, title_fill=TXT):
    out = '<rect x="%s" y="%s" width="%s" height="%s" rx="12" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, w, h, CARD, stroke)
    out += text(x + 16, y + 27, title, 15, title_fill, 600)
    for i, line in enumerate(subs):
        out += text(x + 16, y + 48 + i * 17, line, 12.5, MUTED)
    return out


def token(color, path, start, arrive, T):
    """A glowing dot that travels `path` between start and arrive, then fades."""
    vis = kt(0, (start - .02) / T, start / T, arrive / T, (arrive + .7) / T, 1)
    return ('<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="%s" dur="%gs" repeatCount="indefinite"/>'
            '<circle r="11" fill="%s" opacity=".18"/><circle r="5.5" fill="%s"/>'
            '<animateMotion path="%s" keyPoints="0;0;1;1" keyTimes="%s" calcMode="spline" '
            'keySplines="0 0 1 1;0.45 0 0.55 1;0 0 1 1" dur="%gs" repeatCount="indefinite"/></g>'
            % (vis, T, color, color, path, kt(0, start / T, arrive / T, 1), T))


def flow_svg():
    """How a prompt travels: agent, vow guard, then allowed / blocked / tamper; then vow done."""
    T = 12.0
    W, H = 960, 590
    style = ("<style>.flow{fill:none;stroke:%s;stroke-width:2;stroke-dasharray:6 7;animation:dash 1.1s linear infinite}"
             "@keyframes dash{to{stroke-dashoffset:-13}}</style>" % LINE)
    defs = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % LINE)
    out = [defs, style, '<rect width="%d" height="%d" rx="22" fill="%s"/>' % (W, H, BG)]
    out.append(text(40, 46, "How Monogamy works", 22, TXT, 700))
    out.append(text(40, 70, "Every prompt passes through vow guard before your AI ever sees it.", 13.5, MUTED))

    # main pipeline
    out.append(node(40, 140, 140, 70, "You", ["type a prompt"]))
    out.append(node(220, 125, 180, 100, "Your AI agent", ["Claude Code · Cursor", "Codex · Gemini", "Windsurf"]))
    out.append(node(440, 135, 170, 80, "vow guard", ["runs first, every time"], ACCENT, ACCENT))
    out.append('<path d="M455,278 v58 a70,12 0 0 0 140,0 v-58" fill="%s" stroke="%s" stroke-width="1.5"/>'
               '<ellipse cx="525" cy="278" rx="70" ry="12" fill="%s" stroke="%s" stroke-width="1.5"/>' % (CARD, LINE, CARD, LINE))
    out.append(text(525, 314, "state.json", 14, TXT, 600, anchor="middle"))
    out.append(text(525, 332, "your vow + checks", 12, MUTED, anchor="middle"))
    outcomes = [
        (56, GREEN, "Inside the project", ["Allowed. The agent works only on", "the vow and parks anything else."]),
        (138, RED, "Outside the project", ["Blocked. Prompt parked, attempt", "logged, lock warning shown."]),
        (220, AMBER, "Agent tries to cheat", ["Blocked: breakup, confirm, editing", "the lock or the vow file."]),
    ]
    for y, color, title, subs in outcomes:
        out.append(node(670, y, 250, 74, title, subs, color, color))
    out.append(text(525, 126, "which folder are you in?", 11.5, MUTED, anchor="middle", extra=' font-style="italic"'))

    edges = ["M180,175 L218,175", "M400,175 L438,175", "M525,215 L525,264",
             "M610,175 C640,175 640,93 668,93", "M610,175 L668,175", "M610,175 C640,175 640,257 668,257"]
    out += ['<path class="flow" d="%s" marker-end="url(#arrow)"/>' % d for d in edges]

    # three prompts take turns travelling through the pipeline
    prompts = [("fix the snake collision", GREEN, 93), ("build a crypto bot in ~/other", RED, 175),
               ("agent: delete the vow file", AMBER, 257)]
    for i, (msg, color, ey) in enumerate(prompts):
        s0, arrive = i * 4 + 0.05, i * 4 + 3.0
        out.append(token(color, "M180,175 L610,175 C640,175 640,%d 668,%d" % (ey, ey), s0, arrive, T))
        # outcome card glows on arrival
        out.append('<rect x="670" y="%d" width="250" height="74" rx="12" fill="none" stroke="%s" stroke-width="4" opacity="0">'
                   '<animate attributeName="opacity" values="0;0;.55;0;0" keyTimes="%s" dur="%gs" repeatCount="indefinite"/></rect>'
                   % (ey - 37, color, kt(0, (arrive - .05) / T, arrive / T, (arrive + 1.3) / T, 1), T))
        # the prompt being sent, under the You card
        vis = kt(0, (s0 - .02) / T, s0 / T, arrive / T, (arrive + .7) / T, 1)
        out.append('<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="%s" dur="%gs" repeatCount="indefinite"/>%s</g>'
                   % (vis, T, text(40, 252, "> " + msg, 13, color, 600, MONO)))

    # finishing row
    out.append('<line x1="40" y1="378" x2="920" y2="378" stroke="%s" stroke-width="1"/>' % LINE)
    out.append(text(40, 404, "Finishing", 13, MUTED, 600))
    out.append(node(40, 420, 150, 64, "vow done", ["you or your agent"]))
    out.append(node(230, 420, 200, 64, "Run every check", ["tests · builds · URLs · proof"]))
    out.append(node(470, 398, 240, 64, "All pass", ["Shipped. Streak +1. Unlocked."], GREEN, GREEN))
    out.append(node(470, 476, 240, 64, "Any fail", ["Not done. The lock holds."], RED, RED))
    out += ['<path class="flow" d="%s" marker-end="url(#arrow)"/>' % d for d in
            ["M190,452 L228,452", "M430,452 C450,452 450,430 468,430", "M430,452 C450,452 450,508 468,508"]]
    for i, (color, ey) in enumerate([(GREEN, 430), (RED, 508)]):
        s0 = i * 6 + 0.05
        out.append(token(color, "M190,452 L430,452 C450,452 450,%d 468,%d" % (ey, ey), s0, s0 + 2.6, T))

    # Mori watches the state file
    out.append('<path class="flow" d="M597,318 C700,318 770,330 800,392"/>')
    out.append(mori_at("focused", 768, 388, 1.05))
    out.append(text(831, 562, "Mori reads it every 1.5s", 12, MUTED, anchor="middle"))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d">%s</svg>\n' % (W, H, W, "".join(out))


def story_svg():
    """Five-scene storyboard: vow, wander off, parked, checks, shipped."""
    T, N = 15.0, 5
    W, H = 960, 340
    span = T / N
    out = ['<rect width="%d" height="%d" rx="22" fill="%s"/>' % (W, H, BG)]

    def window(k):  # scene k fades in, holds, fades out
        a, b = k * span, (k + 1) * span
        return kt(0, (a - .01) / T, (a + .35) / T, (b - .35) / T, b / T, 1)

    def at(k, t):  # time t seconds into scene k, as a fraction of the loop
        return (k * span + t) / T

    def term(title, body):
        return ('<rect x="40" y="36" width="600" height="230" rx="14" fill="%s"/>'
                '<circle cx="62" cy="58" r="5" fill="#ff5f57"/><circle cx="80" cy="58" r="5" fill="#febc2e"/><circle cx="98" cy="58" r="5" fill="#28c840"/>'
                '%s%s' % (TERM, text(340, 63, title, 12.5, TERM_MUTED, 500, anchor="middle"), body))

    def typed(k, y, s, color=TERM_TXT, start=.3, dur=1.1, size=14):
        cid = "c%d_%d" % (k, y)
        w = len(s) * size * .62 + 10
        return ('<clipPath id="%s"><rect x="60" y="%s" height="%s" width="0">'
                '<animate attributeName="width" values="0;0;%s;%s" keyTimes="%s" dur="%gs" repeatCount="indefinite"/></rect></clipPath>'
                '<g clip-path="url(#%s)">%s</g>'
                % (cid, f(y - size - 2), f(size + 8), f(w), f(w), kt(0, at(k, start), at(k, start + dur), 1), T, cid,
                   text(62, y, s, size, color, 500, MONO)))

    def appear(k, t, inner, dy=8):
        return ('<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="%s" dur="%gs" repeatCount="indefinite"/>'
                '<animateTransform attributeName="transform" type="translate" values="0 %s;0 %s;0 0;0 0" keyTimes="%s" '
                'calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.3 1;0 0 1 1" dur="%gs" repeatCount="indefinite"/>%s</g>'
                % (kt(0, at(k, t), at(k, t + .35), 1), T, dy, dy, kt(0, at(k, t), at(k, t + .45), 1), T, inner))

    scenes = []
    # 1. take a vow
    scenes.append((term("~/snake-game", typed(0, 108, '$ vow set "Ship snake game" --check "tests::npm test"', size=13.5)
                        + appear(0, 1.5, text(62, 150, "Vow taken. Till deploy do us part.", 15, "#c9b8ff", 600, MONO))
                        + appear(0, 1.9, text(62, 178, "Checks frozen. Agents locked to ~/snake-game.", 13, TERM_MUTED, 400, MONO))),
                   "focused"))
    # 2. wander off, get blocked
    lock = ('<rect x="60" y="138" width="560" height="92" rx="10" fill="#2a1f33" stroke="%s" stroke-width="1.5"/>' % RED
            + text(80, 168, "MONOGAMY LOCK", 15, RED, 700, MONO)
            + text(80, 192, "You're committed to: Ship snake game", 13, TERM_TXT, 400, MONO)
            + text(80, 214, "No one can override this. Not you. Not any AI.", 13, TERM_MUTED, 400, MONO))
    scenes.append((term("~/crypto-bot · Claude Code", typed(1, 108, "> let's build a crypto bot real quick") + appear(1, 1.5, lock, 14)),
                   "angry"))
    # 3. the idea is parked, not lost
    chip = ('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;300 50;300 50" keyTimes="%s" '
            'calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1" dur="%gs" repeatCount="indefinite"/>'
            '<rect x="62" y="96" width="250" height="34" rx="17" fill="#3a2f55"/>%s</g>'
            % (kt(0, at(2, .6), at(2, 1.5), 1), T, text(80, 118, "crypto bot real quick", 13, TERM_TXT, 500, MONO)))
    lot = ('<rect x="350" y="120" width="270" height="120" rx="12" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 5"/>' % TERM_MUTED
           + text(370, 112, "PARKING LOT", 11.5, TERM_MUTED, 700, MONO))
    scenes.append((term("Parking lot", lot + chip + appear(2, 1.8, text(62, 210, "Nothing is lost.", 15, "#c9b8ff", 600, MONO))
                        + appear(2, 2.1, text(62, 234, "It waits until you ship.", 13, TERM_MUTED, 400, MONO))), "focused"))
    # 4. checks pass one by one
    rows = ""
    for i, name in enumerate(["tests pass", "build passes", "live on prod"]):
        t0 = .5 + i * .55
        rows += ('<circle cx="72" cy="%d" r="7" fill="#4d4760"><animate attributeName="fill" values="#4d4760;#4d4760;%s;%s" '
                 'keyTimes="%s" dur="%gs" repeatCount="indefinite"/></circle>'
                 % (104 + i * 34, GREEN, GREEN, kt(0, at(3, t0), at(3, t0 + .15), 1), T)) + text(90, 109 + i * 34, name, 14, TERM_TXT, 500, MONO)
    bar = ('<rect x="62" y="214" width="540" height="8" rx="4" fill="#3a3350"/>'
           '<rect x="62" y="214" height="8" rx="4" fill="%s" width="0"><animate attributeName="width" values="0;0;180;360;540;540" '
           'keyTimes="%s" dur="%gs" repeatCount="indefinite"/></rect>'
           % (GREEN, kt(0, at(3, .5), at(3, .65), at(3, 1.2), at(3, 1.75), 1), T))
    scenes.append((term("vow check", rows + bar + appear(3, 2.0, text(62, 200, "3/3 passing", 13, GREEN, 700, MONO), 4)), "happy"))
    # 5. shipped
    confetti = ""
    for i, (x, color) in enumerate([(120, "#e6c26a"), (210, "#a594f0"), (300, "#5cc995"), (390, "#f07a8e"), (480, "#e6c26a"), (560, "#a594f0")]):
        confetti += ('<rect x="%d" y="80" width="7" height="7" rx="1.5" fill="%s"><animateTransform attributeName="transform" '
                     'type="translate" values="0 0;0 0;%d 160;%d 160" keyTimes="%s" dur="%gs" repeatCount="indefinite"/></rect>'
                     % (x, color, (i % 3 - 1) * 14, (i % 3 - 1) * 14, kt(0, at(4, .2 + i * .1), at(4, 2.4), 1), T))
    scenes.append((term("vow done", confetti + appear(4, .3, text(340, 156, "SHIPPED.", 34, GREEN, 800, MONO, "middle"), 12)
                        + appear(4, .8, text(340, 192, "Streak +1. You're single again.", 15, TERM_TXT, 500, MONO, "middle"))),
                   "happy"))

    for k, (body, mood) in enumerate(scenes):
        out.append('<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="%s" dur="%gs" repeatCount="indefinite"/>%s%s</g>'
                   % (window(k), T, body, mori_at(mood, 700, 34, 1.75)))
    # step pills, the current one lit
    for k, label in enumerate(["Take a vow", "Wander off", "Idea parked", "Checks pass", "Ship it"]):
        x = 40 + k * 178
        lit = '<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="%s" dur="%gs" repeatCount="indefinite"/>' % (window(k), T)
        out.append('<rect x="%d" y="288" width="166" height="32" rx="16" fill="%s" opacity=".12"/>' % (x, ACCENT))
        out.append('<rect x="%d" y="288" width="166" height="32" rx="16" fill="%s" opacity="0">%s</rect>' % (x, ACCENT, lit))
        out.append(text(x + 83, 309, "%d  %s" % (k + 1, label), 12.5, TXT, 600, anchor="middle"))
        out.append('<g opacity="0">%s%s</g>' % (lit, text(x + 83, 309, "%d  %s" % (k + 1, label), 12.5, "#ffffff", 600, anchor="middle")))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d">%s</svg>\n' % (W, H, W, "".join(out))


def main():
    os.makedirs(OUT, exist_ok=True)
    for mood in MOODS:
        with open(os.path.join(OUT, "mori-%s.svg" % mood), "w") as fh:
            fh.write(mood_svg(mood))
    with open(os.path.join(OUT, "mori-shapes.svg"), "w") as fh:
        fh.write(shapes_svg())
    with open(os.path.join(OUT, "flow.svg"), "w") as fh:
        fh.write(flow_svg())
    with open(os.path.join(OUT, "story.svg"), "w") as fh:
        fh.write(story_svg())
    print("wrote", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
