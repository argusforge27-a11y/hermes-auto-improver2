# Research, accuracy and sourcing

A faceless channel has no face to vouch for it, so accuracy is the brand. Do this before outlining.

## Process (Stage 1)

1. Define the angle in one sentence: *what will the viewer understand or be able to do at the end that they could not at the start?*
2. Search broadly first, then deeply. For a 15-20 minute video collect **at least 8-12 distinct sources**, at least 3 of them primary or authoritative
   (government/agency data, peer-reviewed papers, museum or archive pages, company filings, court documents, original interviews, standards bodies).
   Encyclopaedias and news summaries are fine for orientation but are not the last word on a surprising claim.
3. Keep `research.md` in the project folder: one row per fact you will state (claim, number, date, source URL, confidence: *confirmed* by two independent sources, or *single source*, or *disputed*).
4. Cross-check every number, date, name and superlative ("first", "largest", "never") against a second source. When sources disagree, say so in the narration ("estimates range from X to Y") or leave the claim out.
5. Check what has changed recently (laws, prices, records, who holds an office); anything time-sensitive is searched again at the end, right before rendering.
6. List the real sources in `script.json` -> `"sources": [...]`; they go in the description. Do not list sources you did not use.

## Accuracy rules while writing

- State only what the sources support, at the confidence they support. "Historians believe", "according to X", "the most commonly cited figure" are honest hedges; "everyone knows" is not.
- Do not invent quotes, dialogue, statistics, or "a study found". If you cannot cite it, cut it. Paraphrase; quote only short, attributed lines.
- Reconstructed scenes ("imagine you are standing...") are labelled as imagination.
- Claims about **living, named people or companies** (crime, fraud, misconduct, health) need strong primary sourcing or are left out; present allegations as allegations and outcomes (convictions, rulings) as outcomes.
- Medical, legal and financial topics: describe what the evidence shows and what experts say; do not give personalised advice; add a one-line "not professional advice" note in the description.
- Conspiracy theories, pseudoscience and contested politics: present what is known, what is claimed, and what the evidence says, without endorsing the claim; attribute positions to the people who hold them.
- No content that sexualises minors, gives instructions for weapons, drugs, or self-harm, or harasses a group. Decline those topics.

## Images and music (if you use any)

The built-in scenes need no outside media. If the user supplies images or you add them (`image` scene), every file needs a clear right to be used:

- Safe sources: the user's own files; **public-domain or openly licensed** archives such as Wikimedia Commons (read the licence on each file page; CC-BY needs credit, CC-BY-SA needs credit and share-alike), NASA media, the Library of Congress, Smithsonian Open Access, the Internet Archive's public-domain items, national archives.
- Do not scrape Google Images, news photos, film stills, logos, or anything where the owner is unclear. Do not use images of real private people.
- Download into `media/`, keep the original filename, and write the credit line into `script.json` -> `"credits"` (and the `credit` field of the scene), for example `"Photo: Name, via Wikimedia Commons, CC BY-SA 4.0"`.
- Music: the built-in procedural bed is original and free to use. A user's own track must be one they have the right to use on YouTube (their own, or licensed for commercial use, or the platform's own audio library); the credit goes in the description. Never use commercial songs.
- Voice: the narrator is a synthetic voice (Kokoro, Apache-2.0). Do not imitate or clone a real person's voice, and do not make narration that attributes invented statements to real people.

## YouTube policy awareness (tell the user, then let them check)

- YouTube has a policy against mass-produced, repetitive, or "inauthentic" content for monetisation. A faceless channel is fine; what matters is **original scripting, real research, and a recognisable point of view in each video**. Never publish ten videos a day from templates.
- YouTube asks creators to disclose realistic altered or synthetic content in specific cases (for example realistic scenes or voices that could be mistaken for real events or real people). A clearly synthetic narrator over motion graphics usually is not that case, but the policy and the upload form change, so the user should read the current YouTube help pages and answer the disclosure questions in YouTube Studio themselves.
- Do not promise monetisation, views, or revenue. Say plainly that results depend on topic, titles, thumbnails and audience.
