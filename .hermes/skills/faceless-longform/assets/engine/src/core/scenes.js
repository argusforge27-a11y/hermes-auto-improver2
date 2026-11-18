// The scene library. A scene is ONE visual idea that stays on screen for one or more narration lines.
// script.json: a line with  "scene": { "type": "stat", ... }  starts a new scene; lines without "scene" continue the previous one.
// Each type below is (spec, S) => draw(lt, d, t):  lt = seconds since the scene started, d = its length, t = film time.
// S = { i0, i1 (its first/last narration line), st, end, d, ch, chNum, chTitle, title (video), backdrop, cue(lt, type, gain) }.
// Items that can be revealed on a spoken word take "at": "word" (prefix match inside the scene's lines); otherwise they spread evenly.
import { ctx, W, H, TH, col, rgba, mixc, clamp, lerp, seg, eo, eio, eob, TAU, rnd, rr, circle, line, fillAll, card, txt, measure,
  layoutRich, fitRich, drawLayout, parseRich, fmt } from './lib.js';
import { backdrop } from './backdrops.js';
import { drawIcon } from './icons.js';
import { Wd, rangeWords, T } from './timing.js';
import { mapScene } from './maps.js';
import { chartScene } from './charts.js';

export const SCENES = {};
export const MEDIA = {};          // src → HTMLImageElement, filled by main.js before the first frame

