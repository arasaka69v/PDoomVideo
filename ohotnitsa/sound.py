"""Звук «Охотницы»: бит, эффекты, атмосфера и сведение с голосом.

python3 sound.py <out> <часть>  ->  <out>/pN/mix.wav
Бит идёт без остановки через всю часть; его громкость по слоям задаёт
поле «beat» у кадров: нет — только тёмный пэд, True — 808 и хэты, "drop" — всё.
"""
import json, sys, wave
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SR = 48000
OUT = Path(sys.argv[1]); PART = int(sys.argv[2])
rng = np.random.default_rng(PART * 11 + 3)

def T(d): return np.arange(int(d * SR)) / SR
def lp(x, f):
    a = np.exp(-2 * np.pi * f / SR); y = lfilter([1 - a], [1, -a], x); return lfilter([1 - a], [1, -a], y)
def hp(x, f): return x - lp(x, f)
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
def noise(d): return rng.standard_normal(int(d * SR))
def note(m): return 440 * 2 ** ((m - 69) / 12)

# ---------- эффекты ----------
def fx_impact():
    t = T(0.8); n = len(t)
    return np.sin(2*np.pi*(45 + 140*np.exp(-t*20))*t)*env(n, .002, .22)*1.2 + bp(noise(.8), 900, 7000)*env(n, .001, .05)*.8
def fx_boom():
    t = T(3.0); n = len(t)
    return np.sin(2*np.pi*(32 + 60*np.exp(-t*5))*t)*env(n, .01, 1.1)*1.3 + lp(noise(3), 180)*env(n, .02, .9)*4
def fx_heart():
    out = np.zeros(int(.8*SR))
    for off, g in ((0, 1), (.21, .7)):
        t = T(.25); b = np.sin(2*np.pi*(48 + 30*np.exp(-t*30))*t)*env(len(t), .004, .07)*g
        i = int(off*SR); out[i:i+len(b)] += b
    return out * 1.5
def fx_tentacle():
    t = T(1.4); n = len(t)
    wet = bp(noise(1.4), 300, 2500) * (.5 + .5*np.sin(2*np.pi*(9 + 7*t)*t))**2
    whip = bp(noise(1.4), 1500, 8000) * np.exp(-((t - .8)/.05)**2)
    return (wet*1.2 + np.sin(2*np.pi*70*t)*.4)*env(n, .2, .5) + whip*1.4
def fx_whoosh():
    t = T(.6); return bp(noise(.6), 500, 3500) * np.sin(np.pi*t/.6)**2
def fx_blade():
    t = T(1.2); ring = sum(np.sin(2*np.pi*f*t)*a for f, a in ((2300, .3), (3170, .2), (4410, .12)))
    w = np.zeros(len(t)); s = fx_whoosh(); w[:len(s)] += s
    return w + ring*env(len(t), .004, .35)*.7
def fx_metal():
    t = T(1.0); out = sum(np.sin(2*np.pi*f*t) for f in (520, 1340, 2210, 3790))*env(len(t), .001, .25)*.25
    imp = fx_impact(); out[:len(imp)] += imp*.3
    return out
def fx_crash():
    d = 1.6; out = bp(noise(d), 2500, 10000)*env(int(d*SR), .002, .35)*.9
    for k in range(25):
        t = T(.12); c = np.sin(2*np.pi*(2500 + rng.random()*5000)*t)*env(len(t), .001, .03)*.25
        i = int(rng.random()*1.3*SR); out[i:i+len(c)] += c
    imp = fx_impact(); out[:len(imp)] += imp*.6
    return out
def fx_siren():
    d = 4.0; t = T(d); f = 700 + 350*np.sin(2*np.pi*.5*t)
    s = np.sin(np.cumsum(2*np.pi*f/SR)); return lp(s, 2500)*.12*np.minimum(1, t*2)*np.minimum(1, (d - t)*1.5)
def fx_growl():
    d = 1.8; t = T(d)
    g = np.sin(2*np.pi*(65 + 15*np.sin(2*np.pi*4*t))*t) * (.6 + .4*np.sin(2*np.pi*23*t))
    return (np.tanh(g*3)*.35 + bp(noise(d), 200, 1200)*.3) * env(len(t), .3, .9)
def fx_glint():
    t = T(1.5); return sum(np.sin(2*np.pi*f*t)*a for f, a in ((2637, .3), (3951, .2), (5274, .1)))*env(len(t), .002, .5)*.6
def fx_knock():
    out = np.zeros(int(1.0*SR))
    for k in range(3):
        t = T(.15); b = (np.sin(2*np.pi*(180 + 60*np.exp(-t*40))*t) + lp(noise(.15), 2000)*.6)*env(len(t), .001, .03)
        i = int(k*.23*SR); out[i:i+len(b)] += b*1.2
    return out
