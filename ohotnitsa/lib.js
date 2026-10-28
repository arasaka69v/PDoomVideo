// ---------- утилиты ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const easeOut = t => 1 - Math.pow(1 - clamp(t), 3);
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
function vnoise(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
const RED = '#ff1a2e', DRED = '#7a0010';

function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
}
function fill(col) { c.fillStyle = col; c.fillRect(0, 0, W, H); }
function vgrad(stops) {
  const g = c.createLinearGradient(0, 0, 0, H);
  stops.forEach(([o, col]) => g.addColorStop(o, col));
  c.fillStyle = g; c.fillRect(0, 0, W, H);
}
function glow(col, b) { c.shadowColor = col; c.shadowBlur = b; }
function noGlow() { c.shadowBlur = 0; c.shadowColor = 'transparent'; }
function vignette(a = 0.85, col = '0,0,0') {
  const g = c.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.95);
  g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(1, `rgba(${col},${a})`);
  c.fillStyle = g; c.fillRect(0, 0, W, H);
}
function text(s, x, y, size, col, o = {}) {
  c.save();
  c.font = `${o.weight || 'bold'} ${size}px ${o.font || '"DejaVu Sans", sans-serif'}`;
  c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
  if (o.spacing) c.letterSpacing = o.spacing + 'px';
  if (o.glow) glow(o.glow, o.blur || 25);
  if (o.stroke) { c.lineWidth = o.stroke; c.strokeStyle = o.strokeCol || '#000'; c.strokeText(s, x, y); }
  c.fillStyle = col; c.fillText(s, x, y);
  c.restore();
}

// ---------- зерно плёнки ----------
const grains = [0, 1, 2].map(k => {
  const g = document.createElement('canvas'); g.width = g.height = 256;
  const gx = g.getContext('2d'); const im = gx.createImageData(256, 256);
  for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  gx.putImageData(im, 0, 0); return c.createPattern(g, 'repeat');
});

// ---------- небо, луна, город ----------
function moon(x, y, r, col, a = 1) {
  c.save();
  c.globalAlpha = a;
  const g = c.createRadialGradient(x, y, r * 0.2, x, y, r * 3.2);
  g.addColorStop(0, rgba(col, 0.55)); g.addColorStop(0.35, rgba(col, 0.12)); g.addColorStop(1, rgba(col, 0));
  c.fillStyle = g; c.fillRect(x - r * 4, y - r * 4, r * 8, r * 8);
  glow(col, 60); c.fillStyle = col; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); noGlow();
  c.globalAlpha = a * 0.18; c.fillStyle = '#000';
  [[0.3, -0.2, 0.22], [-0.35, 0.25, 0.15], [0.1, 0.45, 0.12], [-0.1, -0.45, 0.1]].forEach(([dx, dy, rr]) => {
    c.beginPath(); c.arc(x + dx * r, y + dy * r, rr * r, 0, 7); c.fill();
  });
  c.restore();
}

const cityLayers = [0, 1, 2].map(L => {
  const bs = []; let x = -200;
  while (x < W + 800) {
    const w = 40 + hash(x * 0.37 + L * 9) * (90 - L * 15);
    const h = (L === 0 ? 260 : L === 1 ? 190 : 120) * (0.45 + hash(x * 0.71 + L) * 0.9);
    const spire = hash(x + L * 3) > 0.85;
    bs.push({ x, w, h, spire, seed: x * 13 + L * 1000 });
    x += w + hash(x + 5) * 12;
  }
  return bs;
});

function skyline(t, o = {}) {
  const base = o.base ?? H - 40;
  const pan = o.pan ?? t * 6;
  const cols = o.dawn ? ['#3a2a3a', '#25182a', '#120a14'] : ['#14141f', '#0c0c14', '#050508'];
  cityLayers.forEach((bs, L) => {
    const par = [0.3, 0.6, 1.0][L];
    c.fillStyle = cols[L];
    bs.forEach(b => {
      const x = b.x - (pan * par) % 900 - 100, y = base - b.h - (2 - L) * 30;
      if (x > W + 50 || x + b.w < -50) return;
      c.fillRect(x, y, b.w, base - y + 60);
      if (b.spire) { c.beginPath(); c.moveTo(x + b.w * 0.4, y); c.lineTo(x + b.w * 0.5, y - 50); c.lineTo(x + b.w * 0.6, y); c.fill(); }
      if (L >= 1 && !o.noWindows) {
        for (let wy = y + 10; wy < base - 10; wy += 14) for (let wx = x + 6; wx < x + b.w - 8; wx += 11) {
          const hv = hash(b.seed + wx * 3.1 + wy * 7.7);
          if (hv > (o.dawn ? 0.93 : 0.8)) {
            const fl = hash(b.seed + wy + Math.floor(t * 0.5 + hv * 10)) > 0.08 ? 1 : 0.2;
            c.fillStyle = hv > 0.97 ? `rgba(255,60,70,${0.6 * fl})` : `rgba(255,${190 + hv * 50 | 0},120,${0.45 * fl})`;
            c.fillRect(wx, wy, 5, 7);
          }
        }
        c.fillStyle = cols[L];
      }
    });
  });
}

