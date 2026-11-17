export HOME=/root; UD=/root/.config/blender/4.2/extensions/.user/user_default/mpfb/data; mkdir -p $UD
until grep -q ASSETS_DONE /opt/r3d/assets.log; do sleep 5; done
for z in /opt/r3d/assets/packs/*.zip; do unzip -qo "$z" -d $UD; done; ls $UD
cd /opt/r3d && SPP=48 PCT=50 /usr/bin/time -f "TIME %e s" blender/blender -b -P sv/r3d/test_scene.py > /opt/r3d/test.log 2>&1
grep -E 'ASSETS|SKINS|HUMANS|RENDER_DONE|TIME|Error' /opt/r3d/test.log | head -20
aws s3 cp /opt/r3d/out/test.png s3://claude-reels-730335199669/r3d/test.png --quiet && echo UP
