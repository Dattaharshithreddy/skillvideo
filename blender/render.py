"""Render one shot script to an MP4 clip on the GPU.

blender -b --factory-startup -P render.py -- SHOT.py OUT.mp4 SECONDS [--quality preview|final] [--still SECONDS]

SHOT.py must define:  build(seconds)  -> creates the whole scene + animation using czlib (cz.reset() is done for you).
--still renders a single PNG (OUT path with .png) at that time, for look checks before the full render.
"""
import importlib.util, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import czlib as cz  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
shot_py, out, secs = argv[0], argv[1], float(argv[2])
quality = argv[argv.index("--quality") + 1] if "--quality" in argv else "final"
still = float(argv[argv.index("--still") + 1]) if "--still" in argv else None
if "--fps" in argv:
    cz.FPS = int(argv[argv.index("--fps") + 1])

cz.reset()
device = cz.gpu_setup()
cz.render_preset(quality)
cz.set_frames(secs)
spec = importlib.util.spec_from_file_location("shot", shot_py)
mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(shot_py)))
spec.loader.exec_module(mod)
mod.build(secs)
S = cz.S
print(f"[render] {os.path.basename(shot_py)} device={device} quality={quality} frames={S.frame_end}", flush=True)

if still is not None:
    S.frame_set(max(1, int(round(still * cz.FPS)) + 1))
    S.render.filepath = out
    bpy.ops.render.render(write_still=True)
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="cz_")
S.render.filepath = os.path.join(tmp, "f_")
t0 = time.time()
bpy.ops.render.render(animation=True)
print(f"[render] {S.frame_end} frames in {time.time() - t0:.0f}s", flush=True)

post = os.environ.get("CZ_POST", "noise=alls=3:allf=t+u,vignette=angle=PI/7")  # subtle film grain + vignette
vf = f"scale=1080:1920:flags=lanczos,{post},format=yuv420p" if post else "scale=1080:1920:flags=lanczos,format=yuv420p"
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(cz.FPS), "-start_number", "1",
                "-i", os.path.join(tmp, "f_%04d.png"), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
                "-crf", "16", out], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f"[render] wrote {out}", flush=True)
