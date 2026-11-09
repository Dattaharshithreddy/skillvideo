"""blender -b --factory-startup -P gpu_test.py : confirms Cycles sees the GPU and times one frame."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import czlib as cz

cz.reset()
dev = cz.gpu_setup()
print("CYCLES device:", dev)
S = cz.render_preset(quality="preview")
cz.world_studio((0.62, 0.68, 0.95), top=(0.85, 0.88, 1.0))
cz.studio_rig()
cz.sphere(1.0, (0, 0, 0), cz.mat_pbr("red", (0.8, 0.05, 0.05), rough=0.2, coat=1))
cam = cz.camera(50)
cz.aim(cam, (0, -6, 0.5), (0, 0, 0))
S.render.filepath = "/tmp/gpu_test.png"
t = time.time()
bpy.ops.render.render(write_still=True)
print(f"render time {time.time() - t:.2f}s at {S.render.resolution_x}x{S.render.resolution_y}")
