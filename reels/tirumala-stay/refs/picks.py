# Combine best Google Maps exterior (left) with the earlier YouTube frame (right) per guest house.
import os, shutil
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
PICK = {'nandakam': 0, 'panchajanyam': 0, 'kausthubham': 0, 'vakulamatha': 0, 'pac5': 0, 'padmavathi': 0, 'sapthagiri': 3}
NAME = {'nandakam': 'Nandakam', 'panchajanyam': 'Panchajanyam', 'kausthubham': 'Kausthubham', 'vakulamatha': 'Vakulamatha',
        'pac5': 'PAC-5 Venkatadri Nilayam', 'padmavathi': 'Padmavathi Guest House', 'sapthagiri': 'Sapthagiri Rest House'}
os.makedirs(f'{D}/best', exist_ok=True)
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
except Exception: F = ImageFont.load_default()
TW, TH = 640, 420
rows = []
for k, i in PICK.items():
    src = f'{D}/maps/{k}/{i:02d}.jpg'
    shutil.copy(src, f'{D}/best/{k}.jpg')
    a = Image.open(src).convert('RGB'); a.thumbnail((TW, TH))
    yt = f'{D}/{k}.jpg'
    b = None
    if os.path.exists(yt): b = Image.open(yt).convert('RGB'); b.thumbnail((TW, TH))
    rows.append((k, a, b))
W = 2 * TW + 30; H = len(rows) * (TH + 60) + 70
sh = Image.new('RGB', (W, H), (16, 14, 12)); d = ImageDraw.Draw(sh)
d.text((10, 15), 'Google Maps (left)   |   YouTube frame (right)', fill=(255, 210, 90), font=F)
y = 70
for k, a, b in rows:
    d.text((10, y), NAME[k], fill=(255, 255, 255), font=F)
    sh.paste(a, (10, y + 45))
    if b: sh.paste(b, (TW + 20, y + 45))
    else: d.text((TW + 30, y + 200), '(no YouTube frame)', fill=(150, 150, 150), font=F)
    y += TH + 60
sh.save(f'{D}/best/picks_sheet.jpg', quality=85)
print('PICKS_DONE', len(rows))
