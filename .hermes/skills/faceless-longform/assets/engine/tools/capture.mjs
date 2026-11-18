// Frame-exact capture through headless Chrome, built for LONG videos: chapters render as separate segments (in parallel,
// resumable) and are joined at the end. No npm packages (Node 22+). Run from the project folder.
//   node tools/capture.mjs check [step=0.5]                       boot, list chapters + scenes + captions, draw the whole film, report errors
//   node tools/capture.mjs cues                                   write data/cues.json + data/chapters.json (for mix.py and the YouTube chapter list)
//   node tools/capture.mjs sheets [step=3] [cols=6] [--chapter N]  contact sheets review/chNN.jpg (a frame every `step` s, time + scene stamped)
//   node tools/capture.mjs frames review/full "12.5,80.2"        full-size JPEGs of those times
//   node tools/capture.mjs thumb [renders/thumbnail.jpg]          the thumbnail (1280x720 JPEG) from script.json "thumbnail"
//   node tools/capture.mjs render [--jobs N] [--chapters 1,3] [--draft] [--force] [--out renders/final.mp4]
//        renders every chapter that changed (cached in renders/segments/), then joins them with data/mix.wav
//   node tools/capture.mjs segment <chapter> [--draft]            render one chapter (what `render` runs per worker)
//   node tools/capture.mjs assemble [--out renders/final.mp4] [--draft]   join existing segments + audio only
//   node tools/capture.mjs preview                                serve the project and print a URL to watch it in a browser
// --draft = 15 fps, lower quality, fastest encoder (about 3x quicker): for checking pacing, not for upload.
// Env: CHROME=/path/to/chrome · FPS=30 · JOBS=n · SOFTWARE_GL=1 · CHROME_HEADLESS=new|shell
import { spawn, spawnSync } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2), flags = new Set(args.filter((a) => a.startsWith('--') && !/^--(jobs|chapters|out|chapter)$/.test(a)));
const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const valueIdx = new Set(['--jobs', '--chapters', '--out', '--chapter'].flatMap((n) => { const i = args.indexOf(n); return i >= 0 ? [i, i + 1] : []; }));
const [mode, ...rest] = args.filter((a, i) => !a.startsWith('--') && !valueIdx.has(i));
const DRAFT = flags.has('--draft');
const FPS = DRAFT ? 15 : +(process.env.FPS || 30);
function findChrome() {
  const fixed = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium',
    '/usr/bin/chromium-browser', '/snap/bin/chromium', '/usr/bin/microsoft-edge', 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find((p) => p && fs.existsSync(p));
  if (fixed) return fixed;
  // browsers downloaded by Playwright / Puppeteer (common on servers and agent machines): prefer a full chrome, then the headless shell
  const home = os.homedir(), roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(home, '.cache/ms-playwright'), path.join(home, 'Library/Caches/ms-playwright'),
    path.join(home, 'AppData/Local/ms-playwright'), '/opt/pw-browsers', '/ms-playwright', path.join(home, '.cache/puppeteer')].filter((r) => r && fs.existsSync(r));
  const names = ['chrome', 'chrome.exe', 'chrome-headless-shell', 'chrome-headless-shell.exe', 'headless_shell'], found = [];
  const look = (d, depth) => { if (depth > 5) return; let es = []; try { es = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of es) { const f = path.join(d, e.name); if (e.isDirectory()) look(f, depth + 1); else if (names.includes(e.name)) found.push(f); } };
  roots.forEach((r) => look(r, 0));
  return found.sort((a, b) => names.indexOf(path.basename(a)) - names.indexOf(path.basename(b)))[0];
}
const CHROME = findChrome();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const pad = (n) => String(n).padStart(2, '0');
const hms = (s) => `${Math.floor(s / 60)}:${pad(Math.floor(s % 60))}`;

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.otf': 'font/otf', '.ttf': 'font/ttf',
  '.woff2': 'font/woff2', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
