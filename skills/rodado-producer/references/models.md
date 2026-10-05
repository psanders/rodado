# Models (fal.ai, prices Oct 2026 — verify on fal.ai/pricing if a run looks off)

Run every model through `scripts/fal.py` (budget check + ledger). Hermes' built-in `image_generate` / `video_generate` don't count against the cap: don't use them for Rodado.

## Seedream 5.0 — images
| Endpoint | Use | Price |
| --- | --- | --- |
| `bytedance/seedream/v5/pro/text-to-image` | New image from a prompt | ~US$0.07 / image |
| `bytedance/seedream/v5/pro/edit` | Image from 1–10 reference images + prompt: same product, same avatar, new scene; restyle a client photo | ~US$0.07 / image |
| `fal-ai/bytedance/seedream/v5/lite/text-to-image`, `…/lite/edit` | Cheap explorations, options before the final | ~US$0.035 / image |

Input (both):
```json
{"prompt": "…", "image_urls": ["@/path/ref1.png", "https://…/ref2.jpg"],
 "image_size": "portrait_4_3", "num_images": 2, "output_format": "png"}
```
`image_urls` only for `edit` (max 10). `image_size`: `portrait_4_3` (slides, 3:4 crop to 4:5), `portrait_16_9` (9:16 Reels), `landscape_16_9`, `square_hd`, or `{"width": 1536, "height": 2048}`.
Seedream renders text well, but Rodado's type is set by the designer: keep "no text" in prompts unless the text is part of the scene (a label on the invented product).

## Seedance 2.5 — video
| Endpoint | Use | Price per output second |
| --- | --- | --- |
| `bytedance/seedance-2.5/image-to-video` | Animate one approved still (product shots) | 480p ~US$0.22 · 720p ~US$0.47 |
| `bytedance/seedance-2.5/reference-to-video` | Video from reference images/clips/audio: the avatar, a product from several angles, a voice | 480p ~US$0.13 · 720p ~US$0.28 |
| `bytedance/seedance-2.5/text-to-video` | Pure prompt (avoid: least control) | 480p ~US$0.22 · 720p ~US$0.47 |
| `bytedance/seedance-2.5/draft/complete` | Finish an approved draft to 1080p (`{"draft_id": "…"}`) | ~US$1.16 (1080p) |

Reference-to-video input:
```json
{"prompt": "@Image1 sits at her desk and says to camera: \"…\" Voice like @Audio1.",
 "image_urls": ["@ref-front.png", "@ref-34.png"], "audio_urls": ["@voice.m4a"],
 "resolution": "720p", "duration": 10, "aspect_ratio": "9:16", "generate_audio": true}
```
Refer to inputs in the prompt as `@Image1…`, `@Video1…`, `@Audio1…` (up to 30 images, 10 clips, 10 audio files; clips/audio 2–30 s).
Image-to-video takes `image_url` (one image). Duration 4–30 s: **always set it** (the script refuses `auto`).
`"draft": true` returns a cheap preview plus `draft_id`; completing it renders 1080p (~US$1.16/s), so use drafts only when the final must be 1080p. Otherwise: test at 480p, final at 720p.
`generate_audio`: true for the avatar (speech, lip-sync); false for product clips (the editor adds music).

## Cost rules of thumb
| Piece | Approx. |
| --- | --- |
| 2 product image options (Seedream Pro) | US$0.14 |
| 5 s product clip, 720p, from a still | US$2.40 |
| 5 s product clip, 480p test | US$1.10 |
| 10 s avatar talking, 720p, references | US$2.85 |
| 15 s avatar talking, 720p, references | US$4.25 |
| Avatar setup (one time) | US$3–6 |
