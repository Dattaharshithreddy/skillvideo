import sys, json, os, numpy as np, wave
os.chdir('/tmp/tts')
cfg = json.load(open('te/fastpitch/config.json'))
for k in ('speakers_file',):
    if k in cfg: cfg[k] = '/tmp/tts/te/fastpitch/speakers.pth'
if 'model_args' in cfg and 'speakers_file' in cfg['model_args']: cfg['model_args']['speakers_file'] = '/tmp/tts/te/fastpitch/speakers.pth'
json.dump(cfg, open('te/fastpitch/config_local.json', 'w'))
from TTS.utils.synthesizer import Synthesizer
s = Synthesizer(tts_checkpoint='te/fastpitch/best_model.pth', tts_config_path='te/fastpitch/config_local.json', tts_speakers_file='te/fastpitch/speakers.pth',
                vocoder_checkpoint='te/hifigan/best_model.pth', vocoder_config='te/hifigan/config.json', use_cuda=False)
print('speakers', getattr(s.tts_model.speaker_manager, 'speaker_names', None), 'sr', s.output_sample_rate)
lines = json.load(open(sys.argv[1]))
for name, spk, text in lines:
    wav = np.array(s.tts(text, speaker_name=spk), dtype=np.float32)
    wav = wav / (abs(wav).max() + 1e-9) * 0.9
    with wave.open('%s.wav' % name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(s.output_sample_rate); w.writeframes((wav * 32767).astype(np.int16).tobytes())
    print(name, len(wav) / s.output_sample_rate)
