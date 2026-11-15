set -x
W=/opt/reel/sv/reels/follow-the-sugar; cd $W/mg; mkdir -p out
O=/opt/reel/share/e1376f7f43dd/sugar; mkdir -p $O
for C in Public Student; do npx remotion render src/index.ts $C out/$C.mp4 --concurrency=4 --log=error; done
for i in 0 1 2 3 4 5 6 7 8 9; do npx remotion still src/index.ts Slide out/student_slide_$((i+1)).png --props="{\"deck\":\"student\",\"idx\":$i}" --log=error; done
for i in 0 1 2 3 4; do npx remotion still src/index.ts Slide out/public_slide_$((i+1)).png --props="{\"deck\":\"public\",\"idx\":$i}" --log=error; done
npx remotion still src/index.ts HighYield out/high_yield.png --log=error
for C in Public Student; do
  ffmpeg -y -v error -i out/$C.mp4 -c:v libx264 -preset fast -crf 24 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart $O/sugar_${C,,}.mp4
  aws s3 cp out/$C.mp4 s3://claude-reels-730335199669/reels/follow-the-sugar-${C,,}.mp4 --region ap-south-1 --quiet
done
cp out/*.png $O/
(cd out && zip -q -j $O/sugar_carousels.zip *.png)
cd /opt/reel/share && (pgrep -f "http.server 8090" >/dev/null || nohup python3 -m http.server 8090 --bind 0.0.0.0 > /tmp/share.log 2>&1 &)
echo MG_DONE
