// Faceless Long-Form engine: canvas, theme colours, math, text layout and drawing primitives.
// Every drawing function uses the shared `ctx` (set once by main.js). All drawing is a pure function of time.
export const W = 1920, H = 1080;
export let ctx = null;
export function setCtx(c) { ctx = c; }

// ---------- theme (filled by main.js from themes.js) ----------
export const TH = {};
export function setTheme(t) { for (const k of Object.keys(TH)) delete TH[k]; Object.assign(TH, t); }
/** resolve a colour name from the theme ("accent", "danger"...) or pass a raw CSS colour through */
export const col = (c) => (c && TH[c] !== undefined && typeof TH[c] === 'string' ? TH[c] : c || TH.accent);

// ---------- math ----------
export const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / ((b - a) || 1e-6));
export const eo = (t) => 1 - Math.pow(1 - t, 3);
export const ei = (t) => t * t * t;
export const eio = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const eob = (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
export const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const TAU = Math.PI * 2;

// ---------- colour ----------
function rgb(hex) {
  let h = String(hex).replace('#', ''); if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  const n = parseInt(h.slice(0, 6), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
export const rgba = (c, a) => { const [r, g, b] = rgb(col(c)); return `rgba(${r},${g},${b},${a})`; };
export const mixc = (c1, c2, t) => { const a = rgb(col(c1)), b = rgb(col(c2)); return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], t))).join(',')})`; };

// ---------- shapes ----------
export function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
export function circle(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fillStyle = fill; ctx.fill(); }
export function line(pts, color, w, dash) {
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]);
}
export function fillAll(color) { ctx.fillStyle = color; ctx.fillRect(-400, -400, W + 800, H + 800); }
/** a card: rounded rect with soft shadow and a hairline edge */
export function card(x, y, w, h, { r = 28, fill = TH.card, edge = TH.cardEdge, shadow = true, alpha = 1 } = {}) {
  ctx.save(); ctx.globalAlpha *= alpha;
  if (shadow) { ctx.shadowColor = TH.shadow || 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; }
  rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); ctx.shadowColor = 'transparent';
  if (edge) { ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke(); }
  ctx.restore();
}

// ---------- text ----------
export const HEAD = () => (TH.serif ? 'Caladea' : 'Inter');
export const fontStr = (size, weight = 700, head = false) => `${head && TH.serif ? 700 : weight} ${Math.round(size)}px ${head ? HEAD() : 'Inter'}`;
/** draw one line of text. opts: size weight fill align base head ls (letter spacing px) alpha stroke (outline colour) */
export function txt(s, x, y, o = {}) {
  const { size = 40, weight = 700, fill = TH.text, align = 'left', base = 'alphabetic', head = false, ls = 0, stroke, alpha = 1 } = o;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = fontStr(size, weight, head); ctx.textAlign = align; ctx.textBaseline = base; ctx.letterSpacing = `${ls}px`; ctx.lineJoin = 'round';
  if (stroke) { ctx.lineWidth = size * 0.16; ctx.strokeStyle = stroke; ctx.strokeText(s, x, y); }
  ctx.fillStyle = fill; ctx.fillText(s, x, y); ctx.letterSpacing = '0px'; ctx.restore();
}
export function measure(s, size, weight = 700, head = false, ls = 0) {
  ctx.save(); ctx.font = fontStr(size, weight, head); ctx.letterSpacing = `${ls}px`; const w = ctx.measureText(s).width; ctx.letterSpacing = '0px'; ctx.restore(); return w;
}
/** "plain *accent words* plain" → [{ w, hi }]  (a * toggles the accent colour; words are split on spaces) */
export function parseRich(str) {
  const out = []; let hi = false;
  for (const part of String(str).split('*')) { for (const w of part.split(/\s+/).filter(Boolean)) out.push({ w, hi }); hi = !hi; }
  return out;
}
/** word-wrap rich text. returns { lines: [{ toks: [{w, hi, x, wd}], wd }], lh, h, size } — drawn by drawLayout */
export function layoutRich(str, maxW, size, { weight = 800, head = true, lh = 1.18, ls = 0 } = {}) {
  const toks = parseRich(str), sp = measure(' ', size, weight, head, ls), lines = []; let cur = { toks: [], wd: 0 };
  for (const t of toks) {
    const wd = measure(t.w, size, weight, head, ls);
    if (cur.toks.length && cur.wd + sp + wd > maxW) { lines.push(cur); cur = { toks: [], wd: 0 }; }
    t.wd = wd; t.x = cur.wd + (cur.toks.length ? sp : 0); cur.toks.push(t); cur.wd = t.x + wd;
  }
  if (cur.toks.length) lines.push(cur);
  return { lines, lh: size * lh, h: lines.length * size * lh, size, weight, head, ls, maxW };
}
/** largest size (≤ max) at which the text fits maxW × maxLines */
export function fitRich(str, maxW, max, min, maxLines, o = {}) {
  for (let s = max; s >= min; s -= 4) { const L = layoutRich(str, maxW, s, o); if (L.lines.length <= maxLines) return L; }
  return layoutRich(str, maxW, min, o);
}
/** draw a layout. anchor: 'center' | 'left'. tokAlpha(i) → 0..1 and tokScale(i) → scale let words animate (kinetic type). Returns nothing. */
export function drawLayout(L, x, y, { align = 'center', fill = TH.text, hi = TH.accent, alpha = 1, tokAlpha, tokScale, stroke } = {}) {
  let k = 0; const y0 = y - (L.h - L.lh) / 2;
  L.lines.forEach((ln, li) => {
    const x0 = align === 'center' ? x - ln.wd / 2 : align === 'right' ? x - ln.wd : x;
    for (const t of ln.toks) {
      const a = (tokAlpha ? tokAlpha(k) : 1) * alpha, sc = tokScale ? tokScale(k) : 1; k++;
      if (a <= 0.003) continue;
      ctx.save(); ctx.translate(x0 + t.x + t.wd / 2, y0 + li * L.lh); ctx.scale(sc, sc);
      txt(t.w, -t.wd / 2, 0, { size: L.size, weight: L.weight, head: L.head, ls: L.ls, fill: t.hi ? hi : fill, alpha: a, base: 'middle', stroke });
      ctx.restore();
    }
  });
}
/** number with thousands separators */
export const fmt = (n, dec = 0) => Number(n).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
