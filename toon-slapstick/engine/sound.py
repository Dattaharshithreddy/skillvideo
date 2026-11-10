"""sound.py - synthesised cartoon orchestra and sound effects, locked to picture frames.

The classic method: the action is timed to a musical beat (12 frames = one beat at 24 fps, 120 bpm)
and the score copies the action ("mickey-mousing"): every step, sneak, rise, fall and hit gets a note.

    score = Score(frames)
    score.music(0, 96, 'calm')        # bed for a section
    score.hit(120, 'bonk')            # a sound effect on frame 120
    score.write('audio.wav')
"""
import math, wave
import numpy as np

SR = 44100
FPS = 24
A4 = 440.0


def hz(n):
    """MIDI note number to frequency."""
    return A4 * 2 ** ((n - 69) / 12)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, a=0.005, r=0.05):
    e = np.ones(n)
    na, nr = max(1, int(SR * a)), max(1, int(SR * r))
    e[:na] = np.linspace(0, 1, na)[:len(e[:na])]
    e[-nr:] *= np.linspace(1, 0, nr)[-len(e[-nr:]):]
    return e


def _lp(x, k):
    """One-pole low-pass, k in 0..1 (smaller = darker)."""
    try:
        from scipy.signal import lfilter
        return lfilter([k], [1, -(1 - k)], x)
    except ImportError:
        pass
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc)
        y[i] = acc
    return y


def _noise(n, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, n)


# ----------------------------------------------------------------- instruments
def xylo(note, d=0.3, v=1.0):
    t = _t(d); f = hz(note)
    return v * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30) + 0.2 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t * 60)) * np.exp(-t * 14) * _env(len(t), 0.001, 0.02)


def pizz(note, d=0.35, v=1.0):
    """Plucked string (Karplus-Strong)."""
    f = hz(note); n = int(SR * d); N = max(2, int(SR / f))
    buf = _noise(N, int(note)); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.996 * 0.5 * (buf[i % N] + buf[(i + 1) % N])
    return v * out * _env(n, 0.001, 0.04)


def reed(note, d=0.25, v=1.0, bright=0.18):
    """Clarinet / bassoon-ish: odd harmonics, soft attack."""
    t = _t(d); f = hz(note)
    x = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 3, 5, 7))
    x *= 1 + 0.01 * np.sin(2 * np.pi * 5.5 * t)
    return v * 0.6 * _lp(x, bright) * _env(len(t), 0.02, 0.05)


def brass(note, d=0.4, v=1.0, wah=0.0):
    t = _t(d); f = hz(note)
    x = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    if wah:
        m = 0.5 + 0.5 * np.sin(2 * np.pi * wah * t - 1.5)
        x = _lp(x, 0.06) * (1 - m) + x * m * 0.6
    else:
        x = _lp(x, 0.25)
    return v * 0.5 * x * _env(len(t), 0.03, 0.08)


def timp(note=41, d=0.6, v=1.0):
    t = _t(d); f = hz(note)
    return v * (np.sin(2 * np.pi * f * t * (1 + 0.3 * np.exp(-t * 30))) * np.exp(-t * 6) + 0.3 * _lp(_noise(len(t), 5), 0.2) * np.exp(-t * 40))


def cymbal(d=0.9, v=1.0):
    t = _t(d); x = _noise(len(t), 9)
    x = x - _lp(x, 0.35)
    return v * 0.5 * x * np.exp(-t * 4.5)


# ----------------------------------------------------------------- sound effects
def slide(n0, n1, d=0.5, v=1.0):
    """Slide whistle: rises and falls, jumps, drooping ears."""
    t = _t(d); f = hz(n0) * (hz(n1) / hz(n0)) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.012 * np.sin(2 * np.pi * 7 * t))) / SR
    return v * 0.7 * (np.sin(ph) + 0.25 * np.sin(2 * ph)) * _env(len(t), 0.02, 0.06)