function rain(t, n = 400, a = 0.35, ang = 0.18) {
  c.save(); c.strokeStyle = `rgba(180,190,220,${a})`; c.lineWidth = 1.2; c.beginPath();
  for (let i = 0; i < n; i++) {
    const sp = 900 + hash(i) * 600, len = 14 + hash(i + 3) * 18;
    const y = (hash(i * 1.7) * (H + 100) + t * sp) % (H + 100) - 50;
    const x = (hash(i * 2.3) * (W + 200) + y * ang) % (W + 200) - 100;
    c.moveTo(x, y); c.lineTo(x + len * ang, y + len);
  }
  c.stroke(); c.restore();
}

function embers(t, n = 60, col = '255,120,40') {
  c.save();
  for (let i = 0; i < n; i++) {
    const life = (t * (0.2 + hash(i) * 0.3) + hash(i * 3)) % 1;
    const x = hash(i * 7) * W + Math.sin(t + i) * 30, y = H - life * H * 1.1;
    c.fillStyle = `rgba(${col},${(1 - life) * 0.9})`;
    c.beginPath(); c.arc(x, y, 1.5 + hash(i) * 2, 0, 7); c.fill();
  }
  c.restore();
}

function smokeLayer(t, col = '30,30,35', a = 0.5, y0 = H * 0.5) {
  c.save();
  for (let i = 0; i < 14; i++) {
    const x = ((hash(i) * W * 1.5 + t * (15 + hash(i + 1) * 25)) % (W * 1.5)) - W * 0.25;
    const y = y0 + (hash(i + 2) - 0.5) * H * 0.7 + Math.sin(t * 0.3 + i) * 20;
    const r = 180 + hash(i + 4) * 220;
    const g = c.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(1, `rgba(${col},0)`);
    c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2);
  }
  c.restore();
}

// ---------- персонажи (силуэты) ----------
const LOOK = {
  kai:  { hair: '#0a0a0e', streak: true, coat: '#111117', rim: RED, eyes: ['kakugan', '#c9d4e0'], hood: true },
  mira: { hair: '#0d1626', coat: '#151a24', rim: '#7fc8ff', eyes: ['#7fc8ff', '#7fc8ff'], bob: true, scarf: '#5a1020' },
  rust: { hair: '#77706a', coat: '#2a2018', rim: '#e0a050', eyes: ['#e0a050', '#e0a050'], beard: true, glasses: true },
  varg: { hair: '#d8d8d8', coat: '#1a1c22', rim: '#e8f0ff', eyes: ['#bcd', '#bcd'], slick: true, long: true, scar: true },
  king: { hair: '#000', coat: '#0c0612', rim: '#b060ff', eyes: ['#c070ff', '#c070ff'], mask: true, long: true, feathers: true },
  ghoul:{ hair: '#050505', coat: '#080808', rim: '#ff5020', eyes: ['kakugan', 'kakugan'] },
  kid:  { hair: '#111', coat: '#16161c', rim: '#888', eyes: [null, null] },
  man:  { hair: '#1a1a1a', coat: '#1c1c22', rim: '#665', eyes: [null, null] },
};

