"""Synthesize the Ear Fly music + SFX bed (12 s, 44.1 kHz stereo) -> music.wav.

Everything is generated: a bouncy marimba-ish pentatonic tune over I-V-vi-IV,
plus timed SFX (ear flaps, liftoff whoosh, glasses plink, jump whoosh,
falling whistle, boing, thud) at the shot-locked beats:
  s01 0.0-2.5  s02 2.5-4.5  s03 4.5-7.0  s04 7.0-9.5  s05 9.5-12.0
Run with the cgi-venv python (numpy + soundfile).
"""
import numpy as np
import soundfile as sf

SR = 44100
DUR = 12.0
t_all = np.arange(int(SR * DUR)) / SR
L = np.zeros_like(t_all)
R = np.zeros_like(t_all)


def put(sig, at, gain=1.0, pan=0.0):
    i0 = int(at * SR)
    n = min(len(sig), len(L) - i0)
    if n <= 0:
        return
    g_l, g_r = (1 - max(pan, 0)) * gain, (1 + min(pan, 0)) * gain
    L[i0:i0 + n] += sig[:n] * g_l
    R[i0:i0 + n] += sig[:n] * g_r


def env(n, a=0.004, d=0.25, tail=0.3):
    e = np.ones(n)
    na, nd = int(a * SR), n - int(a * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.linspace(0, nd / SR / d, nd))
    return e * tail


