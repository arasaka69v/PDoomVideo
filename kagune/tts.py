"""Озвучка: каждая реплика -> wav, плюс timeline.json для рендера.

python3 tts.py <папка_с_голосами> <out>
Голоса — Piper (vits-piper-ru_RU-*), см. README.
"""
import json, subprocess, sys, wave, hashlib
from pathlib import Path
import numpy as np
from piper import PiperVoice, SynthesisConfig
from story import EPISODES, SPEAKERS

VOICES_DIR = Path(sys.argv[1])
OUT = Path(sys.argv[2])
SR = 48000
FPS = 30

# голос Piper, скорость речи (length_scale), обработка ffmpeg
CAST = {
    "kai":   ("ruslan", 1.04, "rubberband=pitch=0.97,aecho=0.8:0.35:30:0.10"),
    "mira":  ("irina",  1.00, "rubberband=pitch=1.05,aecho=0.8:0.3:30:0.08"),
    "rust":  ("dmitri", 1.14, "rubberband=pitch=0.84,bass=g=3,aecho=0.8:0.35:40:0.12"),
    "varg":  ("denis",  1.06, "rubberband=pitch=0.90,bass=g=4,acompressor=threshold=0.1:ratio=3"),
    "king":  ("dmitri", 1.12, "rubberband=pitch=0.76,chorus=0.6:0.9:50|60:0.4|0.32:0.25|0.4:2|1.3,aecho=0.8:0.6:120|240:0.35|0.2"),
    "voice": ("dmitri", 1.15, "rubberband=pitch=0.76,lowpass=f=2500,aecho=0.8:0.7:200|400:0.4|0.25"),
    "ghoul": ("denis",  1.30, "rubberband=pitch=0.68,acrusher=bits=8:mix=0.25,aecho=0.8:0.5:60:0.3"),
    "inner": ("ruslan", 0.95, "rubberband=pitch=0.72,chorus=0.7:0.9:40|70:0.5|0.4:0.3|0.5:2|1.5,aecho=0.8:0.7:90|180:0.5|0.3,volume=1.4"),
}

_loaded = {}
def voice(name):
    if name not in _loaded:
        d = VOICES_DIR / f"vits-piper-ru_RU-{name}-medium"
        _loaded[name] = PiperVoice.load(str(d / f"ru_RU-{name}-medium.onnx"))
    return _loaded[name]

def synth(who, text, path):
    vname, ls, filt = CAST[who]
    raw = path.with_suffix(".raw.wav")
    with wave.open(str(raw), "wb") as w:
        voice(vname).synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.8))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    f"{filt},silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-16:TP=-1.5",
                    "-ar", str(SR), "-ac", "1", str(path)], check=True)
    raw.unlink()

def read(path):
    with wave.open(str(path)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a

def envelope(a):
    hop = SR // FPS
    n = len(a) // hop + 1
    env = [float(np.sqrt(np.mean(a[i*hop:(i+1)*hop] ** 2) + 1e-9)) for i in range(n)]
    m = max(env) or 1
    return [round(min(1, e / m * 1.3), 2) for e in env]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for ep in EPISODES:
        vdir = OUT / f"ep{ep['id']}" / "vo"
        vdir.mkdir(parents=True, exist_ok=True)
        t = 0.0
        shots = []
        for si, s in enumerate(ep["shots"]):
            start = t
            cur = start + s.get("pre", 0.6 if s.get("lines") else 0)
            lines = []
            for li, (who, text) in enumerate(s.get("lines", [])):
                key = hashlib.md5(f"{who}|{text}|{CAST[who]}".encode()).hexdigest()[:10]
                path = vdir / f"{si:02d}_{li}_{who}_{key}.wav"
                if not path.exists():
                    synth(who, text, path)
                a = read(path)
                dur = len(a) / SR
                lines.append({"who": who, "name": SPEAKERS[who]["name"], "color": SPEAKERS[who]["color"],
                              "text": text, "t0": round(cur, 3), "t1": round(cur + dur, 3),
                              "wav": str(path.relative_to(OUT)), "env": envelope(a)})
                cur += dur + 0.45
            end = cur + s.get("hold", 0.8 if s.get("lines") else 3)
            shots.append({**{k: v for k, v in s.items() if k != "lines"}, "i": si,
                          "t0": round(start, 3), "t1": round(end, 3), "lines": lines})
            t = end
        tl = {"id": ep["id"], "title": ep["title"], "dur": round(t, 3), "fps": FPS, "shots": shots}
        (OUT / f"ep{ep['id']}" / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False))
        print(f"ep{ep['id']}: {t:.1f}s, {len(shots)} shots")

if __name__ == "__main__":
    main()