// фигура в полный рост: x,y — точка между ступнями, h — рост
function figure(x, y, h, who, o = {}) {
  const L = LOOK[who] || LOOK.man, t = o.t || 0, f = o.facing || 1, pose = o.pose || 'stand';
  c.save(); c.translate(x, y); c.scale(f * h / 300, h / 300);
  const rim = o.rim || L.rim;
  glow(rim, o.glow ?? 14);
  c.fillStyle = o.color || '#050507'; c.strokeStyle = o.color || '#050507'; c.lineCap = 'round'; c.lineJoin = 'round';
  let hipY = -150, headY = -262, lean = 0, step = 0;
  if (pose === 'walk') { step = Math.sin(t * 6); }
  if (pose === 'kneel') { hipY = -80; headY = -190; lean = 18; }
  if (pose === 'crouch') { hipY = -110; headY = -215; lean = 25; }
  if (pose === 'sit') { hipY = -70; headY = -180; }
  if (pose === 'strike') { lean = 30; }
  if (pose === 'hunch') { lean = 22; headY = -235; }
  // ноги
  c.lineWidth = 26;
  c.beginPath();
  if (pose === 'kneel') { c.moveTo(0, hipY); c.lineTo(-40, -10); c.lineTo(-70, 0); c.moveTo(0, hipY); c.lineTo(50, -40); c.lineTo(55, 0); }
  else if (pose === 'sit') { c.moveTo(0, hipY); c.lineTo(70, hipY + 5); c.lineTo(80, 10); c.moveTo(0, hipY); c.lineTo(60, hipY); c.lineTo(65, 20); }
  else if (pose === 'crouch') { c.moveTo(0, hipY); c.lineTo(-45, -55); c.lineTo(-35, 0); c.moveTo(0, hipY); c.lineTo(50, -50); c.lineTo(60, 0); }
  else { c.moveTo(-8, hipY); c.lineTo(-14 - step * 28, -75); c.lineTo(-18 - step * 40, 0); c.moveTo(8, hipY); c.lineTo(14 + step * 28, -75); c.lineTo(18 + step * 40, 0); }
  c.stroke();
  // туловище
  const sx = lean;
  c.beginPath();
  c.moveTo(-30, hipY + 6); c.lineTo(-44 + sx, headY + 62); c.quadraticCurveTo(sx, headY + 40, 44 + sx, headY + 62); c.lineTo(30, hipY + 6); c.closePath(); c.fill();
  if (L.long) { // длинное пальто / плащ
    c.beginPath(); c.moveTo(-42 + sx, headY + 70); c.lineTo(-62 + Math.sin(t * 2) * 6, -20); c.lineTo(62 + Math.sin(t * 2 + 1) * 6, -20); c.lineTo(42 + sx, headY + 70); c.fill();
    if (L.feathers) for (let i = 0; i < 9; i++) { c.beginPath(); const fx = -60 + i * 15; c.moveTo(fx, -30); c.lineTo(fx + 5 + Math.sin(t * 3 + i) * 3, 5 + hash(i) * 15); c.lineTo(fx + 12, -30); c.fill(); }
  }
  // руки
  c.lineWidth = 20;
  c.beginPath();
  const arm = o.arm || (pose === 'strike' ? 'forward' : pose === 'walk' ? 'swing' : 'down');
  const shY = headY + 70;
  if (arm === 'forward') { c.moveTo(38 + sx, shY); c.lineTo(110 + sx, shY + 10); c.lineTo(170 + sx, shY + 5); c.moveTo(-36 + sx, shY); c.lineTo(-50, shY + 70); c.lineTo(-30, shY + 120); }
  else if (arm === 'reach') { c.moveTo(38 + sx, shY); c.lineTo(100 + sx, shY - 20); c.lineTo(150 + sx, shY - 40); c.moveTo(-36 + sx, shY); c.lineTo(-48, shY + 70); c.lineTo(-40, shY + 130); }
  else if (arm === 'carry') { c.moveTo(38 + sx, shY); c.lineTo(70, shY + 50); c.lineTo(40, shY + 70); c.moveTo(-36 + sx, shY); c.lineTo(-48, shY + 70); c.lineTo(-40, shY + 130); }
  else { const sw = arm === 'swing' ? Math.sin(t * 6) * 20 : 0; c.moveTo(38 + sx, shY); c.lineTo(48 + sw, shY + 70); c.lineTo(40 + sw * 1.5, shY + 130); c.moveTo(-36 + sx, shY); c.lineTo(-48 - sw, shY + 70); c.lineTo(-40 - sw * 1.5, shY + 130); }
  c.stroke();
  // голова и волосы
  const hx = sx * 1.2;
  c.beginPath(); c.ellipse(hx, headY + 18, 25, 31, 0, 0, 7); c.fill();
  c.beginPath();
  if (L.mask) { // корона маски
    for (let i = -2; i <= 2; i++) { c.moveTo(hx + i * 10 - 6, headY - 6); c.lineTo(hx + i * 10, headY - 26 - (2 - Math.abs(i)) * 8); c.lineTo(hx + i * 10 + 6, headY - 6); }
  } else if (L.bob) { c.ellipse(hx, headY + 10, 33, 30, 0, 3.0, 6.5); c.rect(hx - 33, headY + 10, 66, 26); }
  else if (L.slick) { c.ellipse(hx - 4, headY + 6, 30, 22, -0.2, 0, 7); }
  else { c.ellipse(hx, headY + 10, 29, 26, 0, Math.PI, 7); for (let i = 0; i < 7; i++) { const a = -3.0 + i * 0.32, l = 34 + hash(i * 5 + 1) * 10; c.moveTo(hx + Math.cos(a - 0.2) * 24, headY + 14 + Math.sin(a - 0.2) * 24); c.lineTo(hx + Math.cos(a) * l - 6, headY + 14 + Math.sin(a) * l * 0.8); c.lineTo(hx + Math.cos(a + 0.2) * 24, headY + 14 + Math.sin(a + 0.2) * 24); } c.moveTo(hx + 26, headY + 6); c.lineTo(hx + 34, headY + 40); c.lineTo(hx + 20, headY + 22); }
  c.fill();
  if (L.hood && !o.noHood) { c.beginPath(); c.ellipse(hx, headY + 66, 40, 16, 0, 0, 7); c.fill(); }
  if (L.owl) { c.beginPath(); c.moveTo(hx - 24, headY + 4); c.lineTo(hx - 30, headY - 26); c.lineTo(hx - 8, headY - 2); c.moveTo(hx + 24, headY + 4); c.lineTo(hx + 30, headY - 26); c.lineTo(hx + 8, headY - 2); c.fill(); }
  noGlow();
  // глаза
  const eyes = o.eyes || L.eyes;
  const ey = headY + 14;
  if (L.mask) {
    c.fillStyle = '#e8e2ee'; c.beginPath(); c.ellipse(hx, headY + 18, 22, 28, 0, 0, 7); c.fill();
    glow('#c070ff', 20); c.fillStyle = '#c070ff'; c.beginPath(); c.ellipse(hx + 9, ey, 5, 3, 0, 0, 7); c.fill(); noGlow();
    c.strokeStyle = '#333'; c.lineWidth = 1.5; c.beginPath(); c.moveTo(hx - 4, headY - 4); c.lineTo(hx + 2, headY + 20); c.lineTo(hx - 3, headY + 40); c.stroke();
  } else if (L.owl) {
    c.fillStyle = '#d9c7a0'; c.beginPath(); c.ellipse(hx + 4, headY + 14, 26, 15, 0, 0, 7); c.fill();
    glow('#ffb030', 18); c.fillStyle = '#ffb030'; c.beginPath(); c.arc(hx - 6, ey, 5, 0, 7); c.arc(hx + 14, ey, 5, 0, 7); c.fill(); noGlow();
    } else if (o.showEyes !== false) {
    eyes.forEach((e, i) => {
      if (!e) return;
      const ex = hx + (i ? 10 : -10) * 1 + 6;
      if (e === 'kakugan') { glow(RED, 18); c.fillStyle = RED; } else { glow(e, 10); c.fillStyle = e; }
      c.beginPath(); c.ellipse(ex, ey, 4.5, 2.6, 0, 0, 7); c.fill(); noGlow();
    });
  }
  if (o.mask) {
    c.fillStyle = '#ece8ee'; c.beginPath(); c.ellipse(hx + 4, headY + 30, 24, 18, 0, 0, Math.PI); c.lineTo(hx - 20, headY + 22); c.fill();
    c.strokeStyle = RED; c.lineWidth = 3; c.beginPath(); c.moveTo(hx - 16, headY + 34); c.lineTo(hx + 24, headY + 34); c.stroke();
  }
  c.restore();
}

