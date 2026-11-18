// Map scenes: country outlines (Natural Earth 110m, public domain) in a Mercator view that zooms in on a region,
// with highlighted countries, labels, pins and animated routes.
//   { type: "map", focus: "europe" | ["FRA","DEU"] | [lonMin, latMin, lonMax, latMax], highlight: ["FRA"], labels: true,
//     pins: [{ name, lon, lat, at }], routes: [{ from: [lon, lat], to: [lon, lat], at, label }], title }
import { ctx, W, H, TH, col, rgba, clamp, lerp, seg, eo, eio, eob, TAU, circle, line, txt, measure, rr } from './lib.js';

export const WORLD = { countries: [], ready: false };
const REGIONS = {
  world: [-170, -56, 190, 78], europe: [-12, 34, 42, 71], asia: [58, -11, 150, 56], africa: [-20, -36, 52, 38], 'north-america': [-170, 8, -50, 72],
  'south-america': [-84, -57, -32, 14], 'middle-east': [25, 10, 66, 42], india: [66, 5, 100, 38], uk: [-11, 49, 3, 61], oceania: [110, -48, 180, -5], 'east-asia': [95, 15, 150, 55],
};
const merc = (lat) => (180 / Math.PI) * Math.log(Math.tan(Math.PI / 4 + (clamp(lat, -82, 82) * Math.PI) / 360));

/** build Path2D per country in map units (x = longitude°, y = −Mercator°) — called once at boot with data/world.json */
export function initWorld(data) {
  WORLD.countries = data.filter((c) => c.iso !== 'ATA').map((c) => {
    const path = new Path2D(), polys = [];
    for (const poly of c.p) {
      const r0 = poly[0], pts = []; for (let i = 0; i < r0.length; i += 2) pts.push([r0[i] / 10, r0[i + 1] / 10]);
      let area = 0; for (let i = 0; i < pts.length; i++) { const [x1, y1] = pts[i], [x2, y2] = pts[(i + 1) % pts.length]; area += x1 * y2 - x2 * y1; }
      polys.push({ pts, area: Math.abs(area) / 2 });
      for (const ring of poly) { for (let i = 0; i < ring.length; i += 2) { const x = ring[i] / 10, y = -merc(ring[i + 1] / 10); i ? path.lineTo(x, y) : path.moveTo(x, y); } path.closePath(); }
    }
    const big = Math.max(...polys.map((p) => p.area)), main = polys.filter((p) => p.area >= big * 0.35), bb = { x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9 };
    for (const p of main) for (const [x, y] of p.pts) { bb.x0 = Math.min(bb.x0, x); bb.x1 = Math.max(bb.x1, x); bb.y0 = Math.min(bb.y0, y); bb.y1 = Math.max(bb.y1, y); }
    const lp = polys.find((p) => p.area === big).pts, cx = lp.reduce((a, p) => a + p[0], 0) / lp.length, cy = lp.reduce((a, p) => a - merc(p[1]), 0) / lp.length;
    return { iso: c.iso, iso2: c.iso2, name: c.name, path, bb, cx, cy };
  });
  WORLD.ready = true;
}
const byKey = (k) => WORLD.countries.find((c) => c.iso === k || c.iso2 === k || c.name.toLowerCase() === String(k).toLowerCase());

function viewFor(focus) {
  let b;
  if (typeof focus === 'string') { b = REGIONS[focus]; if (!b) throw new Error(`unknown map region "${focus}". Use one of ${Object.keys(REGIONS).join(', ')}, country codes ["FRA"], or [lonMin, latMin, lonMax, latMax]`); }
  else if (focus.length === 4 && typeof focus[0] === 'number') b = focus;
  else {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;   // y in Mercator degrees (north = larger)
    for (const k of focus) { const c = byKey(k); if (!c) throw new Error(`unknown country "${k}" (use ISO-3 codes such as FRA, IND, USA)`); x0 = Math.min(x0, c.bb.x0); x1 = Math.max(x1, c.bb.x1); y0 = Math.min(y0, -c.bb.y1); y1 = Math.max(y1, -c.bb.y0); }
    const padX = Math.max(4, (x1 - x0) * 0.4), padY = Math.max(4, (y1 - y0) * 0.4);
    return fit(x0 - padX, x1 + padX, y0 - padY, y1 + padY, true);
  }
  return fit(b[0], b[2], b[1], b[3], false);
}
/** x0,x1 = longitudes; y0,y1 = latitudes (isLat) or already mercator degrees */
function fit(x0, x1, y0, y1, merc_) {
  const my0 = merc_ ? y0 : merc(y0), my1 = merc_ ? y1 : merc(y1), RW = 1560, RH = 700;
  const s = Math.min(RW / (x1 - x0), RH / Math.abs(my1 - my0)); return { cx: (x0 + x1) / 2, cy: -(my0 + my1) / 2, s };
}

