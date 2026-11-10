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


# ----------------------------------------------------------------- Indian instruments
def tabla(stroke='na', v=1.0, sa=62):
    """Tabla strokes. Treble drum tuned to Sa: na (ringing rim), tin (soft open), te (dry slap).
    Bass drum: ge (deep, with the upward bend of the palm). dha = ge + na, dhin = ge + tin."""
    f = hz(sa + 12)
    if stroke in ('dha', 'dhin'):
        a_ = tabla('ge', v, sa); b_ = tabla('na' if stroke == 'dha' else 'tin', v, sa)
        n = max(len(a_), len(b_)); out = np.zeros(n); out[:len(a_)] += a_; out[:len(b_)] += b_
        return out
    if stroke == 'ge':
        t = _t(0.42); fr = 78 * (1 + 0.55 * np.sin(np.pi * np.minimum(t / 0.16, 1) / 2))
        ph = 2 * np.pi * np.cumsum(fr) / SR
        return v * 1.1 * (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.exp(-t * 9) * _env(len(t), 0.002, 0.05)
    if stroke == 'te':
        t = _t(0.07); x = _noise(len(t), 7)
        return v * 0.55 * (x - _lp(x, 0.3)) * np.exp(-t * 70) + v * 0.3 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 90)
    d, dec = (0.32, 11) if stroke == 'na' else (0.4, 8)
    t = _t(d)
    x = sum(a_ * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dec * (1 + 0.25 * i)) for i, (k, a_) in enumerate(((1, 1.0), (2.0, 0.55), (3.01, 0.4), (4.0, 0.22))))
    click = 0.35 * _noise(len(t), 3) * np.exp(-t * 260)
    return v * (0.5 if stroke == 'tin' else 0.62) * (x + click) * _env(len(t), 0.001, 0.03)


def bansuri(note, d=0.4, v=1.0, slide_from=None):
    """Bamboo flute: breathy, with a slow vibrato that arrives late and an optional glide into the note."""
    t = _t(d); f1 = hz(note)
    f = np.full(len(t), f1)
    if slide_from is not None:
        g_ = np.minimum(t / min(0.09, d * 0.4), 1)
        f = hz(slide_from) * (f1 / hz(slide_from)) ** g_
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(t / 0.25, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    breath = _lp(_noise(len(t), int(note)), 0.25) * 0.10
    return v * 0.7 * (np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph) + breath) * _env(len(t), 0.035, 0.07)


def veena(note, d=0.7, v=1.0):
    """Plucked string with a bright buzz and a small downward bend, veena / sitar family."""
    f = hz(note); n = int(SR * d); N = max(2, int(SR / f))
    buf = _noise(N, int(note) + 5); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.9985 * (0.62 * buf[i % N] + 0.38 * buf[(i + 1) % N])
    out = np.tanh(out * 2.2) * 0.7
    return v * out * _env(n, 0.001, 0.06)


def manjira(v=1.0):
    t = _t(0.7)
    return v * 0.35 * (np.sin(2 * np.pi * 2380 * t) + 0.7 * np.sin(2 * np.pi * 3560 * t) + 0.4 * np.sin(2 * np.pi * 5210 * t)) * np.exp(-t * 6)


def ghatam(v=1.0, note=57):
    t = _t(0.12); f = hz(note)
    return v * 0.8 * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 45) + v * 0.2 * _noise(len(t), 2) * np.exp(-t * 300)


def tanpura(sa, d, v=1.0):
    """Soft drone of Sa and Pa underneath everything."""
    t = _t(d); out = np.zeros(len(t))
    for n_, a_ in ((sa - 12, 1.0), (sa - 5, 0.6), (sa, 0.7), (sa + 12, 0.25)):
        f = hz(n_)
        out += a_ * sum(np.sin(2 * np.pi * f * k * t + k) / k ** 1.3 for k in (1, 2, 3, 4, 5)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.4 * t + n_))
    return v * 0.07 * out * _env(len(t), 0.3, 0.4)


def tihai(v=1.0, sa=62):
    """Three-fold drum cadence that lands hard on the last beat: the classic way to end."""
    step = int(SR * 0.105); out = np.zeros(step * 12 + int(SR * 1.0))
    pat = ['te', 'te', 'dha', None, 'te', 'te', 'dha', None, 'te', 'te', 'dha']
    for i, s_ in enumerate(pat):
        if s_:
            x = tabla(s_, v * (1.25 if i == 10 else 0.9), sa); out[i * step:i * step + len(x)] += x
    i0 = 10 * step
    for x in (manjira(0.9 * v), bansuri(sa + 12, 0.8, 0.6 * v, slide_from=sa + 7)):
        out[i0:i0 + len(x)] += x[:len(out) - i0]
    return out


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


