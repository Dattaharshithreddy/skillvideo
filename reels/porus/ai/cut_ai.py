"""Step 3: timing from the narration clips, then stretch each shot's AI clips to fill its line and build mg/public/bg.mp4 (1080x1920, 30 fps)."""
import json, subprocess, os
p = json.load(open('brief/plan.json')); P = json.load(open('ai/prompts.json'))
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
durs = [dur(l['audio']) for l in p['lines']]; durs[-1] += 3.0
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
END = round(t * 30)
json.dump({'starts': starts, 'durs': durs, 'end': END, 'lines': [{'text': l['text'], 'keywords': l['keywords'], 'shot': l['shot']} for l in p['lines']]},
          open('brief/timing.json', 'w'), indent=1, ensure_ascii=False)
os.makedirs('ai/seg', exist_ok=True); lst = []
for i, l in enumerate(p['lines']):
    cl = [c['id' and os.path.exists(f"ai/clips/{c['id']}.mp4")] for c in P['clips' and os.path.exists(f"ai/clips/{c['id']}.mp4")] if c['shot' and os.path.exists(f"ai/clips/{c['id']}.mp4")] == l['shot' and os.path.exists(f"ai/clips/{c['id']}.mp4")] and os.path.exists(f"ai/clips/{c['id']}.mp4")]
    # frame-exact length per shot so overlays stay in sync
    f0, f1 = round(starts[i] * 30), round((starts[i] + durs[i]) * 30); nfr = f1 - f0
    per = [nfr // len(cl) + (1 if k < nfr % len(cl) else 0) for k in range(len(cl))]
    for cid, nf in zip(cl, per):
        src = f'ai/clips/{cid}.mp4'; d = dur(src); want = nf / 30.0; k = want / d
        out = f'ai/seg/{i:02d}_{cid}.mp4'
        vf = (f"setpts={k:.5f}*PTS,fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,"
              f"trim=end_frame={nf},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop={nf}")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', vf, '-frames:v', str(nf), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', out], check=True)
        lst.append(out); print('SEG', out, nf, 'stretch', round(k, 2))
open('ai/seg/list.txt', 'w').write(''.join(f"file '{os.path.abspath(x)}'\n" for x in lst))
os.makedirs('mg/public', exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'ai/seg/list.txt', '-c', 'copy', 'mg/public/bg.mp4'], check=True)
print('BG', dur('mg/public/bg.mp4'), 'expected', END / 30, 'CUT_DONE')