def fx_door():
    d = 1.4; t = T(d); f = 300 + 200*np.sin(2*np.pi*.6*t)
    cr = np.sign(np.sin(np.cumsum(2*np.pi*f/SR)))*bp(noise(d), 300, 2000)*.15
    return bp(cr, 250, 2500)*np.sin(np.pi*t/d)
def fx_scan():
    d = 1.4; t = T(d); f = 800 + 1600*t/d
    return np.sin(np.cumsum(2*np.pi*f/SR))*.12*(.5 + .5*np.sign(np.sin(2*np.pi*14*t)))*np.minimum(1, (d - t)*5)
def fx_ok():
    out = np.zeros(int(.6*SR))
    for k, f in enumerate((880, 1318)):
        t = T(.18); b = np.sin(2*np.pi*f*t)*env(len(t), .003, .08)*.4; i = int(k*.12*SR); out[i:i+len(b)] += b
    return out
def fx_alarm():
    d = 3.0; t = T(d); f = np.where((t*3) % 1 < .5, 440, 330)
    return np.sign(np.sin(np.cumsum(2*np.pi*f/SR)))*.13*np.minimum(1, (d - t)*2)
def fx_sting():
    t = T(2.5); return sum(np.sin(2*np.pi*f*t + rng.random()*6) for f in (233, 247, 311, 466))*env(len(t), .01, 1)*.22 + fx_boom()[:len(t)]*.4
def fx_glitch():
    d = .5; x = np.round(noise(d)*3)/3; return bp(x, 500, 5000)*(np.sin(2*np.pi*37*T(d)) > 0)*.45
def fx_reload():
    out = np.zeros(int(.8*SR))
    for off in (0, .35):
        t = T(.12); b = bp(noise(.12), 1500, 7000)*env(len(t), .001, .02)*1.2 + np.sin(2*np.pi*900*t)*env(len(t), .001, .02)*.3
        i = int(off*SR); out[i:i+len(b)] += b
    return out
def fx_crystal():
    d = 2.0; out = np.zeros(int(d*SR))
    for k in range(14):
        t = T(.9); f = note(84 + [0, 3, 7, 10, 12, 15][k % 6])
        b = np.sin(2*np.pi*f*t)*env(len(t), .002, .35)*.18; i = int(k*.07*SR); out[i:i+len(b)] += b
    return out + bp(noise(d), 4000, 12000)*env(int(d*SR), .05, .4)*.25

FX = {k[3:]: v for k, v in globals().items() if k.startswith("fx_")}

# ---------- атмосфера ----------
def amb(kind, d):
    t = T(d)
    if kind == "rain":
        drops = (rng.random(len(t)) > .9993)*rng.random(len(t))
        return hp(lp(noise(d), 3000), 500)*.05 + bp(drops, 1500, 6000)*3 + lp(noise(d), 120)*.15
    if kind == "drone":
        return (np.sin(2*np.pi*55*t) + .6*np.sin(2*np.pi*55.6*t) + .3*np.sin(2*np.pi*82.4*t))*.05
    if kind == "cafe":   # гул голосов и посуда
        murmur = bp(noise(d), 250, 1800)*.05*(.7 + .3*np.sin(2*np.pi*.3*t))
        clinks = (rng.random(len(t)) > .99993)*1.0
        return murmur + bp(clinks, 2500, 8000)*2
    if kind == "street":
        return lp(noise(d), 300)*.3 + bp(noise(d), 600, 1500)*.01
    if kind == "wind":
        m = .5 + .5*np.sin(2*np.pi*.13*t)*np.sin(2*np.pi*.07*t + 1)
        return bp(noise(d), 200, 900)*.22*(.3 + m)
    if kind == "room":
        return lp(noise(d), 200)*.08 + np.sin(2*np.pi*60*t)*.004
    return np.zeros(len(t))

# ---------- бит ----------
BPM = 130
CHORDS = [[53, 56, 60], [49, 53, 56], [51, 54, 58], [48, 52, 55]]   # Fm Db Ebm C
BASS = [41, 37, 39, 36]

