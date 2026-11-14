"""Kokoro TTS for each plan line -> audio/lNN.wav (trimmed). Usage: python tts.py KOKORO_DIR"""
import json, subprocess, sys, soundfile as sf
from kokoro_onnx import Kokoro
kd = sys.argv[1]
k = Kokoro(f'{kd}/kokoro-v1.0.onnx', f'{kd}/voices-v1.0.bin')
p = json.load(open('brief/plan.json'))
for l in p['lines']:
    s, sr = k.create(l['text'], voice='am_michael', speed=0.95, lang='en-us'); sf.write('/tmp/raw.wav', s, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '/tmp/raw.wav', '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse',
                    l['audio']], check=True)
print('tts done')
