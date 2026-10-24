// Рендер эпизода: node render.mjs <out> <ep> [--workers=4] [--preview=сек,сек,...]
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const [OUT, EP] = process.argv.slice(2);
const arg = (k, d) => (process.argv.find(a => a.startsWith(`--${k}=`)) || '').split('=')[1] || d;
const WORKERS = +arg('workers', 4);
const dir = path.join(OUT, `ep${EP}`);
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8'));
const FPS = tl.fps, TOTAL = Math.ceil(tl.dur * FPS);

async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('file://' + path.join(here, 'scene.html'));
  await p.evaluate(t => window.setTL(t), tl);
  return p;
}

async function frameJpeg(p, f) {
  const b64 = await p.evaluate(f => { window.draw(f); return document.getElementById('cv').toDataURL('image/jpeg', 0.93).split(',')[1]; }, f);
  return Buffer.from(b64, 'base64');
}

async function segment(browser, a, b, file) {
  const p = await page(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = a; f < b; f++) {
    const buf = await frameJpeg(p, f);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await p.close();
}

const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--font-render-hinting=none'] });
const preview = arg('preview', '');
if (preview) {
  const p = await page(browser);
  fs.mkdirSync(path.join(dir, 'preview'), { recursive: true });
  for (const s of preview.split(',')) {
    const f = Math.round(+s * FPS);
    fs.writeFileSync(path.join(dir, 'preview', `f${String(f).padStart(5, '0')}.jpg`), await frameJpeg(p, f));
  }
  console.log('preview done');
} else {
  // короткие куски по CHUNK кадров; готовые пропускаются — рендер можно прерывать и продолжать
  const CHUNK = 450, parts = [], todo = [];
  for (let a = 0, i = 0; a < TOTAL; a += CHUNK, i++) {
    const file = path.join(dir, `chunk${String(i).padStart(3, '0')}.mp4`); parts.push(file);
    if (!fs.existsSync(file)) todo.push([a, Math.min(TOTAL, a + CHUNK), file]);
  }
  console.log(`ep${EP}: ${todo.length}/${parts.length} chunks to render`);
  await Promise.all(Array.from({ length: WORKERS }, async () => {
    while (todo.length) {
      const [a, b, file] = todo.shift();
      await segment(browser, a, b, file + '.tmp.mp4');
      fs.renameSync(file + '.tmp.mp4', file);
      console.log(`  ep${EP} chunk ${path.basename(file)} ok`);
    }
  }));
  fs.writeFileSync(path.join(dir, 'parts.txt'), parts.map(f => `file '${path.resolve(f)}'`).join('\n'));
  const out = path.join(dir, `kagune_ep${EP}.mp4`);
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'parts.txt'),
    '-i', path.join(dir, 'mix.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: 'inherit' }).on('close', r));
  console.log('done', out);
}
await browser.close();
