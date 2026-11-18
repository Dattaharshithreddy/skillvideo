"""Silent placeholder narration (only where a line's audio is missing) so the scene can be built and stills rendered
before the real voiceover arrives. Durations scale with each line's text length (~127 s total, like the first take)."""
import json, os, subprocess, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if not os.path.exists('brief/plan.json'): subprocess.run([sys.executable, 'plan.py'], check=True)
p = json.load(open('brief/plan.json'))
n = sum(len(l['tts']) for l in p['lines'])
os.makedirs('audio', exist_ok=True)
for l in p['lines']:
    if os.path.exists(l['audio']): continue
    d = 127.0 * len(l['tts']) / n
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', f'{d:.2f}', l['audio']], check=True)
    print('placeholder', l['audio'], round(d, 1))
