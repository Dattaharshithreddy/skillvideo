set -x
W=/opt/reel/sv/reels/porus; cd $W
python3 -u voice_swaram.py make > /opt/reel/pvoice.log 2>&1
F=/home/ubuntu/Swaram/output/narrations/$(python3 -c "import json;print(json.load(open('audio_mini/narrate.json'))['audio_url'].split('/')[-1])")
cp "$F" audio_mini/full.wav && python3 voice_swaram.py split audio_mini/full.wav >> /opt/reel/pvoice.log 2>&1
for f in audio_mini/l*.wav; do echo $f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f); done >> /opt/reel/pvoice.log
echo VOICE_ALLDONE >> /opt/reel/pvoice.log
