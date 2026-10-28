"""Озвучка «Охотницы».

python3 voice.py <папка_с_голосами_piper> <out>

Что делает голос живее, чем «просто TTS»:
  1. Ударения расставляет нейросеть Silero (silero_stress) и передаёт их
     в синтезатор знаком ударения над гласной — без неё espeak ошибается.
  2. Текст синтезируется по предложениям; паузы между ними зависят от
     знака: «.» короче, «...» длиннее, как у живого чтеца.
  3. Каждому герою — свой темп и «разброс» интонации.
  4. Обработка как в студии: срез гула, тёплый низ, разборчивость,
     де-эссер, мягкий компрессор, небольшая комната. Голос не «роботизируется».
"""
import json, re, subprocess, sys, wave, hashlib
from pathlib import Path
import numpy as np
from piper import PiperVoice, SynthesisConfig
from story import PARTS, SPEAKERS

VOICES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out")
SR = 48000
FPS = 30
ACUTE = "́"

# голос, темп (length_scale), выразительность (noise_scale), ритм (noise_w), обработка
CAST = {
    "narr":  ("ruslan", 1.06, 0.62, 0.85, "studio_close"),
    "mark":  ("ruslan", 1.00, 0.66, 0.85, "studio_room"),
    "nika":  ("irina",  0.97, 0.70, 0.90, "studio_room"),
    "grach": ("dmitri", 1.13, 0.50, 0.70, "deep"),
    "sova":  ("denis",  0.93, 0.75, 0.95, "studio_room"),
    "beast": ("denis",  1.30, 0.60, 0.90, "beast"),
}

CHAIN = {
    # срез гула, тепло, разборчивость, де-эссер, компрессор
    "base": "highpass=f=75,equalizer=f=180:t=q:w=1.2:g=2.5,equalizer=f=3200:t=q:w=1.4:g=2.5,"
            "equalizer=f=7500:t=q:w=2:g=-2,deesser=i=0.4,acompressor=threshold=0.12:ratio=2.5:attack=8:release=120:makeup=1.5",
}
FX = {
    "studio_close": CHAIN["base"],
    "studio_room":  CHAIN["base"] + ",aecho=0.9:0.3:23|37:0.07|0.05",
    "deep":         "rubberband=pitch=0.93:formant=preserved," + CHAIN["base"] + ",equalizer=f=120:t=q:w=1:g=3,aecho=0.9:0.3:29:0.06",
    "beast":        "rubberband=pitch=0.72:formant=shifted,acrusher=bits=10:mix=0.15," + CHAIN["base"] + ",aecho=0.8:0.5:45|90:0.25|0.15",
}

# ---------- ударения ----------
_acc = None
def stress(text):
    """Ставит ударения (U+0301) через Silero. Ё не трогаем — она сама ударная."""
    global _acc
    try:
        if _acc is None:
            from silero_stress import load_accentor
            _acc = load_accentor()
        marked = _acc(text)
    except Exception as e:  # без пакета — синтез без подсказок
        print("  ! silero_stress недоступен:", e)
        return text
    # Silero ставит «+» перед ударной гласной -> гласная + знак ударения.
    # Односложным словам («на», «не», «и») ударение не ставим — иначе речь рубленая.
    # Слова с «ё» и так ударные.
    def word(m):
        w = m.group(0); plain = w.replace("+", "")
        if len(re.findall(r"[аеёиоуыэюя]", plain.lower())) < 2 or "ё" in plain.lower():
            return plain
        return re.sub(r"\+([аеиоуыэюяАЕИОУЫЭЮЯ])", lambda v: v.group(1) + ACUTE, w)
    return re.sub(r"[+А-Яа-яЁё]+", word, marked)

# ---------- синтез ----------
_voices = {}
def voice(name):
    if name not in _voices:
        d = VOICES / f"vits-piper-ru_RU-{name}-medium"
        _voices[name] = PiperVoice.load(str(d / f"ru_RU-{name}-medium.onnx"))
    return _voices[name]

def sentences(text):
    """Режем на предложения, сохраняя знак в конце."""
    parts = re.findall(r"[^.!?…]+(?:\.\.\.|[.!?…]+|$)", text.replace("...", "…"))
    return [p.strip() for p in parts if p.strip()]

def pause_after(s):
    if s.endswith("…"): return 0.55
    if s.endswith("?") or s.endswith("!"): return 0.32
    return 0.38

