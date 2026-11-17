"""Combine per-shot tracks (mini3d TRACK runs) into mg/src/labels.json: {shot: {frame: {key: [x, y, visible]}}}, every 2nd frame."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'mini3d/out3')
T = json.load(open(os.path.join(HERE, 'mg/src/timing.json'))); out = {}
for l in T['lines']:
    p = os.path.join(TR, f"tracks_{l['shot']}.json")
    if not os.path.exists(p): print('missing', p); continue
    d = json.load(open(p)); out[l['shot']] = {k: v for k, v in d.items() if (int(k) - 1) % 2 == 0}
json.dump(out, open(os.path.join(HERE, 'mg/src/labels.json'), 'w'), separators=(',', ':'))
print('labels', len(out), 'shots')
