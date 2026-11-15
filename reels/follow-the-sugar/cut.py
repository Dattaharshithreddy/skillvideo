"""Cut both reels' backgrounds from the station render, build the narration tracks and the carousel background stills."""
import json, os, subprocess
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
ST = json.load(open('brief/stations.json')); FPS = 30
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
os.makedirs('mg/public/stills', exist_ok=True)
for k in ('public', 'student'):
    d = f'renders/cut_{k}'; subprocess.run(['rm', '-rf', d]); os.makedirs(d)
    n = 0
    for st, a, m in ST['cuts'][k]:
        base = ST['offset'][st] + a
        for j in range(m):
            src = os.path.abspath(f'renders/seq/f_{min(base + j, ST["offset"][st] + ST["frames"][st] - 1):05d}.jpg')
            n += 1; os.symlink(src, f'{d}/c_{n:05d}.jpg')
    tail = ',tpad=stop_mode=clone:stop_duration=5' if k == 'student' else ''
    sh('ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{d}/c_%05d.jpg', '-vf', 'format=yuv420p' + tail,
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', f'mg/public/bg_{k}.mp4')
    p = json.load(open(f'brief/plan_{k}.json'))
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(p['gap']), 'renders/gap.wav')
    lst = []
    for l in p['lines']: lst += [f"file '{os.path.abspath(l['audio'])}'", f"file '{os.path.abspath('renders/gap.wav')}'"]
    open(f'renders/{k}_audio.txt', 'w').write('\n'.join(lst) + '\n')
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'renders/{k}_audio.txt', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
       '-ar', '48000', f'mg/public/narration_{k}.wav')
    print(k, 'frames', n, 'audio', round(dur(f'mg/public/narration_{k}.wav'), 2))
for st in ST['order']:
    f = ST['offset'][st] + ST['frames'][st] // 2
    sh('cp', f'renders/seq/f_{f:05d}.jpg', f'mg/public/stills/{st}.jpg')
print('CUT_DONE')
