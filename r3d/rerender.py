# Re-render all cameras in an open .blend with a new exposure: blender -b file.blend -P rerender.py  (env EV, PCT, SPP, PREFIX)
import bpy, os
s = bpy.context.scene; s.view_settings.exposure = float(os.environ.get('EV', -1.5)); s.cycles.samples = int(os.environ.get('SPP', 80))
s.render.resolution_percentage = int(os.environ.get('PCT', 50)); pre = os.environ.get('PREFIX', 'court')
cams = [o for o in s.objects if o.type == 'CAMERA']
if not cams:
    TX, TY = 0.7, 9.3
    for name, loc, tgt, lens, fd in (('wide', (-1.2, -9.5, 1.5), (0.2, 7.5, 2.0), 22, 16), ('king', (0.3, 6.2, 1.55), (TX, TY, 1.75), 45, 3.2), ('ministers', (-0.2, 1.8, 1.45), (0.0, 6.4, 1.5), 32, 5.0)):
        bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
        c = cam.constraints.new('TRACK_TO'); c.target = e; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; cam.data.lens = lens
        cam.data.dof.use_dof = True; cam.data.dof.focus_distance = fd; cam.data.dof.aperture_fstop = 4; cams.append(cam)
names = os.environ.get('NAMES', 'wide,king,ministers').split(',')
dims = {'wide': (1080, 1920), 'king': (1080, 1920), 'ministers': (1920, 1080)}
for cam, n in zip(cams, names):
    s.camera = cam; s.render.resolution_x, s.render.resolution_y = dims.get(n, (1080, 1920)); s.render.filepath = f'/opt/r3d/out/{pre}_{n}.png'; bpy.ops.render.render(write_still=True)
print('RERENDER_DONE')
