"""From the narration durations, work out how long each 3D station must be (max over both cuts), the global frame
offset of each station, and an edit list per cut. Also writes the Remotion timing files for both cuts."""
import json, subprocess, math
FPS = 30
ORDER = ['room_in', 'body_wide', 'gut', 'vessels', 'pancreas', 'muscle', 'liver', 'fat', 'pancreas_tired', 'vessels_stuck',
         'kidney', 'eye', 'feet', 'heart', 'room_out', 'room_healthy']
def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)
need = {s: 0 for s in ORDER}; cuts = {}
for k in ('public', 'student'):
    p = json.load(open(f'brief/plan_{k}.json'))
    durs = [dur(l['audio']) + p['gap'] for l in p['lines']]
    starts, t = [], 0.0
    for d in durs: starts.append(t); t += d
    used = {s: 0 for s in ORDER}; edl = []
    for l, s0, d in zip(p['lines'], starts, durs):
        f0 = round(s0 * FPS); f1 = round((s0 + d) * FPS); n = f1 - f0; acc = 0
        for j, (st, share) in enumerate(l['st']):
            m = n - acc if j == len(l['st']) - 1 else round(n * share)
            edl.append([st, used[st], m]); used[st] += m; acc += m
    for s in ORDER: need[s] = max(need[s], used[s])
    cuts[k] = edl
    json.dump({'fps': FPS, 'starts': starts, 'durs': durs,
               'lines': [{'text': l['text'], 'keywords': l['keywords']} for l in p['lines']]},
              open(f'mg/src/timing_{k}.json', 'w'), indent=1)
    print(k, 'total', round(t, 2), 's', sum(e[2] for e in edl), 'frames')
frames = {s: max(need[s] + 8, 45) for s in ORDER}
off, f = {}, 1
for s in ORDER: off[s] = f; f += frames[s]
json.dump({'order': ORDER, 'frames': frames, 'offset': off, 'end': f - 1, 'cuts': cuts}, open('brief/stations.json', 'w'), indent=1)
print('stations', frames, 'end', f - 1)
