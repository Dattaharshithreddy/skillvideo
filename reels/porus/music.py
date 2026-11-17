"""Score for the Puru reel, made from scratch (no samples): a low tanpura-style drone through the whole reel, war drums that build
in demand / river / battle, thunder in the storm, a held low tone for the murder and a warm swell plus a bell at the end.
python3 music.py <timing.json> <out.wav>"""
import json, sys, wave
import numpy as np
T = json.load(open(sys.argv[1])); out = sys.argv[2]
SR = 44100; FPS = 30
starts = np.cumsum([0] + T['nf'][:-1]) / FPS; durs = np.array(T['nf']) / FPS; dur = float(sum(durs)) + 0.5
shot = {l['shot']: (float(a), float(a + d)) for l, a, d in zip(T['lines'], starts, durs)}
n = int(dur * SR); t = np.arange(n) / SR; mix = np.zeros(n); rng = np.random.default_rng(5)
def env(a, b, fi=1.5, fo=1.5):
    return np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)
def pluck(f0, length=5.0):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for k in range(1, 22):
        a = (1.0 / k ** 0.8) * (1 + 0.5 * np.sin(k * 0.9))
        y += a * np.exp(-tt * (0.4 + 0.05 * k)) * np.sin(2 * np.pi * f0 * k * (1 + 0.0002 * k) * tt + rng.uniform(0, 6.28))
    return y * np.minimum(tt / 0.03, 1.0)
SA = 110.0                                   # A2 drone, minor colour for a war story
seq = [SA * 1.5, SA * 2, SA * 2, SA]; notes = {f: pluck(f) for f in set(seq)}; pos, i = 0.0, 0
while pos < dur:
    y = notes[seq[i % 4]]; a = int(pos * SR); b = min(n, a + len(y)); mix[a:b] += 0.16 * y[:b - a]; pos += 1.5; i += 1
pad = sum(np.sin(2 * np.pi * f * t + p) * (0.5 + 0.5 * np.sin(2 * np.pi * t / pr)) for f, p, pr in ((SA / 2, 0, 17), (SA * 1.2, 1, 23), (SA * 1.5, 2, 29)))
mix += 0.03 * pad
def drum(f0=58, length=0.9, noise=0.25):
    m = int(length * SR); tt = np.arange(m) / SR
    f = f0 * (1 + 1.6 * np.exp(-tt * 28)); ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-tt * 6) + noise * rng.standard_normal(m) * np.exp(-tt * 40)
    return y
D1, D2 = drum(55), drum(82, 0.5, 0.35)
def drums(a, b, bpm, gain, accent_every=4):
    beat = 60 / bpm; k = 0; x = a
    while x < b:
        g = gain * (1.0 if k % accent_every == 0 else 0.6) * min(1, (x - a) / 3 + 0.3)
        y = D1 if k % 2 == 0 else D2; s = int(x * SR); e = min(n, s + len(y)); mix[s:e] += g * y[:e - s]; x += beat; k += 1
for name, bpm, g in (('demand', 84, 0.35), ('ambhi', 70, 0.22), ('river', 92, 0.32), ('son', 76, 0.25), ('battle', 116, 0.55)):
    if name in shot: drums(*shot[name], bpm, g)
if 'storm' in shot:                          # thunder rumbles
    a, b = shot['storm']
    for u in (0.12, 0.45, 0.78):
        s = int((a + u * (b - a)) * SR); m = int(4.5 * SR); tt = np.arange(m) / SR
        y = np.convolve(rng.standard_normal(m), np.ones(300) / 300, 'same') * np.exp(-tt * 0.9) * np.minimum(tt / 0.05, 1)
        e = min(n, s + m); mix[s:e] += 2.2 * y[:e - s]
if 'murder' in shot:
    a, b = shot['murder']; mix += 0.08 * np.sin(2 * np.pi * SA / 2 * 0.944 * t) * env(a, b, 0.8, 1.2)
def bell(f0=523.25, length=6.0):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for r, a_, d in ((0.5, 0.5, 0.5), (1.0, 1.0, 0.7), (2.0, 0.6, 1.0), (2.76, 0.45, 1.4), (3.3, 0.3, 1.8), (4.1, 0.25, 2.4)):
        y += a_ * np.exp(-tt * d) * np.sin(2 * np.pi * f0 * r * tt)
    return y * np.minimum(tt / 0.004, 1.0)
bl = bell()
for name, u in (('open', 0.02), ('king', 0.62), ('legacy', 0.45)):
    if name in shot:
        a, b = shot[name]; s = int((a + u * (b - a)) * SR); e = min(n, s + len(bl)); mix[s:e] += 0.22 * bl[:e - s]
if 'legacy' in shot:
    a, b = shot['legacy']; mix += 0.05 * sum(np.sin(2 * np.pi * f * t) for f in (SA, SA * 1.25, SA * 1.5, SA * 2)) * env(a, dur, 2.0, 2.0)
mix *= np.minimum(t / 1.5, 1.0) * np.minimum((dur - t) / 2.5, 1.0)
mix = mix / np.abs(mix).max() * 0.8
w = wave.open(out, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('music', round(dur, 1), 's', out)
