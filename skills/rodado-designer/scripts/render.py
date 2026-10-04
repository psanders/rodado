#!/usr/bin/env python3
"""Render Rodado static posts and carousel slides to PNG (1080 x 1350).

Usage:
    python render.py spec.json            # writes PNGs next to the spec, or to spec["out"]
    python render.py spec.json --out DIR

Only needs Pillow (Hermes ships with it). Fonts are bundled in ../assets/fonts.
Spec format: see ../references/spec.md
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96                      # outer margin
SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "assets" / "fonts"

COLORS = {
    "ink": "#16130F", "ink2": "#221E19", "paper": "#F5EFE4", "sand": "#E9E0D1",
    "red": "#E23D2A", "smoke": "#6E665B", "line": "#D8CDBB",
}
THEMES = {
    "ink":   {"bg": COLORS["ink"],   "fg": COLORS["paper"], "muted": "#A89F92", "rule": "#3A342C"},
    "paper": {"bg": COLORS["paper"], "fg": COLORS["ink"],   "muted": COLORS["smoke"], "rule": COLORS["line"]},
}


def font(name, size):
    files = {
        "serif": "InstrumentSerif-Regular.ttf", "serif-italic": "InstrumentSerif-Italic.ttf",
        "sans": "Inter-Regular.ttf", "sans-bold": "Inter-SemiBold.ttf", "mono": "JetBrainsMono-Regular.ttf",
    }
    return ImageFont.truetype(str(FONTS / files[name]), size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap that respects explicit newlines."""
    lines = []
    for para in str(text).split("\n"):
        words, line = para.split(), ""
        for w in words:
            test = (line + " " + w).strip()
            if draw.textlength(test, font=fnt) <= width or not line:
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def fit(draw, text, kind, width, height, start, minimum, leading=1.08):
    """Largest font size (from start down to minimum) whose wrapped text fits the box."""
    size = start
    while size >= minimum:
        fnt = font(kind, size)
        lines = wrap(draw, text, fnt, width)
        if len(lines) * size * leading <= height:
            return fnt, lines, size
        size -= 4
    fnt = font(kind, minimum)
    return fnt, wrap(draw, text, fnt, width), minimum


def block(draw, xy, lines, fnt, size, fill, leading=1.08):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += size * leading
    return y


def wordmark(draw, x, y, t, size=40, anchor_right=True):
    """roda.do with the red dot, in Instrument Serif."""
    f = font("serif", size)
    parts = [("roda", t["fg"]), (".", COLORS["red"]), ("do", t["fg"])]
    total = sum(draw.textlength(p, font=f) for p, _ in parts)
    cx = x - total if anchor_right else x
    for p, c in parts:
        draw.text((cx, y), p, font=f, fill=c)
        cx += draw.textlength(p, font=f)


def frame(draw, t, index=None, total=None):
    """Shared chrome: slide counter (top-left), wordmark (bottom-right), thin rule."""
    if index is not None and total:
        draw.text((M, M - 8), f"{index:02d}/{total:02d}", font=font("mono", 26), fill=t["muted"])
    draw.line([(M, H - M - 40), (W - M, H - M - 40)], fill=t["rule"], width=2)
    wordmark(draw, W - M, H - M - 12, t, size=40)


def slide_quote(draw, s, t):
    inner_w, top, bottom = W - 2 * M, M + 80, H - M - 120
    fnt, lines, size = fit(draw, s["text"], "serif", inner_w, bottom - top - 120, 140, 64, 1.05)
    text_h = len(lines) * size * 1.05
    y = max(top + 56, (top + bottom) / 2 - text_h / 2)          # vertically centered in the text area
    draw.rectangle([M, y - 56, M + 72, y - 50], fill=COLORS["red"])
    block(draw, (M, y), lines, fnt, size, t["fg"], 1.05)
    if s.get("attribution"):
        draw.text((M, bottom - 10), s["attribution"], font=font("mono", 26), fill=t["muted"])


