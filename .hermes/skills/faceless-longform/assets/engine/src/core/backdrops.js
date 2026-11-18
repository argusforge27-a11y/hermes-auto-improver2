// Animated backgrounds. backdrop(kind, t) fills the whole canvas (plus the margin the camera can reveal).
// kinds: drift · grid · dots · rays · contours · paper · stars · plain.   Chapter or scene "backdrop" overrides the theme default.
import { ctx, W, H, TH, clamp, rnd, TAU, rgba, fillAll } from './lib.js';

let paperTex = null, grainTex = null;
function makePaper() {
  const mk = (n) => { const c = document.createElement('canvas'); c.width = c.height = n; return c; };
  paperTex = mk(512); const g = paperTex.getContext('2d');
  for (let i = 0; i < 5200; i++) { g.fillStyle = `rgba(${rnd(i) > 0.5 ? '90,60,20' : '255,250,235'},${0.025 + rnd(i + 9) * 0.05})`; g.fillRect(rnd(i + 1) * 512, rnd(i + 2) * 512, 1 + rnd(i + 3) * 2.2, 1 + rnd(i + 4) * 2.2); }
  for (let i = 0; i < 140; i++) { g.strokeStyle = `rgba(90,60,20,${0.02 + rnd(i + 7) * 0.035})`; g.lineWidth = 1; g.beginPath(); const x = rnd(i + 5) * 512, y = rnd(i + 6) * 512; g.moveTo(x, y); g.lineTo(x + (rnd(i + 8) - 0.5) * 70, y + (rnd(i + 10) - 0.5) * 22); g.stroke(); }
  grainTex = mk(256); const h = grainTex.getContext('2d');
  for (let i = 0; i < 2600; i++) { h.fillStyle = `rgba(255,255,255,${rnd(i) * 0.05})`; h.fillRect(rnd(i + 1) * 256, rnd(i + 2) * 256, 1.4, 1.4); }
}

function base(t, a = TH.bg, b = TH.bg2) {
  const g = ctx.createLinearGradient(-200, -200, W + 200, H + 200); g.addColorStop(0, a); g.addColorStop(1, b);
  ctx.fillStyle = g; ctx.fillRect(-400, -400, W + 800, H + 800);
}
function vignette(k = 0.32) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.72); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, rgba(TH.ink, k));
  ctx.fillStyle = g; ctx.fillRect(-400, -400, W + 800, H + 800);
}
function blob(x, y, r, c, a) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, rgba(c, a)); g.addColorStop(1, rgba(c, 0));
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
}

const KINDS = {
  plain() { fillAll(TH.bg); },
  drift(t) {
    base(t); const s = t * 0.12;
    blob(W * (0.2 + 0.1 * Math.sin(s)), H * (0.25 + 0.1 * Math.cos(s * 1.3)), 760, 'accent', 0.16);
    blob(W * (0.82 + 0.08 * Math.cos(s * 0.9)), H * (0.78 + 0.08 * Math.sin(s)), 820, 'accent3', 0.14);
    blob(W * (0.55 + 0.12 * Math.sin(s * 0.7 + 2)), H * (0.1 + 0.06 * Math.cos(s)), 560, 'accent2', 0.07);
    vignette(0.3);
  },
  grid(t) {
    base(t); ctx.strokeStyle = TH.grid; ctx.lineWidth = 2; const sp = 96, ox = (t * 14) % sp, oy = (t * 9) % sp;
    ctx.beginPath(); for (let x = -sp + ox; x < W + sp; x += sp) { ctx.moveTo(x, -100); ctx.lineTo(x, H + 100); } for (let y = -sp + oy; y < H + sp; y += sp) { ctx.moveTo(-100, y); ctx.lineTo(W + 100, y); } ctx.stroke();
    blob(W * 0.5, H * 0.5, 900, 'accent', 0.08); vignette(0.35);
  },
  dots(t) {
    base(t); const sp = 54, ox = (t * 6) % sp;
    for (let y = 20; y < H + 40; y += sp) for (let x = -sp + ox; x < W + sp; x += sp) {
      const w = 0.5 + 0.5 * Math.sin(x * 0.006 + y * 0.004 + t * 0.55); ctx.fillStyle = rgba(TH.ink, 0.05 + 0.07 * w); ctx.beginPath(); ctx.arc(x, y, 2.2 + 2.4 * w, 0, TAU); ctx.fill();
    }
    blob(W * 0.85, H * 0.15, 700, 'accent', 0.10); blob(W * 0.1, H * 0.9, 600, 'accent2', 0.08);
  },
  rays(t) {
    base(t); ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(-0.5);
    for (let i = 0; i < 6; i++) { const x = ((i * 520 + t * 24) % 3120) - 1560; ctx.fillStyle = rgba(i % 2 ? 'accent' : 'accent3', 0.05); ctx.fillRect(x, -1500, 190 + 40 * Math.sin(t * 0.3 + i), 3000); }
    ctx.restore(); vignette(0.3);
  },
  contours(t) {
    base(t); ctx.lineWidth = 2;
    for (let k = 0; k < 11; k++) {
      ctx.beginPath(); for (let x = -60; x <= W + 60; x += 40) { const y = H * (0.08 + k * 0.088) + 34 * Math.sin(x * 0.0042 + k * 0.7 + t * 0.2) + 20 * Math.sin(x * 0.011 - k + t * 0.13); x === -60 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.strokeStyle = rgba('accent', 0.07 + 0.02 * (k % 3)); ctx.stroke();
    }
    vignette(0.3);
  },
  stars(t) {
    base(t, TH.bg, TH.bg2);
    for (let i = 0; i < 110; i++) { const x = rnd(i) * (W + 100) - 50, y = rnd(i + 3) * (H + 100) - 50, r = 0.8 + rnd(i + 5) * 2.4, tw = 0.5 + 0.5 * Math.sin(t * (0.4 + rnd(i + 7)) + i); ctx.fillStyle = rgba(TH.text, 0.1 + 0.35 * tw * rnd(i + 9)); ctx.beginPath(); ctx.arc(x - ((t * (4 + 10 * rnd(i + 4))) % 60), y, r, 0, TAU); ctx.fill(); }
    blob(W * 0.5, H * 0.45, 800, 'accent', 0.10); vignette(0.35);
  },
  paper(t) {
    if (!paperTex) makePaper();
    base(t); ctx.fillStyle = ctx.createPattern(paperTex, 'repeat'); ctx.fillRect(-400, -400, W + 800, H + 800);
    const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, W * 0.7); g.addColorStop(0, 'rgba(255,245,215,0)'); g.addColorStop(1, 'rgba(110,70,20,0.30)'); ctx.fillStyle = g; ctx.fillRect(-400, -400, W + 800, H + 800);
  },
};
export const BACKDROPS = Object.keys(KINDS);
export function backdrop(kind, t) { const f = KINDS[kind || TH.backdrop] || KINDS.plain; f(t); }
