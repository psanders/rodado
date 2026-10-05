#!/usr/bin/env python3
"""Cut a vertical Reel (1080 x 1920) from approved clips, with on-screen text, an end card,
continuous sound and a cover image.

Usage:
    python edit.py reel.json [--out DIR]

Spec (paths relative to the spec file):
{
  "name": "2026-10-14-reel-category-snack",
  "clips": [
    {"file": "A008.mp4", "in": 0, "out": 4.5, "text": "Así venderíamos un snack dominicano", "pos": "top"},
    {"file": "A009.mp4", "in": 0.5, "out": 5, "text": "en 15 segundos.", "pos": "bottom", "style": "caption"}
  ],
  "end_card": {"title": "¿Lo probamos con tu producto?", "button": "Escribe ANUNCIO por WhatsApp", "seconds": 2.5, "theme": "ink"},
  "music": "optional/path/to/bed.mp3",      # optional bed under everything, ducked
  "music_volume": 0.25,
  "cover": {"clip": 0, "at": 1.0, "title": "Así venderíamos un snack dominicano"}
}
Writes <name>.mp4 (H.264 + AAC, 30 fps, loudness -14 LUFS) and <name>-cover.jpg, and prints both paths.
Needs ffmpeg/ffprobe (or `pip install imageio-ffmpeg`) and Pillow. Fonts in ../assets/fonts.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 250, 420           # Instagram UI covers the top ~220 px and bottom ~400 px
M = 90
FPS = 30
SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL / "assets" / "fonts"
C = {"ink": "#16130F", "paper": "#F5EFE4", "red": "#E23D2A", "sand": "#E9E0D1"}


def die(msg):
    raise SystemExit(msg)


def ff():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        die("ffmpeg not found: install it or `pip install imageio-ffmpeg`.")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffmpeg failed:\n" + r.stderr[-1500:])
    return r


def probe(path):
    """(duration, has_audio) without ffprobe (works with imageio-ffmpeg too)."""
    err = subprocess.run([ff(), "-i", str(path)], capture_output=True, text=True).stderr
    dur = 0.0
    for line in err.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
    return dur, "Audio:" in err


def font(kind, size):
    files = {"serif": "InstrumentSerif-Regular.ttf", "sans": "Inter-Regular.ttf",
             "sans-bold": "Inter-SemiBold.ttf", "mono": "JetBrainsMono-Regular.ttf"}
    return ImageFont.truetype(str(FONTS / files[kind]), size)


def wrap(d, text, f, width):
    lines, line = [], ""
    for w in str(text).split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= width or not line:
            line = t
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines


def fit(d, text, kind, width, max_lines, start, minimum):
    s = start
    while s >= minimum:
        f = font(kind, s)
        ls = wrap(d, text, f, width)
        if len(ls) <= max_lines:
            return f, ls, s
        s -= 4
    f = font(kind, minimum)
    return f, wrap(d, text, f, width), minimum


def text_overlay(text, pos="top", style="title"):
    """Transparent 1080x1920 PNG with the line placed inside the safe zone."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not text:
        return img
    d = ImageDraw.Draw(img)
    if style == "caption":                                   # Inter on a dark pill, like subtitles
        f, lines, size = fit(d, text, "sans-bold", W - 2 * M - 60, 3, 54, 38)
        lh = size * 1.3
        bh = len(lines) * lh + 44
        y = {"top": SAFE_TOP + 40, "center": (H - bh) / 2, "bottom": H - SAFE_BOTTOM - bh}[pos]
        bw = max(d.textlength(l, font=f) for l in lines) + 60
        x = (W - bw) / 2
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=26, fill=(22, 19, 15, 200))
        ty = y + 22
        for l in lines:
            d.text(((W - d.textlength(l, font=f)) / 2, ty), l, font=f, fill=C["paper"])
            ty += lh
        return img
    f, lines, size = fit(d, text, "serif", W - 2 * M, 4, 104, 64)    # serif title with a soft shadow
    lh = size * 1.04
    th = len(lines) * lh
    y = {"top": SAFE_TOP + 20, "center": (H - th) / 2, "bottom": H - SAFE_BOTTOM - th}[pos]
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))            # soft dark band so text reads on any shot
    bd = ImageDraw.Draw(band)
    top, bot = int(y - 140), int(y + th + 140)
    for yy in range(max(0, top), min(H, bot)):
        k = 1 - abs((yy - (top + bot) / 2) / ((bot - top) / 2))
        bd.line([(0, yy), (W, yy)], fill=(15, 12, 10, int(150 * min(1, k * 1.6))))
    img.alpha_composite(band)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    ty = y
    for l in lines:
        sd.text((M, ty + 3), l, font=f, fill=(0, 0, 0, 170))
        ty += lh
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    ty = y
    for l in lines:
        d.text((M, ty), l, font=f, fill=C["paper"])
        ty += lh
    return img


