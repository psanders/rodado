# Prompting for Rodado

## The look (every prompt)
Premium product advertising, shot like a real commercial: one hero product, natural warm Caribbean light (morning sun or golden hour), shallow depth of field, rich real textures (wood, stone, linen, ceramic, condensation, steam), clean uncluttered set, colors that sit well next to ink #16130F, cream #F5EFE4 and brand red #E23D2A. Photographic, not illustrated, not "AI glossy".
Always add: no text, no letters, no logos, no watermark.

Write prompts in English, in this order: subject → action/moment → setting → light → camera → mood. 40–90 words. Concrete beats adjectives ("a ceramic cup of black coffee with a thin ring of crema" not "delicious coffee").

## Framing (by where it goes)
| Placement | Aspect | Notes |
| --- | --- | --- |
| Full-bleed slide (`cover`, `media`, `quote-media`, `cta`) | 3:4 (cropped to 4:5) | Product in the upper-middle; the bottom third calm and darker: text goes there |
| Top of a `point-media` slide | 16:9 or 3:2 | Product centered, room left and right |
| One half of a `compare` | 16:9 | Same framing for both halves |
| Reel shot (editor, later) | 9:16 | Product centered; keep 130 px top and 320 px bottom calm |

## Clips (Seedance 2.5)
- Animate an approved still when you can (`image-to-video`): the prompt then describes only motion and camera ("slow push-in, steam rising, a drop of condensation runs down the bottle").
- Several angles of the same product, or the avatar → `reference-to-video` and name the refs in the prompt (`@Image1`, `@Image2`).
- One motion per clip. Slow, smooth, commercial: push-in, orbit, pour, splash, reveal, light sweep. No cuts unless asked.
- Clips for carousels and statics: 4–6 s, `generate_audio: false` (they play muted in the feed).
- Clips for Reels: `generate_audio: true`, always. Seedance makes the sound with the picture at no extra cost, so write it into the prompt as its own sentence: what we hear, in order. Example: "Sound: waves and wind, the crunch of a chip at 0:03, a light upbeat Caribbean guitar groove underneath, no voice." Speech only for the host or when the copy has an exact line. No copyrighted songs, no famous-artist styles.
- After a Reel clip, check the audio too: extract it (`ffmpeg -i A0NN.mp4 -vn /tmp/a.wav`) and confirm it isn't silent (`ffmpeg -i /tmp/a.wav -af volumedetect -f null - 2>&1 | grep mean_volume`, should be above -40 dB). Silent → regenerate once with a stronger "Sound:" line.

## Images (Seedream 5)
- Same product in a new scene → `edit` with the product photo(s) as `image_urls`, prompt: "The product from @Image1 on …". Keep label, shape and color exact.
- Before/after: make the "before" a deliberately plain phone photo (flat light, cluttered counter), the "after" a styled scene, same product refs for both.

## Costs
See `references/models.md`.
