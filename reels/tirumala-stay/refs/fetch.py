"""Find real photos of each guest house: search the web (DuckDuckGo HTML), read each result's og:image and inline photos,
download the larger ones to refs/<key>/NN.jpg, then make a labelled contact sheet refs/sheet_<key>.jpg."""
import os, re, sys, json, io, urllib.parse, concurrent.futures as cf
import requests
from PIL import Image, ImageDraw, ImageFont
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
Q = {
 'nandakam': ['Nandakam rest house Tirumala', 'Nandakam guest house Tirumala photo'],
 'panchajanyam': ['Panchajanyam rest house Tirumala', 'Panchajanyam guest house Tirumala building'],
 'kausthubham': ['Kausthubham rest house Tirumala', 'Kousthubham guest house Tirumala'],
 'vakulamatha': ['Vakulamatha rest house Tirumala', 'Mathrusri Vakuladevi rest house Tirumala'],
 'pac5': ['Venkatadri Nilayam PAC 5 Tirumala', 'PAC-5 Tirumala pilgrim amenities complex building'],
 'padmavathi': ['Sri Padmavathi guest house Tirumala', 'Padmavathi guest house area Tirumala building'],
 'varaha': ['Varahaswamy guest house Tirumala', 'Varahaswami rest house Tirumala'],
 'sapthagiri': ['Sapthagiri guest house Tirumala', 'Sapthagiri cottages Tirumala'],
}
SEED = {'nandakam': ['https://tirupatitirumalainfo.com/wp-content/uploads/2023/05/Nandakam-Rest-House.jpg'],
        'vakulamatha': ['https://gotirupati.com/wp-content/uploads/2021/03/Vaikula-Matha-Resthouse-Copy.jpg'],
        'pac5': ['https://www.tirthayatra.org/wp-content/uploads/2025/10/ttttd-1.jpg']}
S = requests.Session(); S.headers.update(UA)
def search(q):
    try:
        r = S.post('https://html.duckduckgo.com/html/', data={'q': q}, timeout=20)
        links = re.findall(r'class="result__a" href="([^"]+)"', r.text)
        out = []
        for l in links:
            m = re.search(r'uddg=([^&]+)', l); u = urllib.parse.unquote(m.group(1)) if m else l
            if 'youtube.com' in u or 'facebook.com' in u: continue
            out.append(u)
        return out[:7]
    except Exception as e: print('search fail', q, e); return []
def bing(q):
    try:
        h = S.get('https://www.bing.com/images/search', params={'q': q, 'form': 'HDRSC2', 'first': 1}, timeout=20).text
        u = re.findall(r'murl&quot;:&quot;(.*?)&quot;', h)
        print('bing', q, len(u), flush=True); return u[:12]
    except Exception as e: print('bing fail', e); return []
def page_imgs(u):
    try:
        h = S.get(u, timeout=20).text
    except Exception: return []
    imgs = re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', h)
    imgs += re.findall(r'<img[^>]+(?:data-src|src)=["\']([^"\']+\.(?:jpe?g|webp|png))', h, re.I)
    return [urllib.parse.urljoin(u, i) for i in imgs if not re.search(r'logo|icon|avatar|emoji|gravatar|ads|banner|blank|thumb-?\d', i, re.I)][:8]
def grab(u):
    try:
        r = S.get(u, timeout=25)
        im = Image.open(io.BytesIO(r.content)).convert('RGB')
        return u, im if min(im.size) >= 380 else None
    except Exception: return u, None
font = ImageFont.load_default()
for key in (sys.argv[1:] or list(Q)):
    os.makedirs(f'refs/{key}', exist_ok=True)
    cands = list(SEED.get(key, []))
    for q in Q[key]:
        cands += bing(q)
        for p in search(q): cands += page_imgs(p)
    seen, ims = set(), []
    with cf.ThreadPoolExecutor(8) as ex:
        for u, im in ex.map(grab, [c for c in dict.fromkeys(cands)][:60]):
            if im is None: continue
            sig = im.resize((8, 8)).tobytes()
            if sig in seen: continue
            seen.add(sig); ims.append((u, im))
    ims = ims[:12]; meta = []
    for i, (u, im) in enumerate(ims):
        im.save(f'refs/{key}/{i:02d}.jpg', quality=92); meta.append(u)
    json.dump(meta, open(f'refs/{key}/sources.json', 'w'), indent=1)
    W = 4; th = 300; tw = 300
    sheet = Image.new('RGB', (tw * W, (th + 20) * max(1, (len(ims) + W - 1) // W)), (20, 15, 10))
    for i, (u, im) in enumerate(ims):
        t = im.copy(); t.thumbnail((tw, th)); x, y = (i % W) * tw, (i // W) * (th + 20)
        sheet.paste(t, (x + (tw - t.width) // 2, y)); ImageDraw.Draw(sheet).text((x + 6, y + th + 4), f'{key} {i:02d}', fill=(255, 210, 90), font=font)
    sheet.save(f'refs/sheet_{key}.jpg', quality=80)
    print(key, len(ims), 'photos', flush=True)
print('FETCH_DONE')
