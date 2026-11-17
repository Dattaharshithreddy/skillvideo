# kitiki-style pipeline: Blender 4.2 + MPFB2 (CC0 MakeHuman assets) on the build server
set -x
B=/opt/r3d/blender/blender; A=/opt/r3d/assets; mkdir -p $A/packs; cd $A
until [ -f /opt/r3d/setup.log ]; do sleep 10; done
# MPFB2 extension zip from extensions.blender.org API
python3 - <<'PY'
import json, urllib.request
d = json.load(urllib.request.urlopen('https://extensions.blender.org/api/v1/extensions/?type=add-on&blender_version=4.2.3&platform=linux-x64'))
for e in d.get('data', []):
    if e.get('id') == 'mpfb':
        print('MPFB', e['version'], e['archive_url']); urllib.request.urlretrieve(e['archive_url'], '/opt/r3d/assets/mpfb.zip')
PY
ls -la mpfb.zip
# asset packs (CC0): scrape each pack page for its .zip link
python3 - <<'PY'
import re, urllib.request, os
base = 'https://static.makehumancommunity.org/assets/assetpacks/'
packs = ['makehuman_system_assets', 'skins01', 'skins02', 'hair01', 'hair02', 'shirts01', 'shirts02', 'pants01', 'pants02', 'dress01', 'skirts01', 'suits01', 'shoes01', 'makehuman_system_poses', 'poses01', 'poses02', 'system_clothes_materials01']
for p in packs:
    try:
        html = urllib.request.urlopen(base + p + '.html', timeout=30).read().decode('utf8', 'ignore')
        zs = sorted(set(re.findall(r'href="([^"]+\.zip)"', html)))
        for z in zs[:1]:
            url = z if z.startswith('http') else urllib.request.urljoin(base + p + '.html', z)
            out = '/opt/r3d/assets/packs/' + os.path.basename(url)
            if not os.path.exists(out): urllib.request.urlretrieve(url, out)
            print('PACK', p, os.path.getsize(out) // 1024, 'KB', url)
        if not zs: print('NOZIP', p)
    except Exception as e: print('ERR', p, e)
PY
$B -b --command extension install-file -r user_default -e $A/mpfb.zip > /tmp/mpfb_install.log 2>&1; tail -3 /tmp/mpfb_install.log
echo ASSETS_DONE
