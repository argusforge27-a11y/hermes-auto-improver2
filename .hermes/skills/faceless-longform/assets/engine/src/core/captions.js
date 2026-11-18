// Captions for long videos: calm subtitles, 1-2 lines, bottom centre, the word being spoken in the highlight colour.
// script.json "captions": "subtitle" (default) or "none".  A line can opt out with "nocaps": true (when the scene already shows the words).
// Chunking: a new subtitle starts after a comma / full stop (once it has 3+ words) or at 7 words, so it reads like speech.
import { ctx, W, H, TH, clamp, lerp, seg, eo, rr, fontStr } from './lib.js';
import { T, lineWords } from './timing.js';

export const CAP = { y: 976, size: 44, maxW: 1480, maxWords: 7 };
let chunks = [];

export function buildCaptions(flat) {
  chunks = [];
  flat.lines.forEach((ln, i) => {
    if (ln.nocaps) return; const ws = lineWords(i); if (!ws.length) return;
    let cur = [];
    const flush = () => { if (cur.length) chunks.push({ line: i, s: cur[0].s - 0.04, words: cur }); cur = []; };
    ws.forEach((w, k) => { cur.push(w); const end = /[,;:.?!—–]$/.test(w.w) && cur.length >= 3; if (end || cur.length >= CAP.maxWords || (cur.length >= 5 && k < ws.length - 1 && /[,]$/.test(w.w))) flush(); });
    flush();
  });
  chunks.forEach((c, k) => { const next = chunks[k + 1], last = c.words[c.words.length - 1]; c.e = Math.min(last.e + 0.35, next ? Math.max(next.s, last.e + 0.05) : T.dur); });
  return chunks;
}
export const captionList = () => chunks;

export function drawCaption(t, mode) {
  if (mode === 'none') return; const c = chunks.find((q) => t >= q.s && t < q.e); if (!c) return;
  const lt = t - c.s, a = eo(seg(lt, 0, 0.12)) * (1 - eo(seg(t, c.e - 0.1, c.e))), size = CAP.size;
  ctx.save(); ctx.globalAlpha *= a; ctx.font = fontStr(size, 700); ctx.letterSpacing = '0px';
  const sp = ctx.measureText(' ').width, ws = c.words.map((w) => ({ ...w, wd: ctx.measureText(w.w).width }));
  const width = (arr) => arr.reduce((s, w) => s + w.wd, 0) + sp * (arr.length - 1);
  let rows = [ws];
  if (width(ws) > CAP.maxW && ws.length > 1) { let best = null; for (let i = 1; i < ws.length; i++) { const A = ws.slice(0, i), B = ws.slice(i), m = Math.max(width(A), width(B)); if (!best || m < best.m) best = { m, rows: [A, B] }; } rows = best.rows; }
  const lh = size * 1.28, boxW = Math.max(...rows.map(width)) + 64, boxH = rows.length * lh + 20, y0 = CAP.y - boxH + lh * 0.52 + 12 * (rows.length - 1) * 0 ;
  const top = CAP.y + 38 - boxH; rr(W / 2 - boxW / 2, top, boxW, boxH, 18); ctx.fillStyle = TH.capBox; ctx.fill();
  ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  rows.forEach((row, ri) => {
    let x = W / 2 - width(row) / 2; const y = top + 10 + lh * (ri + 0.78);
    for (const w of row) { const on = t >= w.s - 0.03 && t < w.e + 0.12; ctx.fillStyle = on ? TH.capHi : TH.capText; ctx.fillText(w.w, x, y); x += w.wd + sp; }
  });
  ctx.restore();
}