// ---------- кагуне ----------
// щупальца из точки (x,y). o: n, len, spread, base (угол), t, target{x,y,k}, width, col
function kagune(x, y, o) {
  const n = o.n || 4, t = o.t || 0, segs = 22;
  const grow = o.grow ?? 1;
  const len = (o.len || 320) * grow;
  const col = o.col || RED;
  for (let i = 0; i < n; i++) {
    const side = n === 1 ? 0 : (i / (n - 1)) * 2 - 1;
    let a = (o.base ?? -Math.PI / 2) + side * (o.spread ?? 1.1);
    let px = x, py = y;
    const pts = [[px, py]];
    const ph = i * 1.7 + (o.seed || 0);
    for (let k = 1; k <= segs; k++) {
      const u = k / segs;
      a += Math.sin(t * (1.6 + i * 0.13) + ph + u * 5) * 0.11 * (o.wiggle ?? 1) + side * 0.02;
      px += Math.cos(a) * len / segs; py += Math.sin(a) * len / segs;
      if (o.target) {
        const tk = o.target.k * Math.pow(u, 1.4);
        const tx = o.target.x + side * 40 * (1 - o.target.k), ty = o.target.y + Math.sin(i * 2) * 30;
        pts.push([lerp(px, lerp(x, tx, u), tk), lerp(py, lerp(y, ty, u), tk)]);
      } else pts.push([px, py]);
    }
    const w0 = (o.width || 26) * (0.8 + 0.3 * hash(i));
    const L = [], R = [];
    for (let k = 0; k < pts.length; k++) {
      const p = pts[k], q = pts[Math.min(k + 1, pts.length - 1)], pp = pts[Math.max(k - 1, 0)];
      const dx = q[0] - pp[0], dy = q[1] - pp[1], dl = Math.hypot(dx, dy) || 1;
      const w = w0 * Math.pow(1 - k / pts.length, 0.65) * (k === 0 ? 0.7 : 1);
      L.push([p[0] - dy / dl * w / 2, p[1] + dx / dl * w / 2]); R.push([p[0] + dy / dl * w / 2, p[1] - dx / dl * w / 2]);
    }
    c.save();
    glow(col, o.blur ?? 28);
    const g = c.createLinearGradient(x, y, pts[segs][0], pts[segs][1]);
    g.addColorStop(0, o.dark || '#3a0008'); g.addColorStop(0.35, col); g.addColorStop(1, o.tip || '#ff6a6a');
    c.fillStyle = g;
    c.beginPath(); c.moveTo(L[0][0], L[0][1]);
    L.forEach(p => c.lineTo(p[0], p[1])); c.lineTo(pts[segs][0], pts[segs][1]);
    for (let k = R.length - 1; k >= 0; k--) c.lineTo(R[k][0], R[k][1]);
    c.closePath(); c.fill(); noGlow();
    // сегменты-чешуйки
    c.strokeStyle = 'rgba(40,0,6,0.65)'; c.lineWidth = 2;
    c.beginPath();
    for (let k = 2; k < segs; k += 2) { c.moveTo(L[k][0], L[k][1]); c.quadraticCurveTo(pts[k + 1][0], pts[k + 1][1], R[k][0], R[k][1]); }
    c.stroke();
    // яркая жила
    c.strokeStyle = 'rgba(255,190,190,0.55)'; c.lineWidth = 1.5; c.beginPath();
    pts.forEach((p, k) => k ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.stroke();
    c.restore();
  }
}

// кагуне-крылья (Мира): кристаллические осколки
function wings(x, y, t, col = '#7fc8ff', s = 1) {
  c.save(); glow(col, 25);
  for (let side of [-1, 1]) for (let i = 0; i < 6; i++) {
    const a = -Math.PI / 2 + side * (0.5 + i * 0.22) + Math.sin(t * 3 + i) * 0.05;
    const l = (120 + i * 25) * s;
    c.fillStyle = rgba(col, 0.55 + 0.07 * i);
    c.beginPath(); c.moveTo(x, y);
    c.lineTo(x + Math.cos(a - 0.08) * l * 0.5, y + Math.sin(a - 0.08) * l * 0.5);
    c.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l);
    c.lineTo(x + Math.cos(a + 0.08) * l * 0.5, y + Math.sin(a + 0.08) * l * 0.5);
    c.fill();
  }
  c.restore();
}

