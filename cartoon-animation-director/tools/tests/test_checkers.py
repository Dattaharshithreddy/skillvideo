#!/usr/bin/env python3
"""Tests for the read-only checkers. Run: python3 tests/test_checkers.py
Each test builds a known case in a temporary folder or in memory. Nothing in the project is written."""
import io, os, subprocess, sys, tempfile, textwrap
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import check_keys, check_safe_area, check_docs, check_protected, check_audio
from _load import ROOT, ENGINE

HEAD = "import sys\nsys.path.insert(0, %r)\nfrom toon import Stage, W, GROUND\nfrom chars import Bheemu, Gaju\nfrom scene import Prop\nfrom show import ball\n" % ENGINE
HOP = HEAD + textwrap.dedent('''
    st = Stage(30); g = Gaju(x=W / 2, y=GROUND, face=0.0); g.twos = %s; st.add(g)
    for fr, ln, ease, pose in [(6, 5, 'out', dict(sy=0.78, sx=1.28)), (8, 2, 'snap', dict(y=GROUND - 30, sy=1.2, sx=0.83)),
                               (14, 6, 'out', dict(y=GROUND - 80, sy=1.0, sx=1.0)), (18, 4, 'in', dict(y=GROUND - 6, sy=1.12, sx=0.89)),
                               (19, 1, 'lin', dict(y=GROUND, sy=0.72, sx=1.39)), (22, 3, 'out', dict(sy=1.06, sx=0.94)), (28, 6, 'io', dict(sy=1.0, sx=1.0))]:
        g.move(fr - ln, fr, ease, **pose)
    if __name__ == '__main__':
        raise SystemExit('the checker must not run the render block')
''')
HIT = HEAD + textwrap.dedent('''
    C = %d
    st = Stage(C + 20); bheemu = Bheemu(x=W / 2, y=GROUND, face=0.0); bl = Prop(ball, x=W / 2, y=-400); st.add(bheemu, bl)
    bl.move(C - 6, C, 'in', y=GROUND - 500); bheemu.set(C, sy=0.88, sx=1.09); bheemu.move(C + 2, C + 10, 'elastic', sy=1.0, sx=1.0)
''')
results = []
STATUS = lambda: subprocess.run(['git', '-C', ROOT, 'status', '--porcelain'], capture_output=True, text=True).stdout
BEFORE = STATUS()


def case(name, ok, detail=''):
    results.append(ok); print('%s  %s%s' % ('PASS' if ok else 'FAIL', name, ('  [' + detail + ']') if detail else ''))


def write(d, name, text):
    p = os.path.join(d, name); open(p, 'w').write(text); return p


with tempfile.TemporaryDirectory() as d:
    # --- check_keys
    out = io.StringIO(); n = check_keys.run(write(d, 'hop_twos.py', HOP % 'True'), out=out); t = out.getvalue()
    case('keys: the document 3 hop on twos reports the lost squash at engine frame 19', n >= 1 and 'LOST' in t and 'frame   19' in t and 'sy' in t, t.strip().splitlines()[1] if n else t)
    out = io.StringIO(); n = check_keys.run(write(d, 'hop_ones.py', HOP % 'False'), out=out)
    case('keys: the same hop on ones reports nothing', n == 0)
    out = io.StringIO(); n = check_keys.run(write(d, 'hit_odd.py', HIT % 141), contacts=[141], out=out); t = out.getvalue()
    case('keys: a contact on odd engine frame 141 is reported as held', n == 1 and 'CONTACT' in t and 'HELD' in t)
    out = io.StringIO(); n = check_keys.run(write(d, 'hit_even.py', HIT % 140), contacts=[140], out=out)
    case('keys: a contact on even engine frame 140 is not reported', n == 0)
    out = io.StringIO(); n = check_keys.run(os.path.join(d, 'hit_odd.py'), show_all=True, out=out)
    case('keys: --all lists the one-frame-late squash', 'LATE' in out.getvalue())
    # --- check_safe_area
    p = write(d, 'stand.py', HEAD + "st = Stage(4); gaju = Gaju(x=W / 2, y=GROUND, face=0.0); st.add(gaju)\n")
    out = io.StringIO(); w = check_safe_area.episode(p, 1, dict(top=288, bottom=672, left=48, right=192), out=out)
    g = w['gaju']; exp = (1480 - (1920 - 672)) / 250.0
    case('safe area: Gaju at rest, default camera: feet 440 px above the bottom, %.0f%% of body in a 672 px band' % (100 * exp), abs(min(g['feet']) - 440) < 0.5 and abs(g['bottom'] - exp) < 0.005, 'got feet %.0f, share %.3f' % (min(g['feet']), g['bottom']))
    out = io.StringIO(); w = check_safe_area.episode(p, 1, dict(top=180, bottom=390, left=0, right=100), out=out)
    case('safe area: the same pose is clear of a 390 px band', w['gaju']['bottom'] == 0)
    # --- check_docs
    k = os.path.join(d, 'knowledge'); os.makedirs(k)
    write(k, 'Good.md', '# G\nVersion 1.0\n\n## 0. A\n\n## 1. B\n\nSee `toon.py` and `references/07-qc-rubric.md`.\n\n## 2. Change log\n')
    write(k, 'Bad.md', '# B\nVersion 1.0\n\n## 0. A\n\n## 2. B\n\n![x](figures/none.png) and `no_such_file_anywhere.py`.\n\nChange log\n')
    out = io.StringIO(); n = check_docs.run([k], out=out); t = out.getvalue()
    case('docs: a clean file passes and a broken one reports link, path and numbering', n == 3 and 'broken link' in t and 'file not found' in t and 'out of sequence' in t and 'ok    ' in t, '%d problems' % n)
    # --- check_protected
    now = check_protected.hashes(); changed = dict(now); first = sorted(now)[0]; changed[first] = 'x'
    case('protected: an altered hash is reported, identical hashes are not', check_protected.compare(now, now) == [] and check_protected.compare(changed, now) == ['CHANGED: %s' % first])
    case('protected: a new or missing protected file is reported', len(check_protected.compare({**now, 'toon-slapstick/engine/new.py': 'h'}, now)) == 1 and len(check_protected.compare({}, now)) == len(now))
    out = io.StringIO(); n = check_protected.run(out=out)
    case('protected: the real repository is clean against the manifest', n == 0, out.getvalue().strip().splitlines()[-1])
    # --- check_audio
    clip = os.path.join(d, 't.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=108x192:r=24:d=3', '-f', 'lavfi', '-i', 'sine=f=440:d=2', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono:d=1',
                    '-filter_complex', '[1:a][2:a]concat=n=2:v=0:a=1[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', clip], check=True)
    m = check_audio.measure(clip)
    case('audio: a 440 Hz test tone measures a plausible loudness and one silence', m['audio'] and m['lufs'] is not None and -30 < m['lufs'] < -10 and len(m['silences']) == 1, 'I=%s LUFS, peak=%s, silences=%d' % (m['lufs'], m['peak'], len(m['silences'])))
    mute = os.path.join(d, 'm.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=108x192:r=24:d=1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mute], check=True)
    case('audio: a file with no audio stream is reported as such', check_audio.measure(mute)['audio'] is False)

# the checkers must not have written anything inside the repository
case('read-only: git status of the whole repository is the same after the tests as before', STATUS() == BEFORE)
print('\n%d of %d passed' % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
