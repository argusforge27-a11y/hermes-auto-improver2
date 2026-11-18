# Writing a 15-20 minute script that people finish

Read this before Stage 2 (the script). The engine can draw anything; what decides whether a long faceless video works is
the script. Viewers leave a long video when it feels like a list of facts with no reason to keep going.

## Length and word budget

| Target | Narration words (Kokoro, speed 1.0, about 2.7 words/s incl. pauses) | Chapters | Scenes |
|---|---|---|---|
| 8-10 min | 1,300-1,600 | 5-7 | 70-110 |
| 12-15 min | 1,900-2,400 | 7-10 | 110-170 |
| 15-20 min | 2,400-3,300 | 8-13 | 150-240 |

A scene lasts 4-12 seconds, so a 16-minute video has roughly 120-200 scenes. If the script is under the budget, do not pad;
find the missing story (a counter-argument, an example, a consequence). If it is over, cut a chapter, not words from every chapter.

## The shape of the whole video

1. **Hook (0:00-0:40).** State the most interesting thing, a question, or a stake in the first sentence. Promise something specific
   the viewer will get by the end ("by the end you will know why X, and it is not what you think"). No channel intro, no "before we
   start", no greeting. The hook is chapter 0 (`"hook": true`).
2. **Context in one chapter (about 1-2 min).** Only what the viewer needs to follow the next part. Cut anything they could look up.
3. **The body: 5-10 chapters of 1-2.5 minutes each.** Each chapter is a small story, not a topic (see blueprint below).
4. **The turn (around 60-70%).** A surprise, a reversal, or a harder question. Without one, long videos sag in the middle.
5. **The payoff.** Deliver exactly what the hook promised. Then say what it means, one level up.
6. **The close (under 30 s).** One-sentence takeaway, one call to action (subscribe OR a next video, never a list). End on the idea, not on "thanks for watching".

## Chapter blueprint (repeat for every chapter)

- **Open with a question, a claim, or a scene**, never "Now let's talk about". The chapter title card is a label; the first line is the hook of that chapter.
- **3-5 beats**, each beat = one claim + one concrete example (a name, a number, a place, a date, a small story).
- **One re-hook scene** (stat, chart, map, quote, callout) at the strongest fact.
- **A bridge in the last line** that raises a question the next chapter answers ("but that raises a problem...").

## Retention devices (use them on purpose)

- **Open loops.** Plant a question early ("we will come back to why the fire started at night") and pay it off 3-8 minutes later. Keep 2-3 loops open at any time.
- **Pattern interrupt about every 45-75 seconds:** a stat, a callout, a map, a quote, a switch of scene type, a change of music mood by chapter. The scene library is the toolbox; `check_script.py` warns when 80 s pass with none.
- **Escalate.** Each chapter should raise the stakes, the scale, or the strangeness of the previous one.
- **Specifics beat adjectives.** "Eleven hundred miles of sewers" not "a huge network". One surprising number per chapter, always with something to compare it to.
- **Address the viewer sparingly.** "You" works for stakes and thought experiments; constant "you" sounds like an ad.
- **Reasons, not lists.** If a paragraph can be reordered without loss, it is a list; find the because/therefore/but that links the beats.
- **Cut the throat-clearing.** Delete "it is important to note", "as we all know", "in today's video", "let that sink in", "buckle up", "without further ado".

## Writing for the ear (the voice reads this out loud)

- Short sentences. Average 12-16 words; vary them. A one-word sentence after a long one lands hard.
- **One line = one beat = at most one picture idea**, 8-22 words. The script is a list of lines; sentences can run across lines.
- Write numbers and dates **the way they are said**: "eighteen fifty-eight", "three hundred million", "twenty twenty-four", "two point five percent". Digits make the voice stumble, and `check_script.py` flags them.
- Spell out acronyms the voice would mangle ("N A S A" only if you want it spelled; "NASA" is read as a word). Put hard names in the most natural phonetic spelling and listen once.
- Use commas for breath. Kokoro pauses at commas and full stops; the pause after a full stop is `gap` (0.35 s) and 0.9 s at a chapter end.
- No parentheses, no semicolons, no brackets, no emoji, no markdown in narration text. `*` marks an accent word only in scene text, not in narration.
- Read the whole script aloud once before approval. Anything that makes you run out of breath or trip is rewritten.

## Types of video and their skeletons

- **Explainer ("how does X work", "why is X")**: question hook -> the simple version -> where the simple version breaks -> the real mechanism in 3-5 steps -> a counter-intuitive consequence -> what it means for the viewer.
- **History / story ("the rise and fall of X")**: scene-setting cold open at the climax -> "how did we get here" -> rise (2-3 chapters, each a decision) -> turning point -> fall -> aftermath -> why it still matters.
- **Mystery / true story**: the unexplained fact -> the people and the place -> the timeline of what is known -> each theory in its own chapter with evidence for and against -> what the best evidence supports and what is still unknown. Never present a theory as proven; never accuse a named living person.
- **Top-N / listicle**: hook with the best entry hinted -> criteria in one line -> entries from lowest to highest with `rank` scenes, each with a surprising fact -> the number one with the most story -> a quick honorable mention.
- **How-to / tutorial**: the result first (what you will have) -> materials or prerequisites -> numbered steps as `flow`/`bullets` scenes -> the 2-3 most common mistakes -> a final checklist.
- **Opinion / analysis (finance, tech, culture)**: a claim you will test -> the strongest version of the other side -> the data (charts) -> where the data is weak -> your conclusion, stated with the right amount of doubt. Facts and opinion must be clearly separated in the wording.

## Script review checklist (run before the user sees it)

- [ ] The first sentence works as a video title on its own.
- [ ] Hook promise is specific and is paid off in the last third.
- [ ] Every chapter starts with a question, claim, or scene and ends with a bridge.
- [ ] Every number has a unit, a year, and a source in `sources`.
- [ ] No more than 80 s without a re-hook scene; no scene longer than 14 s.
- [ ] At least 3 different scene types per chapter; never 3 identical scene types in a row.
- [ ] No sentence the voice cannot say (digits, symbols, stacked abbreviations).
- [ ] The ending says what it means, then stops.