function serve(port = 0) {
  return new Promise((res) => {
    const srv = http.createServer((req, r) => {
      const u = decodeURIComponent(req.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); r.end(); return; }
      r.writeHead(200, { 'Content-Type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      fs.createReadStream(f).pipe(r);
    });
    srv.listen(port, '127.0.0.1', () => res(srv));
  });
}

async function launchChrome(noSandbox) {
  const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'lf-chrome-'));
  const shell = /headless[-_]shell/.test(path.basename(CHROME)), head = process.env.CHROME_HEADLESS || (shell ? 'shell' : 'new');
  const chrome = spawn(CHROME, [shell ? '--headless' : `--headless=${head}`, '--remote-debugging-port=0', `--user-data-dir=${prof}`, '--no-first-run', '--no-default-browser-check',
    '--hide-scrollbars', '--window-size=1920,1080', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage', ...(process.env.SOFTWARE_GL ? ['--use-angle=swiftshader'] : []),
    ...(noSandbox || process.env.CHROME_NO_SANDBOX || process.getuid?.() === 0 ? ['--no-sandbox'] : []), '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
    '--font-render-hinting=none', 'about:blank'], { stdio: 'ignore' });
  let dbg;
  for (let i = 0; i < 200 && !dbg; i++) { try { dbg = fs.readFileSync(path.join(prof, 'DevToolsActivePort'), 'utf8').split('\n')[0].trim(); } catch { await sleep(100); } }
  if (!dbg) { chrome.kill('SIGKILL'); try { fs.rmSync(prof, { recursive: true, force: true }); } catch {} }
  return { chrome, prof, dbg };
}

