// Timing: everything on screen is placed on the narration's clock.
//   data/lines.json  { duration, lines: [{ i, text, start, end }] }   (voice.py, or estimate.py for a preview)
//   data/words.json  [{ w, line, s, e }]                                (words.py, or estimate.py)
// script.json has chapters[].lines[]; flattenScript() gives one flat list (line index i = position in that list).
export const T = { dur: 0, lines: [], words: [] };
const norm = (w) => String(w).toLowerCase().replace(/[^a-z0-9']+/g, '');

/** chapters → flat lines, each tagged with ch (chapter index) and first (first line of its chapter) */
export function flattenScript(script) {
  if (script.lines && !script.chapters) script = { ...script, chapters: [{ title: script.title || 'Video', lines: script.lines }] };
  const lines = []; script.chapters.forEach((c, ci) => c.lines.forEach((ln, k) => lines.push({ ...ln, ch: ci, first: k === 0 })));
  return { chapters: script.chapters, lines };
}

export async function loadTiming() {
  const get = async (f) => { const r = await fetch(f, { cache: 'no-store' }); if (!r.ok) throw new Error(`missing ${f}: run ./lf voice then ./lf words (or ./lf estimate)`); return r.json(); };
  const lines = await get('data/lines.json'), words = await get('data/words.json');
  T.lines = lines.lines; T.words = words; T.dur = lines.duration; return T;
}
export const L = (i) => { const l = T.lines[i]; if (!l) throw new Error(`no line ${i}`); return l.start; };
export const Le = (i) => { const l = T.lines[i]; if (!l) throw new Error(`no line ${i}`); return l.end; };
/** start (or end) time of the first word matching `word` (prefix, case/punctuation ignored) inside lines i0..i1. Throws if absent. */
export function Wd(word, i0, i1 = i0, which = 's') {
  const n = norm(word); const hit = T.words.find((w) => w.line >= i0 && w.line <= i1 && norm(w.w).startsWith(n));
  if (!hit) throw new Error(`word "${word}" not found in lines ${i0}${i1 !== i0 ? '-' + i1 : ''}: ${T.lines.slice(i0, i1 + 1).map((l) => l.text).join(' / ')}`);
  return hit[which];
}
export const lineWords = (i) => T.words.filter((w) => w.line === i);
export const rangeWords = (i0, i1) => T.words.filter((w) => w.line >= i0 && w.line <= i1);