def synth_sentence(who, s):
    vname, ls, ns, nw, _ = CAST[who]
    v = voice(vname)
    # вопрос и восклицание чуть быстрее, многоточие — медленнее
    k = 0.95 if s[-1] in "!?" else 1.06 if s.endswith("…") else 1.0
    cfg = SynthesisConfig(length_scale=ls * k, noise_scale=ns, noise_w_scale=nw)
    ph = v.phonemize(stress(s))
    ph = [[p for p in sent if p != '"'] for sent in ph]  # лишний маркер вторичного ударения
    audio = []
    for sent in ph:
        ids = v.phonemes_to_ids(sent)
        a = v.phoneme_ids_to_audio(ids, cfg)
        audio.append(np.asarray(a, dtype=np.float32).flatten())
    a = np.concatenate(audio) if audio else np.zeros(1, np.float32)
    # обрезать тишину по краям
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 200): nz[-1] + 1200]
    return a, v.config.sample_rate

def synth_line(who, text, path):
    chunks, words = [], []
    sr0 = None; t = 0.0
    for s in sentences(text):
        a, sr0 = synth_sentence(who, s)
        dur = len(a) / sr0
        # слова внутри предложения — по длине, для субтитров «караоке»
        ws = s.replace("…", "...").split()
        tot = sum(len(w) + 2 for w in ws)
        acc = 0
        for w in ws:
            w0 = t + dur * acc / tot; acc += len(w) + 2
            words.append([w, round(w0, 3), round(t + dur * acc / tot, 3)])
        chunks.append(a); pz = pause_after(s)
        chunks.append(np.zeros(int(pz * sr0), np.float32))
        t += dur + pz
    a = np.concatenate(chunks[:-1])
    raw = path.with_suffix(".raw.wav")
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr0)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    fx = FX[CAST[who][4]]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    f"aresample={SR}:resampler=soxr,{fx},loudnorm=I=-17:TP=-1.5:LRA=9",
                    "-ar", str(SR), "-ac", "1", str(path)], check=True)
    raw.unlink()
    # длина после обработки может чуть отличаться — подгоняем тайминги слов
    real = read(path)
    k = (len(real) / SR) / max(t - pause_after(sentences(text)[-1]), 1e-3)
    for w in words: w[1] = round(w[1] * k, 3); w[2] = round(w[2] * k, 3)
    return words

def read(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def envelope(a):
    hop = SR // FPS
    env = [float(np.sqrt(np.mean(a[i*hop:(i+1)*hop] ** 2) + 1e-9)) for i in range(len(a) // hop + 1)]
    m = max(env) or 1
    return [round(min(1, e / m * 1.4), 2) for e in env]

def main():
    only = sys.argv[3] if len(sys.argv) > 3 else None
    for part in PARTS:
        if only and str(part["id"]) != only: continue
        d = OUT / f"p{part['id']}"; (d / "vo").mkdir(parents=True, exist_ok=True)
        t = 0.0; shots = []
        for si, s in enumerate(part["shots"]):
            start = t; cur = start + s.get("pre", 0.35 if s.get("lines") else 0)
            lines = []
            for li, (who, text) in enumerate(s.get("lines", [])):
                key = hashlib.md5(f"{who}|{text}|{CAST[who]}|{FX[CAST[who][4]]}|v3".encode()).hexdigest()[:10]
                path = d / "vo" / f"{si:02d}_{li}_{who}_{key}.wav"
                wj = path.with_suffix(".json")
                if not path.exists() or not wj.exists():
                    wj.write_text(json.dumps(synth_line(who, text, path), ensure_ascii=False))
                words = json.loads(wj.read_text())
                a = read(path); dur = len(a) / SR
                lines.append({"who": who, "name": SPEAKERS[who]["name"], "color": SPEAKERS[who]["color"],
                              "text": text, "t0": round(cur, 3), "t1": round(cur + dur, 3),
                              "words": [[w, round(cur + a0, 3), round(cur + a1, 3)] for w, a0, a1 in words],
                              "wav": str(path.relative_to(OUT)), "env": envelope(a)})
                cur += dur + 0.3
            end = cur + s.get("hold", 0.45 if s.get("lines") else 2.5)
            shots.append({**{k: v for k, v in s.items() if k != "lines"}, "i": si,
                          "t0": round(start, 3), "t1": round(end, 3), "lines": lines})
            t = end
        tl = {"id": part["id"], "title": part["title"], "dur": round(t, 3), "fps": FPS, "shots": shots}
        (d / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False))
        print(f"part {part['id']}: {t:.1f}s")

if __name__ == "__main__":
    main()
