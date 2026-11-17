"""Soft devotional bed made from scratch (no samples): tanpura-style drone in C#, temple bells at the opening and the close.
Usage: python3 music.py <seconds> <out.wav> <bell times, comma separated>"""
import sys, wave
import numpy as np
SR = 44100; dur = float(sys.argv[1]); out = sys.argv[2]; bells = [float(x) for x in sys.argv[3].split(',') if x]
n = int(dur * SR); t = np.arange(n) / SR; mix = np.zeros(n)
rng = np.random.default_rng(4)
def pluck(f0, length=5.5):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for k in range(1, 26):
        a = (1.0 / k ** 0.75) * (1 + 0.6 * np.sin(k * 0.9))          # buzzing bridge: uneven, rich upper harmonics
        y += a * np.exp(-tt * (0.35 + 0.045 * k)) * np.sin(2 * np.pi * f0 * k * (1 + 0.00025 * k) * tt + rng.uniform(0, 6.28))
    return y * np.minimum(tt / 0.03, 1.0)
SA = 138.59; seq = [SA * 1.5, SA * 2, SA * 2, SA]; step = 1.35; i = 0; pos = 0.0
notes = {f: pluck(f) for f in set(seq)}
while pos < dur:
    y = notes[seq[i % 4]]; a = int(pos * SR); b = min(n, a + len(y)); mix[a:b] += 0.22 * y[:b - a]; pos += step; i += 1
pad = sum(np.sin(2 * np.pi * f * t + p) * (0.5 + 0.5 * np.sin(2 * np.pi * t / pr)) for f, p, pr in ((SA / 2, 0, 17), (SA, 1, 23), (SA * 1.5, 2, 29), (SA * 2, 3, 13)))
mix += 0.035 * pad
def bell(f0=523.25, length=6.0):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for r, a, d in ((0.5, 0.5, 0.5), (1.0, 1.0, 0.7), (2.0, 0.6, 1.0), (2.76, 0.45, 1.4), (3.3, 0.3, 1.8), (4.1, 0.25, 2.4), (5.43, 0.2, 3.2), (6.8, 0.12, 4.0)):
        y += a * np.exp(-tt * d) * np.sin(2 * np.pi * f0 * r * tt)
    return y * np.minimum(tt / 0.004, 1.0)
bl = bell()
for bt in bells:
    a = int(bt * SR); b = min(n, a + len(bl))
    if a < n: mix[a:b] += 0.30 * bl[:b - a]
env = np.minimum(t / 1.5, 1.0) * np.minimum((dur - t) / 2.5, 1.0); mix *= env
mix = mix / np.abs(mix).max() * 0.8
w = wave.open(out, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('music', round(dur, 1), 's', out)
