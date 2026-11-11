#!/usr/bin/env python3
"""check_docs.py - READ-ONLY. Checks the Markdown documents for broken links and paths.

    python3 check_docs.py [folder ...]        (default: knowledge/ and proposals/ and the pilot folder if present)

For every .md file: image and file links resolve; every `backticked` name ending in .md .py .json .sh
resolves somewhere in the repository; numbered `## N.` sections run in sequence; a version line and a
change log are present (knowledge documents only). It reads files and prints. Exit 1 if anything is found.
"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
GENERATED = {'manifest.json', 'check.png', 'out.mp4', 'audio.wav', 'episode.py', 'ep.mp4', 'new.mp4', 'reference.mp4', 'episode.mp4', 'scene.py', 'config.json'}


def repo_files():
    out = set()
    for r, d, fs in os.walk(ROOT):
        if '.git' in r.split(os.sep):
            continue
        for f in fs:
            out.add(os.path.relpath(os.path.join(r, f), ROOT))
    return out


def check_file(path, files, bases, knowledge=False):
    t = open(path, encoding='utf-8').read(); probs = []
    here = os.path.dirname(path)
    for target in re.findall(r'\]\(([^)#\s]+)', t):
        if re.match(r'^[a-z]+://', target) or target.startswith('mailto:'):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(here, target))):
            probs.append('broken link: %s' % target)
    for tok in sorted(set(re.findall(r'`([^`\s]+\.(?:md|py|json|sh))`', t))):
        if any(c in tok for c in '<>*{}') or os.path.basename(tok) in GENERATED:
            continue
        if tok in files or os.path.relpath(os.path.normpath(os.path.join(here, tok)), ROOT) in files:
            continue
        if '/' in tok:
            if not any(f.endswith('/' + tok) or f == tok for f in files):
                probs.append('path not found: %s' % tok)
        elif tok not in bases:
            probs.append('file not found: %s' % tok)
    nums = [int(n) for n in re.findall(r'^## (\d+)\.', t, flags=re.M)]
    if nums and nums != list(range(nums[0], nums[0] + len(nums))):
        probs.append('section numbers out of sequence: %s' % nums)
    if knowledge and not t.startswith('---'):
        if not re.search(r'^Version \d+\.\d+', t, flags=re.M) and '**PROPOSALS ONLY' not in t:
            probs.append('no version line')
        if 'Change log' not in t:
            probs.append('no change log')
    return probs


def run(folders, out=sys.stdout):
    files = repo_files(); bases = {os.path.basename(f) for f in files}; total = 0; n = 0
    for folder in folders:
        for r, d, fs in os.walk(folder):
            for f in sorted(fs):
                if f.endswith('.md'):
                    p = os.path.join(r, f); n += 1
                    probs = check_file(p, files, bases, knowledge=os.path.basename(os.path.normpath(r)) == 'knowledge')
                    total += len(probs)
                    print('%s  %s' % ('ok  ' if not probs else 'FAIL', os.path.relpath(p, ROOT)), file=out)
                    for x in probs:
                        print('      ' + x, file=out)
    print('%d file(s), %d problem(s)' % (n, total), file=out)
    return total


if __name__ == '__main__':
    base = os.path.join(ROOT, 'cartoon-animation-director')
    folders = sys.argv[1:] or [x for x in (os.path.join(base, 'knowledge'), os.path.join(base, 'proposals'), os.path.join(base, 'pilot')) if os.path.isdir(x)]
    sys.exit(1 if run(folders) else 0)
