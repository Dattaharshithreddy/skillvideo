"""Lesson 1 exercise: six Bheemu key poses, in colour and as silhouettes. Run: python3 make.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Stage, W, H
from chars import Bheemu
from show import SHOCK
from PIL import Image, ImageDraw, ImageFont
import numpy as np

Bheemu.shadow = 0
POSES = [('1 neutral', dict()),
         ('2 reach up', dict(armR=(46, -340), handR='open', armL=(-30, 20), pitch=-0.6, pupil=(0.3, -0.9), sy=1.06, sx=0.97, rot=3)),
         ('3 wind-up to pull', dict(face=1, yaw=0.8, rot=-12, armR=(150, -150), armL=(130, -110), handR='grip', handL='grip', brow_ang=20, smile=-0.6)),
         ('4 shock', dict(armL=(-110, -230), armR=(110, -210), handL='open', handR='open', sy=1.12, sx=0.93, glasses_dy=-18, **SHOCK)),
         ('5 sitting dazed', dict(sit=1.0, glasses_rot=14, glasses_dy=10, head_rot=8, pupil_s=0.5, pupil=(0.5, 0.5), smile=-0.2)),
         ('6 run', dict(face=1, yaw=1.0, rot=14, wheel=1.0, stride=38, step=0.3, armR=(110, -120), armL=(-90, -60), scarf_fly=1.0, brow_ang=14))]
st = Stage(2); st.grain = 0
st.cut(0, x=W / 2, y=H / 2, zoom=1.0)
for i, (_, kw) in enumerate(POSES):
    st.add(Bheemu(x=190 + (i % 3) * 350, y=880 + (i // 3) * 900, sx=kw.pop('sx', 1.0) * 0.52, sy=kw.pop('sy', 1.0) * 0.52, **kw))
st.still(0, 'colour.png', 1.0)
im = Image.open('colour.png').convert('RGB'); a = np.asarray(im).astype(int)
bg = a[5, 5]
mask = (np.abs(a - bg).sum(axis=2) > 40)
sil = np.where(mask[..., None], 20, 245).astype(np.uint8).repeat(3, axis=2)
out = Image.new('RGB', (W * 2, H), 'white'); out.paste(im, (0, 0)); out.paste(Image.fromarray(sil), (W, 0))
d = ImageDraw.Draw(out); f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
for i, (name, _) in enumerate(POSES):
    for ox in (0, W):
        d.text((ox + 60 + (i % 3) * 350, 300 + (i // 3) * 900), name, font=f, fill=(150, 30, 40))
out.crop((0, 260, W * 2, 1900)).resize((1620, 1230)).save('L01_silhouettes_attempt1.png'); os.remove('colour.png')
