// Chart scenes: bar · hbar · line · donut, animated in on the narration.
//   { type: "chart", kind: "bar", title, labels: [..], values: [..], unit: "%", prefix: "$", highlight: 2 | [0,3], source: "...", max: 100 }
//   line: series: [{ name, values }]  (labels = x axis)       donut: labels + values (share of the total)
import { ctx, W, H, TH, col, rgba, clamp, lerp, seg, eo, eio, eob, TAU, circle, line, txt, measure, rr, card, fmt, fitRich, drawLayout } from './lib.js';

const niceMax = (v) => { const p = Math.pow(10, Math.floor(Math.log10(v || 1))), f = v / p; return ([1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].find((s) => f <= s + 1e-9) || 10) * p; };
const PAL = () => [TH.accent, TH.accent2, TH.accent3, TH.danger, TH.good];

export function chartScene(sp, S, { bg, reveals, heading, ap }) {
  const kind = sp.kind || 'bar', hlSet = new Set([].concat(sp.highlight ?? [])), labels = sp.labels || [];
  const series = sp.series || [{ name: '', values: sp.values }], n = labels.length || series[0].values.length;
  const rt = kind === 'line' ? [0.8] : reveals(labels.map((l, i) => (sp.at && sp.at[i] ? { at: sp.at[i] } : l)), S, { t0: 0.8, tail: 1.2 });
  rt.forEach((r) => S.cue(r, 'pop', 0.35));
  const fv = (v) => `${sp.prefix || ''}${fmt(v, sp.decimals ?? (Number.isInteger(v) ? 0 : 1))}${sp.unit || ''}`;
  const maxV = sp.max ?? niceMax(Math.max(...series.flatMap((s) => s.values)) * (kind === 'line' ? 1.05 : 1.0));
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    const x0 = 250, x1 = 1700, y0 = sp.title ? 330 : 230, y1 = 820, vals = series[0].values;
    if (kind === 'bar') {
      ctx.lineWidth = 2; for (let k = 0; k <= 4; k++) { const y = y1 - ((y1 - y0) * k) / 4; line([[x0, y], [x1, y]], rgba(TH.text, 0.12), 2); txt(fv((maxV * k) / 4), x0 - 22, y + 10, { size: 26, weight: 600, fill: TH.muted, align: 'right' }); }
      const bw = Math.min(150, ((x1 - x0) / n) * 0.62), gap = (x1 - x0) / n;
      vals.forEach((v, i) => {
        const a = eo(seg(lt, rt[i], rt[i] + 0.8)), h = ((y1 - y0) * v / maxV) * a, x = x0 + gap * (i + 0.5) - bw / 2, c = hlSet.size ? (hlSet.has(i) ? TH.accent2 : rgba('accent', 0.55)) : PAL()[0];
        ctx.save(); ctx.shadowColor = rgba(c, 0.35); ctx.shadowBlur = 24; rr(x, y1 - h, bw, Math.max(0, h), [14, 14, 0, 0]); ctx.fillStyle = c; ctx.fill(); ctx.restore();
        txt(labels[i], x + bw / 2, y1 + 48, { size: 28, weight: 700, align: 'center', alpha: ap(lt, rt[i], 0.4) });
        if (a > 0.05) txt(fv(lerp(0, v, a)), x + bw / 2, y1 - h - 18, { size: 34, weight: 900, align: 'center', alpha: clamp(a * 2) });
      });
    } else if (kind === 'hbar') {
      const rowH = (y1 - y0 + 40) / n, lw = 300; const bx = x0 + lw - 80, bmax = x1 - bx - 170;
      vals.forEach((v, i) => {
        const a = eo(seg(lt, rt[i], rt[i] + 0.8)), y = y0 - 10 + i * rowH, c = hlSet.size ? (hlSet.has(i) ? TH.accent2 : rgba('accent', 0.55)) : TH.accent, h = Math.min(54, rowH - 18);
        txt(labels[i], bx - 24, y + rowH / 2 + 10, { size: 32, weight: 700, align: 'right', alpha: ap(lt, rt[i], 0.4) });
        rr(bx, y + (rowH - h) / 2, bmax * (v / maxV) * a, h, 12); ctx.fillStyle = c; ctx.fill();
        if (a > 0.05) txt(fv(lerp(0, v, a)), bx + bmax * (v / maxV) * a + 20, y + rowH / 2 + 12, { size: 34, weight: 900, alpha: clamp(a * 2) });
      });
    } else if (kind === 'line') {
      const p = eio(seg(lt, rt[0], rt[0] + 2.6)); for (let k = 0; k <= 4; k++) { const y = y1 - ((y1 - y0) * k) / 4; line([[x0, y], [x1, y]], rgba(TH.text, 0.1), 2); txt(fv((maxV * k) / 4), x0 - 22, y + 10, { size: 26, weight: 600, fill: TH.muted, align: 'right' }); }
      labels.forEach((l, i) => { if (n <= 14 || i % Math.ceil(n / 12) === 0) txt(String(l), x0 + ((x1 - x0) * i) / Math.max(1, n - 1), y1 + 46, { size: 26, weight: 600, fill: TH.muted, align: 'center' }); });
      series.forEach((s, si) => {
        const c = PAL()[si % 5], pts = s.values.map((v, i) => [x0 + ((x1 - x0) * i) / Math.max(1, n - 1), y1 - ((y1 - y0) * v) / maxV]), upto = p * (pts.length - 1), part = [];
        for (let i = 0; i < pts.length; i++) { if (i <= upto) part.push(pts[i]); else { const f = upto - (i - 1); if (f > 0 && i > 0) part.push([lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)]); break; } }
        if (part.length > 1) { ctx.save(); ctx.shadowColor = rgba(c, 0.5); ctx.shadowBlur = 20; line(part, c, 8); ctx.restore(); const e = part[part.length - 1]; circle(e[0], e[1], 14, TH.bg); circle(e[0], e[1], 9, c); txt(fv(s.values[Math.min(pts.length - 1, Math.round(upto))]), e[0], e[1] - 30, { size: 34, weight: 900, align: 'center' }); }
        if (series.length > 1) { txt(s.name, x1 - 10, y0 - 30 + si * 40, { size: 30, weight: 800, fill: c, align: 'right' }); }
      });
    } else if (kind === 'donut') {
      const tot = vals.reduce((a, b) => a + b, 0), cx = 640, cy = 560, R = 270; let a0 = -Math.PI / 2;
      vals.forEach((v, i) => { const a = eio(seg(lt, rt[i], rt[i] + 0.9)), sw = (v / tot) * TAU * a; ctx.strokeStyle = PAL()[i % 5]; ctx.lineWidth = 70; ctx.lineCap = 'butt'; ctx.beginPath(); ctx.arc(cx, cy, R, a0, a0 + sw); ctx.stroke(); a0 += (v / tot) * TAU; });
      txt(sp.center || fv(tot), cx, cy + 20, { size: 90, weight: 900, head: true, align: 'center' }); if (sp.centerLabel) txt(sp.centerLabel, cx, cy + 76, { size: 30, weight: 600, fill: TH.muted, align: 'center' });
      vals.forEach((v, i) => { const a = ap(lt, rt[i], 0.5), y = 330 + i * 92; ctx.save(); ctx.globalAlpha *= a; circle(1130, y, 18, PAL()[i % 5]); txt(labels[i], 1170, y + 12, { size: 40, weight: 700 }); txt(`${fmt((v / tot) * 100, 0)}%`, 1700, y + 12, { size: 40, weight: 900, align: 'right' }); ctx.restore(); });
    }
  };
}
