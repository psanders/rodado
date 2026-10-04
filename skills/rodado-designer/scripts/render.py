#!/usr/bin/env python3
"""Compose Rodado posts (statics and carousels) from text + media atoms.

Usage:
    python render.py spec.json [--out DIR]

Each slide picks a layout and fills it with atoms: text fields and media files
(images .png/.jpg/.webp, videos .mp4/.mov/.webm). A slide with a video becomes an
MP4 (plus a -poster.png to look at); every other slide becomes a PNG. 1080 x 1350.

Needs Pillow; video slides also need ffmpeg (on PATH, or `pip install imageio-ffmpeg`).
Spec format and layouts: ../references/spec.md
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96
SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "assets" / "fonts"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}

C = {"ink": "#16130F", "paper": "#F5EFE4", "sand": "#E9E0D1", "red": "#E23D2A",
     "smoke": "#6E665B", "line": "#D8CDBB"}
THEMES = {
    "ink":   {"bg": C["ink"],   "fg": C["paper"], "muted": "#A89F92", "rule": "#3A342C", "accent": C["red"], "dark": True},
    "paper": {"bg": C["paper"], "fg": C["ink"],   "muted": C["smoke"], "rule": C["line"], "accent": C["red"], "dark": False},
    "sand":  {"bg": C["sand"],  "fg": C["ink"],   "muted": C["smoke"], "rule": "#CDBFA8", "accent": C["red"], "dark": False},
    "red":   {"bg": C["red"],   "fg": C["paper"], "muted": "#F7C9BF", "rule": "#EE7A6A", "accent": C["ink"], "dark": True},
}
ON_MEDIA = {"bg": C["ink"], "fg": C["paper"], "muted": "#D9D0C3", "rule": "#8A8177", "accent": C["red"], "dark": True}


# ---------- helpers ----------

def font(kind, size):
    files = {"serif": "InstrumentSerif-Regular.ttf", "serif-italic": "InstrumentSerif-Italic.ttf",
             "sans": "Inter-Regular.ttf", "sans-bold": "Inter-SemiBold.ttf", "mono": "JetBrainsMono-Regular.ttf"}
    return ImageFont.truetype(str(FONTS / files[kind]), size)


def rgba(hex_color, a=255):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def wrap(d, text, fnt, width):
    lines = []
    for para in str(text).split("\n"):
        line = ""
        for w in para.split():
            test = (line + " " + w).strip()
            if d.textlength(test, font=fnt) <= width or not line:
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def fit(d, text, kind, width, height, start, minimum, leading):
    size = start
    while size > minimum:
        f = font(kind, size)
        lines = wrap(d, text, f, width)
        if len(lines) * size * leading <= height:
            return f, lines, size
        size -= 4
    f = font(kind, minimum)
    return f, wrap(d, text, f, width), minimum


def block(d, x, y, lines, f, size, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += size * leading
    return y


def block_h(lines, size, leading):
    return len(lines) * size * leading


def highlight_block(d, x, y, lines, f, size, fill, accent, leading, words):
    """Like block(), but words in `words` are drawn in the accent color."""
    marks = {w.strip(".,;:¿?¡!\"'").lower() for w in words}
    space = d.textlength(" ", font=f)
    for ln in lines:
        cx = x
        for w in ln.split(" "):
            col = accent if w.strip(".,;:¿?¡!\"'").lower() in marks else fill
            d.text((cx, y), w, font=f, fill=col)
            cx += d.textlength(w, font=f) + space
        y += size * leading
    return y


def cover_crop(img, w, h, focus=0.5):
    img = img.convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((max(w, round(img.width * s)), max(h, round(img.height * s))), Image.LANCZOS)
    left = int((img.width - w) * 0.5)
    top = int((img.height - h) * focus)
    return img.crop((left, top, left + w, top + h))


def gradient(fg, box, a_top, a_bottom, color=C["ink"]):
    x, y, w, h = box
    g = Image.new("RGBA", (w, h))
    gd = ImageDraw.Draw(g)
    for i in range(h):
        a = int(a_top + (a_bottom - a_top) * (i / max(1, h - 1)))
        gd.line([(0, i), (w, i)], fill=rgba(color, a))
    fg.alpha_composite(g, (x, y))


def chip(d, x, y, text, t, size=26, pad=18, bg=None, fg_col=None):
    f = font("mono", size)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 2 * pad - 6], radius=8,
                        fill=rgba(bg or C["ink"], 215))
    d.text((x + pad, y + pad - 4), text, font=f, fill=fg_col or C["paper"])


def wordmark(d, x_right, y, t, size=40):
    f = font("serif", size)
    parts = [("roda", t["fg"]), (".", C["red"] if t is not THEMES["red"] else C["ink"]), ("do", t["fg"])]
    cx = x_right - sum(d.textlength(p, font=f) for p, _ in parts)
    for p, col in parts:
        d.text((cx, y), p, font=f, fill=col)
        cx += d.textlength(p, font=f)


# ---------- slide canvas ----------

class Slide:
    def __init__(self, t):
        self.t = t                      # theme for text + chrome
        self.bg = Image.new("RGB", (W, H), t["bg"])
        self.fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.fg)
        self.media = []                 # [(path, (x, y, w, h), focus)]
        self.counter_pill = False       # counter sits on top of media

    def place(self, path, box, focus=0.5):
        self.media.append((path, box, focus))
        if path.suffix.lower() not in VIDEO_EXT:
            x, y, w, h = box
            self.bg.paste(cover_crop(Image.open(path), w, h, focus), (x, y))


def chrome(s, index, total):
    t, d = s.t, s.d
    if index is not None and total:
        label = f"{index:02d}/{total:02d}"
        if s.counter_pill:
            chip(d, M - 18, M - 26, label, t, size=24, pad=14)
        else:
            d.text((M, M - 8), label, font=font("mono", 26), fill=t["muted"])
    d.line([(M, H - M - 40), (W - M, H - M - 40)], fill=rgba(t["rule"], 200), width=2)
    wordmark(d, W - M, H - M - 12, t)


# ---------- layouts ----------
# Each takes (slide, spec_slide, media_paths) and draws into slide.fg / places media.

TEXT_TOP, TEXT_BOTTOM = M + 80, H - M - 90     # usable text band above the chrome rule
INNER = W - 2 * M


def L_quote(s, x, med):
    t, d = s.t, s.d
    f, lines, size = fit(d, x["text"], "serif", INNER, TEXT_BOTTOM - TEXT_TOP - 160, 140, 64, 1.05)
    y = max(TEXT_TOP + 56, (TEXT_TOP + TEXT_BOTTOM) / 2 - block_h(lines, size, 1.05) / 2)
    d.rectangle([M, y - 56, M + 72, y - 50], fill=t["accent"])
    block(d, M, y, lines, f, size, t["fg"], 1.05)
    if x.get("attribution"):
        d.text((M, TEXT_BOTTOM - 20), x["attribution"], font=font("mono", 26), fill=t["muted"])


def L_statement(s, x, med):
    """Huge words filling the slide; `highlight` words in the accent color."""
    t, d = s.t, s.d
    f, lines, size = fit(d, x["text"], "serif", INNER, TEXT_BOTTOM - TEXT_TOP - 40, 260, 90, 0.98)
    y = TEXT_BOTTOM - block_h(lines, size, 0.98) - 10       # anchored low, like a poster
    highlight_block(d, M, y, lines, f, size, t["fg"], t["accent"], 0.98, (x.get("highlight") or "").split())
    if x.get("label"):
        d.text((M, TEXT_TOP - 10), x["label"].upper(), font=font("mono", 28), fill=t["accent"])


def L_number(s, x, med):
    t, d = s.t, s.d
    f, lines, size = fit(d, x["number"], "serif", INNER, 520, 420, 160, 0.95)
    nh = block_h(lines, size, 0.95)
    if x.get("text"):
        f2, l2, s2 = fit(d, x["text"], "serif", INNER, 300, 72, 44, 1.08)
        th = 40 + block_h(l2, s2, 1.08)
    else:
        th = 0
    lh = 90 if x.get("label") else 0
    y = TEXT_TOP + max(0, (TEXT_BOTTOM - TEXT_TOP - lh - nh - th) / 2)
    if x.get("label"):
        d.text((M, y), x["label"].upper(), font=font("mono", 28), fill=t["accent"])
        y += lh
    y = block(d, M - 8, y, lines, f, size, t["accent"] if x.get("accent_number", True) else t["fg"], 0.95)
    if x.get("text"):
        block(d, M, y + 40, l2, f2, s2, t["fg"], 1.08)


def full_bleed(s, path, x, strength=1.0):
    s.place(path, (0, 0, W, H), x.get("focus", 0.5))
    gradient(s.fg, (0, int(H * 0.30), W, int(H * 0.70)), 0, int(235 * strength))
    gradient(s.fg, (0, 0, W, 260), int(120 * strength), 0)
    s.t = ON_MEDIA
    s.counter_pill = False


def L_quote_media(s, x, med):
    full_bleed(s, med[0], x)
    t, d = s.t, s.d
    f, lines, size = fit(d, x["text"], "serif", INNER, 520, 118, 60, 1.04)
    y = TEXT_BOTTOM - block_h(lines, size, 1.04) - (50 if x.get("attribution") else 0)
    d.rectangle([M, y - 44, M + 72, y - 38], fill=C["red"])
    block(d, M, y, lines, f, size, t["fg"], 1.04)
    if x.get("attribution"):
        d.text((M, TEXT_BOTTOM - 20), x["attribution"], font=font("mono", 26), fill=t["muted"])


def L_media(s, x, med):
    """The picture or clip is the slide; optional short caption."""
    s.place(med[0], (0, 0, W, H), x.get("focus", 0.5))
    gradient(s.fg, (0, H - 420, W, 420), 0, 210)
    gradient(s.fg, (0, 0, W, 220), 110, 0)
    s.t = ON_MEDIA
    if x.get("caption"):
        f, lines, size = fit(s.d, x["caption"], "sans-bold", INNER, 140, 40, 30, 1.25)
        block(s.d, M, TEXT_BOTTOM - block_h(lines, size, 1.25), lines, f, size, C["paper"], 1.25)
    if x.get("label"):
        chip(s.d, M, TEXT_TOP - 10, x["label"].upper(), s.t, bg=C["red"])


def L_cover(s, x, med):
    t, d = s.t, s.d
    if med:                                     # photo/clip cover: title over the media
        full_bleed(s, med[0], x)
        t, d = s.t, s.d
        f, lines, size = fit(d, x["title"], "serif", INNER, 480, 120, 60, 1.03)
        y = TEXT_BOTTOM - 90 - block_h(lines, size, 1.03) - (80 if x.get("subtitle") else 0)
        if x.get("kicker"):
            chip(d, M, y - 80, x["kicker"].upper(), t, bg=C["red"])
        y = block(d, M, y, lines, f, size, t["fg"], 1.03)
        if x.get("subtitle"):
            f2, l2, s2 = fit(d, x["subtitle"], "sans", INNER, 60, 36, 28, 1.3)
            block(d, M, y + 28, l2, f2, s2, t["muted"], 1.3)
    else:
        y = M + 120
        if x.get("kicker"):
            d.text((M, y), x["kicker"].upper(), font=font("mono", 28), fill=t["accent"])
            y += 70
        f, lines, size = fit(d, x["title"], "serif", INNER, 760, 128, 64, 1.04)
        y = block(d, M, y, lines, f, size, t["fg"], 1.04)
        if x.get("subtitle"):
            f2, l2, s2 = fit(d, x["subtitle"], "sans", INNER, 200, 40, 30, 1.3)
            block(d, M, y + 30, l2, f2, s2, t["muted"], 1.3)
    f = font("sans-bold", 30)
    ay = H - M - 110
    d.text((M, ay), "Desliza", font=f, fill=t["fg"])
    ax = M + d.textlength("Desliza", font=f) + 18
    d.line([(ax, ay + 18), (ax + 36, ay + 18)], fill=C["red"], width=4)
    d.polygon([(ax + 36, ay + 8), (ax + 50, ay + 18), (ax + 36, ay + 28)], fill=C["red"])


def text_stack(s, x, top, bottom, title_start=96, center=True):
    """label + title + body, vertically centered between top and bottom."""
    t, d = s.t, s.d
    f, l, sz = fit(d, x["title"], "serif", INNER, (bottom - top) * 0.45, title_start, 52, 1.05)
    th = block_h(l, sz, 1.05)
    if x.get("body"):
        bf, bl, bs = fit(d, x["body"], "sans", INNER, (bottom - top) - th - 120, 42, 28, 1.35)
        bh = block_h(bl, bs, 1.35) + 36
    else:
        bh = 0
    lh = 70 if x.get("label") else 0
    total = lh + th + bh
    y = top + max(0, ((bottom - top) - total) / 2) if center else top
    if x.get("label"):
        d.text((M, y), x["label"].upper(), font=font("mono", 28), fill=t["accent"])
        y += lh
    y = block(d, M, y, l, f, sz, t["fg"], 1.05)
    if x.get("body"):
        block(d, M, y + 36, bl, bf, bs, t["fg"], 1.35)


def L_point(s, x, med):
    text_stack(s, x, TEXT_TOP + 40, TEXT_BOTTOM - 20)


def L_point_media(s, x, med):
    """Media on top (bleeds to the edges), text underneath."""
    mh = int(x.get("media_height", 660))
    s.place(med[0], (0, 0, W, mh), x.get("focus", 0.5))
    gradient(s.fg, (0, 0, W, 180), 90, 0)
    s.counter_pill = True
    text_stack(s, x, mh + 56, TEXT_BOTTOM - 10, title_start=80, center=False)


def L_compare(s, x, med):
    """Two pictures/clips stacked, each with a label: before/after, A/B."""
    t, d = s.t, s.d
    top = TEXT_TOP
    if x.get("title"):
        f, l, sz = fit(d, x["title"], "serif", INNER, 150, 72, 44, 1.05)
        top = block(d, M, TEXT_TOP, l, f, sz, t["fg"], 1.05) + 30
    gap = 20
    bh = int((TEXT_BOTTOM - 10 - top - gap) / 2)
    labels = x.get("labels", ["Antes", "Después"])
    for i, p in enumerate(med[:2]):
        by = int(top + i * (bh + gap))
        s.place(p, (M, by, INNER, bh), x.get("focus", 0.5))
        if i < len(labels):
            chip(d, M + 20, by + 20, labels[i].upper(), t, bg=C["red"] if i else C["ink"])


def L_list(s, x, med):
    t, d = s.t, s.d
    items = x.get("items", [])
    f, l, sz = fit(d, x["title"], "serif", INNER, 260, 88, 52, 1.05)
    body = font("sans", 40)
    wrapped = [wrap(d, it, body, INNER - 90) for it in items]
    total = block_h(l, sz, 1.05) + 50 + sum(len(w) * 52 + 34 for w in wrapped)
    y = TEXT_TOP + max(20, (TEXT_BOTTOM - TEXT_TOP - total) / 2)
    y = block(d, M, y, l, f, sz, t["fg"], 1.05) + 50
    for i, lines in enumerate(wrapped, 1):
        d.text((M, y + 4), f"{i:02d}", font=font("mono", 30), fill=t["accent"])
        y = block(d, M + 90, y, lines, body, 40, t["fg"], 1.3) + 34


def L_cta(s, x, med):
    if med:
        full_bleed(s, med[0], x, strength=1.15)
    t, d = s.t, s.d
    f, l, sz = fit(d, x["title"], "serif", INNER, 480, 112, 60, 1.04)
    bh = 96 + 44 if x.get("button") else 0
    nf = font("sans", 32)
    nl = wrap(d, x["note"], nf, INNER) if x.get("note") else []
    total = block_h(l, sz, 1.04) + 60 + bh + len(nl) * 44
    y = (TEXT_BOTTOM - total - 20) if med else TEXT_TOP + max(40, (TEXT_BOTTOM - TEXT_TOP - total) / 2)
    y = block(d, M, y, l, f, sz, t["fg"], 1.04) + 60
    if x.get("button"):
        bf = font("sans-bold", 38)
        bw = d.textlength(x["button"], font=bf) + 80
        btn = C["ink"] if s.t is THEMES["red"] else C["red"]
        d.rounded_rectangle([M, y, M + bw, y + 96], radius=48, fill=btn)
        d.text((M + 40, y + 26), x["button"], font=bf, fill=C["paper"])
        y += bh
    if nl:
        block(d, M, y, nl, nf, 32, t["muted"], 1.375)


LAYOUTS = {
    "quote": (L_quote, 0), "statement": (L_statement, 0), "number": (L_number, 0),
    "quote-media": (L_quote_media, 1), "media": (L_media, 1),
    "cover": (L_cover, 0), "point": (L_point, 0), "point-media": (L_point_media, 1),
    "compare": (L_compare, 2), "list": (L_list, 0), "cta": (L_cta, 0),
}


# ---------- video ----------

def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("Video slides need ffmpeg: install it, or `pip install imageio-ffmpeg` into this Python.")


def probe_duration(ff, path):
    out = subprocess.run([ff, "-i", str(path)], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    return 6.0


def frame_of(ff, path, at, tmp):
    out = Path(tmp) / f"frame-{abs(hash((str(path), at)))}.png"
    subprocess.run([ff, "-y", "-loglevel", "error", "-ss", str(at), "-i", str(path), "-frames:v", "1", str(out)], check=True)
    return out


def write_video(s, out_mp4, poster_png, max_seconds, tmp):
    ff = ffmpeg_bin()
    vids = [(p, b, f) for p, b, f in s.media if p.suffix.lower() in VIDEO_EXT]
    dur = min(max_seconds, min(probe_duration(ff, p) for p, _, _ in vids))
    bg_path, fg_path = Path(tmp) / "bg.png", Path(tmp) / "fg.png"
    s.bg.save(bg_path)
    s.fg.save(fg_path)
    cmd = [ff, "-y", "-loglevel", "error", "-loop", "1", "-i", str(bg_path)]
    for p, _, _ in vids:
        cmd += ["-i", str(p)]
    cmd += ["-loop", "1", "-i", str(fg_path)]
    chains, last = [], "0:v"
    for i, (p, (x, y, w, h), focus) in enumerate(vids, 1):
        chains.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                      f"crop={w}:{h}:(in_w-{w})/2:(in_h-{h})*{focus},setsar=1,fps=30[v{i}]")
        chains.append(f"[{last}][v{i}]overlay={x}:{y}[b{i}]")
        last = f"b{i}"
    chains.append(f"[{last}][{len(vids) + 1}:v]overlay=0:0,format=yuv420p[out]")
    cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-t", f"{dur:.2f}", "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-an", "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)
    poster = s.bg.copy()
    for p, (x, y, w, h), focus in vids:
        poster.paste(cover_crop(Image.open(frame_of(ff, p, min(1.0, dur / 2), tmp)), w, h, focus), (x, y))
    poster = poster.convert("RGBA")
    poster.alpha_composite(s.fg)
    poster.convert("RGB").save(poster_png, optimize=True)


# ---------- main ----------

def render(spec, out_dir, base):
    out_dir.mkdir(parents=True, exist_ok=True)
    slides = spec["slides"]
    n = len(slides)
    name = spec.get("name", "post")
    paths = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, x in enumerate(slides, 1):
            layout = x.get("layout") or x.get("type")
            if layout not in LAYOUTS:
                sys.exit(f"slide {i}: unknown layout '{layout}'. Use one of: {', '.join(LAYOUTS)}")
            fn, need = LAYOUTS[layout]
            med = x.get("media") or []
            med = [med] if isinstance(med, str) else med
            med = [(base / m).resolve() for m in med]
            for m in med:
                if not m.exists():
                    sys.exit(f"slide {i}: media not found: {m}")
            if len(med) < need:
                sys.exit(f"slide {i}: layout '{layout}' needs {need} media file(s)")
            s = Slide(THEMES[x.get("theme", spec.get("theme", "ink"))])
            fn(s, x, med)
            chrome(s, i if n > 1 else None, n if n > 1 else None)
            stem = name if n == 1 else f"{name}-{i:02d}"
            if any(p.suffix.lower() in VIDEO_EXT for p, _, _ in s.media):
                mp4, poster = out_dir / f"{stem}.mp4", out_dir / f"{stem}-poster.png"
                write_video(s, mp4, poster, float(x.get("max_seconds", spec.get("max_seconds", 12))), tmp)
                paths += [str(mp4), str(poster)]
            else:
                img = s.bg.convert("RGBA")
                img.alpha_composite(s.fg)
                p = out_dir / f"{stem}.png"
                img.convert("RGB").save(p, optimize=True)
                paths.append(str(p))
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_path = Path(sys.argv[1]).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else spec_path.parent
    for p in render(spec, out, spec_path.parent):
        print(p)
