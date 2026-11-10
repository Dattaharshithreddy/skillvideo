"""Make an inspection grid from the shot clips (run with cgi-venv python).
Usage: python grid.py OUT.png  [frames per shot = 4]"""
import subprocess, sys, tempfile, os
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "grid.png"
NF = int(sys.argv[2]) if len(sys.argv) > 2 else 4
SHOTS = ["s01", "s02", "s03", "s04", "s05"]
tmp = tempfile.mkdtemp()
W, H = 232, 412
cv = Image.new("RGB", (W * NF, H * len(SHOTS)), (25, 25, 28))
for r, s in enumerate(SHOTS):
    clip = f"clips/{s}.mp4"
    probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v",
                            "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", clip],
                           capture_output=True, text=True)
    n = int(probe.stdout.strip() or 60)
    picks = [int((n - 8) * k / (NF - 1)) + 2 for k in range(NF)]
    sel = "+".join(f"eq(n\\,{p})" for p in picks)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", clip, "-vf",
                    f"select='{sel}',scale={W}:{H}", "-fps_mode", "drop", f"{tmp}/{s}_%d.png"], check=True)
    for c in range(NF):
        f = f"{tmp}/{s}_{c + 1}.png"
        if os.path.exists(f):
            cv.paste(Image.open(f), (c * W, r * H))
cv.save(OUT)
print("wrote", OUT)
