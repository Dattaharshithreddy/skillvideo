"""Send each guest-house photo to the local Model Forge server and save the textured GLB to /out/mf."""
import base64, json, os, time, urllib.request
B = 'http://127.0.0.1:8000'
G = 'https://lh3.googleusercontent.com/'
SZ = '=w1600-h1200-k-no'
PICS = {   # best exterior per guest house, picked from Google Maps place photos (see refs/picks.py)
    'nandakam': 'grass-cs/AABkmLeuPB3P0zsTxEM7tcT4e_ZrxHWocqWaCYFaQtx1Q0c4AwmoWm9d6hqdwGcutwxxpgU-fXeMtK_QV_GwK7NkWhPtkAD71XGu_dJRpfNIwYHNjv4oCioCmqibi-YxKjUgLJlUuOE63pZJT70',
    'panchajanyam': 'grass-cs/AABkmLeWczRzfl1UixCbesMr0EXh5VbhAjSQikLWre7gCSPzz-r0KgOllkBdt6RpCeVIh65Enc_Ywy1fIZuykosL1jrBpPV8zSrHSCzx-mae_oPPVliArKNG0rAauUI4S23dPKNDBnZ8jQ',
    'kausthubham': 'grass-cs/AABkmLeGEyN2vgXdoXo7OG6otuY5eJAdMB4Z79rotYq7EKLCC9A7DHTjqeZ2tnSOgHRc-KT5Jx7tT7i1YrIsWAEHJqvM7UkfnmTfKcjvqlkU-BdS2EzR0lt-Wjiom4H3Ner_UcDX0tNHts_MvDoR',
    'vakulamatha': 'grass-cs/AABkmLfOumxy0qRu2qy1WuPJvOz68tHttaZU2FTcChJwVu8_CIlhGD3_EsKLQMizp4rstbIdKebCDaJUwGGH2x9znU7m7Fzd5pxy3cj8_2L2RaVfTyWiRyojS4ONICMGz5GOfakJ8b38',
    'pac5': 'grass-cs/AABkmLfA_VIxQAloOoe6RiCHnZ0v_C68I9ZmqOEMQQzg4qSo-iDbVtOaIwzlcsXiObR8ZqHEMfNvwCevR_tCpkpe-Cuc5WMClrNxBRuYoZy8G9q2erLJnXoxF1LjKRanAxgnsf5FCCp89Jlxh6U',
    'padmavathi': 'grass-cs/AABkmLfTogIDtR_j_KlXATJ551O844FHWrUht_8VuaQUPs3XnYWngnZYKNTT21xQM6mQqcLZXElnVKwOsV-rbFGTZ9P22jCHk6r9tan_meiTdIdD-byo7YM2LhC0-8r55MJ-SuOw6m5s',
    'sapthagiri': 'grass-cs/AABkmLf8jAA6nmw7Nwbz4A2x5asXeolKlpEZYLFliBJigFRFhGTzKY7mWk7X2TICoNa7G_Yv8I35Mo_ga4h15HR4xn10Ou4p7Ew08r7LHeSUV3FFC-bJ9-HcP2IhIPz4R5mdfCoLwjWecQ',
}
UA = {'User-Agent': 'Mozilla/5.0'}
H = {'Content-Type': 'application/json'}
tids = {}
for k, p in PICS.items():
    out = f'/out/mf/b_{k}_m.glb'
    if os.path.exists(out) and not os.environ.get('FORCE'): print('have', k); continue
    jpg = urllib.request.urlopen(urllib.request.Request(G + p + SZ, headers=UA), timeout=60).read()
    open(f'/out/mf/ref_{k}.jpg', 'wb').write(jpg)
    body = json.dumps({'mode': 'image', 'image': 'data:image/jpeg;base64,' + base64.b64encode(jpg).decode(),
                       'texture': True, 'quality': 'high', 'polycount': 60000, 'fresh': True}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(B + '/generate', data=body, headers=H), timeout=120))
    tids[k] = r['task_id']; print('queued', k, r, flush=True)
t0 = time.time()
while tids and time.time() - t0 < 3 * 3600:
    time.sleep(20)
    for k, t in list(tids.items()):
        s = json.load(urllib.request.urlopen(B + f'/status/{t}', timeout=60))
        if s['status'] == 'succeeded':
            open(f'/out/mf/b_{k}_m.glb', 'wb').write(urllib.request.urlopen(B + f'/models/{t}.glb').read())
            print('done', k, round(time.time() - t0), 's', flush=True); del tids[k]
        elif s['status'] == 'failed':
            print('failed', k, str(s.get('error'))[:300], flush=True); del tids[k]
    print('..', {k: 'waiting' for k in tids}, flush=True)
print('MF_DONE')
