---
name: writing-clarity
description: Produce clear, audience-appropriate writing.
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Writing Clarity

Works WITH power-core (confirm the goal, audience and criteria first). `SKILL` = this folder.

1. **Decide**: who reads it, what they should know or do afterwards, how long it should be. Put the main point first.
2. **Draft plainly**: short concrete sentences, active voice, specific nouns and numbers. One idea per paragraph.
3. **Spoken scripts**: write for the ear. Connected sentences that sound like a person talking, contractions, no list-like
   fragments. Check with `python SKILL/scripts/readability.py <file> --spoken`, which flags sentences over ~20 words.
4. **Cut**: remove filler (very, really, basically, in order to), repeated ideas and throat-clearing openings.
5. **Check**: `python SKILL/scripts/readability.py <file>` for sentence length, repeated words, passive hints and filler.
6. **Accuracy pass**: every fact, name, figure and quote matches its source. Original wording only; do not copy others' text.
7. **Match the user's language and tone.** Keep formatting minimal unless it helps the reader.

