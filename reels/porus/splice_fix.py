"""Replace chosen sentences in a finished narration with new takes, keeping everything else untouched.
python3 splice_fix.py <narration.wav> <align.json [[i,start,end],...]> <takes dir: part-0000N.wav, part-0100N.wav> <out.wav> <out sentences.json>
Of the two takes per line, the one closest to the expected length (from the speaker's own pace) is used.
Each new take is trimmed, matched in loudness to the speech around it and joined with 15 ms fades."""
import json, sys, os, re
import numpy as np, soundfile as sf, librosa

SRC, AL, TK, OUT, SOUT = sys.argv[1:6]
P = json.load(open(os.path.join(TK, 'parts.json'))) if os.path.exists(os.path.join(TK, 'parts.json')) else None
ALL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'porus_parts.json')))
SR = 24000
w, _ = librosa.load(SRC, sr=SR, mono=True)
al = {i: (a, b) for i, a, b in json.load(open(AL))}
chars = lambda t: len(re.sub(r'[^ఀ-౿]', '', t))
rate = np.median([(b - a) / max(1, chars(ALL[i]['text'])) for i, (a, b) in al.items()])   # s per letter
fixes = sorted({int(f.split('-')[1].split('.')[0]) % 1000 for f in os.listdir(TK) if f.startswith('part-')})
rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-9)

def take(i):
    best = None
    for t in (0, 1000):
        f = os.path.join(TK, f'part-{t + i:05d}.wav')
        if not os.path.exists(f): continue
        x, _ = librosa.load(f, sr=SR, mono=True); x, _ = librosa.effects.trim(x, top_db=40)
        err = abs(len(x) / SR - rate * chars(ALL[i]['text']))
        print(f'line {i} take {t // 1000}: {len(x) / SR:.2f}s (expected {rate * chars(ALL[i]["text"]):.2f}s)')
        if best is None or err < best[0]: best = (err, x)
    return best[1]

out, sents, pos, shift = [], [], 0, 0.0
fade = int(0.015 * SR)
for i in sorted(al):
    a, b = al[i]
    if i in fixes:
        s0 = int(a * SR); s1 = int(b * SR)
        nxt = al.get(i + 1, (len(w) / SR,))[0]
        # the aligned span may run into the following pause: end the old speech where the sound drops
        seg = w[s0:s1]; e = librosa.feature.rms(y=seg, frame_length=1024, hop_length=256)[0]
        loud = np.where(e > 0.1 * e.max())[0]
        s1 = s0 + (loud[-1] + 2) * 256 if len(loud) else s1
        x = take(i)
        ctx = np.concatenate([w[max(0, s0 - 3 * SR):s0], w[s1:s1 + 3 * SR]])
        x = x * (rms(ctx[np.abs(ctx) > 0.02]) / rms(x[np.abs(x) > 0.02]))
        x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
        out.append(w[pos:s0]); out.append(x)
        ns = s0 / SR + shift; ne = ns + len(x) / SR
        shift += len(x) / SR - (s1 - s0) / SR; pos = s1
        sents.append({'para': ALL[i]['para'], 'start': round(ns, 3), 'end': round(ne, 3), 'text': ALL[i]['text']})
    else:
        sents.append({'para': ALL[i]['para'], 'start': round(a + shift, 3), 'end': round(b + shift, 3), 'text': ALL[i]['text']})
out.append(w[pos:])
y = np.concatenate(out); y = y / max(1.0, np.abs(y).max() / 0.98)
sf.write(OUT, y, SR)
json.dump(sents, open(SOUT, 'w'), ensure_ascii=False, indent=1)
print(f'narration {len(y) / SR:.1f}s, replaced {fixes}')