def end_card(spec, path):
    t = spec.get("theme", "ink")
    bg, fg = (C["ink"], C["paper"]) if t == "ink" else (C["paper"], C["ink"])
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    f, lines, size = fit(d, spec.get("title", ""), "serif", W - 2 * M, 4, 120, 70)
    y = H * 0.36
    for l in lines:
        d.text((M, y), l, font=f, fill=fg)
        y += size * 1.04
    y += 60
    if spec.get("button"):
        bf = font("sans-bold", 44)
        bw = d.textlength(spec["button"], font=bf) + 90
        d.rounded_rectangle([M, y, M + bw, y + 110], radius=55, fill=C["red"])
        d.text((M + 45, y + 30), spec["button"], font=bf, fill=C["paper"])
        y += 150
    if spec.get("note"):
        d.text((M, y), spec["note"], font=font("sans", 34), fill=fg)
    wf = font("serif", 52)                                   # roda.do wordmark, red dot
    parts = [("roda", fg), (".", C["red"]), ("do", fg)]
    x = W - M - sum(d.textlength(p, font=wf) for p, _ in parts)
    for p, col in parts:
        d.text((x, H - SAFE_BOTTOM - 10), p, font=wf, fill=col)
        x += d.textlength(p, font=wf)
    img.save(path)


def render(spec, out_dir, base):
    out_dir.mkdir(parents=True, exist_ok=True)
    name = spec.get("name", "reel")
    clips = spec.get("clips") or die("No clips in the spec.")
    tmp = Path(tempfile.mkdtemp())
    segs = []
    for i, c in enumerate(clips):
        src = (base / c["file"]).resolve()
        if not src.exists():
            die(f"Clip not found: {src}")
        dur, has_audio = probe(src)
        a = float(c.get("in", 0))
        b = min(float(c.get("out", dur)), dur)
        if b - a < 0.5:
            die(f"Clip {i + 1} is too short after trimming ({b - a:.2f} s).")
        ov = tmp / f"t{i}.png"
        text_overlay(c.get("text", ""), c.get("pos", "top"), c.get("style", "title")).save(ov)
        seg = tmp / f"s{i}.mp4"
        audio_in = ["-i", str(src)] if has_audio and c.get("audio", True) else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        aidx = "0:a" if has_audio and c.get("audio", True) else "2:a"
        cmd = [ff(), "-y", "-loglevel", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", str(src), "-i", str(ov)]
        if aidx == "2:a":
            cmd += audio_in
        fade = min(0.08, (b - a) / 4)
        cmd += ["-filter_complex",
                f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}[v];"
                f"[v][1:v]overlay=0:0,format=yuv420p[vo];"
                f"[{aidx}]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{b - a},"
                f"afade=t=in:d={fade},afade=t=out:st={max(0, b - a - fade)}:d={fade}[ao]",
                "-map", "[vo]", "-map", "[ao]", "-t", f"{b - a}", "-c:v", "libx264", "-preset", "medium",
                "-crf", "19", "-c:a", "aac", "-b:a", "192k", str(seg)]
        run(cmd)
        segs.append(seg)
    if spec.get("end_card"):
        ec = spec["end_card"]
        png = tmp / "end.png"
        end_card(ec, png)
        sec = float(ec.get("seconds", 2.5))
        seg = tmp / "end.mp4"
        run([ff(), "-y", "-loglevel", "error", "-loop", "1", "-t", f"{sec}", "-i", str(png),
             "-f", "lavfi", "-t", f"{sec}", "-i", "anullsrc=r=48000:cl=stereo",
             "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-c:a", "aac", "-b:a", "192k", "-shortest", str(seg)])
        segs.append(seg)
    joined = tmp / "joined.mp4"
    n = len(segs)
    inputs = sum((["-i", str(s)] for s in segs), [])
    run([ff(), "-y", "-loglevel", "error", *inputs, "-filter_complex",
         "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", str(joined)])
    final = out_dir / f"{name}.mp4"
    total, _ = probe(joined)
    if spec.get("music"):
        music = (base / spec["music"]).resolve()
        vol = float(spec.get("music_volume", 0.25))
        af = (f"[1:a]volume={vol},atrim=0:{total},afade=t=out:st={max(0, total - 1.5)}:d=1.5[m];"
              f"[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        run([ff(), "-y", "-loglevel", "error", "-i", str(joined), "-stream_loop", "-1", "-i", str(music),
             "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", str(final)])
    else:
        run([ff(), "-y", "-loglevel", "error", "-i", str(joined), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)])
    cv = spec.get("cover", {"clip": 0, "at": 1.0})
    ci = int(cv.get("clip", 0))
    csrc = (base / clips[ci]["file"]).resolve()
    frame = tmp / "cover-frame.png"
    run([ff(), "-y", "-loglevel", "error", "-ss", f"{float(clips[ci].get('in', 0)) + float(cv.get('at', 1.0))}",
         "-i", str(csrc), "-frames:v", "1", "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
         str(frame)])
    cover = Image.open(frame).convert("RGBA")
    if cv.get("title"):                                      # keep the title inside the 3:4 grid crop
        cover.alpha_composite(text_overlay(cv["title"], "center", "title"))
    cpath = out_dir / f"{name}-cover.jpg"
    cover.convert("RGB").save(cpath, "JPEG", quality=92)
    shutil.rmtree(tmp, ignore_errors=True)
    secs, has_a = probe(final)
    print(final)
    print(cpath)
    print(f"duration {secs:.1f} s · audio {'yes' if has_a else 'NO'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sp = Path(sys.argv[1]).resolve()
    spec = json.loads(sp.read_text(encoding="utf-8"))
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else sp.parent
    render(spec, out, sp.parent)
