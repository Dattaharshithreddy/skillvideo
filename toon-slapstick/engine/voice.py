"""voice.py - spoken Telugu lines for the humans (Ammamma and Chintu). Bheemu and Gaju never talk.

The wav files in ../voice were made with the free AI4Bharat Indic-TTS Telugu model (female speaker);
tools/tts_telugu.py shows how. Ammamma is the voice lowered a little, Chintu is the same voice raised.

    speak(ep, amma, 44, 'a_kapala')        # plays the line from frame 44 and moves her mouth
"""
import os, wave
import numpy as np
from scipy.signal import resample_poly, resample
from sound import SR

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'voice')
SHIFT = {'a': -1.5, 'c': 5.0}          # semitones, by file prefix: a_ = Ammamma, c_ = Chintu


def load(name):
    with wave.open(os.path.join(DIR, name + '.wav'), 'rb') as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        sr = w.getframerate()
    k = 2 ** (SHIFT.get(name[0], 0.0) / 12.0)                  # resampling shifts pitch and speed together
    n = int(len(x) * SR / sr / k)
    x = resample(x, n)
    lead = np.argmax(np.abs(x) > 0.02)                         # trim leading silence so lips and sound start together
    return x[max(0, lead - 200):]


def speak(ep, actor, f, name, v=1.0, duck=0.45):
    """Play a line at frame f, flap the speaker's mouth while it lasts. Returns the frame it ends."""
    x = load(name) * v
    ep.sc._add(ep.sc.fx, f, x)
    n = int(len(x) / SR * ep.sc.fps)
    ep.sc.duck(f, f + n, duck)
    win = int(SR / ep.sc.fps)
    for i in range(0, n, 2):                                   # mouth follows loudness, on twos
        seg = x[i * win:(i + 2) * win]
        a = float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0
        actor.set(f + i, mouth_open=min(0.8, a * 5.0))
    actor.set(f + n, mouth_open=0.0)
    return f + n
