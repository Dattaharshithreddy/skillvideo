#!/usr/bin/env python3
"""check_protected.py - READ-ONLY. Have any protected files changed, and is the review branch unmerged?

    python3 check_protected.py                 compare protected files with protected_manifest.json and with git
    python3 check_protected.py --drift         also run the model drift check
    python3 check_protected.py --print-hashes  print current hashes as JSON (to stdout only; writes nothing)

Protected: the engine, character code, presets, the model baseline and episode 1 (Production_Pipeline.md 5.1).
The manifest of approved hashes is a plain file kept beside this script. This script never writes it:
it is updated by hand, in its own commit, only after Harshith has approved a change to a protected file.
Exit 1 if a protected file differs from the manifest, is modified in the working tree, or the review
branch has been merged into the current branch.
"""
import glob, hashlib, json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'protected_manifest.json')
PATTERNS = ['toon-slapstick/engine/*.py', 'cartoon-animation-director/knowledge/model_baseline.json', 'toon-slapstick/episodes/01-dosa-snatch/episode.py']
REVIEW = 'review/stage1-character-refs'


def hashes(root=ROOT):
    out = {}
    for pat in PATTERNS:
        for p in sorted(glob.glob(os.path.join(root, pat))):
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    return out


def compare(now, approved):
    probs = []
    for k in sorted(set(now) | set(approved)):
        if k not in approved:
            probs.append('NEW protected file not in the manifest: %s' % k)
        elif k not in now:
            probs.append('MISSING protected file: %s' % k)
        elif now[k] != approved[k]:
            probs.append('CHANGED: %s' % k)
    return probs


def git(*a):
    return subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True, text=True)


def run(drift=False, out=sys.stdout):
    probs = []
    now = hashes()
    if os.path.exists(MANIFEST):
        man = json.load(open(MANIFEST))
        probs += compare(now, man['files'])
        print('manifest: %d protected files, recorded %s at commit %s' % (len(man['files']), man.get('recorded'), man.get('commit')), file=out)
    else:
        probs.append('no protected_manifest.json beside this script'); print('manifest: missing', file=out)
    dirty = [l for l in git('status', '--porcelain', '--', 'toon-slapstick/engine', 'cartoon-animation-director/knowledge/model_baseline.json', 'toon-slapstick/episodes/01-dosa-snatch').stdout.splitlines() if l.strip()]
    for l in dirty:
        probs.append('uncommitted change to a protected path: %s' % l.strip())
    print('working tree: %s' % ('clean on protected paths' if not dirty else '%d change(s)' % len(dirty)), file=out)
    ref = 'origin/' + REVIEW
    if git('rev-parse', '--verify', '-q', ref).returncode != 0:
        print('review branch: %s not found locally (run git fetch); not checked' % ref, file=out)
    elif git('merge-base', '--is-ancestor', ref, 'HEAD').returncode == 0:
        probs.append('review branch %s HAS BEEN MERGED into the current branch' % REVIEW); print('review branch: MERGED', file=out)
    else:
        print('review branch: exists, not merged into the current branch', file=out)
    if drift:
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'cartoon-animation-director', 'knowledge', 'figures', 'make_cd_figures.py'), 'check'], capture_output=True, text=True)
        lines = [l for l in r.stdout.splitlines() if 'PASS' in l or 'FAIL' in l]
        print('drift check: ' + '; '.join(' '.join(l.split()) for l in lines), file=out)
        if any('FAIL' in l for l in lines) or not lines:
            probs.append('model drift check did not pass for every character')
    for p in probs:
        print('FAIL: ' + p, file=out)
    print('PASS: protected files unchanged' if not probs else '%d problem(s)' % len(probs), file=out)
    return len(probs)


if __name__ == '__main__':
    if '--print-hashes' in sys.argv:
        print(json.dumps(hashes(), indent=1)); sys.exit(0)
    sys.exit(1 if run('--drift' in sys.argv) else 0)
