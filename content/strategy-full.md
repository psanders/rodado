# Rodado Content System

Full content strategy, imported from the Claude doc "Rodado Content System" (Oct 4, 2026):
https://claude.ai/code/artifact/d521395d-a38f-4ad9-a5df-24cf73b393bf
`strategy.md` is the short operational version in Spanish. If they disagree, the doc wins; update both.

## Audience

We talk directly to the marketing managers of mid-size Dominican brands that spend US$800–5,000 a month on marketing. Content is in Spanish, for @rodado.creativo on Instagram. Agencies that find us on their own are welcome, but we don't create content for them.

| | |
| --- | --- |
| Who | Marketing manager or head of marketing at a DR product brand, reporting to a GM or owner |
| Budget | US$800–5,000 a month on marketing overall (media spend, materials, other efforts). Below that is not our customer; above it usually has an agency |
| Their brands | Food and drinks, beauty and personal care, retail chains and consumer products, sold in supermarkets, stores or online |
| How to spot them | 5+ active ads in the Meta Ad Library, a marketing role on LinkedIn, products in chains like Sirena, Nacional or Bravo |
| Their pain | They need new creatives every month, shoots take weeks to coordinate, and ads fatigue before the next shoot is ready |
| What they are judged on | Sales and ROAS from Meta, delivered on time, on brand, without surprises for their boss |
| What they must believe | 1. The ads look premium and show the real product. 2. Rodado delivers on time, every time. 3. Their boss will approve it. |
| Main objections | "AI looks cheap or fake", "my GM won't approve AI", "US$299 seems too cheap to be good" |

## End goal

The one number that matters: qualified WhatsApp conversations, meaning a brand in our budget range talking to us about an ad. The US$299 ad is the entry; the real win is a brand that orders every month.

| Horizon | Target | Why this number |
| --- | --- | --- |
| Weeks 1–4 | 5 qualified conversations | Proves the content reaches the right people |
| Weeks 5–8 | 12 conversations, 3 first orders | Proves conversations convert at US$299 |
| Weeks 9–12 | 20 conversations, 6 orders, 2 brands ordering every month | Proves the entry ad turns into recurring work |

These targets are a first guess from a zero baseline. Reset them at the end of week 4 using real numbers.

**Qualified** means: a brand (not a solo seller), already running Meta ads, and a monthly marketing budget of US$800 or more. Ask about budget in the first WhatsApp reply.

**Leading indicators**, in funnel order: reach among non-followers, saves and shares, profile visits, new followers who are brands or marketing people, link taps to WhatsApp, conversations.

**Attribution**: the bio link opens WhatsApp with the prefilled text "Hola, vengo de Instagram y quiero un anuncio para mi marca". Post CTAs ask people to write the keyword ANUNCIO. Any chat with either one counts.

## Pillars

Four pillars, each answering one of the beliefs a marketing manager needs before writing to us. Goal on top: qualified brand conversations that become monthly orders.

| Pillar | Answers | What it is | Slot |
| --- | --- | --- | --- |
| Proof | "Does it look premium?" | Storyboard to final ad, real products, 3 cuts per story | Mon + Fri |
| Creative strategy | "Do they understand Meta?" | Meta ideas managers save: hooks, cuts, ad fatigue | Tue |
| Category ideas | "Could this work for my product?" | How we would sell coffee, rum, beauty, snacks in 30 s, always with invented brands like Guaraguao | Wed |
| Trust | "Will my boss approve it?" | Process, deadlines, guarantee, AI myths | Thu |

Saturday's one-liner rotates pillars. Sunday's post asks for the WhatsApp chat. Never use a real brand without permission.

## Formats

Five formats only, each built from assets already made for clients.

| Format | What it is | Best for pillar | Effort |
| --- | --- | --- | --- |
| Reel: storyboard to ad | Split screen: the storyboard scene, then the finished shot, 15–30 s | Proof | Low: reuse project files |
| Reel: category concept | A short ad for an invented brand in a DR category | Category ideas | Medium |
| Carousel: framework | 6–8 slides teaching one Meta creative idea, last slide = CTA | Creative strategy, Trust | Medium |
| Carousel: FAQ | One real question a manager asks (AI, approvals, deadlines) answered plainly | Trust | Low |
| Static: one-liner | One strong opinion on a branded card, for shares and comments | Any | Low |

Add a sixth format (talking-head Reel or client testimonial) only after week 4 if the data says the audience wants a face.

## Weekly cadence

Seven posts a week, one per day, fixed rhythm: 4 Reels, 2 carousels, 1 static. Slots stay the same every week so results compare cleanly.

