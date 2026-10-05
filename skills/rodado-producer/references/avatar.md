# The host (brand avatar)

One recurring character who presents Rodado's ideas on Instagram. She is openly AI: Rodado sells AI-made ads, so the host is proof of craft, not a disguise.

## Rules
- Never presented as a real person. Bio and the first posts say she's Rodado's AI host. On Instagram, turn on the AI label ("AI info") on every post where she appears; the publisher (or Pedro) does this.
- Never resembles a real person, celebrity or client. Never endorses a real brand.
- Only says things Pedro approved (the copywriter's script). No prices or promises beyond the offer facts.
- Always the same face, hair, voice and look: reuse the approved references every time; never regenerate her from text alone.

## Files
`$CONTENT_DATA/avatar/<name>/`:
- `bible.md` — who she is (from `assets/avatar-bible.md`), approved by Pedro.
- `refs/` — approved reference images: `front.png`, `three-quarter.png`, `profile.png`, `full.png`, `smile.png`, `explaining.png` (+ outfit variants).
- `voice/voice.m4a` — approved 6–15 s voice reference (her voice, clean, no music).

## Setup (once, ~US$3–6, three approvals)
1. **Bible.** Fill `assets/avatar-bible.md` from Rodado's audience and voice; send it to Pedro. Approval 1.
2. **Face.** Seedream 5 Pro text-to-image, 4 options (`num_images: 4`, `portrait_4_3`), prompt from the bible's look section: studio portrait, natural skin texture, soft window light, plain warm background, looking at camera. Pedro picks one. Approval 2.
3. **Sheet.** Seedream 5 Pro edit with the chosen face as `image_urls`: one call per view (front, three-quarter, profile, full body standing in the Rodado studio, smiling, mid-sentence gesture). Same outfit, same light. Check every image against the face: same eyes, nose, hairline, skin tone, age. Redo any that drift. Save to `refs/`.
4. **Voice.** Seedance 2.5 reference-to-video, 480p, 8 s, `generate_audio: true`, refs = front + three-quarter, a neutral line from the bible ("Hola, soy … de Rodado. Cada semana te muestro cómo se hace un anuncio que vende."). Pedro listens. Approval 3. Extract the voice: `ffmpeg -i clip.mp4 -vn -ac 1 -ar 44100 voice/voice.m4a`.
Then send Pedro the sheet as one image (a contact sheet) and the clip.

## Using her
- **Still** (cover, quote-media, point-media): Seedream 5 Pro edit, `image_urls` = 2–4 refs (front, three-quarter + the closest pose), prompt = the scene and action. US$0.07.
- **Talking clip** (Reel, carousel cover video): script first (copywriter; Spanish, ≤ 2.5 words per second, 6–15 s). Seedance 2.5 reference-to-video, refs = 3 images + `voice.m4a`, prompt: `@Image1 … says to camera: "<script>". Voice and accent like @Audio1. <setting>, <camera>.` Test at 480p if the shot is new (≈US$1.30 for 10 s), final at 720p (≈US$2.85 for 10 s). Max 2 finals per clip; then ask Pedro.
- **Check** every clip: same face as the refs, lip-sync matches, Spanish pronunciation, no extra words, hands fine. Grab 3 frames + listen (transcribe if you can) before sending.
- Budget: at most one talking clip per week until the analyst shows her posts bring chats.
