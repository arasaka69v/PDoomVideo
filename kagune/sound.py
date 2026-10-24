"""Звук: эмбиент, эффекты, музыка и сведение с голосом.

python3 sound.py <out> <номер эпизода>  ->  <out>/epN/mix.wav
Все звуки синтезируются здесь же, без сэмплов.
"""
import json, sys, wave
from pathlib import Path
import numpy as np

SR = 48000
OUT = Path(sys.argv[1])
EP = int(sys.argv[2])
rng = np.random.default_rng(EP * 7 + 1)

def t_(d): return np.arange(int(d * SR)) / SR

def lp(x, cut):
    """Однополюсный фильтр нижних частот (дважды)."""
    a = np.exp(-2 * np.pi * cut / SR)
    from scipy.signal import lfilter
    y = lfilter([1 - a], [1, -a], x)
    return lfilter([1 - a], [1, -a], y)

def hp(x, cut): return x - lp(x, cut)

def bp(x, lo, hi): return hp(lp(x, hi), lo)

def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)

def noise(d): return rng.standard_normal(int(d * SR))

def pink(d):
    w = noise(d)
    return lp(w, 900) * 3 + lp(w, 150) * 6 + w * 0.15

# ---------- эффекты ----------
def sfx_impact():
    d = 0.9; t = t_(d); n = len(t)
    body = np.sin(2 * np.pi * (40 + 120 * np.exp(-t * 18)) * t) * env_ad(n, 0.002, 0.25)
    crack = bp(noise(d), 800, 6000) * env_ad(n, 0.001, 0.05)
    return (body * 1.1 + crack * 0.7)

def sfx_boom():
    d = 3.5; t = t_(d); n = len(t)
    sub = np.sin(2 * np.pi * (30 + 50 * np.exp(-t * 4)) * t) * env_ad(n, 0.01, 1.2)
    rum = lp(noise(d), 200) * env_ad(n, 0.02, 1.0) * 4
    return sub * 1.2 + rum

def sfx_heartbeat():
    d = 0.8; out = np.zeros(int(d * SR))
    for off, amp in ((0, 1.0), (0.22, 0.7)):
        tt = t_(0.25); n = len(tt)
        b = np.sin(2 * np.pi * (45 + 30 * np.exp(-tt * 30)) * tt) * env_ad(n, 0.004, 0.07) * amp
        i = int(off * SR); out[i:i + n] += b
    return out * 1.4

def sfx_tentacle():
    d = 1.6; t = t_(d); n = len(t)
    wet = bp(noise(d), 300, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * (9 + 6 * t) * t)) ** 2
    growl = np.sin(2 * np.pi * (70 + 20 * np.sin(2 * np.pi * 3 * t)) * t) * 0.5
    whip = bp(noise(d), 1500, 7000) * np.exp(-((t - 0.9) / 0.06) ** 2)
    e = env_ad(n, 0.25, 0.6)
    return (wet * 1.2 + growl) * e + whip * 1.2

def sfx_whoosh():
    d = 0.7; t = t_(d); n = len(t)
    x = noise(d)
    e = np.sin(np.pi * t / d) ** 2
    return bp(x, 400, 3000) * e * 0.9

def sfx_blade():
    d = 1.4; t = t_(d); n = len(t)
    ring = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((2300, 0.3), (3170, 0.2), (4410, 0.12)))
    return sfx_whoosh_pad(d) + ring * env_ad(n, 0.005, 0.4) * 0.8

def sfx_whoosh_pad(d):
    x = np.zeros(int(d * SR)); w = sfx_whoosh(); x[:len(w)] += w; return x

def sfx_sting():
    d = 3.0; t = t_(d); n = len(t)
    cl = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in (220, 233, 311, 466, 622))
    return cl * env_ad(n, 0.02, 1.2) * 0.25 + sfx_boom()[:n] * 0.4

def sfx_glitch():
    d = 0.6; x = noise(d)
    x = np.round(x * 3) / 3
    gate = (np.sin(2 * np.pi * 37 * t_(d)) > 0).astype(float)
    return bp(x, 500, 5000) * gate * 0.5

def sfx_beep():
    t = t_(0.18); return np.sin(2 * np.pi * 1046 * t) * env_ad(len(t), 0.005, 0.08) * 0.35