async function openPage(port) {
  if (!CHROME) throw new Error('Chrome not found: install Google Chrome or Chromium, or set CHROME=/path/to/chrome (a Playwright or Puppeteer download also works: npx playwright install chromium)');
  let { chrome, prof, dbg } = await launchChrome(false);
  if (!dbg) ({ chrome, prof, dbg } = await launchChrome(true));      // second try without the sandbox (containers and some Linux setups need it)
  if (!dbg) throw new Error(`Chrome did not start (${CHROME}). In a container try CHROME_NO_SANDBOX=1; on a bare server install the shared libraries (Debian/Ubuntu: sudo apt install -y libnss3 libatk-bridge2.0-0 libgbm1 libasound2) or use the Playwright download.`);
  const r = await fetch(`http://127.0.0.1:${dbg}/json/new?${encodeURIComponent(`http://127.0.0.1:${port}/index.html?capture=1`)}`, { method: 'PUT' });
  const target = await r.json(), ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pend = new Map(), logs = [];
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    else if (m.method === 'Runtime.exceptionThrown') logs.push('EXCEPTION ' + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
    else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') logs.push('ERROR ' + m.params.args.map((a) => a.value ?? a.description).join(' '));
  };
  let dead = false;
  ws.onclose = () => { dead = true; for (const p of pend.values()) p.rej(new Error('Chrome closed the connection (it crashed or ran out of memory)')); pend.clear(); };
  const send = (method, params = {}) => new Promise((res, rej) => { if (dead) return rej(new Error('Chrome is not running (it crashed or ran out of memory)')); const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async (expr) => { const x = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }); if (x.exceptionDetails) throw new Error(x.exceptionDetails.exception?.description || x.exceptionDetails.text); return x.result.value; };
  await send('Runtime.enable');
  for (let i = 0; ; i++) {
    const st = await ev('window.OP ? (OP.bootError ? "ERR:" + OP.bootError : OP.ready) : false').catch(() => false);
    if (st === true) break;
    if (typeof st === 'string') throw new Error('boot failed: ' + (process.env.LF_DEBUG ? st + '\n' + logs.join('\n') : st.replace(/^ERR:(Error: )?/, '').split('\n')[0] + '  (set LF_DEBUG=1 for the full trace)'));
    if (i > 1800) throw new Error('boot timeout\n' + logs.join('\n'));
    await sleep(100);
  }
  const close = () => { try { ws.close(); } catch {} chrome.kill('SIGKILL'); setTimeout(() => { try { fs.rmSync(prof, { recursive: true, force: true }); } catch {} }, 300); };
  return { ev, logs, close };
}
const jpg = (d) => Buffer.from(d.slice(d.indexOf(',') + 1), 'base64');
const STAMP = (t, q, label) => `(() => { OP.draw(${t}); const cv = document.getElementById('cv'), c = cv.getContext('2d'); c.setTransform(1,0,0,1,0,0); c.fillStyle = 'rgba(0,0,0,0.78)'; c.fillRect(0, 0, 330, 70); c.fillStyle = '#fff'; c.font = '700 44px sans-serif'; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText(${JSON.stringify(label)}, 14, 52); return cv.toDataURL('image/jpeg', ${q}); })()`;
const readJSON = (f) => {
  const full = path.join(ROOT, f);
  if (!fs.existsSync(full)) throw new Error(`${f} is missing. ${/data\/(lines|words)/.test(f) ? 'Create timing first: ./lf voice then ./lf words (or ./lf estimate for a quick draft).' : /chapters|cues/.test(f) ? 'Run ./lf cues first.' : ''}`);
  try { return JSON.parse(fs.readFileSync(full, 'utf8')); } catch (e) { throw new Error(`${f} is not valid JSON (${e.message}). If it is data/*.json, delete it and rebuild it with the step that creates it.`); }
};
process.on('uncaughtException', (e) => { console.error('ERROR: ' + (e && e.message || e)); process.exit(1); });

// ---------- segment cache keys ----------
function walk(dir) { return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)])); }
function engineHash() {
  const h = crypto.createHash('sha1'); for (const f of walk(path.join(ROOT, 'src')).sort()) h.update(f).update(fs.readFileSync(f));
  const w = path.join(ROOT, 'data/world.json'); h.update(String(fs.statSync(w).size)); return h.digest('hex');
}
function chapterKeys(chs) {
  const script = readJSON('script.json'), tl = readJSON('data/lines.json').lines, words = readJSON('data/words.json'), eh = engineHash();
  const sc = script.chapters || [{ title: 'Video', lines: script.lines }]; let off = 0; const range = sc.map((c) => { const r = [off, off + c.lines.length - 1]; off += c.lines.length; return r; });
  const { chapters: _c, lines: _l, ...globals } = script;
  return chs.map((c) => {
    const h = crypto.createHash('sha1'); h.update(eh).update(String(FPS)).update(DRAFT ? 'draft' : 'final').update(JSON.stringify(globals)).update(`${c.start.toFixed(2)}-${c.end.toFixed(2)}`);
    const lo = range[Math.max(0, c.i - 1)][0], hi = range[c.i][1];
    h.update(JSON.stringify(sc.slice(Math.max(0, c.i - 1), c.i + 1))).update(JSON.stringify(tl.slice(lo, hi + 1).map((l) => [l.start, l.end]))).update(JSON.stringify(words.filter((w) => w.line >= lo && w.line <= hi).map((w) => [w.s, w.e])));
    for (const ch of sc.slice(Math.max(0, c.i - 1), c.i + 1)) for (const ln of ch.lines) if (ln.scene?.src) { const p = path.join(ROOT, ln.scene.src); if (fs.existsSync(p)) { const s = fs.statSync(p); h.update(`${s.size}-${s.mtimeMs}`); } }
    if (script.thumbnail?.image) h.update('thumb');
    return h.digest('hex').slice(0, 16);
  });
}
const segPath = (i) => path.join(ROOT, 'renders/segments', `${DRAFT ? 'draft-' : ''}ch${pad(i)}.mp4`);
const frameRange = (c, last, dur) => [Math.round(c.start * FPS), last ? Math.ceil(dur * FPS) : Math.round(c.end * FPS)];

