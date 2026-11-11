#!/usr/bin/env python3
"""new_episode.py - create the standard folder structure for one episode.

    python3 new_episode.py 11-milk-bowl [--root ../../toon-slapstick/episodes]

Naming: episode folder NN-short-name; shots s01, s02...; frames <ep>_<shot>_<stage>_f00001.png;
versions v001, v002... (never overwrite an approved version). manifest.json lists every asset and its status.
"""
import argparse, datetime, json, os

FOLDERS = ['research', 'characters/designs', 'characters/model_sheets', 'backgrounds', 'script', 'storyboard', 'animatic',
           'keyframes', 'inbetweens', 'clean', 'colour', 'sound/effects', 'sound/music_dialogue', 'comp', 'renders', 'qc']

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name'); ap.add_argument('--root', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'toon-slapstick', 'episodes'))
    a = ap.parse_args()
    base = os.path.join(a.root, a.name)
    for f in FOLDERS:
        os.makedirs(os.path.join(base, f), exist_ok=True)
        keep = os.path.join(base, f, '.gitkeep')
        if not os.listdir(os.path.join(base, f)):
            open(keep, 'w').close()
    man = os.path.join(base, 'manifest.json')
    if not os.path.exists(man):
        json.dump({'episode': a.name, 'created': datetime.date.today().isoformat(), 'format': {'width': 1080, 'height': 1920, 'fps': 24},
                   'naming': {'frames': '<episode>_<shot>_<stage>_f00001.png', 'versions': 'v001, v002 ... never overwrite an approved version'},
                   'stages': {k: 'not started' for k in ('script', 'storyboard', 'animatic', 'assets', 'keys', 'inbetweens', 'cleanup', 'comp', 'effects', 'sound', 'edit', 'render', 'qc')},
                   'shots': [], 'assets': []}, open(man, 'w'), indent=2)
    print('created', os.path.abspath(base))