def sfx_alarm():
    d = 4.0; t = t_(d)
    f = np.where((t * 2) % 1 < 0.5, 660, 880)
    ph = np.cumsum(2 * np.pi * f / SR)
    return np.sign(np.sin(ph)) * 0.12 * lp(np.ones_like(t), 50) * np.minimum(1, (d - t) * 2)

def sfx_steps():
    d = 4.0; out = np.zeros(int(d * SR))
    for k in range(7):
        s = lp(noise(0.12), 900) * env_ad(int(0.12 * SR), 0.002, 0.03) * 3
        s += bp(noise(0.12), 2000, 6000) * env_ad(int(0.12 * SR), 0.001, 0.015) * 0.6  # мокрый асфальт
        i = int(k * 0.55 * SR); out[i:i + len(s)] += s
    return out

def sfx_crows():
    d = 3.0; out = np.zeros(int(d * SR))
    for k in range(6):
        cd = 0.35; t = t_(cd)
        f = 700 + 200 * np.sin(np.pi * t / cd) + rng.random() * 200
        caw = np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))) * bp(noise(cd), 600, 3000) * 0.3
        caw = bp(caw, 500, 3500) * np.sin(np.pi * t / cd) ** 0.5
        i = int((k * 0.42 + rng.random() * 0.2) * SR); out[i:i + len(caw)] += caw * 0.5
    return out

def sfx_chain():
    d = 1.5; out = np.zeros(int(d * SR))
    for k in range(9):
        t = t_(0.2)
        c = sum(np.sin(2 * np.pi * f * t) for f in (1800 + rng.random() * 900, 3900 + rng.random() * 900)) * env_ad(len(t), 0.001, 0.04)
        i = int((k * 0.13 + rng.random() * 0.05) * SR); out[i:i + len(c)] += c * 0.25
    return out

def sfx_glass():
    d = 2.0; out = bp(noise(d), 3000, 9000) * env_ad(int(d * SR), 0.002, 0.3) * 0.8
    for k in range(20):
        t = t_(0.15); f = 3000 + rng.random() * 5000
        c = np.sin(2 * np.pi * f * t) * env_ad(len(t), 0.001, 0.03) * 0.2
        i = int(rng.random() * 1.6 * SR); out[i:i + len(c)] += c
    return out

SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_") and k != "sfx_whoosh_pad"}

# ---------- эмбиент ----------
def amb(kind, d):
    t = t_(d)
    if kind == "rain":
        x = hp(pink(d), 400) * 0.08
        drops = (rng.random(len(t)) > 0.9993) * rng.random(len(t))
        x += bp(drops, 1500, 6000) * 4
        return x + lp(noise(d), 120) * 0.15
    if kind == "drone":
        return (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 55.7 * t) + 0.3 * np.sin(2 * np.pi * 82.4 * t)) * 0.06 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    if kind == "metro":
        return lp(noise(d), 180) * 0.5 + np.sin(2 * np.pi * 50 * t) * 0.02 + bp(noise(d), 800, 1200) * 0.01
    if kind == "fire":
        crack = (rng.random(len(t)) > 0.998) * rng.standard_normal(len(t))
        return lp(noise(d), 400) * 0.5 + bp(crack, 1000, 6000) * 2.0
    if kind == "wind":
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
        return bp(noise(d), 200, 900) * 0.25 * (0.3 + mod)
    if kind == "lab":
        return np.sin(2 * np.pi * 120 * t) * 0.012 + bp(noise(d), 2000, 4000) * 0.004 + lp(noise(d), 100) * 0.1
    if kind == "city":
        return lp(noise(d), 300) * 0.35 + np.sin(2 * np.pi * 0.05 * t) * 0 + hp(pink(d), 2000) * 0.01
    return np.zeros(len(t))

# ---------- музыка ----------
def note(m): return 440 * 2 ** ((m - 69) / 12)

