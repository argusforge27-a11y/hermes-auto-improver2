// Thumbnail: drawn with the same engine (theme colours, fonts, icons), exported as a 1280×720 JPEG by `capture.mjs thumb`.
//   script.json "thumbnail": { "text": "THE *GREAT* STINK", "sub": "London, 1858", "icon": "warning", "image": "media/x.jpg", "backdrop": "rays", "color": "accent2" }
import { ctx, W, H, TH, col, rgba, fillAll, rr, txt, fitRich, drawLayout } from './lib.js';
import { backdrop } from './backdrops.js';
import { drawIcon } from './icons.js';
import { MEDIA } from './scenes.js';

export function drawThumb(sp, title) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const img = sp.image && MEDIA[sp.image];
  if (img) { const sc = Math.max(W / img.width, H / img.height); ctx.drawImage(img, W / 2 - (img.width * sc) / 2, H / 2 - (img.height * sc) / 2, img.width * sc, img.height * sc); const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(0,0,0,0.78)'); g.addColorStop(0.7, 'rgba(0,0,0,0.2)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
  else { backdrop(sp.backdrop || 'rays', 3); }
  const c = col(sp.color || 'accent2'), hasIcon = !!sp.icon, maxW = hasIcon ? 1100 : 1650;
  const L = fitRich(sp.text || title, maxW, 250, 110, 3, { weight: 900, head: true, lh: 1.04 });
  drawLayout(L, 110, 540 - (sp.sub ? 40 : 0), { align: 'left', fill: img ? '#FFFFFF' : TH.text, hi: c, stroke: img ? 'rgba(0,0,0,0.65)' : undefined });
  if (sp.sub) { rr(110, 540 - 40 + L.h / 2 + 30, 40 + 0, 0, 0); txt(sp.sub.toUpperCase(), 118, 540 - 40 + L.h / 2 + 100, { size: 54, weight: 900, ls: 6, fill: c, stroke: img ? 'rgba(0,0,0,0.6)' : undefined }); }
  if (hasIcon) { ctx.save(); ctx.shadowColor = rgba(c, 0.55); ctx.shadowBlur = 60; drawIcon(sp.icon, 1480, 520, 520, { color: c, lw: 5 }); ctx.restore(); }
}
