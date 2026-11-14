#!/bin/bash
# Telugu narration in the user's cloned voice (Swaram/voicebox profile "Datta", IndicF5)
cd "$(dirname "$0")"; mkdir -p audio_te
python3 - <<'PY'
import json, subprocess, sys
sys.path.insert(0, '/opt/reel/myvoice'); from gen import gen
p = json.load(open('brief/plan_te.json'))
for l in p['lines']:
    raw = l['audio'].replace('.wav', '_raw.wav')
    gen(l['tts'], 'indicf5', raw, lang='te', seed=11)
    subprocess.run(['ffmpeg','-y','-v','error','-i',raw,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse','-ar','24000','-ac','1',l['audio']], check=True)
PY