def pad(d, chords, bar):
    """Тёмный синт-пэд: пилы через фильтр, по аккорду на такт."""
    t = t_(d); out = np.zeros(len(t))
    for i in range(int(np.ceil(d / bar))):
        ch = chords[i % len(chords)]
        a, b = int(i * bar * SR), min(len(t), int((i + 1) * bar * SR + 0.5 * SR))
        tt = t[a:b] - t[a]
        seg = np.zeros(b - a)
        for m in ch:
            for det in (-0.08, 0.08):
                f = note(m) * (1 + det / 100)
                seg += 2 * ((f * tt) % 1) - 1
        e = np.minimum(1, tt / 1.5) * np.minimum(1, np.maximum(0, (b - a) / SR - tt) / 0.5)
        out[a:b] += seg * e
    return lp(out, 700) * 0.035

def drums(d, bpm=140):
    out = np.zeros(int(d * SR)); beat = 60 / bpm
    kick = (lambda tt: np.sin(2 * np.pi * (45 + 90 * np.exp(-tt * 35)) * tt) * env_ad(len(tt), 0.002, 0.18))(t_(0.4))
    snare = (lambda n: bp(noise(0.3), 1000, 6000) * env_ad(n, 0.001, 0.08) + np.sin(2 * np.pi * 190 * t_(0.3)) * env_ad(n, 0.001, 0.05))(int(0.3 * SR))
    hat = bp(noise(0.05), 6000, 12000) * env_ad(int(0.05 * SR), 0.001, 0.015)
    pattern = "K.hK.hS.K.hKShSh"
    k = 0; tpos = 0.0
    while tpos < d - 0.5:
        c = pattern[k % 16]; i = int(tpos * SR)
        for ch, smp, g in (("K", kick, 0.9), ("S", snare, 0.5), ("h", hat, 0.25)):
            if c == ch:
                n = min(len(smp), len(out) - i); out[i:i + n] += smp[:n] * g
        if c in "KS":
            n = min(len(hat), len(out) - i); out[i:i + n] += hat[:n] * 0.15
        k += 1; tpos += beat / 4
    bass = np.zeros_like(out); tt = t_(d)
    bass = np.sign(np.sin(2 * np.pi * note(33) * tt)) * 0.05 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * tt / beat * 2)))
    return out * 0.7 + lp(bass, 300)

CHORDS = {
    1: [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 58], [40, 47, 52, 56]],  # Am F Gm E
    2: [[38, 45, 50, 53], [34, 41, 46, 50], [36, 43, 48, 51], [33, 40, 45, 49]],  # Dm Bb Cm A
    3: [[40, 47, 52, 55], [36, 43, 48, 52], [38, 45, 50, 54], [35, 42, 47, 51]],  # Em C D B
}

def read(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * g

def fade(x, f=0.4):
    n = min(int(f * SR), len(x) // 2)
    if n > 0:
        r = np.linspace(0, 1, n); x[:n] *= r; x[-n:] *= r[::-1]
    return x

def main():
    tl = json.loads((OUT / f"ep{EP}" / "timeline.json").read_text())
    D = tl["dur"] + 0.5; N = int(D * SR)
    vo = np.zeros(N); fx = np.zeros(N); bed = np.zeros(N); mus = np.zeros(N); drm = np.zeros(N)
    for s in tl["shots"]:
        d = s["t1"] - s["t0"]
        if s.get("amb"):
            place(bed, fade(amb(s["amb"], d + 0.6), 0.5), max(0, s["t0"] - 0.3))
        for name, off in s.get("sfx", []):
            place(fx, SFX[name](), s["t0"] + off, 0.8)
        if s.get("fight"):
            place(drm, fade(drums(d), 0.3), s["t0"])
        for ln in s["lines"]:
            place(vo, read(OUT / ln["wav"]), ln["t0"])
    mus = pad(D, CHORDS[EP], 60 / 70 * 4 * 2)
    # ducking: музыка и фон тише под голосом
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    lvl = uniform_filter1d(maximum_filter1d(np.abs(vo), int(0.3 * SR)), int(0.2 * SR))
    duck = 1 - 0.55 * np.clip(lvl * 4, 0, 1)
    mix = vo * 1.0 + fx * 0.55 + bed * duck * 0.9 + mus * duck * 1.0 + drm * duck * 0.55
    # плавно в конце
    mix[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    mix = np.tanh(mix * 1.1) * 0.9
    st = np.stack([mix, mix], 1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(OUT / f"ep{EP}" / "mix.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(f"ep{EP} mix: {D:.1f}s peak={np.abs(mix).max():.2f}")

if __name__ == "__main__":
    main()
