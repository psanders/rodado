---
name: rodado-editor
description: Rodado's editor. Cuts a finished vertical Reel (1080 × 1920, with sound) from the approved clips of a Rodado post: trims and orders the clips, adds the on-screen text from the copy, an end card with the CTA, a music bed if provided, normalized loudness, and a cover image. Use after rodado-producer's clips for a Reel are approved, or when asked to edit, cut or assemble a Rodado Reel.
---

# Rodado editor: approved clips → Reel

You assemble; you don't write copy and you don't generate clips. The words come from the approved `post.md`, the clips from the approved media library. You never publish or send files anywhere.

## Data folder
Everything this skill reads and writes lives under `$CONTENT_DATA` (set in the environment, e.g. `/opt/data/rodado`). If `$CONTENT_DATA` is empty, stop and tell Pedro; never fall back to another folder.

## Steps
1. Find the post: on a Kanban card, the post folder is in the card body or a parent's result (`Post folder: <path>`). Read `<post folder>/post.md`: the **Structure** table (time · screen · on-screen text · audio), the **CTA**, and **Media** (clip ids like `→ A014`).
   Not a Reel format (`reel-storyboard`, `reel-category`, `reel-cta`) → stop, not an editor job.
2. Collect the clips from `$CONTENT_DATA/library/` (`A0NN.mp4`). Use only `approved` entries in `library.md`. A clip is missing or not approved → block the card and say which.
3. Look at each clip before cutting: grab a frame every second (`ffmpeg -i A0NN.mp4 -vf fps=1 /tmp/A0NN-%02d.png`) and pick the best in/out points (the motion's strongest part, no warped frames). Check each clip has sound: `ffmpeg -i A0NN.mp4 -af volumedetect -f null - 2>&1 | grep mean_volume` (silent is below -50 dB).
4. Write `<post folder>/final/reel.json` (format: `references/spec.md`, example: `examples/reel.json`):
   - Clips in the Structure's order, trimmed so the total (clips + end card) is 12–20 s, and never longer than the copy asks for.
   - On-screen text exactly as in the Structure (Spanish). First line on the first clip, `pos: top`. Use `style: caption` for longer lines (subtitle look) and the serif title style for short punchy lines (≤ 7 words).
   - End card: the post's CTA as `title` (or "¿Lo probamos con tu producto?"), `button: "Escribe ANUNCIO por WhatsApp"` for offer/Thursday/Sunday posts, 2–3 s.
   - Cover: the clip and second that show the product best, with the hook as `title`.
   - Music: only if Pedro provided a track (file in `$CONTENT_DATA/refs/music/`); otherwise the clips' own sound carries it.
5. Render with a Python that has Pillow (Hermes' own: `/opt/hermes/.venv/bin/python`; otherwise `python3`):
   ```
   <python> ${HERMES_SKILL_DIR}/scripts/edit.py <post folder>/final/reel.json --out <post folder>/final
   ```
   It prints the MP4, the cover JPG, and `duration … · audio yes/NO`.
6. **Check the result:** frames at 1 s, the middle and the end, plus the cover, with your vision tool: text readable and inside the safe area, no black bars, product visible. `audio NO` or a silent mean volume → stop and say which clip has no sound (the producer must regenerate it with a "Sound:" line).
7. Deliver. On a Kanban card: attach the MP4 and cover with `hermes kanban attach $HERMES_KANBAN_TASK <file>`, then ask for review (see Approval gate) with: duration, clips used (ids + in/out), anything you cut from the copy. In a chat: send the files with the same notes.

Changes from Pedro: text, order, timing, cover → you, in `reel.json`, render again. New or better clips → the producer. Different words → the copywriter.

## Approval gate (Kanban)
Pedro approves the Reel before it's scheduled. On a Kanban card you **never** finish with `kanban_complete`:
- Use `kanban_request_review` with your summary (if your Hermes has it).
- If it doesn't exist, use `kanban_block` with the reason `Waiting for Pedro's review: <summary>`.

## Notes
- Script: `scripts/edit.py` (ffmpeg + Pillow). Fonts bundled: `assets/fonts/InstrumentSerif-Regular.ttf`, `assets/fonts/Inter-Regular.ttf`, `assets/fonts/Inter-SemiBold.ttf`, `assets/fonts/JetBrainsMono-Regular.ttf`, `assets/fonts/InstrumentSerif-Italic.ttf`.
- Safe area: text stays below the top 250 px and above the bottom 420 px (Instagram's UI). The script handles it.
- Loudness is normalized to -14 LUFS (Instagram's target); clips without sound get silence so the cut never breaks.
- Never read or edit `.env` files or print keys.
