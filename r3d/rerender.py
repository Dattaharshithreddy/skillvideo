# Re-render all cameras in an open .blend with a new exposure: blender -b file.blend -P rerender.py  (env EV, PCT, SPP, PREFIX)
import bpy, os
s = bpy.context.scene; s.view_settings.exposure = float(os.environ.get('EV', -1.5)); s.cycles.samples = int(os.environ.get('SPP', 80))
s.render.resolution_percentage = int(os.environ.get('PCT', 50)); pre = os.environ.get('PREFIX', 'court')
cams = [o for o in s.objects if o.type == 'CAMERA']
names = os.environ.get('NAMES', 'wide,king,ministers').split(',')
dims = {'wide': (1080, 1920), 'king': (1080, 1920), 'ministers': (1920, 1080)}
for cam, n in zip(cams, names):
    s.camera = cam; s.render.resolution_x, s.render.resolution_y = dims.get(n, (1080, 1920)); s.render.filepath = f'/opt/r3d/out/{pre}_{n}.png'; bpy.ops.render.render(write_still=True)
print('RERENDER_DONE')