export function mapScene(sp, S, { bg, reveals, heading, ap }) {
  const focus = sp.focus || 'world', V = viewFor(focus), hl = new Set((sp.highlight || []).map((k) => byKey(k)?.iso).filter(Boolean));
  for (const k of sp.highlight || []) if (!byKey(k)) throw new Error(`map: unknown country "${k}" in highlight`);
  const pins = sp.pins || [], routes = sp.routes || [], items = [...pins, ...routes], rt = reveals(items, S, { t0: 1.4, tail: 1.2 }); rt.forEach((r) => S.cue(r, 'pop', 0.6));
  const zoomIn = sp.zoom !== false;
  return (lt, d, t) => {
    bg(S, sp, t); heading(sp.title, lt);
    if (!WORLD.ready) return;
    const k = zoomIn ? eio(seg(lt, 0, 1.8)) : 1, s = V.s * lerp(0.7, 1, k), cx = V.cx, cy = V.cy;
    const tx = (lon) => W / 2 + (lon - cx) * s, ty = (lat) => H / 2 - 10 + (-merc(lat) - cy) * s;
    ctx.save(); ctx.translate(W / 2, H / 2 - 10); ctx.scale(s, s); ctx.translate(-cx, -cy);
    // graticule
    ctx.lineWidth = 1.5 / s; ctx.strokeStyle = rgba(TH.text, 0.06); ctx.beginPath();
    for (let lon = -180; lon <= 180; lon += 30) { ctx.moveTo(lon, -merc(80)); ctx.lineTo(lon, -merc(-80)); }
    for (let lat = -60; lat <= 80; lat += 20) { ctx.moveTo(-180, -merc(lat)); ctx.lineTo(180, -merc(lat)); } ctx.stroke();
    ctx.lineJoin = 'round'; ctx.lineWidth = 1.6 / s;
    for (const c of WORLD.countries) {
      const on = hl.has(c.iso), a = on ? ap(lt, 0.5, 0.8) : 1; ctx.fillStyle = on ? rgba('accent', 0.35 + 0.5 * a) : TH.land; ctx.strokeStyle = on ? rgba('accent', 0.95) : TH.landEdge; ctx.lineWidth = (on ? 2.6 : 1.4) / s;
      ctx.fill(c.path); ctx.stroke(c.path);
    }
    ctx.restore();
    if (sp.labels !== false) for (const iso of hl) { const c = WORLD.countries.find((q) => q.iso === iso); const a = ap(lt, 1.0, 0.6), lx = W / 2 + (c.cx - cx) * s, ly = H / 2 - 10 + (c.cy - cy) * s; if (pins.some((p) => Math.hypot(tx(p.lon) - lx, ty(p.lat) - ly) < 130)) continue; txt(c.name.toUpperCase(), lx, ly, { size: clamp(11 * Math.sqrt(s), 26, 46), weight: 900, ls: 3, align: 'center', base: 'middle', alpha: a, stroke: rgba(TH.bg, 0.8) }); }
    pins.forEach((p, i) => {
      const a = ap(lt, rt[i], 0.4), x = tx(p.lon), y = ty(p.lat), c = p.color || 'accent2';
      const ring = ((lt - rt[i]) % 1.6) / 1.6; if (lt > rt[i]) { ctx.save(); ctx.globalAlpha *= (1 - ring) * 0.6; ctx.strokeStyle = col(c); ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(x, y, 14 + 40 * ring, 0, TAU); ctx.stroke(); ctx.restore(); }
      circle(x, y, 17 * eob(seg(lt, rt[i], rt[i] + 0.4)), TH.bg); circle(x, y, 11 * eob(seg(lt, rt[i], rt[i] + 0.4)), col(c));
      if (p.name) { const w = measure(p.name, 34, 800) + 36, left = x + w + 30 > W - 100; ctx.save(); ctx.globalAlpha *= a; card2(left ? x - 26 - w : x + 26, y - 30, w, 60, p.name); ctx.restore(); }
    });
    routes.forEach((r, j) => {
      const i = pins.length + j, p = clamp((lt - rt[i]) / 1.5), e = eio(p), x0 = tx(r.from[0]), y0 = ty(r.from[1]), x1 = tx(r.to[0]), y1 = ty(r.to[1]), mx = (x0 + x1) / 2, my = (y0 + y1) / 2 - Math.hypot(x1 - x0, y1 - y0) * 0.22;
      if (p <= 0) return; const pts = []; for (let q = 0; q <= 40; q++) { const u = (q / 40) * e; pts.push([(1 - u) * (1 - u) * x0 + 2 * (1 - u) * u * mx + u * u * x1, (1 - u) * (1 - u) * y0 + 2 * (1 - u) * u * my + u * u * y1]); }
      line(pts, col(r.color || 'accent2'), 7); circle(x0, y0, 10, col(r.color || 'accent2')); const [hx, hy] = pts[pts.length - 1]; circle(hx, hy, 14, col(r.color || 'accent2'));
      if (r.label && p > 0.9) { const a = ap(lt, rt[i] + 1.4, 0.4); ctx.save(); ctx.globalAlpha *= a; card2(mx - (measure(r.label, 32, 800) + 36) / 2, my - 52, measure(r.label, 32, 800) + 36, 56, r.label, 32); ctx.restore(); }
    });
  };
}
function card2(x, y, w, h, label, size = 34) { rr(x, y, w, h, 14); ctx.fillStyle = rgba(TH.ink, 0.86); ctx.fill(); txt(label, x + w / 2, y + h / 2 + 1, { size, weight: 800, fill: '#fff', align: 'center', base: 'middle' }); }