// ---------- helpers ----------
const bg = (S, sp, t) => backdrop(sp.backdrop || S.backdrop, t);
const ap = (lt, t0, dur = 0.5) => eo(seg(lt, t0, t0 + dur));
/** when each item appears (seconds into the scene). items with "at" land on that spoken word; the rest are spread evenly between. */
export function reveals(items, S, { t0 = 0.5, tail = 1.0 } = {}) {
  const n = items.length, out = new Array(n).fill(null);
  items.forEach((it, k) => { if (it && typeof it === 'object' && it.at) out[k] = Math.max(0.15, Wd(it.at, S.i0, S.i1) - S.st - 0.06); });
  let prev = -1;
  for (let k = 0; k <= n; k++) {
    if (k < n && out[k] === null) continue;
    const c = k - prev - 1;
    if (c > 0) {
      const a = prev < 0 ? t0 : out[prev], b = k === n ? Math.max(a + 0.4 * c, S.d - tail) : out[k];
      for (let j = 1; j <= c; j++) out[prev + j] = prev < 0 ? (k === n ? lerp(a, b, (j - 1) / c) : lerp(a, b, (j - 1) / c)) : lerp(a, b, j / (c + 1));
    }
    prev = k;
  }
  for (let k = 1; k < n; k++) out[k] = Math.max(out[k], out[k - 1] + 0.12);
  return out;
}
const itemText = (it) => (typeof it === 'string' ? it : it.text ?? it.label ?? '');
/** scene heading: small accent bar + title, top left */
function heading(title, lt, x = 150, y = 120, size = 54) {
  if (!title) return; const a = ap(lt, 0.05, 0.5);
  ctx.save(); ctx.globalAlpha *= a; rr(x, y - 14, 10 * 1 + 70 * a, 8, 4); ctx.fillStyle = TH.accent; ctx.fill(); ctx.restore();
  txt(title, x, y + 50, { size, weight: 800, head: true, alpha: a });
}
const kick = (s, x, y, o = {}) => txt(String(s).toUpperCase(), x, y, { size: 28, weight: 800, fill: TH.accent, ls: 7, ...o });
const nrm = (w) => String(w).toLowerCase().replace(/[^a-z0-9']+/g, '');

// ---------- title / chapter ----------
SCENES.title = (sp, S) => {
  const text = sp.title || S.title;
  return (lt, d, t) => {
    bg(S, { backdrop: sp.backdrop || 'stars' }, t);
    const L = fitRich(text, 1560, 150, 64, 3, { weight: 900, head: true }), y = H / 2 - 20;
    if (sp.kicker) kick(sp.kicker, W / 2, y - L.h / 2 - 56, { align: 'center', alpha: ap(lt, 0.1, 0.5) });
    drawLayout(L, W / 2, y, { tokAlpha: (k) => ap(lt, 0.2 + k * 0.09, 0.5), tokScale: (k) => lerp(0.9, 1, eob(seg(lt, 0.2 + k * 0.09, 0.8 + k * 0.09))), hi: TH.accent2 });
    const bw = 300 * ap(lt, 1.0, 0.7); rr(W / 2 - bw / 2, y + L.h / 2 + 34, bw, 8, 4); ctx.fillStyle = TH.accent; ctx.fill();
    if (sp.sub) txt(sp.sub, W / 2, y + L.h / 2 + 128, { size: 44, weight: 500, fill: TH.muted, align: 'center', alpha: ap(lt, 1.2, 0.6) });
  };
};
SCENES.chapter = (sp, S) => (lt, d, t) => {
  bg(S, sp, t);
  const n = String(sp.n ?? S.chNum).padStart(2, '0'), a = ap(lt, 0.0, 0.7);
  txt(n, W / 2, H / 2 + 200, { size: 620, weight: 900, fill: rgba('accent', 0.11), align: 'center', alpha: a });
  kick(sp.kicker || `Chapter ${n}`, W / 2, H / 2 - 120, { align: 'center', alpha: ap(lt, 0.15, 0.5) });
  const L = fitRich(sp.title || S.chTitle, 1500, 130, 64, 2, { weight: 900, head: true });
  drawLayout(L, W / 2, H / 2 + 10, { tokAlpha: (k) => ap(lt, 0.3 + k * 0.08, 0.5), tokScale: (k) => lerp(0.92, 1, ap(lt, 0.3 + k * 0.08, 0.6)), hi: TH.accent2 });
  const bw = 360 * ap(lt, 0.8, 0.8); rr(W / 2 - bw / 2, H / 2 + L.h / 2 + 50, bw, 8, 4); ctx.fillStyle = TH.accent; ctx.fill();
  if (sp.sub) txt(sp.sub, W / 2, H / 2 + L.h / 2 + 140, { size: 42, weight: 500, fill: TH.muted, align: 'center', alpha: ap(lt, 1.1, 0.6) });
};

// ---------- text, kinetic, callout, quote ----------
SCENES.text = (sp, S) => (lt, d, t) => {
  bg(S, sp, t); const left = sp.align === 'left', x = left ? 190 : W / 2, maxW = left ? 1400 : 1500;
  const L = fitRich(sp.headline, maxW, 112, 52, 4, { weight: 800, head: true }), sub = sp.sub ? layoutRich(sp.sub, maxW - 100, 42, { weight: 500, head: false, lh: 1.35 }) : null;
  const total = L.h + (sub ? sub.h + 36 : 0) + (sp.icon ? 190 : 0) + (sp.kicker ? 56 : 0), top = H / 2 - 40 - total / 2;
  let y = top;
  if (sp.icon) { const a = ap(lt, 0.0, 0.5); drawIcon(sp.icon, left ? x + 70 : x, y + 70, 150 * (0.8 + 0.2 * eob(seg(lt, 0, 0.6))), { color: sp.color || 'accent', t: lt, alpha: a }); y += 190; }
  if (sp.kicker) { kick(sp.kicker, x, y + 18, { align: left ? 'left' : 'center', alpha: ap(lt, 0.05, 0.5) }); y += 56; }
  const a = ap(lt, 0.1, 0.65); ctx.save(); ctx.translate(0, (1 - a) * 36);
  drawLayout(L, x, y + L.h / 2, { align: left ? 'left' : 'center', alpha: a, hi: TH[sp.hi] ? TH[sp.hi] : TH.accent2 }); ctx.restore();
  if (sub) drawLayout(sub, x, y + L.h + 36 + sub.h / 2 - 8, { align: left ? 'left' : 'center', fill: TH.muted, alpha: ap(lt, 0.7, 0.6) });
};
SCENES.kinetic = (sp, S) => {
  const text = sp.text || T.lines.slice(S.i0, S.i1 + 1).map((l) => l.text).join(' '), toks = parseRich(text), spoken = rangeWords(S.i0, S.i1);
  let cur = 0; const times = toks.map((tk, k) => {   // word k appears when the same word is spoken (best effort), else spread over the scene
    const n = nrm(tk.w); let j = -1; for (let q = cur; q < spoken.length && q < cur + 6; q++) if (n && (nrm(spoken[q].w) === n || (n.length > 2 && nrm(spoken[q].w).startsWith(n.slice(0, 3))))) { j = q; break; }
    if (j >= 0) { cur = j + 1; return spoken[j].s - S.st - 0.04; } return 0.15 + (S.d - 1.2) * (k / Math.max(1, toks.length));
  }).map((v, k, a) => Math.max(0.1, k && v < a[k - 1] ? a[k - 1] + 0.05 : v));
  return (lt, d, t) => {
    bg(S, sp, t); const L = fitRich(text, 1560, sp.size || 170, 64, 5, { weight: 900, head: true });
    drawLayout(L, W / 2, H / 2 - 30, { tokAlpha: (k) => ap(lt, times[k], 0.2), tokScale: (k) => lerp(0.8, 1, eob(seg(lt, times[k], times[k] + 0.3))), hi: TH[sp.hi] ? TH[sp.hi] : TH.accent2 });
  };
};
SCENES.callout = (sp, S) => {
  S.cue(0, 'hit', 1);
  return (lt, d, t) => {
    const c = col(sp.color || 'accent2'); fillAll(c);
    const k = ap(lt, 0, 0.35), shake = lt < 0.5 ? Math.sin(lt * 90) * (1 - lt / 0.5) * 8 : 0;
    ctx.save(); ctx.translate(shake, 0); const sc = lerp(1.7, 1, eob(clamp(lt / 0.4)));
    const L = fitRich(sp.text, 1600, sp.size || 260, 90, 3, { weight: 900, head: true });
    ctx.translate(W / 2, H / 2 - (sp.sub ? 40 : 0)); ctx.scale(sc, sc); ctx.translate(-W / 2, -(H / 2 - (sp.sub ? 40 : 0)));
    drawLayout(L, W / 2, H / 2 - (sp.sub ? 40 : 0), { fill: TH.ink, hi: '#FFFFFF', alpha: k }); ctx.restore();
    if (sp.sub) txt(sp.sub, W / 2, H / 2 + L.h / 2 + 30, { size: 46, weight: 700, fill: TH.ink, align: 'center', alpha: ap(lt, 0.4, 0.5) });
  };
};
SCENES.quote = (sp, S) => (lt, d, t) => {
  bg(S, sp, t); const a = ap(lt, 0.05, 0.7);
  txt('“', 190, 330, { size: 360, weight: 900, head: true, fill: rgba('accent', 0.35), alpha: a });
  const L = fitRich(sp.quote, 1340, 76, 40, 6, { weight: 700, head: true, lh: 1.28 }), y0 = H / 2 - 40 - (sp.who ? 40 : 0);
  ctx.save(); ctx.translate(0, (1 - a) * 28); drawLayout(L, 290, y0 + L.h / 2 - 30, { align: 'left', alpha: a, hi: TH.accent2 }); ctx.restore();
  const ay = y0 + L.h + 24; rr(290, ay - 8, 80 * ap(lt, 0.6, 0.6), 6, 3); ctx.fillStyle = TH.accent; ctx.fill();
  if (sp.who) { txt(sp.who, 290, ay + 56, { size: 42, weight: 800, alpha: ap(lt, 0.7, 0.5) }); if (sp.role) txt(sp.role, 290, ay + 104, { size: 32, weight: 500, fill: TH.muted, alpha: ap(lt, 0.8, 0.5) }); }
};

// ---------- stat ----------
SCENES.stat = (sp, S) => {
  const num = typeof sp.value === 'number', dec = sp.decimals ?? (num && !Number.isInteger(sp.value) ? 1 : 0), t0 = sp.at ? Math.max(0.2, Wd(sp.at, S.i0, S.i1) - S.st - 0.1) : 0.35, dur = 1.5;
  if (num) S.cue(t0 + dur, 'chime', 0.7);
  return (lt, d, t) => {
    bg(S, sp, t); const k = eo(seg(lt, t0, t0 + dur)), v = num ? lerp(sp.from ?? 0, sp.value, k) : sp.value;
    const body = `${sp.prefix || ''}${num ? fmt(v, dec) : v}${sp.suffix || ''}`, a = ap(lt, 0.05, 0.5), cy = H / 2 - (sp.label ? 40 : 0);
    const color = col(sp.color || 'accent');
    if (sp.ring) {   // ring = a percentage drawn as a circle
      const R = 300; ctx.save(); ctx.lineWidth = 26; ctx.lineCap = 'round'; ctx.strokeStyle = rgba(color, 0.16); ctx.beginPath(); ctx.arc(W / 2, cy, R, 0, TAU); ctx.stroke();
      ctx.strokeStyle = color; ctx.beginPath(); ctx.arc(W / 2, cy, R, -Math.PI / 2, -Math.PI / 2 + TAU * clamp(v / (sp.max || 100)), false); ctx.stroke(); ctx.restore();
    }
    let size = sp.ring ? 190 : 270; while (measure(body, size, 900, true) > (sp.ring ? 480 : 1500) && size > 80) size -= 8;
    txt(body, W / 2, cy + size * 0.36, { size, weight: 900, head: true, fill: color, align: 'center', alpha: a });
    if (sp.label) { const L = fitRich(sp.label, 1300, 58, 36, 2, { weight: 700, head: false }); drawLayout(L, W / 2, cy + (sp.ring ? 380 : 240) , { alpha: ap(lt, 0.5, 0.6), hi: TH.accent2 }); }
    if (sp.sub) txt(sp.sub, W / 2, cy + (sp.ring ? 450 : 330), { size: 34, weight: 500, fill: TH.muted, align: 'center', alpha: ap(lt, 0.9, 0.6) });
    if (sp.icon) drawIcon(sp.icon, W / 2, cy - (sp.ring ? 0 : 250), 110, { color: sp.color || 'accent', alpha: 0.9 * a, t: lt });
  };
};

// ---------- lists & comparisons ----------
SCENES.bullets = (sp, S) => {
  const items = sp.items, rt = reveals(items, S, { t0: 0.6 }); rt.forEach((r) => S.cue(r, 'pop', 0.6));
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    const n = items.length, top = sp.title ? 270 : 170, rowH = clamp((H - top - 190) / n, 96, 150);
    items.forEach((it, k) => {
      const a = ap(lt, rt[k], 0.5), text = itemText(it), sub = typeof it === 'object' ? it.sub : null, y = top + k * rowH;
      ctx.save(); ctx.globalAlpha *= a; ctx.translate((1 - a) * -70, 0);
      card(170, y, 1580, rowH - 22, { r: 22, shadow: false, fill: rgba('card', TH.name === 'daylight' ? 1 : 0.85) });
      const cy = y + (rowH - 22) / 2;
      circle(250, cy, 32, rgba('accent', 0.18)); if (sp.numbered === false) circle(250, cy, 10, TH.accent); else txt(String(k + 1), 250, cy + 1, { size: 38, weight: 900, fill: TH.accent, align: 'center', base: 'middle' });
      const L = fitRich(text, 1300, 50, 34, 2, { weight: 700, head: false }); drawLayout(L, 320, cy - (sub ? 22 : 0), { align: 'left', hi: TH.accent2 });
      if (sub) txt(sub, 320, cy + 38, { size: 28, weight: 500, fill: TH.muted });
      ctx.restore();
    });
  };
};
SCENES.compare = (sp, S) => {
  const A = sp.left, B = sp.right, pts = [];
  const nA = (A.points || []).length, nB = (B.points || []).length, max = Math.max(nA, nB), order = [];
  for (let k = 0; k < max; k++) { if (k < nA) order.push({ side: 0, it: A.points[k] }); if (k < nB) order.push({ side: 1, it: B.points[k] }); }
  const rt = reveals(order.map((o) => o.it), S, { t0: 0.9 }); order.forEach((o, i) => { o.t = rt[i]; S.cue(rt[i], 'pop', 0.5); });
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    const top = sp.title ? 250 : 150, h = H - top - 200;
    [[A, 160, 'accent', 0], [B, 1000, 'accent2', 1]].forEach(([X, x, c, side]) => {
      const a = ap(lt, 0.1 + side * 0.15, 0.6); ctx.save(); ctx.globalAlpha *= a; ctx.translate(0, (1 - a) * 40);
      card(x, top, 760, h, { r: 30 }); rr(x, top, 760, 14, 7); ctx.fillStyle = col(c); ctx.fill();
      if (X.icon) drawIcon(X.icon, x + 90, top + 100, 90, { color: c, t: lt });
      txt(X.title, x + (X.icon ? 170 : 50), top + 112, { size: 54, weight: 900, head: true, fill: col(c) }); ctx.restore();
      order.filter((o) => o.side === side).forEach((o, k) => {
        const pa = ap(lt, o.t, 0.45), y = top + 200 + k * ((h - 230) / Math.max(nA, nB, 1));
        ctx.save(); ctx.globalAlpha *= pa; ctx.translate((1 - pa) * (side ? 60 : -60), 0);
        circle(x + 56, y + 14, 9, col(c)); const L = fitRich(itemText(o.it), 620, 44, 30, 2, { weight: 600, head: false }); drawLayout(L, x + 90, y + 14, { align: 'left', hi: TH.accent2 }); ctx.restore();
      });
    });
    const va = ap(lt, 0.3, 0.5); circle(W / 2, top + h / 2, 56 * eob(seg(lt, 0.3, 0.8)), TH.bg); circle(W / 2, top + h / 2, 48 * eob(seg(lt, 0.3, 0.8)), TH.ink);
    txt('VS', W / 2, top + h / 2 + 2, { size: 40, weight: 900, fill: '#FFFFFF', align: 'center', base: 'middle', alpha: va });
  };
};
SCENES.flow = (sp, S) => {
  const steps = sp.steps, n = steps.length, rt = reveals(steps, S, { t0: 0.7 }); rt.forEach((r) => S.cue(r, 'pop', 0.6));
  const vert = sp.dir === 'v';
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    const top = sp.title ? 240 : 140;
    steps.forEach((st, k) => {
      const a = ap(lt, rt[k], 0.55), c = ['accent', 'accent3', 'accent2'][k % 3];
      let x, y, w, h; if (vert) { w = 1100; h = clamp((H - top - 190) / n - 26, 90, 160); x = W / 2 - w / 2; y = top + k * (h + 26); } else { const gap = 70; w = (1620 - gap * (n - 1)) / n; h = 380; x = 150 + k * (w + gap); y = H / 2 - h / 2 + 20; }
      if (k > 0) {   // arrow from the previous step
        const pa = ap(lt, rt[k] - 0.25, 0.3); ctx.save(); ctx.globalAlpha *= pa; ctx.strokeStyle = TH.muted; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.beginPath(); if (vert) { ctx.moveTo(W / 2 - 11, y - 20); ctx.lineTo(W / 2, y - 7); ctx.lineTo(W / 2 + 11, y - 20); } else { const ax = x - 35; ctx.moveTo(ax - 22, y + h / 2); ctx.lineTo(ax + 22, y + h / 2); ctx.moveTo(ax + 8, y + h / 2 - 14); ctx.lineTo(ax + 22, y + h / 2); ctx.lineTo(ax + 8, y + h / 2 + 14); } ctx.stroke(); ctx.restore();
      }
      ctx.save(); ctx.globalAlpha *= a; ctx.translate(0, (1 - a) * 34); card(x, y, w, h, { r: 26 }); rr(x, y, vert ? 14 : w, vert ? h : 12, 6); ctx.fillStyle = col(c); ctx.fill();
      if (vert) { circle(x + 70, y + h / 2, 30, rgba(c, 0.2)); txt(String(k + 1), x + 70, y + h / 2 + 1, { size: 34, weight: 900, fill: col(c), align: 'center', base: 'middle' }); const L = fitRich(st.label, w - 200, 46, 30, 2, { weight: 800, head: false }); drawLayout(L, x + 130, y + h / 2 - (st.sub ? 16 : 0), { align: 'left' }); if (st.sub) txt(st.sub, x + 130, y + h / 2 + 34, { size: 30, weight: 500, fill: TH.muted }); }
      else { if (st.icon) drawIcon(st.icon, x + w / 2, y + 105, 100, { color: c, t: lt }); else txt(String(k + 1), x + w / 2, y + 105, { size: 90, weight: 900, fill: rgba(c, 0.8), align: 'center', base: 'middle', head: true });
        const L = fitRich(st.label, w - 50, 42, 28, 2, { weight: 800, head: false }); drawLayout(L, x + w / 2, y + 230, {}); if (st.sub) { const S2 = layoutRich(st.sub, w - 60, 28, { weight: 500, head: false, lh: 1.3 }); drawLayout(S2, x + w / 2, y + 296 + (S2.lines.length > 1 ? 10 : 0), { fill: TH.muted }); } }
      ctx.restore();
    });
  };
};
SCENES.rank = (sp, S) => (lt, d, t) => {
  bg(S, sp, t); const a = ap(lt, 0.0, 0.6), pop = eob(seg(lt, 0.0, 0.6));
  txt('#', 300, 560, { size: 200, weight: 900, head: true, fill: rgba('accent', 0.55), align: 'center', alpha: a });
  txt(String(sp.n), 510, 640, { size: 520 * (0.8 + 0.2 * pop), weight: 900, head: true, fill: TH.accent, align: 'center', alpha: a });
  const x = 860; kick(sp.kicker || (sp.total ? `${sp.n} of ${sp.total}` : 'Number ' + sp.n), x, 380, { alpha: ap(lt, 0.2, 0.5) });
  const L = fitRich(sp.title, 880, 96, 48, 3, { weight: 900, head: true }); drawLayout(L, x, 470 + L.h / 2 - 20, { align: 'left', alpha: ap(lt, 0.25, 0.6), hi: TH.accent2 });
  let y = 470 + L.h + 50; if (sp.sub) { const S2 = layoutRich(sp.sub, 880, 38, { weight: 500, head: false, lh: 1.35 }); drawLayout(S2, x, y + S2.h / 2 - 20, { align: 'left', fill: TH.muted, alpha: ap(lt, 0.6, 0.6) }); y += S2.h + 30; }
  if (sp.stat) { txt(sp.stat, x, y + 40, { size: 64, weight: 900, head: true, fill: TH.accent2, alpha: ap(lt, 0.9, 0.5) }); if (sp.statLabel) txt(sp.statLabel, x, y + 90, { size: 30, weight: 600, fill: TH.muted, alpha: ap(lt, 0.9, 0.5) }); }
  if (sp.total) for (let k = 0; k < sp.total; k++) { const done = k >= sp.total - sp.n, cur = k === sp.total - sp.n; circle(300 + k * (1320 / Math.max(1, sp.total - 1)) , 900, cur ? 14 : 9, done ? TH.accent : rgba(TH.text, 0.2)); }
};
SCENES.icons = (sp, S) => {
  const items = sp.items, rt = reveals(items, S, { t0: 0.5 }); rt.forEach((r) => S.cue(r, 'pop', 0.6));
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt); const n = items.length, gap = 50, w = Math.min(440, (1620 - gap * (n - 1)) / n), total = n * w + (n - 1) * gap, x0 = W / 2 - total / 2, top = sp.title ? 300 : 230, h = 520;
    items.forEach((it, k) => {
      const a = ap(lt, rt[k], 0.55), x = x0 + k * (w + gap), c = ['accent', 'accent2', 'accent3', 'accent'][k % 4];
      ctx.save(); ctx.globalAlpha *= a; ctx.translate(0, (1 - a) * 50); card(x, top, w, h, { r: 30 });
      circle(x + w / 2, top + 150, 92, rgba(c, 0.16)); drawIcon(it.icon, x + w / 2, top + 150, 112 * (0.85 + 0.15 * eob(seg(lt, rt[k], rt[k] + 0.6))), { color: c, t: lt });
      const L = fitRich(it.label, w - 50, 46, 30, 2, { weight: 800, head: false }); drawLayout(L, x + w / 2, top + 330, {});
      if (it.sub) { const S2 = layoutRich(it.sub, w - 70, 30, { weight: 500, head: false, lh: 1.3 }); drawLayout(S2, x + w / 2, top + 400 + S2.h / 2 - 16, { fill: TH.muted }); } ctx.restore();
    });
  };
};
SCENES.icon = (sp, S) => (lt, d, t) => {
  bg(S, sp, t); const right = sp.side === 'right', ix = right ? 1400 : 520, tx = right ? 190 : 900, a = ap(lt, 0.0, 0.6);
  const pulse = 1 + 0.03 * Math.sin(lt * 2.2); circle(ix, H / 2 - 20, 250 * pulse * (0.7 + 0.3 * a), rgba(sp.color || 'accent', 0.10)); circle(ix, H / 2 - 20, 190 * pulse, rgba(sp.color || 'accent', 0.14));
  drawIcon(sp.icon, ix, H / 2 - 20, 250 * (0.8 + 0.2 * eob(seg(lt, 0, 0.7))), { color: sp.color || 'accent', t: lt, lw: 5, alpha: a });
  const L = fitRich(sp.headline, 820, 92, 46, 4, { weight: 800, head: true }), sub = sp.sub ? layoutRich(sp.sub, 780, 40, { weight: 500, head: false, lh: 1.35 }) : null, tot = L.h + (sub ? sub.h + 30 : 0), y0 = H / 2 - 20 - tot / 2;
  if (sp.kicker) kick(sp.kicker, tx, y0 - 30, { alpha: ap(lt, 0.15, 0.5) });
  ctx.save(); const b = ap(lt, 0.2, 0.6); ctx.translate((right ? -1 : 1) * (1 - b) * -50, 0); drawLayout(L, tx, y0 + L.h / 2 - 12, { align: 'left', alpha: b, hi: TH.accent2 }); ctx.restore();
  if (sub) drawLayout(sub, tx, y0 + L.h + 30 + sub.h / 2 - 14, { align: 'left', fill: TH.muted, alpha: ap(lt, 0.7, 0.6) });
};