def slide_cover(draw, s, t):
    inner_w = W - 2 * M
    y = M + 120
    if s.get("kicker"):
        draw.text((M, y), s["kicker"].upper(), font=font("mono", 28), fill=COLORS["red"])
        y += 70
    fnt, lines, size = fit(draw, s["title"], "serif", inner_w, 760, 128, 64, 1.04)
    y = block(draw, (M, y), lines, fnt, size, t["fg"], 1.04)
    if s.get("subtitle"):
        y += 30
        f, l, sz = fit(draw, s["subtitle"], "sans", inner_w, 200, 40, 30, 1.3)
        block(draw, (M, y), l, f, sz, t["muted"], 1.3)
    f = font("sans-bold", 30)
    draw.text((M, H - M - 110), "Desliza", font=f, fill=t["fg"])
    ax, ay = M + draw.textlength("Desliza", font=f) + 18, H - M - 92   # arrow drawn by hand (not in the font subset)
    draw.line([(ax, ay), (ax + 36, ay)], fill=COLORS["red"], width=4)
    draw.polygon([(ax + 36, ay - 10), (ax + 50, ay), (ax + 36, ay + 10)], fill=COLORS["red"])


def slide_point(draw, s, t):
    inner_w = W - 2 * M
    y = M + 120
    if s.get("label"):
        draw.text((M, y), s["label"].upper(), font=font("mono", 28), fill=COLORS["red"])
        y += 70
    f, l, sz = fit(draw, s["title"], "serif", inner_w, 420, 96, 56, 1.05)
    y = block(draw, (M, y), l, f, sz, t["fg"], 1.05) + 40
    if s.get("body"):
        f, l, sz = fit(draw, s["body"], "sans", inner_w, H - M - 160 - y, 44, 30, 1.35)
        block(draw, (M, y), l, f, sz, t["muted"] if s.get("muted_body") else t["fg"], 1.35)


def slide_list(draw, s, t):
    inner_w = W - 2 * M
    y = M + 120
    f, l, sz = fit(draw, s["title"], "serif", inner_w, 300, 88, 56, 1.05)
    y = block(draw, (M, y), l, f, sz, t["fg"], 1.05) + 50
    body = font("sans", 40)
    for i, item in enumerate(s.get("items", []), 1):
        draw.text((M, y + 4), f"{i:02d}", font=font("mono", 30), fill=COLORS["red"])
        lines = wrap(draw, item, body, inner_w - 90)
        y = block(draw, (M + 90, y), lines, body, 40, t["fg"], 1.3) + 34


def slide_cta(draw, s, t):
    inner_w = W - 2 * M
    y = M + 160
    f, l, sz = fit(draw, s["title"], "serif", inner_w, 520, 112, 60, 1.04)
    y = block(draw, (M, y), l, f, sz, t["fg"], 1.04) + 60
    if s.get("button"):
        bf = font("sans-bold", 38)
        bw = draw.textlength(s["button"], font=bf) + 80
        draw.rounded_rectangle([M, y, M + bw, y + 96], radius=48, fill=COLORS["red"])
        draw.text((M + 40, y + 26), s["button"], font=bf, fill=COLORS["paper"])
        y += 140
    if s.get("note"):
        f, l, sz = fit(draw, s["note"], "sans", inner_w, 200, 34, 26, 1.35)
        block(draw, (M, y), l, f, sz, t["muted"], 1.35)


KINDS = {"quote": slide_quote, "cover": slide_cover, "point": slide_point, "list": slide_list, "cta": slide_cta}


def render(spec, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    slides = spec["slides"]
    theme = THEMES[spec.get("theme", "ink")]
    name = spec.get("name", "post")
    paths = []
    for i, s in enumerate(slides, 1):
        t = THEMES[s.get("theme", spec.get("theme", "ink"))] if s.get("theme") else theme
        img = Image.new("RGB", (W, H), t["bg"])
        d = ImageDraw.Draw(img)
        KINDS[s["type"]](d, s, t)
        frame(d, t, i if len(slides) > 1 else None, len(slides) if len(slides) > 1 else None)
        fname = f"{name}.png" if len(slides) == 1 else f"{name}-{i:02d}.png"
        p = out_dir / fname
        img.save(p, "PNG", optimize=True)
        paths.append(str(p))
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_path = Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path(spec.get("out", spec_path.parent))
    for p in render(spec, out):
        print(p)
