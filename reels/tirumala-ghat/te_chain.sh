W=/opt/reel/sv/reels/tirumala-ghat; cd $W; python3 plan.py > /dev/null
python3 -u voice_swaram.py make > /opt/reel/swmake.log 2>&1
F=/home/ubuntu/Swaram/output/narrations/$(python3 -c "import json;print(json.load(open('audio_te/narrate.json'))['audio_url'].split('/')[-1])")
cp "$F" audio_te/full.wav && python3 voice_swaram.py split audio_te/full.wav >> /opt/reel/swmake.log 2>&1
aws s3 cp audio_te/full.wav s3://swaram-media-730335199669/narration/tirumala-te-datta-v2.wav --region ap-south-1 --quiet && echo S3_OK >> /opt/reel/swmake.log
ffmpeg -y -v error -f lavfi -i color=c=black:s=720x1280:r=10 -i audio_te/full.wav -shortest -c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart /opt/reel/share/e1376f7f43dd/tirumala_telugu_voice_v2.mp4
echo VOICE2_DONE >> /opt/reel/swmake.log
bash close_test.sh > /opt/reel/ctest_out.txt 2>&1