async function renderSegment(P, chs, dur, i) {
  const c = chs[i], [f0, f1] = frameRange(c, i === chs.length - 1, dur), out = segPath(i); fs.mkdirSync(path.dirname(out), { recursive: true });
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', DRAFT ? 'ultrafast' : 'veryfast', '-crf', DRAFT ? '28' : '18',
    '-tune', 'animation', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', String(FPS * 2), '-movflags', '+faststart', out + '.part.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  let ffErr = null; ff.stdin.on('error', (e) => { ffErr = e; });
  const t0 = Date.now(), n = f1 - f0;
  try {
    for (let k = 0; k < n; k++) {
      if (ffErr) throw new Error('ffmpeg stopped while encoding (disk full or ffmpeg missing?): ' + ffErr.message);
      const b = jpg(await P.ev(`OP.frame(${(f0 + k) / FPS}, ${DRAFT ? 0.75 : 0.93})`));
      if (!ff.stdin.write(b)) await new Promise((r) => ff.stdin.once('drain', r));
      if (k % 90 === 0) process.stdout.write(`\r  ch${pad(i)} ${k}/${n} frames`);
    }
  } catch (e) {   // stop ffmpeg cleanly and remove the partial file so the retry starts from nothing
    ff.kill('SIGKILL'); await new Promise((r) => (ff.exitCode !== null ? r() : ff.once('close', r))); try { fs.rmSync(out + '.part.mp4', { force: true }); } catch {} throw e;
  }
  ff.stdin.end(); await new Promise((r) => ff.on('close', r)); fs.renameSync(out + '.part.mp4', out);
  console.log(`\r  ch${pad(i)} "${c.title}": ${n} frames (${hms(c.start)}–${hms(c.end)}) in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
}

function assemble(chs, outFile) {
  const segs = chs.map((c) => segPath(c.i)), miss = segs.filter((s) => !fs.existsSync(s));
  if (miss.length) throw new Error('missing segments (run `render` first): ' + miss.map((m) => path.basename(m)).join(' '));
  const list = path.join(ROOT, 'renders/segments/list.txt'); fs.writeFileSync(list, segs.map((s) => `file '${s.replace(/'/g, "'\\''")}'`).join('\n'));
  const mix = path.join(ROOT, 'data/mix.wav'), hasMix = fs.existsSync(mix); fs.mkdirSync(path.dirname(outFile), { recursive: true });
  const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, ...(hasMix ? ['-i', mix] : ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']),
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-shortest', '-movflags', '+faststart', outFile], { stdio: 'inherit' });
  if (r.status) throw new Error('ffmpeg assemble failed');
  const size = fs.statSync(outFile).size / 1e6; console.log(`${outFile} (${size.toFixed(0)} MB, ${hasMix ? 'with data/mix.wav' : 'SILENT: no data/mix.wav, run tools/mix.py'})`);
}

