// Boot: fonts → script + theme → timing → world map + images → scenes. Then draw(t) renders film time t (a pure function of t).
// window.OP is the API tools/capture.mjs drives: ready, bootError, duration(), draw(t), frame(t, q), chapters(), shots(), captions(), cues(), warnings(), thumb().
import { W, H, setCtx, setTheme, TH, ctx, clamp, lerp, seg, eo, eio, rr, txt, rgba } from './core/lib.js';
import { THEMES } from './core/themes.js';
import { T, loadTiming, flattenScript, L } from './core/timing.js';
import { buildCaptions, drawCaption, captionList } from './core/captions.js';
import { SCENES, MEDIA } from './core/scenes.js';
import { initWorld } from './core/maps.js';
import { backdrop } from './core/backdrops.js';
import { drawThumb } from './core/thumb.js';

const cv = document.getElementById('cv');
setCtx(cv.getContext('2d'));
const OP = (window.OP = { ready: false });
let scenes = [], chapters = [], cues = [], warnings = [], SCRIPT = null, FLAT = null, HOOK = false;
const LEAD = 0.15;          // a picture arrives slightly before the first word of its line
const TRANS = 0.38;         // scene change length

function buildScenes() {
  const sceneStarts = [];
  FLAT.lines.forEach((ln, i) => {
    let spec = ln.scene;
    if (!spec && i === 0) spec = { type: 'title' };
    else if (!spec && ln.first) spec = { type: HOOK && ln.ch === 0 ? 'title' : 'chapter' };
    if (spec) sceneStarts.push({ spec, i0: i, ch: ln.ch });
  });
  scenes = sceneStarts.map((sc, k) => {
    const next = sceneStarts[k + 1], st = sc.i0 === 0 ? 0 : Math.max(0, L(sc.i0) - LEAD), end = next ? Math.max(st + 0.5, L(next.i0) - LEAD) : T.dur;
    const ch = FLAT.chapters[sc.ch], chNum = ch.n ?? (HOOK ? sc.ch : sc.ch + 1);
    const S = { i0: sc.i0, i1: (next ? next.i0 : FLAT.lines.length) - 1, st, end, d: end - st, ch: sc.ch, chNum, chTitle: ch.title, title: SCRIPT.title, script: SCRIPT,
      backdrop: ch.backdrop || TH.backdrop, cue: (lt, type, gain = 1) => cues.push({ t: +(st + lt).toFixed(3), type, gain }) };
    const make = SCENES[sc.spec.type]; if (!make) throw new Error(`line ${sc.i0}: unknown scene type "${sc.spec.type}". Types: ${Object.keys(SCENES).join(', ')}`);
    if (k > 0 && sc.spec.in !== 'cut' && !sc.spec.quiet && sc.spec.type !== 'callout') S.cue(0, 'whoosh', 0.5);
    const draw = make(sc.spec, S);
    if (S.d < 1.3) warnings.push(`scene ${k + 1} (line ${sc.i0}, ${sc.spec.type}) is only ${S.d.toFixed(1)} s long`);
    return { id: 'S' + String(k + 1).padStart(3, '0'), type: sc.spec.type, spec: sc.spec, st, end, d: S.d, i0: S.i0, i1: S.i1, ch: sc.ch, draw };
  });
  chapters = FLAT.chapters.map((c, i) => { const first = scenes.find((s) => s.ch === i); return { i, title: c.title, n: c.n ?? (HOOK ? i : i + 1), start: i === 0 ? 0 : first ? first.st : 0, mood: c.mood }; });
  chapters.forEach((c, i) => { c.end = i < chapters.length - 1 ? chapters[i + 1].start : T.dur; });
}

const sceneIndexAt = (t) => { let lo = 0, hi = scenes.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (scenes[m].st <= t) lo = m; else hi = m - 1; } return lo; };

function drawScene(sc, t, alpha, dx, scale) {
  const lt = t - sc.st, zoom = 1 + (sc.spec.zoom ?? 0.035) * eio(clamp(lt / sc.d));
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(W / 2 + dx, H / 2); ctx.scale(zoom * scale, zoom * scale); ctx.translate(-W / 2, -H / 2);
  sc.draw(lt, sc.d, t); ctx.restore();
}