SFX = dict(tihai=tihai, manjira=manjira, ghatam=ghatam, bonk=bonk, crash=crash, whoosh=whoosh, zip=zipp, munch=munch, gulp=gulp, pop=pop, flap=flap, sniff=sniff,
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

    # -- Indian music beds (default). Sa = D (midi 62). Raga Mohanam: S R2 G3 P D2, a bright five-note scale.
    MOHANAM = (0, 2, 4, 7, 9)

    def _deg(self, sa, d, scale=None):
        scale = scale or self.MOHANAM
        return sa + 12 * (d // len(scale)) + scale[d % len(scale)]

    def raga(self, f0, f1, mood='calm', sa=62, v=1.0):
        """Indian score on the same beat grid. One matra = half a beat = 6 frames; the groove is an 8-matra cycle.
        moods: calm (flute tune over tabla), sneak (low veena and clay-pot ticks), chase (fast tabla, flute runs),
        sweet (slow flute and veena)."""
        M = self.BEAT / 2
        n = int((f1 - f0) / M)
        self._add(self.mus, f0, tanpura(sa, (f1 - f0) / self.fps + 0.4, v * (0.5 if mood == 'sneak' else 1.0)))
        groove = {'calm': ['dha', 'ge', 'na', 'te', 'na', 'te', 'dhin', 'na'],
                  'sweet': ['dhin', None, 'na', None, 'tin', None, 'na', 'te'],
                  'chase': ['dha', 'te', 'te', 'na', 'ge', 'te', 'na', 'te'],
                  'sneak': [None, None, None, None, None, None, None, None]}[mood]
        tune = {  # (scale degree or None for a rest, length in matras)
            'calm': [(2, 2), (3, 1), (4, 1), (3, 2), (2, 2), (1, 1), (2, 1), (0, 2), (None, 2), (4, 2), (5, 1), (4, 1), (3, 2), (2, 1), (3, 1), (2, 2), (None, 2), (None, 2)],
            'sweet': [(4, 4), (3, 2), (2, 2), (3, 3), (2, 1), (0, 4), (2, 4), (3, 2), (4, 2), (5, 6), (None, 2)],
        }
        for i in range(n):
            f = f0 + i * M
            s_ = groove[i % 8]
            if s_:
                self._add(self.mus, f, tabla(s_, 0.62 * v, sa))
            if mood == 'chase':
                if i % 2 == 0:
                    self._add(self.mus, f + M / 2, tabla('te', 0.4 * v, sa))
                run = [0, 1, 2, 3, 4, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5]
                self._add(self.mus, f, bansuri(self._deg(sa + 12, run[i % 16]), 0.13, 0.5 * v))
                self._add(self.mus, f + M / 2, bansuri(self._deg(sa + 12, run[(i + 1) % 16]), 0.11, 0.38 * v))
                if i % 4 == 0:
                    self._add(self.mus, f, manjira(0.5 * v)); self._add(self.mus, f, veena(sa - 12, 0.3, 0.6 * v))
            elif mood == 'sneak':
                walk = [0, None, 1, None, 4, None, 1, None]
                if walk[i % 8] is not None:
                    self._add(self.mus, f, veena(sa - 12 + walk[i % 8], 0.5, 0.75 * v))
                if i % 8 in (3, 7):
                    self._add(self.mus, f, ghatam(0.45 * v))
            elif i % 8 == 0:
                self._add(self.mus, f, veena(sa - 12, 0.9, 0.5 * v)); self._add(self.mus, f + M * 4, veena(sa - 5, 0.7, 0.4 * v))
        if mood in tune:
            f = f0; prev = None; k = 0
            while f < f1 - M:
                d, ln = tune[mood][k % len(tune[mood])]
                if d is not None:
                    note = self._deg(sa + 12, d)
                    self._add(self.mus, f, bansuri(note, ln * M / self.fps * 0.96, 0.6 * v, slide_from=prev))
                    prev = note
                else:
                    prev = None
                f += ln * M; k += 1

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