def boing(note=50, d=0.7, v=1.0):
    t = _t(d); f = hz(note) * (1 + 0.9 * np.exp(-t * 4) * np.sin(2 * np.pi * 13 * t) + 0.5 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return v * 0.8 * (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-t * 3.2) * _env(len(t), 0.002, 0.05)


def bonk(v=1.0, note=76):
    t = _t(0.16)
    return v * (np.sin(2 * np.pi * hz(note) * t) * np.exp(-t * 55) + 0.6 * np.sin(2 * np.pi * 150 * t) * np.exp(-t * 30) + 0.3 * _noise(len(t), 3) * np.exp(-t * 200))


def crash(v=1.0):
    t = _t(1.1)
    x = _lp(_noise(len(t), 11), 0.5) * np.exp(-t * 5) + 0.9 * np.sin(2 * np.pi * 62 * t * (1 + 0.4 * np.exp(-t * 20))) * np.exp(-t * 7)
    x[:len(_t(0.9))] += cymbal(0.9, 0.7)
    for k, off in enumerate((0.12, 0.22, 0.36)):      # bits of crockery rattling down
        i = int(SR * off); b = bonk(0.3, 84 + k * 3)
        x[i:i + len(b)] += b
    return v * 0.9 * x


def whoosh(d=0.35, v=1.0, up=True):
    n = int(SR * d); x = _noise(n, 21); out = np.empty(n); acc = 0.0
    for i in range(n):
        u = i / n
        k = 0.02 + 0.5 * (u if up else 1 - u) ** 2
        acc += k * (x[i] - acc); out[i] = acc
    return v * 1.6 * out * np.sin(np.pi * np.arange(n) / n) ** 1.5


def zipp(v=1.0, d=0.22):
    """Zip / ricochet for a character vanishing in a streak."""
    t = _t(d); f = 300 * (12 ** (t / d))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return v * (0.6 * np.sin(ph) * _env(len(t), 0.005, 0.03) + whoosh(d, 0.7))


def munch(v=1.0):
    out = np.zeros(int(SR * 0.16)); b = (_noise(1500, 4) - _lp(_noise(1500, 4), 0.3)) * np.exp(-np.arange(1500) / 300)
    out[:1500] += b; out[2400:3900] += b * 0.6
    return v * 1.2 * out


def gulp(v=1.0):
    t = _t(0.22); f = 180 + 420 * np.sin(np.pi * t / 0.22) ** 2
    return v * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.05)


def pop(v=1.0, note=72):
    t = _t(0.08); f = hz(note) * (1 + 3 * np.exp(-t * 90))
    return v * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)


def flap(v=1.0):
    return whoosh(0.13, v * 0.9, up=False)


def sniff(v=1.0):
    n = int(SR * 0.12); x = _noise(n, 31); x = x - _lp(x, 0.2)
    return v * 0.5 * x * np.sin(np.pi * np.arange(n) / n)


def skid(v=1.0, d=0.5):
    t = _t(d); f = 1500 - 700 * t / d
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f * (1 + 0.03 * np.sin(2 * np.pi * 45 * t))) / SR))
    return v * 0.25 * _lp(x, 0.3) * _env(len(t), 0.01, 0.12)


def wah_fail(v=1.0):
    """Sad trombone: wah wah wah waaah."""
    parts = [brass(58, 0.3, 1, 3.5), brass(57, 0.3, 1, 3.5), brass(56, 0.3, 1, 3.5), brass(55, 0.9, 1, 1.4)]
    return v * np.concatenate(parts)


def tada(v=1.0):
    n = int(SR * 0.9); out = np.zeros(n)
    for note in (60, 64, 67, 72):
        b = brass(note, 0.16, 0.5); out[:len(b)] += b
        c = brass(note + (0 if note != 72 else 0), 0.7, 0.5); i = int(SR * 0.2); out[i:i + len(c)] += c[:n - i]
    cy = cymbal(0.7, 0.5); i = int(SR * 0.2); out[i:i + len(cy)] += cy[:n - i]
    return v * out


SFX = dict(bonk=bonk, crash=crash, whoosh=whoosh, zip=zipp, munch=munch, gulp=gulp, pop=pop, flap=flap, sniff=sniff,
           skid=skid, boing=boing, wah=wah_fail, tada=tada, timp=timp, cymbal=cymbal)