// ---------- timeline ----------
SCENES.timeline = (sp, S) => {
  const ev = sp.events, n = ev.length, rt = reveals(ev, S, { t0: 0.7 }); rt.forEach((r) => S.cue(r, 'pop', 0.6));
  const sp_ = n <= 5 ? 1480 / Math.max(1, n - 1) : 340, x0 = n <= 5 ? 220 : 240, ly = H / 2 + 40;
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    const prog = ev.map((e, k) => ap(lt, rt[k], 0.5)), p = prog.reduce((a, b) => a + b, 0), scroll = n <= 5 ? 0 : Math.max(0, x0 + Math.max(0, p - 1) * sp_ - 1300);
    ctx.save(); ctx.translate(-scroll, 0);
    const xEnd = x0 + (n - 1) * sp_; line([[x0 - 120, ly], [xEnd + 120, ly]], rgba(TH.text, 0.16), 8);
    line([[x0 - 120, ly], [x0 + Math.max(0, p - 1) * sp_, ly]], TH.accent, 8);
    ev.forEach((e, k) => {
      const x = x0 + k * sp_, a = prog[k], up = k % 2 === 0, c = [TH.accent, TH.accent2, TH.accent3][k % 3];
      circle(x, ly, 20 * eob(seg(lt, rt[k], rt[k] + 0.4)), TH.bg); circle(x, ly, 14 * eob(seg(lt, rt[k], rt[k] + 0.4)), c);
      ctx.save(); ctx.globalAlpha *= a; const dir = up ? -1 : 1; line([[x, ly + dir * 26], [x, ly + dir * (70 - (1 - a) * 20)]], rgba(c, 0.6), 4);
      const L = layoutRich(e.label, 330, 32, { weight: 600, head: false, lh: 1.25 }), blockH = 70 + L.h, y = up ? ly - 90 - blockH + 52 : ly + 96;
      card(x - 175, up ? ly - 90 - blockH : ly + 80, 350, blockH + 20, { r: 20, shadow: false, fill: rgba('card', 0.92) });
      txt(String(e.date), x, (up ? ly - 90 - blockH : ly + 80) + 56, { size: 46, weight: 900, head: true, fill: c, align: 'center' });
      drawLayout(L, x, (up ? ly - 90 - blockH : ly + 80) + 84 + L.h / 2 - 14, { fill: TH.text }); ctx.restore();
    });
    ctx.restore();
  };
};

