import json, subprocess
p = json.load(open('brief/plan.json')); durs = []
for l in p['lines']:
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', l['audio']], capture_output=True, text=True).stdout)
    durs.append(d + p['gap'])
st = []; t = 0
for d in durs: st.append(t); t += d
json.dump({'fps': 30, 'starts': st, 'durs': durs, 'lines': [{'text': l['text'], 'keywords': l['keywords']} for l in p['lines']]}, open('mg/src/timing.json', 'w'), indent=1)
print('timing', round(t, 2))