# ----------------------------------------------------------------- score
class Score:
    BEAT = 12  # frames per beat

    def __init__(self, frames, fps=FPS):
        self.fps = fps
        self.n = int(SR * (frames / fps + 1.5))
        self.mus = np.zeros(self.n)
        self.fx = np.zeros(self.n)

    def _add(self, buf, f, x):
        i = int(SR * f / self.fps)
        if i >= self.n or i < 0:
            return
        x = x[:self.n - i]
        buf[i:i + len(x)] += x

    # -- effects and single notes, placed on frames
    def hit(self, f, name, v=1.0, **kw):
        self._add(self.fx, f, SFX[name](v=v, **kw))

    def note(self, f, inst, note, d=0.3, v=1.0):
        self._add(self.fx, f, inst(note, d, v))

    def slide(self, f, n0, n1, frames=10, v=1.0):
        self._add(self.fx, f, slide(n0, n1, frames / self.fps, v))

    def steps(self, f0, f1, every=6, notes=(60, 64), inst=None, v=0.7):
        """One note per footstep. Use for walks (every 6-8), sneaks (every 8-12) and runs (every 3)."""
        inst = inst or pizz
        for i, f in enumerate(range(f0, f1, every)):
            self._add(self.fx, f, inst(notes[i % len(notes)], 0.25, v))

    def run(self, f0, f1, start=60, every=2, v=0.5, up=True, scale=(0, 2, 4, 5, 7, 9, 11)):
        """Fast scale run for scrambles and zips."""
        for i, f in enumerate(range(f0, f1, every)):
            k = i if up else -i
            self._add(self.fx, f, xylo(start + 12 * (k // 7) + scale[k % 7], 0.18, v))

    # -- music beds
    def music(self, f0, f1, mood='calm', key=60, v=1.0):
        B = self.BEAT
        beats = int((f1 - f0) / B)
        maj = (0, 4, 7)
        prog = {'calm': [0, 0, 5, 7], 'chase': [0, 5, 7, 0], 'sneak': [0, 0, 0, 0], 'sweet': [0, 9, 5, 7]}[mood]
        tune = {
            'calm': [0, 4, 7, 9, 7, 4, 2, 4, 5, 9, 12, 9, 7, 5, 4, 2],
            'sweet': [12, 11, 9, 7, 9, 7, 4, 0, 5, 7, 9, 12, 11, 7, 12, 12],
        }
        for b in range(beats):
            f = f0 + b * B
            root = key + prog[(b // 4) % 4] - 12
            minor = prog[(b // 4) % 4] == 9
            tri = (0, 3, 7) if minor else maj
            if mood in ('calm', 'sweet'):
                if b % 2 == 0:
                    self._add(self.mus, f, pizz(root - 12, 0.4, 0.8 * v))
                else:
                    for k in tri:
                        self._add(self.mus, f, reed(root + 12 + k, 0.14, 0.22 * v))
                    self._add(self.mus, f, pizz(root - 5, 0.3, 0.5 * v))
                for h in (0, 1):   # melody in eighth notes, with a few rests so it breathes
                    idx = (b * 2 + h) % 16
                    if (b * 2 + h) % 8 != 7:
                        self._add(self.mus, f + h * B / 2, xylo(key + 12 + tune[mood][idx], 0.28, 0.42 * v))
            elif mood == 'sneak':
                walk = [0, 1, 2, 3, 4, 3, 2, 1]
                self._add(self.mus, f, pizz(key - 24 + walk[b % 8], 0.3, 0.9 * v))
                if b % 4 == 3:
                    self._add(self.mus, f + B / 2, reed(key + 6, 0.12, 0.3 * v))
            elif mood == 'chase':
                self._add(self.mus, f, pizz(root - 12, 0.25, 0.9 * v)); self._add(self.mus, f + B / 2, pizz(root - 5, 0.2, 0.7 * v))
                for q in range(4):  # sixteenth-note gallop
                    sc = (0, 2, 4, 5, 7, 9, 11, 12)
                    i = (b * 4 + q)
                    n = sc[i % 8] if (i // 8) % 2 == 0 else sc[7 - i % 8]
                    self._add(self.mus, f + q * B / 4, xylo(root + 24 + n, 0.12, 0.34 * v))
                    if q % 2 == 1:
                        for k in tri:
                            self._add(self.mus, f + q * B / 4, brass(root + 12 + k, 0.08, 0.16 * v))
                if b % 4 == 0:
                    self._add(self.mus, f, cymbal(0.3, 0.25 * v))

    def duck(self, f0, f1, amount=0.25):
        """Pull the music down between two frames (before a big hit, or for a silent beat)."""
        a, b = int(SR * f0 / self.fps), int(SR * f1 / self.fps)
        ramp = int(SR * 0.04)
        g = np.ones(self.n)
        g[a:b] = amount
        g[max(0, a - ramp):a] = np.linspace(1, amount, len(g[max(0, a - ramp):a]))
        g[b:b + ramp] = np.linspace(amount, 1, len(g[b:b + ramp]))
        self.mus *= g

    def write(self, path, music_gain=0.5, fx_gain=0.85):
        x = self.mus * music_gain + self.fx * fx_gain
        # tiny room echo so it sounds like a recording stage, then soft clip
        d = int(SR * 0.085)
        x[d:] += 0.18 * x[:-d]
        x = np.tanh(x * 0.9)
        x = x / (np.abs(x).max() + 1e-9) * 0.92
        pcm = (x * 32767).astype(np.int16)
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(np.repeat(pcm[:, None], 2, 1).tobytes())
        return path
