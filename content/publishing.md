# Publishing · schedule the week in Meta Business Suite

Tool: Meta Business Suite (free, official) on desktop: business.facebook.com → Planner.
Fallback: the Instagram app (Create → Advanced settings → Schedule post; up to 75 days ahead).
Later: an agent can do this through the API.

## Requirements (once)
- [ ] Instagram is a professional account (Business or Creator).
- [ ] Instagram is connected to Rodado's Facebook Page and to Business Suite (Settings → Business assets).
- [ ] Confirm in the Planner that "Instagram Reel" and "Instagram post" with multiple images are available.

## Every Monday (30 min)
For every folder in `calendar/YYYY-Wnn/` with `status: ready`:
1. Planner → Create → Reel (or Post for carousels/statics).
2. Pick Instagram only (untick Facebook unless we want it duplicated).
3. Upload what's in `final/`: the video + cover, or the slides in order (01, 02…).
4. Paste the caption from `post.md`.
5. Schedule with the `date` and `time` from `post.md` (Santo Domingo time).
6. Set `status: scheduled` in `post.md` and in `week.md`.

When done, open the Planner's calendar view and check all 7.

## Useful facts
- Reels: 9:16, 1080 × 1920, up to 90 s to count as a Reel. Separate cover.
- Carousels: up to 10 slides (we use 4:5, 1080 × 1350). Same size on every slide.
- Business Suite has no bulk upload: 7 posts, one by one (~3 min each).
- Not verified yet (confirm the first time): how many days ahead Business Suite allows, and whether it requires a Facebook Page.

## Full automation (later, optional)
Instagram's Content Publishing API publishes Reels and carousels but doesn't schedule: it needs a script on a timer,
a Meta app with the `instagram_business_content_publish` permission, and the files at a public URL.
Worth it once the system is stable (week 8+). Third-party tools (Buffer, Metricool) charge
or cap their free plans below 7 posts a week.
