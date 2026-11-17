"""Pick, sentence by sentence, the take that sounds most like Datta (Resemblyzer speaker embedding vs his reference clips),
then rebuild one clip per shot (audio_mini/lNN.wav). Usage: python select_takes.py <ref_dir> <take ids...>"""
import json, sys, glob, os, subprocess
import numpy as np, soundfile as sf
from resemblyzer import VoiceEncoder, preprocess_wav
os.chdir('/opt/reel/sv/reels/porus')
ref_dir, takes = sys.argv[1], sys.argv[2:]
p = json.load(open('brief/plan.json')); owner = json.load(open('audio_mini/owner.json'))
enc = VoiceEncoder('cuda' if os.environ.get('CUDA', '1') == '1' else 'cpu')
refs = [preprocess_wav(f) for f in sorted(glob.glob(ref_dir + '/*.wav'))]
ref = enc.embed_speaker(refs)
segs = {}                                # take -> list of (audio, sr)
for k in takes:
    y, sr = sf.read(f'audio_mini/full{k}.wav'); y = y if y.ndim == 1 else y.mean(1)
    L = json.load(open(f'audio_mini/narrate{k}.json'))['lines']
    st = [float(x.get('start', x.get('start_s', 0))) for x in L] + [len(y) / sr]
    segs[k] = [(y[int(st[j] * sr):int(st[j + 1] * sr)], sr) for j in range(len(L))]
n = len(owner); assert all(len(v) == n for v in segs.values()), {k: len(v) for k, v in segs.items()}
score = np.zeros((len(takes), n)); durs = np.zeros((len(takes), n))
for a, k in enumerate(takes):
    for j, (y, sr) in enumerate(segs[k]):
        durs[a, j] = len(y) / sr
        w = preprocess_wav(y.astype(np.float32), source_sr=sr)
        score[a, j] = float(np.dot(enc.embed_utterance(w), ref)) if len(w) > 8000 else 0.0
med = np.median(durs, 0); bad = (durs / med > 1.35) | (durs / med < 0.7)
adj = score - 0.25 * bad
pick = adj.argmax(0)
print('take means', {k: round(float(score[a].mean()), 3) for a, k in enumerate(takes)})
for j in range(n): print('SENT', j, 'shot', owner[j], 'pick', takes[pick[j]], 'scores', [round(x, 3) for x in score[:, j]], 'durs', [round(x, 2) for x in durs[:, j]])
print('weakest', sorted(range(n), key=lambda j: adj[pick[j], j])[:6], [round(float(adj[pick[j], j]), 3) for j in sorted(range(n), key=lambda j: adj[pick[j], j])[:6]])
# loudness: match voiced RMS per sentence
def vrms(y):
    fr = y[:len(y) // 512 * 512].reshape(-1, 512); r = np.sqrt((fr ** 2).mean(1)); r = r[r > r.max() * 0.1] if r.max() > 0 else r
    return float(np.sqrt((r ** 2).mean())) if len(r) else 1e-3
chosen = [segs[takes[pick[j]]][j] for j in range(n)]
tgt = np.median([vrms(y) for y, _ in chosen])
for i, l in enumerate(p['lines']):
    parts = []
    for j in range(n):
        if owner[j] != i: continue
        y, sr = chosen[j]; y = y * min(3.0, tgt / max(vrms(y), 1e-4)); f = int(0.008 * sr)
        y = y.copy(); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); parts.append(y)
    out = np.clip(np.concatenate(parts), -0.99, 0.99); sf.write(l['audio'], out, sr)
    print('LINE', i + 1, round(len(out) / sr, 2))
json.dump({'takes': takes, 'pick': [takes[x] for x in pick], 'score': score.tolist()}, open('audio_mini/picks.json', 'w'))
print('SELECT_DONE')
