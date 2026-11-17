"""Download a few YouTube tours of each guest house (480p, first 4 minutes) and pull one frame every 3 s,
then build a numbered contact sheet per building: refs/yt/<key>/fNNN.jpg, refs/ytsheet_<key>.jpg."""
import os, subprocess, sys, glob
from PIL import Image, ImageDraw
V = {'nandakam': ['beXukeAYC2k', 'eUMZqMs5CLU', 'zTDBuhbMk7g'], 'panchajanyam': ['isq3J43HanQ', 'aM4xCp8ynKg', 'FdbCWbdFfRo'],
     'kausthubham': ['WJCoUSuL38U', '9pKSQZ60lkU', 'I-e4GkucY08'], 'vakulamatha': ['MSXB7XeeY-A', 'TmBHGncBIIg', 'JIgnv74P3fY'],
     'pac5': ['QRNjD1KElsw', 'k4lmJ7lHLUM', '6ncENNMzitg'], 'padmavathi': ['5sIyj0BjGT4', 'E2yaEQwW9tw'],
     'varaha': ['6eUIy9sEJ2I', 'NcSbh0a8ukQ'], 'sapthagiri': ['ROwKnRIxemA', 'Mb8FuGV8CKE'], 'snc': ['ni5bZluUcGs']}
keys = sys.argv[1:] or list(V)
for key in keys:
    d = f'refs/yt/{key}'; os.makedirs(d, exist_ok=True); n = 0
    for vid in V[key]:
        out = f'/tmp/yt_{vid}.mp4'
        if not os.path.exists(out):
            r = subprocess.run(['yt-dlp', '-q', '--no-warnings', '-f', 'bv*[height<=480][ext=mp4]/b[height<=480]/b', '--download-sections', '*0-240',
                                '-o', out, f'https://www.youtube.com/watch?v={vid}'], capture_output=True, text=True)
            if r.returncode: print('yt fail', vid, r.stderr[-200:].strip(), flush=True); continue
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', 'fps=1/3,scale=480:-2', '-q:v', '4', f'{d}/{vid}_%03d.jpg'])
    fs = sorted(glob.glob(f'{d}/*.jpg')); print(key, len(fs), 'frames', flush=True)
    if not fs: continue
    W, tw = 6, 240
    ims = [Image.open(f) for f in fs[:72]]; th = int(tw * ims[0].height / ims[0].width)
    sh = Image.new('RGB', (W * tw, ((len(ims) + W - 1) // W) * (th + 16)), (15, 10, 5)); dr = ImageDraw.Draw(sh)
    for i, (f, im) in enumerate(zip(fs, ims)):
        t = im.resize((tw, th)); x, y = (i % W) * tw, (i // W) * (th + 16); sh.paste(t, (x, y)); dr.text((x + 4, y + th + 2), f'{i}', fill=(255, 210, 80))
    sh.save(f'refs/ytsheet_{key}.jpg', quality=78)
    open(f'refs/yt/{key}/index.txt', 'w').write('\n'.join(fs[:72]))
print('YT_DONE')
