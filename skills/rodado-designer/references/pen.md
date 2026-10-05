# Pen (pen.dev) for hero pieces

Pen is an AI design agent that builds an editable design file (.pen, opens in Pencil) and exports it. Use it where originality matters most; keep `render.py` for routine slides and every slide with video (Pen can't place video).

## When
- Statics: every other static is a Pen design (alternate with `render.py` layouts; check the design log).
- Carousels: the cover is a Pen design every other week; the other slides stay `render.py` so the set feels like one piece. Match the Pen cover's theme in the spec.
- Never for a slide that holds a clip.
- Cost: one run ≈ US$0.50–2 in model usage (logged from Pen's usage report into the same ledger and cap as the producer).

## How
Needs `PEN_CLI_KEY` and `PEN_AGENT_API_KEY` in the environment (Hermes hides its own `ANTHROPIC_API_KEY` from scripts) and the CLI at `/opt/data/tools/pen` (or `PEN_BIN`).

1. Write `<post folder>/final/pen-brief.md` from the template below. Exact Spanish text, the approved media file names, the layout idea in one or two sentences, and what to avoid (the last 6 designs in the design log).
2. Run:
   ```
   <python> ${HERMES_SKILL_DIR}/scripts/pen_design.py --brief <post folder>/final/pen-brief.md --out <post folder>/final --name <stem> [--media <approved image> ...]
   ```
   It writes `<stem>.pen` and `<stem>.png` (1080 × 1350), and logs the cost. `--dry-run` shows the cost check without running.
3. Look at the PNG like any other slide. One retry with a sharper brief if it misses; after that, use `render.py` and say so.
4. Pedro can open `<stem>.pen` in Pencil to tweak it himself.

## Brief template
```
Design ONE Instagram post frame, exactly 1080 x 1350 px, for Rodado Creativo (roda.do), a Dominican studio that makes AI video ads for Meta.
Put nothing else on the canvas.

Text (Spanish, use exactly, no other text except the wordmark):
- <role>: "<text>"
- …

Images to place (attached): <file> — <what it shows, how to crop>.

Idea: <one or two sentences: the layout concept, e.g. "the quote breaks across the photo, the word 'campaña' in red at the bottom edge">.

Brand system:
- Colors: ink #16130F, paper #F5EFE4, sand #E9E0D1, red #E23D2A (accent only), smoke #6E665B.
- Type: Instrument Serif for headlines (large, tight leading), Inter for body, JetBrains Mono for small labels. Nothing else.
- "roda.do" wordmark, small, bottom-right, Instrument Serif, the dot in red.
- Generous margins (96 px), editorial and premium, lots of air. No gradients except a dark fade behind text on photos. No icons, no emoji, no stock-template look, no drop shadows.
- Keep text 130 px from the top and out of the bottom 120 px.

Avoid repeating: <last designs from the design log>.
```