def beat_stems(D):
    beat = 60 / BPM; bar = beat * 4; N = int(D*SR)
    pad = np.zeros(N); b808 = np.zeros(N); drums = np.zeros(N); hats = np.zeros(N); bell = np.zeros(N)
    nb = int(np.ceil(D / bar)) + 1
    for bi in range(nb):
        b0 = bi * bar; ci = bi % 4
        # пэд
        a, z = int(b0*SR), min(N, int((b0 + bar)*SR))
        if a >= N: break
        tt = np.arange(z - a)/SR; seg = np.zeros(z - a)
        for m in CHORDS[ci]:
            for det in (-.1, .1):
                f = note(m)*(1 + det/100); seg += 2*((f*tt) % 1) - 1
        pad[a:z] += lp(seg, 900)*.02*np.minimum(1, tt/.3)
        # 808: на 1 и «и» 3-й доли
        for off, m in ((0, BASS[ci]), (beat*2.5, BASS[ci] + (12 if bi % 2 else 0))):
            t = T(1.4); f = note(m)*(1 + 1.5*np.exp(-t*30))
            s = np.tanh(np.sin(np.cumsum(2*np.pi*f/SR))*2.2)*env(len(t), .003, .55)*.42
            i = int((b0 + off)*SR); n = min(len(s), N - i)
            if n > 0: b808[i:i+n] += s[:n]
        # бочка + хлопок (хлопок на 3-й доле — «полутемп»)
        for off in (0, beat*2.5):
            t = T(.3); k = np.sin(2*np.pi*(50 + 120*np.exp(-t*40))*t)*env(len(t), .002, .1)*.7
            i = int((b0 + off)*SR); n = min(len(k), N - i)
            if n > 0: drums[i:i+n] += k[:n]
        t = T(.35); clap = bp(noise(.35), 900, 5000)*env(len(t), .002, .09)*.55 + bp(noise(.35), 2000, 8000)*env(len(t), .001, .02)*.3
        i = int((b0 + beat*2)*SR); n = min(len(clap), N - i)
        if n > 0: drums[i:i+n] += clap[:n]
        # хэты: восьмые, в конце такта — ролл тридцать вторыми
        steps = [s*beat/2 for s in range(8)]
        if bi % 2: steps = steps[:6] + [beat*3 + k*beat/8 for k in range(8)]
        for off in steps:
            t = T(.05); h = bp(noise(.05), 7000, 14000)*env(len(t), .001, .015)*.25
            i = int((b0 + off)*SR); n = min(len(h), N - i)
            if n > 0: hats[i:i+n] += h[:n]
        # мелодия-колокол (фонк)
        mel = [72, 75, 77, 75, 72, 70, 72, 68] if ci % 2 == 0 else [72, 75, 80, 79, 77, 75, 72, 75]
        for k, m in enumerate(mel):
            t = T(.3); f = note(m)
            s = (np.sign(np.sin(2*np.pi*f*t))*.5 + np.sin(2*np.pi*f*1.48*t)*.5)*env(len(t), .001, .08)
            s = bp(s, 500, 4000)*.09
            i = int((b0 + k*beat/2)*SR); n = min(len(s), N - i)
            if n > 0: bell[i:i+n] += s[:n]
    return pad, b808, drums, hats, bell

def read(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768

def place(buf, x, t, g=1.0):
    i = int(t*SR)
    if i >= len(buf): return
    n = min(len(x), len(buf) - i); buf[i:i+n] += x[:n]*g

def fade(x, f=.3):
    n = min(int(f*SR), len(x)//2)
    if n > 0: r = np.linspace(0, 1, n); x[:n] *= r; x[-n:] *= r[::-1]
    return x

def main():
    tl = json.loads((OUT/f"p{PART}"/"timeline.json").read_text())
    D = tl["dur"] + .3; N = int(D*SR)
    vo = np.zeros(N); fx = np.zeros(N); bed = np.zeros(N)
    lvl = np.zeros(N)  # 0 — пэд, 1 — бит, 2 — дроп
    for s in tl["shots"]:
        d = s["t1"] - s["t0"]
        if s.get("amb"): place(bed, fade(amb(s["amb"], d + .5), .4), max(0, s["t0"] - .25))
        for name, off in s.get("sfx", []): place(fx, FX[name](), s["t0"] + off, .75)
        for ln in s["lines"]: place(vo, read(OUT/ln["wav"]), ln["t0"])
        b = s.get("beat"); lvl[int(s["t0"]*SR):int(s["t1"]*SR)] = 2 if b == "drop" else 1 if b else 0
    lvl = uniform_filter1d(lvl, int(.25*SR))
    pad, b808, drums, hats, bell = beat_stems(D)
    g1 = np.clip(lvl, 0, 1); g2 = np.clip(lvl - 1, 0, 1)
    music = pad*(1 - .3*g2) + b808*g1 + hats*g1*.8 + drums*(.35*g1 + .65*g2) + bell*g2
    music = np.tanh(music*1.3)*.75
    v = uniform_filter1d(maximum_filter1d(np.abs(vo), int(.25*SR)), int(.15*SR))
    duck = 1 - .5*np.clip(v*4, 0, 1)
    mix = vo*1.05 + fx*.55 + bed*duck*.8 + music*duck*.85
    mix[-int(.8*SR):] *= np.linspace(1, 0, int(.8*SR))
    mix = np.tanh(mix*1.05)*.92
    pcm = (np.clip(np.stack([mix, mix], 1), -1, 1)*32767).astype(np.int16)
    with wave.open(str(OUT/f"p{PART}"/"mix.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(f"part {PART} mix {D:.1f}s peak {np.abs(mix).max():.2f}")

if __name__ == "__main__":
    main()
