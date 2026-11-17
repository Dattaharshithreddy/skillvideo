import bpy
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE_NEXT'
e = s.eevee
e.taa_render_samples = 48
e.use_shadows = True
e.use_raytracing = True
try:
    e.ray_tracing_options.resolution_scale = '2'; e.ray_tracing_method = 'SCREEN'
    e.use_fast_gi = True; e.fast_gi_resolution = '2'
    e.shadow_ray_count = 2; e.shadow_step_count = 8
except Exception as ex: print('eevee opt', ex)
s.render.use_motion_blur = False
s.render.use_persistent_data = True
s.render.use_overwrite = False
s.render.use_placeholder = False