function draw(t) {
  t = clamp(t, 0, T.dur - 1e-4);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.letterSpacing = '0px'; ctx.setLineDash([]);
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const i = sceneIndexAt(t), sc = scenes[i], lt = t - sc.st, tr = sc.spec.in === 'cut' ? 0 : TRANS;
  if (i > 0 && tr > 0 && lt < tr) {
    const prev = scenes[i - 1], p = eo(lt / tr), kind = sc.spec.in || 'fade';
    if (kind === 'push') { drawScene(prev, t, 1, -p * W * 0.22, 1); drawScene(sc, t, p, (1 - p) * W * 0.22, 1); }
    else if (kind === 'zoom') { drawScene(prev, t, 1, 0, 1); drawScene(sc, t, p, 0, lerp(1.12, 1, p)); }
    else { drawScene(prev, t, 1, 0, 1); drawScene(sc, t, p, 0, 1); }
  } else drawScene(sc, t, 1, 0, 1);
  ctx.globalAlpha = 1; ctx.letterSpacing = '0px';
  // source tag (stat / chart / quote ...): "source": "IMF, 2024"
  if (sc.spec.source) { const a = eo(seg(lt, 0.8, 1.3)); txt(/^source/i.test(sc.spec.source) ? sc.spec.source : `Source: ${sc.spec.source}`, 150, H - 168, { size: 24, weight: 600, fill: TH.muted, alpha: a }); }
  // chapter banner (a slim label that slides in for 3 s at the start of every chapter after the hook)
  const ch = chapters[sc.ch], first = scenes.find((s) => s.ch === sc.ch);
  if (SCRIPT.chapterBanner !== false && ch.i > 0 && first && first.type !== 'chapter' && t >= ch.start + 0.3 && t < ch.start + 3.6) {
    const a = eo(seg(t, ch.start + 0.3, ch.start + 0.8)) * (1 - eo(seg(t, ch.start + 3.0, ch.start + 3.6))), label = `${String(ch.n).padStart(2, '0')}  ${ch.title.toUpperCase()}`;
    ctx.save(); ctx.font = '800 26px Inter'; ctx.letterSpacing = '4px'; const w = ctx.measureText(label).width + 56; ctx.letterSpacing = '0px'; ctx.restore();
    ctx.save(); ctx.globalAlpha = a; ctx.translate((1 - a) * -40, 0); rr(0, 56, w + 20, 60, [0, 30, 30, 0]); ctx.fillStyle = TH.accent; ctx.fill();
    txt(label, 34, 94, { size: 26, weight: 800, fill: TH.onAccent, ls: 4 }); ctx.restore();
  }
  // fade from / to black
  const fade = Math.min(clamp(t / 0.5), clamp((T.dur - t) / 1.0));
  if (fade < 1) { ctx.fillStyle = '#000'; ctx.globalAlpha = 1 - fade; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
  drawCaption(t, SCRIPT.captions);
}

async function loadImage(src) {
  await new Promise((res, rej) => { const im = new Image(); im.onload = () => { MEDIA[src] = im; res(); }; im.onerror = () => rej(new Error(`image not found: ${src} (put it in media/)`)); im.src = src; });
}

(async () => {
  try {
    await Promise.all([400, 500, 600, 700, 800, 900].map((w) => document.fonts.load(`${w} 40px Inter`)).concat(document.fonts.load('700 40px Caladea')));
    SCRIPT = await (await fetch('script.json', { cache: 'no-store' })).json();
    const th = THEMES[SCRIPT.theme || 'midnight']; if (!th) throw new Error(`unknown theme "${SCRIPT.theme}". Themes: ${Object.keys(THEMES).join(', ')}`);
    setTheme(th); await loadTiming(); FLAT = flattenScript(SCRIPT);
    HOOK = FLAT.chapters[0].hook === true || (FLAT.chapters[0].hook === undefined && FLAT.chapters.length > 1 && /hook|cold open|intro/i.test(FLAT.chapters[0].title || ''));
    if (FLAT.lines.length !== T.lines.length) throw new Error(`script.json has ${FLAT.lines.length} lines but data/lines.json has ${T.lines.length}: re-run ./lf voice then ./lf words (or ./lf estimate) after editing the script`);
    initWorld(await (await fetch('data/world.json')).json());
    const srcs = new Set(); FLAT.lines.forEach((l) => l.scene?.src && srcs.add(l.scene.src)); if (SCRIPT.thumbnail?.image) srcs.add(SCRIPT.thumbnail.image);
    await Promise.all([...srcs].map(loadImage));
    buildCaptions(FLAT); buildScenes();
    OP.script = SCRIPT; OP.duration = () => T.dur; OP.draw = draw;
    OP.frame = (t, q = 0.92) => { draw(t); return cv.toDataURL('image/jpeg', q); };
    OP.thumb = (q = 0.95) => { drawThumb(SCRIPT.thumbnail || { text: SCRIPT.title }, SCRIPT.title); return cv.toDataURL('image/jpeg', q); };
    OP.shots = () => scenes.map((s) => ({ id: s.id, type: s.type, at: +s.st.toFixed(3), end: +s.end.toFixed(3), ch: s.ch, line: s.i0 }));
    OP.chapters = () => chapters.map((c) => ({ i: c.i, title: c.title, start: +c.start.toFixed(3), end: +c.end.toFixed(3), mood: c.mood || null }));
    OP.captions = () => captionList().map((c) => ({ s: +c.s.toFixed(3), e: +c.e.toFixed(3), text: c.words.map((w) => w.w).join(' ') }));
    OP.cues = () => cues.slice().sort((a, b) => a.t - b.t);
    OP.warnings = () => warnings;
    OP.ready = true;
    const q = new URLSearchParams(location.search);
    if (!q.has('capture')) {   // preview: real time with sound; ?t=12.3 holds a frame
      if (q.has('t')) draw(+q.get('t'));
      else {
        const audio = new Audio('data/mix.wav'); let t0 = null; const btn = document.getElementById('play'); btn.hidden = false;
        btn.onclick = () => { btn.hidden = true; t0 = performance.now(); audio.currentTime = 0; audio.play().catch(() => {}); };
        const loop = (now) => { const t = t0 == null ? 0 : (now - t0) / 1000; draw(t); if (t0 != null && t > T.dur) { t0 = null; btn.hidden = false; } requestAnimationFrame(loop); };
        requestAnimationFrame(loop);
      }
    }
  } catch (e) { OP.bootError = String(e && e.stack || e); console.error(e); }
})();