// ---------- image (your own pictures, public-domain archive photos...) ----------
SCENES.image = (sp, S) => (lt, d, t) => {
  const img = MEDIA[sp.src]; fillAll(TH.ink); if (!img) { txt(`missing image ${sp.src}`, W / 2, H / 2, { size: 40, fill: '#fff', align: 'center' }); return; }
  const k = clamp(lt / d), mo = sp.motion || 'in', zin = mo === 'in' ? lerp(1.0, 1.12, k) : mo === 'out' ? lerp(1.12, 1.0, k) : 1.06;
  const fit = sp.fit === 'contain' ? 0.78 : 1, sc = (sp.fit === 'contain' ? Math.min((W * fit) / img.width, (H * fit) / img.height) : Math.max(W / img.width, H / img.height)) * zin;
  const dx = mo === 'left' ? lerp(40, -40, k) : mo === 'right' ? lerp(-40, 40, k) : 0, dy = mo === 'up' ? lerp(30, -30, k) : 0;
  if (sp.fit === 'contain') { backdrop(sp.backdrop || S.backdrop, t); ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 18; ctx.fillStyle = '#000'; ctx.fillRect(W / 2 - (img.width * sc) / 2 + dx, H / 2 - 30 - (img.height * sc) / 2 + dy, img.width * sc, img.height * sc); ctx.restore(); }
  ctx.save(); ctx.translate(W / 2 + dx, H / 2 + dy - (sp.fit === 'contain' ? 30 : 0)); ctx.scale(sc, sc); ctx.drawImage(img, -img.width / 2, -img.height / 2); ctx.restore();
  if (sp.fit !== 'contain') { const g = ctx.createLinearGradient(0, H * 0.55, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)'); ctx.fillStyle = g; ctx.fillRect(-100, 0, W + 200, H + 100); }
  if (sp.caption) { const a = ap(lt, 0.4, 0.5); card(150, 120, 20 + measure(sp.caption, 40, 800) + 20, 76, { r: 16, shadow: false, fill: 'rgba(5,8,15,0.7)', edge: null, alpha: a }); txt(sp.caption, 170, 172, { size: 40, weight: 800, fill: '#fff', alpha: a }); }
  if (sp.credit) txt(sp.credit, W - 60, H - 150, { size: 22, weight: 500, fill: 'rgba(255,255,255,0.75)', align: 'right', stroke: 'rgba(0,0,0,0.5)' });
};

// ---------- data scenes (maps.js, charts.js) ----------
SCENES.map = (sp, S) => mapScene(sp, S, { bg, reveals, heading, ap });
SCENES.chart = (sp, S) => chartScene(sp, S, { bg, reveals, heading, ap });

// ---------- outro ----------
SCENES.outro = (sp, S) => (lt, d, t) => {
  bg(S, { backdrop: sp.backdrop || 'stars' }, t); const a = ap(lt, 0.1, 0.7);
  const L = fitRich(sp.title || 'Thanks for watching', 1500, 120, 60, 2, { weight: 900, head: true }); drawLayout(L, W / 2, 380, { alpha: a, hi: TH.accent2 });
  if (sp.sub) txt(sp.sub, W / 2, 380 + L.h / 2 + 70, { size: 42, weight: 500, fill: TH.muted, align: 'center', alpha: ap(lt, 0.5, 0.6) });
  (sp.items || []).forEach((it, k) => { const x = W / 2 + (k - ((sp.items.length - 1) / 2)) * 560, b = ap(lt, 0.9 + k * 0.25, 0.55); ctx.save(); ctx.globalAlpha *= b; ctx.translate(0, (1 - b) * 30);
    card(x - 250, 640, 500, 150, { r: 75, fill: k ? TH.card : TH.accent, edge: k ? TH.cardEdge : null }); txt(it, x, 716, { size: 42, weight: 900, fill: k ? TH.text : TH.onAccent, align: 'center', base: 'middle' }); ctx.restore(); });
};