// клинок охотника (из кагуне)
function blade(x, y, ang, len, t, col = '#d0e4ff') {
  c.save(); c.translate(x, y); c.rotate(ang);
  glow(col, 22);
  const g = c.createLinearGradient(0, 0, len, 0); g.addColorStop(0, '#333'); g.addColorStop(0.15, '#9aa'); g.addColorStop(1, '#fff');
  c.fillStyle = g;
  c.beginPath(); c.moveTo(0, -5); c.lineTo(len * 0.85, -12); c.lineTo(len, 0); c.lineTo(len * 0.85, 8); c.lineTo(0, 5); c.fill();
  c.fillStyle = '#8a0010'; for (let i = 1; i < 6; i++) { c.fillRect(len * i / 7, -3, 10, 6); }
  noGlow(); c.fillStyle = '#222'; c.fillRect(-30, -6, 30, 12);
  c.restore();
}

// ---------- портреты для диалогов ----------
function portrait(who, x, y, s, t, mouth, o = {}) {
  const L = LOOK[who];
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
  const dim = o.dim ? 0.45 : 1;
  c.globalAlpha = dim;
  const breathe = Math.sin(t * 1.6) * 2;
  c.translate(0, breathe);
  if (!o.maskOnly) {
  // плечи
  glow(L.rim, 30);
  c.fillStyle = L.coat;
  c.beginPath(); c.moveTo(-190, 260); c.quadraticCurveTo(-170, 70, -60, 50); c.lineTo(60, 50); c.quadraticCurveTo(170, 70, 190, 260); c.fill();
  if (L.long) { c.fillStyle = '#0a0b0e'; c.beginPath(); c.moveTo(-80, 40); c.lineTo(-40, 120); c.lineTo(0, 70); c.lineTo(40, 120); c.lineTo(80, 40); c.lineTo(60, -10); c.lineTo(-60, -10); c.fill(); }
  if (L.feathers) { c.fillStyle = '#120818'; for (let i = 0; i < 14; i++) { const a = Math.PI + i / 13 * Math.PI; c.beginPath(); c.moveTo(Math.cos(a) * 120, 70 + Math.sin(a) * 30); c.lineTo(Math.cos(a) * 200, 60 + Math.sin(a) * 90 + Math.sin(t * 2 + i) * 4); c.lineTo(Math.cos(a + 0.12) * 120, 70 + Math.sin(a + 0.12) * 30); c.fill(); } }
  if (L.hood) { c.fillStyle = '#0c0c12'; c.beginPath(); c.ellipse(0, 55, 110, 30, 0, 0, 7); c.fill(); }
  if (L.scarf) { c.fillStyle = L.scarf; c.beginPath(); c.ellipse(0, 50, 80, 26, 0, 0, 7); c.fill(); c.fillRect(30, 50, 26, 90); }
  noGlow();
  // шея
  c.fillStyle = '#1d1b22'; c.fillRect(-26, 0, 52, 55);
  }
  // лицо
  const skin = c.createLinearGradient(-80, 0, 80, 0);
  skin.addColorStop(0, '#2b2630'); skin.addColorStop(0.6, '#3d3640'); skin.addColorStop(1, rgba(L.rim, 0.55));
  c.fillStyle = skin;
  c.beginPath(); c.moveTo(-72, -90); c.quadraticCurveTo(-78, -10, -40, 30); c.quadraticCurveTo(0, 62, 40, 30); c.quadraticCurveTo(78, -10, 72, -90); c.quadraticCurveTo(0, -150, -72, -90); c.fill();
  // контурный свет
  c.strokeStyle = rgba(L.rim, 0.8); c.lineWidth = 2.5; glow(L.rim, 12);
  c.beginPath(); c.moveTo(72, -90); c.quadraticCurveTo(78, -10, 40, 30); c.quadraticCurveTo(10, 55, 0, 52); c.stroke(); noGlow();
  if (L.mask) {
    if (o.maskOnly) { c.restore(); c.save(); c.translate(x, y); c.scale(s, s); }
    const mg = c.createLinearGradient(-70, -120, 70, 50); mg.addColorStop(0, '#fff'); mg.addColorStop(1, '#a9a0b5');
    c.fillStyle = mg;
    c.beginPath(); c.moveTo(-76, -95); c.quadraticCurveTo(-82, -5, -40, 35); c.quadraticCurveTo(0, 66, 40, 35); c.quadraticCurveTo(82, -5, 76, -95); c.quadraticCurveTo(0, -155, -76, -95); c.fill();
    c.fillStyle = '#e8e2ee';
    for (let i = -3; i <= 3; i++) { c.beginPath(); c.moveTo(i * 22 - 12, -118 + Math.abs(i) * 6); c.lineTo(i * 22, -175 + Math.abs(i) * 18); c.lineTo(i * 22 + 12, -118 + Math.abs(i) * 6); c.fill(); }
    c.strokeStyle = '#222'; c.lineWidth = 3; c.beginPath(); c.moveTo(-10, -140); c.lineTo(5, -60); c.lineTo(-8, -10); c.lineTo(10, 40); c.stroke();
    c.fillStyle = '#000'; c.beginPath(); c.ellipse(-32, -45, 20, 9, 0.15, 0, 7); c.fill(); c.beginPath(); c.ellipse(32, -45, 20, 9, -0.15, 0, 7); c.fill();
    glow('#c070ff', 25); c.fillStyle = '#d090ff'; c.beginPath(); c.arc(32, -45, 5, 0, 7); c.fill(); c.beginPath(); c.arc(-32, -45, 3, 0, 7); c.fill(); noGlow();
    // нарисованная улыбка
    c.strokeStyle = '#300'; c.lineWidth = 3; c.beginPath(); c.moveTo(-40, 10); c.quadraticCurveTo(0, 30 + mouth * 10, 40, 10); c.stroke();
    c.fillStyle = '#8a0010'; c.beginPath(); c.moveTo(32, -36); c.lineTo(36, 0); c.lineTo(29, -36); c.fill();
    if (o.maskOnly) { c.restore(); return; }
  } else {
    // глаза
    const blink = (Math.sin(t * 0.9 + x) > 0.985) ? 0.1 : 1;
    L.eyes.forEach((e, i) => {
      const ex = i ? 32 : -32, ey = -42;
      c.save(); c.translate(ex, ey); c.scale(1, blink);
      const kak = e === 'kakugan' || o.kakugan;
      c.fillStyle = kak ? '#050005' : '#d8dde8';
      c.beginPath(); c.moveTo(-22, 0); c.quadraticCurveTo(0, -14, 22, -2); c.quadraticCurveTo(0, 12, -22, 0); c.fill();
      const ic = kak ? RED : e;
      glow(ic, kak ? 25 : 10); c.fillStyle = ic; c.beginPath(); c.arc(2, -1, 8, 0, 7); c.fill(); noGlow();
      c.fillStyle = kak ? '#ff8090' : '#000'; c.beginPath(); c.arc(2, -1, kak ? 2.5 : 3.5, 0, 7); c.fill();
      c.fillStyle = 'rgba(255,255,255,0.8)'; c.beginPath(); c.arc(-1, -4, 2, 0, 7); c.fill();
      if (kak) { c.strokeStyle = 'rgba(200,0,20,0.7)'; c.lineWidth = 1.5; for (let k = 0; k < 4; k++) { c.beginPath(); c.moveTo(14, 2); c.quadraticCurveTo(30, 8 + k * 6, 26 + k * 4, 20 + k * 8); c.stroke(); } }
      c.restore();
      c.strokeStyle = '#0a0a0a'; c.lineWidth = 3.5; c.beginPath(); c.moveTo(ex - 24, ey - 20 + (i ? 2 : 0)); c.quadraticCurveTo(ex, ey - 28, ex + 24, ey - 20 - (i ? 0 : 2)); c.stroke();
    });
    if (L.glasses) { c.strokeStyle = '#b08040'; c.lineWidth = 2.5; c.beginPath(); c.arc(-32, -42, 21, 0, 7); c.moveTo(53, -42); c.arc(32, -42, 21, 0, 7); c.moveTo(-11, -42); c.lineTo(11, -42); c.stroke(); }
    if (L.scar) { c.strokeStyle = 'rgba(200,120,130,0.8)'; c.lineWidth = 3; c.beginPath(); c.moveTo(20, -75); c.lineTo(42, -10); c.stroke(); }
    // нос
    c.strokeStyle = 'rgba(0,0,0,0.45)'; c.lineWidth = 2; c.beginPath(); c.moveTo(4, -30); c.lineTo(8, -5); c.lineTo(0, -2); c.stroke();
    // рот
    const m = clamp(mouth);
    c.fillStyle = '#1a0508';
    c.beginPath(); c.ellipse(0, 18, 14 + m * 4, 1.5 + m * 9, 0, 0, 7); c.fill();
    if (L.beard) { c.fillStyle = '#5c5650'; c.beginPath(); c.moveTo(-60, -5); c.quadraticCurveTo(-50, 50, 0, 70); c.quadraticCurveTo(50, 50, 60, -5); c.quadraticCurveTo(40, 30, 0, 32); c.quadraticCurveTo(-40, 30, -60, -5); c.fill(); c.fillStyle = '#1a0508'; c.beginPath(); c.ellipse(0, 18, 12, 1 + m * 7, 0, 0, 7); c.fill(); }
  }
  if (L.owl) {
    const og = c.createLinearGradient(0, -110, 0, 10); og.addColorStop(0, '#f2e6c8'); og.addColorStop(1, '#a8916a');
    c.fillStyle = og; c.beginPath(); c.moveTo(-95, -60); c.quadraticCurveTo(-100, -120, -60, -150); c.lineTo(-40, -110); c.quadraticCurveTo(0, -125, 40, -110); c.lineTo(60, -150);
    c.quadraticCurveTo(100, -120, 95, -60); c.quadraticCurveTo(60, 0, 12, 10); c.lineTo(0, 30); c.lineTo(-12, 10); c.quadraticCurveTo(-60, 0, -95, -60); c.fill();
    c.strokeStyle = 'rgba(90,60,30,0.6)'; c.lineWidth = 2;
    for (let i = 0; i < 10; i++) { c.beginPath(); c.arc(-34, -45, 30 + i * 2.2, 3.4 + i * 0.05, 6.0); c.stroke(); c.beginPath(); c.arc(34, -45, 30 + i * 2.2, 3.4, 6.0 - i * 0.05); c.stroke(); }
    [[-34, -45], [34, -45]].forEach(([ex, ey]) => { c.fillStyle = '#000'; c.beginPath(); c.arc(ex, ey, 24, 0, 7); c.fill();
      glow('#ffb030', 30); c.fillStyle = '#ffb030'; c.beginPath(); c.arc(ex, ey, 11, 0, 7); c.fill(); noGlow(); c.fillStyle = '#000'; c.beginPath(); c.arc(ex, ey, 4, 0, 7); c.fill(); });
    c.fillStyle = '#6a4a20'; c.beginPath(); c.moveTo(-10, -20); c.lineTo(10, -20); c.lineTo(0, 12); c.fill();
  }
  if (o.mask) {
    const mg = c.createLinearGradient(0, -30, 0, 60); mg.addColorStop(0, '#fbf8fb'); mg.addColorStop(1, '#bdb6c4');
    c.fillStyle = mg; c.beginPath(); c.moveTo(-74, -22); c.quadraticCurveTo(0, -36, 74, -22); c.quadraticCurveTo(70, 20, 40, 32); c.quadraticCurveTo(0, 62, -40, 32); c.quadraticCurveTo(-70, 20, -74, -22); c.fill();
    c.strokeStyle = RED; c.lineWidth = 5; glow(RED, 14); c.beginPath(); c.moveTo(-60, 8); c.lineTo(60, 8); c.stroke(); noGlow();
    c.strokeStyle = '#222'; c.lineWidth = 2.5; for (let i = -5; i <= 5; i++) { c.beginPath(); c.moveTo(i * 11, 0); c.lineTo(i * 11, 16); c.stroke(); }
    if (o.cracked) { c.strokeStyle = '#111'; c.lineWidth = 3; c.beginPath(); c.moveTo(50, -24); c.lineTo(38, -4); c.lineTo(52, 12); c.lineTo(44, 30); c.stroke(); c.fillStyle = '#0a0a0e'; c.beginPath(); c.moveTo(74, -22); c.lineTo(50, -24); c.lineTo(38, -4); c.lineTo(66, 4); c.fill(); }
  }
  if (o.hurt) { c.fillStyle = 'rgba(170,0,20,0.85)'; c.beginPath(); c.moveTo(-60, -70); c.quadraticCurveTo(-50, -40, -56, 0); c.lineTo(-48, 0); c.quadraticCurveTo(-44, -40, -52, -72); c.fill(); }
  // волосы
  c.fillStyle = L.hair; glow(rgba(L.rim, 0.6), 15);
  c.beginPath();
  if (L.bob) {
    c.moveTo(-95, 30); c.quadraticCurveTo(-110, -150, 0, -150); c.quadraticCurveTo(110, -150, 95, 30); c.lineTo(70, 30); c.lineTo(72, -70);
    for (let i = 0; i <= 6; i++) c.lineTo(70 - i * 23, -78 + (i % 2) * 18); c.lineTo(-72, 30); c.closePath();
  } else if (L.slick) {
    c.moveTo(-78, -40); c.quadraticCurveTo(-90, -150, 10, -152); c.quadraticCurveTo(100, -150, 80, -60); c.quadraticCurveTo(40, -120, -60, -100); c.lineTo(-74, -30);
  } else if (L.mask) {
    c.moveTo(-80, -60); c.quadraticCurveTo(-90, 60, -110, 120); c.lineTo(-70, 40); c.lineTo(-76, -40);
    c.moveTo(80, -60); c.quadraticCurveTo(90, 60, 110, 120); c.lineTo(70, 40); c.lineTo(76, -40);
  } else if (L.beard) {
    c.moveTo(-78, -50); c.quadraticCurveTo(-80, -140, 0, -145); c.quadraticCurveTo(80, -140, 78, -50); c.quadraticCurveTo(50, -110, -50, -105); c.closePath();
  } else {
    // растрёпанные (Кай)
    c.moveTo(-85, 0); c.lineTo(-95, -80);
    const tips = [[-100, -140], [-60, -170], [-20, -165], [20, -178], [60, -160], [95, -130], [98, -60], [85, 0]];
    c.quadraticCurveTo(-110, -150, -60, -160); tips.forEach(([px, py], i) => c.lineTo(px + Math.sin(t * 2 + i) * 1.5, py));
    c.lineTo(72, -60);
    for (let i = 0; i <= 7; i++) c.lineTo(72 - i * 20, -60 - (i % 2 ? 30 : 0) + (i > 3 ? 10 : 0));
    c.lineTo(-75, -30); c.closePath();
  }
  c.fill(); noGlow();
  if (L.streak) { c.fillStyle = '#e8e8f0'; c.beginPath(); c.moveTo(20, -150); c.lineTo(42, -70); c.lineTo(30, -40); c.lineTo(18, -90); c.fill(); }
  if (o.chains) { c.strokeStyle = '#777'; c.lineWidth = 6; for (let i = 0; i < 9; i++) { c.beginPath(); c.ellipse(-170 + i * 42, 150 + Math.sin(i) * 8, 16, 8, 0.3, 0, 7); c.stroke(); } }
  c.restore();
}

