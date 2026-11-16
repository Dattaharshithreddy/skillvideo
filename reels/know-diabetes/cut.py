"""Cut the reel background from the 'Follow the Sugar' station render. A station that is needed for longer than it was
rendered is slowed down evenly instead of freezing. Writes mg/src/timing.json, mg/public/bg.mp4 and narration.wav."""
import json, os, subprocess
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); FPS = 30; TAIL = 75
SRC = '../follow-the-sugar'; ST = json.load(open(f'{SRC}/brief/stations.json'))
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
p = json.load(open('brief/plan.json')); durs = [dur(l['audio']) + p['gap'] for l in p['lines']]
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
edl, used = [], {}
for i, (l, s0, d) in enumerate(zip(p['lines'], starts, durs)):
    n = round((s0 + d) * FPS) - round(s0 * FPS) + (TAIL if i == len(durs) - 1 else 0); acc = 0
    for j, (st, share) in enumerate(l['st']):
        m = n - acc if j == len(l['st']) - 1 else round(n * share)
        edl.append([st, used.get(st, 0), m]); used[st] = used.get(st, 0) + m; acc += m
d_ = 'renders/cut'; subprocess.run(['rm', '-rf', d_]); os.makedirs(d_); os.makedirs('mg/public', exist_ok=True)
n, cuts, prev = 0, [], None
for st, a, m in edl:
    if prev is not None and st != prev: cuts.append(n)
    prev = st; avail = ST['frames'][st] - 8; k = min(1.0, avail / used[st])
    for j in range(m):
        src = os.path.abspath(f"{SRC}/renders/seq/f_{ST['offset'][st] + min(avail - 1, int((a + j) * k)):05d}.jpg")
        n += 1; os.symlink(src, f'{d_}/c_{n:05d}.jpg')
sh('ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{d_}/c_%05d.jpg', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', 'mg/public/bg.mp4')
lst = [f"file '{os.path.abspath(l['audio'])}'" for l in p['lines']]      # the lines are exact slices of one take: join with no gaps
open('renders/audio.txt', 'w').write('\n'.join(lst) + '\n')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'renders/audio.txt', '-af', 'volume=1.0,apad=pad_dur=3', '-ar', '48000', 'mg/public/narration.wav')
json.dump({'fps': FPS, 'starts': starts, 'durs': durs, 'cuts': cuts, 'end': n, 'lines': [{'text': l['text'], 'keywords': l['keywords']} for l in p['lines']]},
          open('mg/src/timing.json', 'w'), indent=1)
print('frames', n, 'seconds', round(n / FPS, 1), 'slowdowns', {s: round(min(1.0, (ST['frames'][s] - 8) / u), 2) for s, u in used.items()}); print('CUT_DONE')
