"""Score made from scratch (no samples) for the Porus miniature reel: low drone, war drums (nagara-style) that build into
the battle, thunder under the storm, and a soft tanpura + bell for the ending. Reads brief/timing.json.
Usage: <blender python> music_mini.py out.wav"""
import sys, json, wave
import numpy as np
T = json.load(open('brief/timing.json')); SR = 44100
dur = T['end'] / 30.0; n = int(dur * SR); t = np.arange(n) / SR; mix = np.zeros(n); rng = np.random.default_rng(11)
st = {l['shot']: (T['starts'][i], T['starts'][i] + T['durs'][i]) for i, l in enumerate(T['lines'])}
def add(y, at, g):
    a = int(at * SR); b = min(n, a + len(y))
    if 0 <= a < n: mix[a:b] += g * y[:b - a]
# drone: D, A, D' with slow beating
D = 73.42
dr = sum(np.sin(2 * np.pi * f * t + p) * (0.55 + 0.45 * np.sin(2 * np.pi * t / pr + p)) for f, p, pr in ((D, 0, 19), (D * 1.5, 1, 23), (D * 2, 2, 31), (D * 2.997, 3, 13)))
drone_g = np.full(n, 0.05)
for k in ('murder',):
    a, b = st[k]; drone_g[int(a * SR):int(b * SR)] = 0.03
mix += dr * drone_g
def drum(f0=58, length=0.9, slap=0.25):
    m = int(length * SR); tt = np.arange(m) / SR
    f = f0 * (1 + 1.2 * np.exp(-tt * 28)); ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-tt * 5.5) + slap * rng.standard_normal(m) * np.exp(-tt * 45)
    return y * np.minimum(tt / 0.002, 1)
big, small = drum(52, 1.2, 0.2), drum(110, 0.4, 0.5)
def pattern(a, b, bpm, g, accent=4):
    beat = 60.0 / bpm; k = 0; x = a
    while x < b:
        add(big if k % accent == 0 else small, x, g * (1.0 if k % accent == 0 else 0.6)); x += beat; k += 1
pattern(st['open'][0] + 0.5, st['open'][1], 54, 0.35)
pattern(st['demand'][0], st['demand'][1], 60, 0.45)
pattern(st['river'][0], st['river'][1], 66, 0.4)
pattern(st['son'][0], st['son'][1], 72, 0.35)
pattern(st['battle'][0], st['battle'][1], 104, 0.55, 2)
# thunder in the storm
a, b = st['storm']
for q in (0.06, 0.3, 0.52, 0.8):
    m = int(3.5 * SR); tt = np.arange(m) / SR; nz = rng.standard_normal(m)
    lp = np.convolve(nz, np.ones(220) / 220, mode='same') * np.exp(-tt * 1.1) * np.minimum(tt / 0.05, 1)
    add(lp / np.abs(lp).max(), a + (b - a) * q + 0.15, 0.55)
rain = np.convolve(rng.standard_normal(n), np.ones(6) / 6, mode='same')
env = np.zeros(n); env[int((a - 1.5) * SR):int(b * SR)] = 1.0; env = np.convolve(env, np.ones(SR) / SR, mode='same')
mix += 0.05 * rain * env
# ending: tanpura + bell
def pluck(f0, length=5.0):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for k in range(1, 22):
        y += (1.0 / k ** 0.75) * np.exp(-tt * (0.35 + 0.05 * k)) * np.sin(2 * np.pi * f0 * k * tt + rng.uniform(0, 6.28))
    return y * np.minimum(tt / 0.03, 1)
a, b = st['legacy']; seq = [D * 1.5 * 2, D * 4, D * 4, D * 2]; x = a; i = 0
while x < dur - 1:
    add(pluck(seq[i % 4]), x, 0.12); x += 1.4; i += 1
def bell(f0=587.3, length=6.0):
    m = int(length * SR); tt = np.arange(m) / SR; y = np.zeros(m)
    for r, g, d in ((0.5, 0.5, 0.5), (1.0, 1.0, 0.7), (2.0, 0.6, 1.0), (2.76, 0.45, 1.4), (4.1, 0.25, 2.4), (5.43, 0.2, 3.2)):
        y += g * np.exp(-tt * d) * np.sin(2 * np.pi * f0 * r * tt)
    return y * np.minimum(tt / 0.004, 1)
add(bell(), b - 3.2, 0.3)
fade = np.minimum(t / 1.0, 1.0) * np.minimum((dur - t) / 2.0, 1.0); mix *= fade
mix = mix / np.abs(mix).max() * 0.85
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('music', round(dur, 1))
