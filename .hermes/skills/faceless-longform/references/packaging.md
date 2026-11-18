# Packaging: title, thumbnail, description, chapters, upload

Packaging decides whether the video gets clicked. Do it after the film is final, but think about the title while outlining (Gate 1).

## Title (offer 3, recommend 1)

- 45-65 characters; the specific, curiosity-creating part in the first 40.
- Promise something the video actually delivers. No false claims, no "you won't believe", no all-caps words, no emoji walls.
- Patterns that work honestly: *Why X happened*, *How X really works*, *The strange story of X*, *What nobody explains about X*, *X vs Y: which one is right?*. Avoid first-person claims the channel cannot back ("I spent 100 hours").
- Keep the main keyword natural; do not stuff.

## Thumbnail

`./lf thumb` draws `script.json` -> `thumbnail` as a 1280x720 JPEG (well under YouTube's 2 MB limit) using the video's theme:
`{ "text": "THE *GREAT* STINK", "sub": "London, 1858", "icon": "warning", "color": "accent2", "backdrop": "rays", "image": "media/photo.jpg" }`.
Rules: 2-4 big words, one focal icon or image, high contrast, readable at phone size, and it must not contradict the title; the thumbnail adds a second hook, it does not repeat the title.
Render 2-3 variants (different `text`/`icon`/`color`) and let the user choose; they can also A/B test in YouTube Studio.
After rendering, **view the thumbnail** and check it at small size (`ffmpeg -i thumb.jpg -vf scale=320:180 small.jpg`).

## Description (write it; the user pastes it)

1. First two lines (the only part shown before "more"): what the video answers, with the main keyword, and why to watch to the end.
2. A 2-4 sentence summary.
3. **Chapters**: `./lf chapters` writes `renders/chapters.txt` (starts at 0:00, 3+ chapters, 10 s+ each). Paste it as is.
4. **Sources**: the list from `script.json` -> `sources` (and `credits` for images and music).
5. A short disclosure line if appropriate (for example that narration is synthetic) and the not-advice note for medical/legal/financial topics.
6. No links the channel does not own, no keyword dumps. 3-5 hashtags at most.

## Tags, comment, end

- 5-10 tags is plenty; YouTube relies on title, thumbnail and content more than tags.
- Suggest a pinned comment that asks one specific question about the topic.
- The call to action in the film is one thing (subscribe OR watch next).

## Upload

Default: give the user the MP4, thumbnail, title options, description and chapter list, and let them upload in **YouTube Studio**; Studio handles thumbnails,
chapters, end screens, cards, visibility, the altered/synthetic content questions and the "made for kids" setting, which they must answer themselves.

Only if the user explicitly asks you to upload and a YouTube upload tool is connected (for example through Zapier): confirm title, description, category, visibility
(**private or unlisted first**) and the "not made for kids" answer, then upload. A 15-20 minute 1080p file is hundreds of MB; if the tool rejects the size, say so and hand the file over for manual upload instead of re-encoding it badly.
Never publish publicly without the user saying so in this conversation, and never answer the policy questions on their behalf.

## Pre-publish check

- [ ] Watched the draft at least once (or reviewed every contact sheet) and read the captions for typos.
- [ ] All facts rechecked; time-sensitive ones searched again today.
- [ ] Credits and sources in the description; music/image licences confirmed.
- [ ] Title, thumbnail and first line of the film all promise the same thing.
- [ ] Policy questions in Studio answered by the user.
