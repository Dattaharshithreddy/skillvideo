#!/usr/bin/env python3
"""check_keys.py - READ-ONLY. Reports keys that the hold on twos hides or delays.

    python3 check_keys.py <episode.py> [--contacts 140,192] [--all]

What it reports (it changes nothing and fixes nothing; a person reads the list):

  LOST   a key on an odd engine frame that is a peak or a trough of its parameter, on an actor running
         on twos. The engine shows the previous frame's drawing there, and the value has moved on by
         the next frame, so the extreme is never drawn. (Engine_Change_Proposals.md, P1)
         Only misses of at least 10% of that parameter's whole range are listed; smaller ones cannot
         be seen. A listed key is a place to LOOK, not a proven defect: a soft landing may be intended.
  LATE   an instant change (`set`) on an odd engine frame on an actor on twos: it appears one frame
         late. Only listed with --all, because many are harmless.
  CONTACT  for each frame given with --contacts: which characters show a held drawing on that frame.
         A prop on ones arrives on time; a character on twos may not. (P3)

Exit code: 0 if nothing was reported, 1 if something was. Film frame = engine frame + 1.
"""
import argparse, math, sys
from _load import load_stage, name_of

TOL = 1e-6
MIN_SHARE = 0.10      # a lost extreme is reported only if the miss is at least this share of the parameter's whole range


def held(a, f):
    """True if the engine shows frame f-1's pose on frame f (same rule as Actor.frame_pose)."""
    if not getattr(a, 'twos', False) or f % 2 == 0:
        return False
    return math.hypot(a.value('x', f) - a.value('x', f - 1), a.value('y', f) - a.value('y', f - 1)) < 26


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def scan(a, frames):
    lost, late = [], []
    for p, ks in a.keys.items():
        for f, v, ease in ks:
            if f <= 0 or f >= frames or not held(a, f):
                continue
            if ease == 'step':
                if a.value(p, f - 1) != v:
                    late.append((f, p, a.value(p, f - 1), v))
                continue
            if not _num(v):
                continue
            b, n = a.value(p, f - 1), a.value(p, f + 1)
            if not (_num(b) and _num(n)):
                continue
            if (v > b + TOL and v > n + TOL) or (v < b - TOL and v < n - TOL):
                shown = [a.frame_pose(g)[p] for g in (f - 1, f, f + 1)]
                best = min(shown, key=lambda s: abs(s - v))
                vals = [k[1] for k in ks if _num(k[1])]
                span = (max(vals) - min(vals)) or 1.0
                if abs(best - v) > max(1e-3, MIN_SHARE * span):   # ignore misses too small to see
                    lost.append((f, p, v, best))
    return sorted(lost), sorted(late)


def run(path, contacts=(), show_all=False, out=sys.stdout):
    st, ns = load_stage(path)
    n = 0
    print('check_keys (read-only): %s, %d frames, %d actors' % (path, st.frames, len(st.actors)), file=out)
    for a in st.actors:
        if not getattr(a, 'twos', False):
            continue
        lost, late = scan(a, st.frames)
        nm = name_of(a, ns)
        for f, p, v, best in lost:
            n += 1
            print('LOST    %-10s %-10s engine frame %4d (film %4d): keyed %.3f, nearest value drawn %.3f' % (nm, p, f, f + 1, v, best), file=out)
        if show_all:
            for f, p, old, v in late:
                n += 1
                print('LATE    %-10s %-10s engine frame %4d (film %4d): %r -> %r appears on frame %d' % (nm, p, f, f + 1, old, v, f + 1), file=out)
    for c in contacts:
        for a in st.actors:
            if hasattr(a, 'HEIGHT') and getattr(a, 'twos', False) and a.value('show', c) >= 0.5:
                if held(a, c):
                    n += 1
                    print('CONTACT %-10s engine frame %4d (film %4d): drawing is HELD from frame %d; key the contact on an even engine frame' % (name_of(a, ns), c, c + 1, c - 1), file=out)
    print('%d finding(s)' % n if n else 'no findings', file=out)
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('episode'); ap.add_argument('--contacts', default=''); ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    sys.exit(1 if run(a.episode, [int(x) for x in a.contacts.split(',') if x], a.all) else 0)