| Day | Format | Pillar | Job of the post |
| --- | --- | --- | --- |
| Monday | Reel: storyboard to ad | Proof | Show the work |
| Tuesday | Carousel: framework | Creative strategy | Earn saves from marketing managers |
| Wednesday | Reel: category concept | Category ideas | Make a manager picture their own product |
| Thursday | Carousel: FAQ or framework | Trust | Remove the "will my boss approve it?" doubt |
| Friday | Reel: storyboard to ad | Proof | Show a different category |
| Saturday | Static: one-liner | Any | Spark comments and shares |
| Sunday | Reel: best cut + direct CTA | Offer | Ask for the WhatsApp chat |

Post at 12:00 or 19:00 Santo Domingo time; test which wins in weeks 1–2, then keep it. Managers browse during work hours, so 12:00 is the first bet.

**Outbound alongside content**: mid-size DR brands are a list of perhaps 100–300 names, so content alone grows slowly. Pedro sends 10+ direct messages a day to managers on the target list, using the week's posts as proof and the free 2-direction storyboard as the door-opener. Agents research and draft; Pedro sends.

## Idea system

Ideas are never made up on the day. Hermes runs this with the skill `rodado-strategist`:

1. **Idea pitch (Mon, Wed, Fri 9:00, WhatsApp):** Hermes pitches one idea at a time; Pedro answers sí / no / a tweak, until 3 are approved. Each pitch says what the post looks like, where the idea came from, why it works, why it fits Rodado, and its format and slot.
2. **Bank:** approved ideas go to the idea bank in Hermes (`$CONTENT_DATA/ideas/bank.md`). Every pitch and every "no" is logged so nothing is pitched twice.
3. **Sunday plan (17:00, WhatsApp):** Hermes picks next week's 7 from the bank, one per slot. Pedro approves; Hermes creates a copywriter card per post (`rodado-copywriter`), ending in Review; carousels and statics also get a designer card (`rodado-designer`) that starts once the copy is approved.
4. **Inbox:** anything Pedro sends Hermes (an idea, a link, a screenshot, a client's question) is saved and pitched first.

Sources, rotated by weekday: inbox, ad watch (Meta Ad Library), DR calendar, manager questions, Meta changes, category scan, production notes, objections, craft and format, our own results. Details in `skills/rodado-strategist/references/sources.md`.

`content/ideas/bank.csv` is the W41 history; the live bank is in Hermes.

## Measurement

Five numbers per post and one per week. Change one thing at a time.

| Metric | Where | What it tells us |
| --- | --- | --- |
| Reach from non-followers | Instagram Insights, per post | Whether the hook travels |
| Average watch time (Reels) | Insights, per Reel | Whether the first 2 seconds hold |
| Saves + shares | Insights, per post | Whether managers find it useful |
| Profile visits | Insights, per post | Whether it creates curiosity about Rodado |
| Qualified WhatsApp chats | WhatsApp, prefilled text or ANUNCIO, budget confirmed | The goal |

Rank posts by qualified chats first, then saves + shares.

**90-day loop**

1. Weeks 1–4, explore: keep the pillar mix and cadence fixed. Only test posting time and hook styles.
2. Weeks 5–8, double down: shift 2 of the 7 slots to the best pillar × format. Drop the weakest format.
3. Weeks 9–12, expand: add one channel (LinkedIn first, then a talking-head Reel or Stories) and measure it against the baseline.

**Decision rule**: a format stays if it beats the account median on saves + shares or produces a WhatsApp chat within 4 weeks. Otherwise it is replaced.

## Decisions (Oct 4, 2026)

| Topic | Decision |
| --- | --- |
| Price | Keep US$299. The US$800–5,000 covers their whole marketing; Rodado is one line in that budget. |
| Monthly offer | Not now. Define it once demand shows up; keep the offer simple until then. |
| Outbound | Pedro sends 10+ direct messages a day to managers on the target list. |
| Client work | Cacao Mae and Cera work can be shown, with their logos replaced by invented look-alike logos. |
| Volume | 7 posts a week. If a week slips, drop Saturday first. Never drop Sunday. |
| Website | Update the "Ideal para" list later. |
| Publishing | Meta Business Suite for now; API publishing later via `rodado-publisher`. |

## Automation (agents)

Recurring jobs are written as skills in `skills/` at the repo root (agentskills format), so any agent can run them. The agent setup itself lives outside this repo.

| Profile | Job | Access | Never |
| --- | --- | --- | --- |
| `rodado` | Ideas, briefs, copy, audit, weekly report, prospect research and DM drafts | Repo only, no external credentials | Spend money, publish, message anyone |
| `rodado-studio` | Carousels, statics, Reel assembly, image/video generation | Generation API keys with a monthly cap; writes only `final/` and `sources/` | Change strategy or copy, publish |
| `rodado-publisher` | Schedule approved posts, pull Instagram metrics into `log.csv` | Meta token (publish + insights); reads only approved posts | Write or edit content |

Human approval points: weekly ideas, copy + audit, visuals. Anything that reaches a person or the public needs Pedro's approval until a step runs 4 weeks without edits.