// ---------- main ----------
const srv = await serve(mode === 'preview' ? 8765 : 0), port = srv.address().port;
if (mode === 'preview') console.log(`open http://127.0.0.1:${port}/  (Ctrl+C to stop)`);
else if (mode === 'assemble') {
  const chs = readJSON('data/chapters.json'); assemble(chs, path.resolve(ROOT, opt('--out') || `renders/${DRAFT ? 'draft' : 'final'}.mp4`)); srv.close();
} else {
  const P = await openPage(port);
  try {
    const dur = await P.ev('OP.duration()'), chs = await P.ev('OP.chapters()');
    if (mode === 'check') {
      const step = +(rest[0] || 0.5); console.log(`duration ${dur.toFixed(2)} s (${hms(dur)}), ${chs.length} chapters`);
      const shots = await P.ev('OP.shots()'); console.log('chapters:');
      for (const c of chs) { const sc = shots.filter((s) => s.ch === c.i); console.log(`  ${pad(c.i)} ${hms(c.start).padStart(5)} → ${hms(c.end).padStart(5)} (${(c.end - c.start).toFixed(0).padStart(3)} s, ${String(sc.length).padStart(2)} scenes)  ${c.title}`); }
      const kinds = {}; for (const s of shots) kinds[s.type] = (kinds[s.type] || 0) + 1; console.log(`scenes: ${shots.length} (${Object.entries(kinds).map(([k, v]) => `${k} ${v}`).join(', ')}), avg ${(dur / shots.length).toFixed(1)} s`);
      const long = shots.filter((s) => s.end - s.at > 14); for (const s of long) console.log(`  note: ${s.id} (${s.type}, line ${s.line}) lasts ${(s.end - s.at).toFixed(1)} s: consider adding a scene change`);
      for (const w of await P.ev('OP.warnings()')) console.log('  warning: ' + w);
      let bad = 0; for (let t = 0; t < dur; t += step) { try { await P.ev(`OP.draw(${t})`); } catch (e) { bad++; if (bad < 15) console.log(`ERROR at ${t.toFixed(2)}: ${e.message.split('\n')[0]}`); } }
      if (P.logs.length) console.log([...new Set(P.logs)].slice(0, 10).join('\n'));
      console.log(bad || P.logs.length ? 'CHECK FAILED' : 'CHECK OK');
    } else if (mode === 'cues') {
      const cues = await P.ev('OP.cues()'); fs.mkdirSync(path.join(ROOT, 'data'), { recursive: true });
      fs.writeFileSync(path.join(ROOT, 'data/cues.json'), JSON.stringify({ duration: dur, cues }, null, 1)); fs.writeFileSync(path.join(ROOT, 'data/chapters.json'), JSON.stringify(chs, null, 1));
      console.log(`data/cues.json: ${cues.length} cues · data/chapters.json: ${chs.length} chapters · ${dur.toFixed(1)} s`);
    } else if (mode === 'frames') {
      const dir = path.resolve(ROOT, rest[0] || 'review/frames'); fs.mkdirSync(dir, { recursive: true });
      for (const t of (rest[1] || '0').split(',').map(Number)) fs.writeFileSync(path.join(dir, `t${t.toFixed(2)}.jpg`), jpg(await P.ev(`OP.frame(${t}, 0.92)`)));
      console.log(dir);
    } else if (mode === 'thumb') {
      const out = path.resolve(ROOT, rest[0] || 'renders/thumbnail.jpg'); fs.mkdirSync(path.dirname(out), { recursive: true });
      const tmp = out + '.full.jpg'; fs.writeFileSync(tmp, jpg(await P.ev('OP.thumb(0.97)')));
      const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', tmp, '-vf', 'scale=1280:720:flags=lanczos', '-q:v', '2', out]); fs.rmSync(tmp, { force: true });
      if (r.status) throw new Error('ffmpeg: ' + r.stderr); console.log(`${out} (${(fs.statSync(out).size / 1e3).toFixed(0)} KB, YouTube allows up to 2 MB)`);
    } else if (mode === 'sheets') {
      const step = +(rest[0] || 3), cols = +(rest[1] || 6), only = opt('--chapter'), shots = await P.ev('OP.shots()'); fs.mkdirSync(path.join(ROOT, 'review'), { recursive: true });
      for (const c of chs) {
        if (only !== undefined && +only !== c.i) continue;
        const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'lf-sheet-')); let n = 0;
        for (let t = c.start + step / 2; t < c.end; t += step) { const sc = [...shots].reverse().find((s) => s.at <= t); fs.writeFileSync(path.join(tmp, `f${String(n++).padStart(4, '0')}.jpg`), jpg(await P.ev(STAMP(t, 0.8, `${t.toFixed(1)} ${sc?.id || ''}`)))); }
        if (!n) { fs.rmSync(tmp, { recursive: true, force: true }); continue; }
        const rows = Math.ceil(n / cols), out = path.join(ROOT, `review/ch${pad(c.i)}.jpg`);
        const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(tmp, 'f%04d.jpg'), '-vf', `scale=480:270,tile=${cols}x${rows}:padding=4:color=black`, '-frames:v', '1', '-q:v', '3', out]);
        fs.rmSync(tmp, { recursive: true, force: true }); if (r.status) throw new Error('ffmpeg: ' + r.stderr); console.log(`${out} (${n} frames, every ${step} s, "${c.title}")`);
      }
    } else if (mode === 'segment') {
      await renderSegment(P, chs, dur, +rest[0]);
    } else if (mode === 'render') {
      const only = opt('--chapters')?.split(',').map(Number), keys = chapterKeys(chs), force = flags.has('--force'), ramJobs = Math.max(1, Math.floor(os.freemem() / 1e9 / 0.7)), jobs = +(opt('--jobs') || process.env.JOBS || Math.max(1, Math.min(4, Math.floor(os.cpus().length / 2), ramJobs)));
      fs.mkdirSync(path.join(ROOT, 'renders/segments'), { recursive: true });
      const todo = chs.filter((c) => (!only || only.includes(c.i)) && (force || !fs.existsSync(segPath(c.i)) || (fs.existsSync(segPath(c.i) + '.key') ? fs.readFileSync(segPath(c.i) + '.key', 'utf8') : '') !== keys[c.i]));
      const total = todo.reduce((a, c) => a + (c.end - c.start), 0);
      try {   // disk check: segments + the joined file need about 1 MB per second of final video (a quarter of that for a draft)
        const st = fs.statfsSync(ROOT), freeMB = st.bavail * st.bsize / 1e6, needMB = total * (DRAFT ? 0.25 : 1.0) * 2;
        if (freeMB < needMB) throw new Error(`not enough free disk space: about ${needMB.toFixed(0)} MB needed, ${freeMB.toFixed(0)} MB free. Free some space (delete renders/segments/ of old projects) and run again.`);
        if (freeMB < needMB * 2) console.log(`  note: only ${(freeMB / 1000).toFixed(1)} GB free; this render needs about ${(needMB / 1000).toFixed(1)} GB`);
      } catch (e) { if (/not enough free disk/.test(e.message)) throw e; }
      if (!opt('--jobs') && !process.env.JOBS && ramJobs < Math.min(4, Math.floor(os.cpus().length / 2))) console.log(`  note: ${(os.freemem() / 1e9).toFixed(1)} GB RAM free, so ${jobs} parallel Chrome worker(s) (each needs about 0.7 GB)`);
      console.log(`${chs.length} chapters, ${todo.length} to render (${hms(total)} of video at ${FPS} fps, ${jobs} parallel)${DRAFT ? ' [draft]' : ''}; ${chs.length - todo.length} cached`);
      P.close();   // workers boot their own Chrome
      const queue = [...todo], t0 = Date.now(); let failed = 0;
      const worker = async () => {
        while (queue.length) {
          const c = queue.shift(); let code = 1;
          for (let attempt = 1; attempt <= 3 && code !== 0; attempt++) {     // a Chrome crash (usually memory) costs one chapter, not the whole film
            if (attempt > 1) { console.log(`  ch${pad(c.i)} failed, retrying (attempt ${attempt}/3)`); try { fs.rmSync(segPath(c.i) + '.part.mp4', { force: true }); } catch {} await sleep(1500); }
            code = await new Promise((res) => spawn(process.execPath, [fileURLToPath(import.meta.url), 'segment', String(c.i), ...(DRAFT ? ['--draft'] : [])], { stdio: 'inherit', env: process.env }).on('close', res));
          }
          if (code === 0) fs.writeFileSync(segPath(c.i) + '.key', keys[c.i]); else { failed++; console.log(`  ch${pad(c.i)} FAILED after 3 attempts`); }
        }
      };
      await Promise.all(Array.from({ length: Math.min(jobs, todo.length) }, worker));
      if (failed) throw new Error(`${failed} chapter(s) failed; fix the error above and run render again (finished chapters are kept)`);
      console.log(`rendered in ${((Date.now() - t0) / 60000).toFixed(1)} min`);
      if (!only) { fs.writeFileSync(path.join(ROOT, 'data/chapters.json'), JSON.stringify(chs, null, 1)); assemble(chs, path.resolve(ROOT, opt('--out') || `renders/${DRAFT ? 'draft' : 'final'}.mp4`)); }
      else console.log('partial render: run `render` without --chapters to assemble the film');
      srv.close(); process.exit(0);
    } else console.log('modes: check · cues · sheets · frames · thumb · render · segment · assemble · preview');
  } finally { P.close(); srv.close(); }
}