def pluck(freq, dur=0.5, bright=0.35):
    """Marimba-ish pluck: sine + soft overtones with a fast decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t)
         + bright * np.sin(2 * np.pi * freq * 2.01 * t)
         + 0.15 * np.sin(2 * np.pi * freq * 3.98 * t))
    return s * env(n, d=0.22, tail=1.0)


def bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    e = np.minimum(1, np.linspace(0, 12, n)) * np.exp(-t / (dur * 0.9))
    return s * e


def shaker(dur=0.05):
    n = int(dur * SR)
    s = np.random.default_rng(1).standard_normal(n)
    s = np.diff(np.concatenate([[0], s]))          # high-pass-ish
    return s * env(n, d=0.03, tail=1.0)


def noise_burst(dur, lp=0.15, seed=2):
    """Low-passed noise burst (one-pole), the body of flaps/whooshes/thuds."""
    n = int(dur * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += lp * (x[i] - acc)
        y[i] = acc
    return y / (np.abs(y).max() + 1e-9)


def sweep(f0, f1, dur, vib=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if vib:
        ph += vib * np.sin(2 * np.pi * 6 * t)
    return np.sin(ph)


# ---------------------------------------------------------------- music
C, D, E, G, A = 261.63, 293.66, 329.63, 392.0, 440.0
C5, D5, E5, G5, A5 = [2 * x for x in (C, D, E, G, A)]
BEAT = 60 / 112                                     # 112 BPM, eighth = BEAT/2
chords = [(0.0, [C, E, G], C / 2),                  # C
          (3.0, [D, G, 392.0 / 2 * 2], G / 2),      # G-ish
          (6.0, [C, E, A], A / 4),                  # Am
          (9.0, [C, 349.23, A], 349.23 / 2)]        # F
melody = [  # (time, freq, len_in_eighths) — bouncy, sparse, ends on the button
    (0.00, E5, 1), (0.54, G5, 1), (1.07, A5, 2), (2.14, G5, 1),
    (3.00, D5, 1), (3.54, G5, 1), (4.07, E5, 2), (4.80, D5, 1),
    (5.36, E5, 1), (5.89, G5, 1), (6.43, A5, 2), (7.50, 2 * C5, 2),
    (8.04, A5, 1), (8.57, G5, 1), (9.11, E5, 1), (9.64, D5, 1),
    (10.18, E5, 2), (11.30, 2 * C5, 3)]
for at, f, ln in melody:
    put(pluck(f, 0.30 + 0.12 * ln), at, gain=0.16, pan=0.15)
for at, notes, b in chords:
    for rep in range(3):
        for k, f in enumerate(notes):
            put(pluck(f, 0.35, bright=0.2), at + rep * 1.0 + k * 0.02, gain=0.05, pan=-0.2)
    put(bass(b, 2.6), at, gain=0.16)
put(bass(C / 2, 1.6), 11.3, gain=0.18)             # button
for k in range(int(DUR / (BEAT / 2))):
    at = k * BEAT / 2
    if at < 11.2 and k % 2 == 1:
        put(shaker(), at, gain=0.045, pan=0.3)

# ---------------------------------------------------------------- SFX
# s02: first slow flaps
for i, at in enumerate((3.15, 3.65, 4.10)):
    put(noise_burst(0.14, lp=0.10, seed=10 + i) * env(int(0.14 * SR), d=0.06, tail=1), at, gain=0.5)
# s02->s04: fast flutter, amplitude-modulated noise at ~flap rate
flut = noise_burst(5.0, lp=0.12, seed=42)
tf = np.arange(len(flut)) / SR
flut *= 0.5 + 0.5 * np.sin(2 * np.pi * 6.5 * tf)
flut *= np.minimum(1, np.linspace(0, 8, len(flut))) * np.exp(-np.maximum(0, tf - 4.2) * 2)
put(flut, 4.45, gain=0.22)
# s03: liftoff whoosh + glasses plink
put(sweep(160, 900, 0.9) * noise_burst(0.9, lp=0.5, seed=7) * env(int(0.9 * SR), d=0.5, tail=1), 5.0, gain=0.5)
put(pluck(1180, 0.12, bright=0.6), 6.15, gain=0.4)
put(pluck(760, 0.14, bright=0.6), 6.22, gain=0.4)
# s04: hover flutter + jump whoosh + miss swish + frustrated hop
put(flut[:int(2.4 * SR)], 7.0, gain=0.20)
put(sweep(300, 90, 0.45) * env(int(0.45 * SR), d=0.3, tail=1), 7.25, gain=0.5)
put(noise_burst(0.3, lp=0.4, seed=9) * env(int(0.3 * SR), d=0.12, tail=1), 7.75, gain=0.45)
put(noise_burst(0.2, lp=0.35, seed=11) * env(int(0.2 * SR), d=0.1, tail=1), 8.95, gain=0.35)
# s05: tired sputter flaps, falling whistle, BOING on the belly, slide, floor thud
sput = noise_burst(1.1, lp=0.10, seed=12)
ts = np.arange(len(sput)) / SR
sput *= (0.5 + 0.5 * np.sin(2 * np.pi * (5 - 3 * ts / 1.1) * ts)) * np.exp(-ts * 1.5)
put(sput, 9.55, gain=0.4)
put(sweep(950, 280, 0.62, vib=0.4) * env(int(0.62 * SR), d=0.5, tail=1), 10.35, gain=0.30)
n_b = int(0.5 * SR)
tb = np.arange(n_b) / SR
boing = np.sin(2 * np.pi * (150 + 70 * np.exp(-tb * 6) * np.sin(2 * np.pi * 11 * tb)) * tb)
put(boing * env(n_b, d=0.22, tail=1), 10.55, gain=0.55)
put(noise_burst(0.16, lp=0.05, seed=13) * env(int(0.16 * SR), d=0.07, tail=1), 10.56, gain=0.5)   # thump body
put(noise_burst(0.22, lp=0.05, seed=14) * env(int(0.22 * SR), d=0.09, tail=1), 11.15, gain=0.5)   # floor thud
put(pluck(2 * A5, 0.3, bright=0.5), 11.55, gain=0.12)                                             # tiny sparkle

mix = np.stack([L, R], axis=1)
peak = np.abs(mix).max()
mix = mix / peak * 0.85
sf.write("music.wav", mix.astype(np.float32), SR)
print("music.wav written:", mix.shape[0] / SR, "s, peak", float(peak))
