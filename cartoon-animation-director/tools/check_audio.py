#!/usr/bin/env python3
"""check_audio.py - READ-ONLY. Measures the sound of rendered files. It cannot tell if anything sounds good.

    python3 check_audio.py <file.mp4|wav> [more files ...]

Per file: integrated loudness (LUFS), loudness range, true peak (dBTP), sample rate, channels, and
silent stretches of half a second or more. Numbers only. Whether the sound is acceptable is decided by
a person listening (Sound_Design.md). Targets such as -14 LUFS are conventions, not rules.
"""
import re, subprocess, sys


def measure(path):
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name,sample_rate,channels', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    if not pr:
        return dict(file=path, audio=False)
    codec, sr, ch = pr.split(',')[:3]
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true,silencedetect=n=-50dB:d=0.5', '-vn', '-f', 'null', '-'], capture_output=True, text=True).stderr
    tail = err[err.rfind('Summary:'):]
    g = lambda pat: (float(re.search(pat, tail).group(1)) if re.search(pat, tail) else None)
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r'silence_start: ([-\d.]+)', err), re.findall(r'silence_end: ([-\d.]+)', err))]
    return dict(file=path, audio=True, codec=codec, rate=int(sr), channels=int(ch), lufs=g(r'I:\s+([-\d.]+) LUFS'), lra=g(r'LRA:\s+([-\d.]+) LU'), peak=g(r'Peak:\s+([-\d.]+) dBFS'), silences=sil)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print('check_audio (read-only; numbers only, nobody has listened)')
    print('| File | Codec | Rate | Ch | Integrated (LUFS) | Range (LU) | True peak (dBTP) | Silences >= 0.5 s |')
    print('|---|---|---|---|---|---|---|---|')
    for p in sys.argv[1:]:
        m = measure(p)
        if not m['audio']:
            print('| %s | NO AUDIO STREAM | | | | | | |' % p.split('/')[-1]); continue
        print('| %s | %s | %d | %d | %s | %s | %s | %d |' % (p.split('/')[-1], m['codec'], m['rate'], m['channels'], m['lufs'], m['lra'], m['peak'], len(m['silences'])))
