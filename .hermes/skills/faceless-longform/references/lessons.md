# Lessons: what makes the pipeline smooth and the videos good

Read before Stage 2 (script) and when anything fails. Each line is a rule plus the reason.

## Pipeline
1. **Run `./lf doctor` first, `./lf lint` before voice, `./lf check` before any render.** Each is seconds; the failures they catch cost minutes (a bad `at` word, a typo'd theme, a missing image) after a long voice or render.
2. **Never change `script.json` text after voicing without re-running voice + words.** The line count and timings must match `data/lines.json`; the engine refuses to boot otherwise. Editing only scene fields (colors, values) needs no re-voicing, but re-render that chapter.
3. **Do a quick draft on estimated timing (`./lf estimate`, then `./lf draft`) to review visuals while the voice is still being made.** It overwrites nothing real; voice + words replace it later.
4. **Long jobs go in the background** (`./lf bg voice`, `bg draft`, `bg final`) and are polled with `./lf status`; terminal tools time out and a dead shell loses progress otherwise.
5. **Render drafts at 15 fps; final once.** Chapters are cached by content, so after the draft is approved only touched chapters redraw. After the final, run `./lf qa` (it also lists frames to view).
6. **If Chrome dies mid-render it is nearly always memory.** The renderer retries each chapter up to 3 times and picks workers to fit RAM; if it still fails use `--jobs 1`.
7. **The soundtrack is joined last.** If audio and picture disagree after edits, re-run `./lf cues`, `./lf mix`, then render (a render with no `data/mix.wav` is silent; QA flags it).
8. **Never edit files inside the skill folder while a project is running;** projects hold their own copy of the engine. To change the look for all future videos edit `assets/engine/`.

## Voice
9. Write numbers as said ("nineteen ninety-four"), no symbols (% $ & /), no abbreviations (e.g., vs., Dr.), no URLs, no ALL-CAPS words: the lint warns on each, the voice mangles them.
10. Respell a mispronounced name in the top-level `"pronounce": {"Thames": "Temz"}` map: the voice says the respelling, captions keep the real spelling. Only that sentence is re-spoken.
11. One sentence under about 30 words; split long ones. A flat sentence usually needs a comma or a split, not a different voice.

## Story and retention
12. The hook must show motion and a concrete claim in the first 3 seconds and pay off its promise within 30-45 s; open with the most surprising true fact, not the topic.
13. A new visual every 4-12 s, a re-hook (stat, map, chart, callout, quote) at least every 80 s, never three identical scene types in a row. Contact sheets of a chapter that "feels flat" show repeated layouts: change types, not colours.
14. Scenes show the shape (a number, a sequence, a contrast); the voice carries the detail. A bullets scene that repeats the narration word for word loses viewers.
15. Fact-check last, not first: every number, date, name and "first/only/largest" claim against `research.md` after the script is final. A claim that cannot be confirmed is cut or hedged.
16. Chapters of 1-3 minutes with names viewers understand ("Intro", not "The Hook"; `./lf chapters` renames it); YouTube needs at least 3 chapters, each 10 s or longer, the first at 0:00.

## Delivery
17. Be upfront: synthetic narrator, generated motion graphics, no promised results; the user answers YouTube's altered/synthetic-content and made-for-kids questions and checks current monetisation policy.
18. Rights: only own or openly licensed images and music, credit them in `credits`; no imitation of real voices.
