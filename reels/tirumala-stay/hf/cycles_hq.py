"""Render settings for Hugging Face GPU jobs: Cycles on the GPU (OptiX/CUDA). HF containers expose the GPU for compute
only, so EEVEE cannot use it. Haze comes from a mist pass in the compositor (cheap) instead of a world volume (slow)."""
import bpy, os
s = bpy.context.scene
s.render.engine = 'CYCLES'
p = bpy.context.preferences.addons['cycles'].preferences
for dt in ('OPTIX', 'CUDA'):
    try:
        p.compute_device_type = dt; p.get_devices()
        for d in p.devices: d.use = d.type != 'CPU'
        print('CYCLES DEVICE', dt, [d.name for d in p.devices if d.use]); break
    except Exception as e: print('no', dt, e)
c = s.cycles
c.device = 'GPU'
c.samples = int(os.environ.get('SPP', '64')); c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03
c.use_denoising = True
try: c.denoiser = 'OPTIX'
except Exception: pass
c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 2; c.transmission_bounces = 4; c.volume_bounces = 0
c.caustics_reflective = False; c.caustics_refractive = False; c.blur_glossy = 1.0
c.use_auto_tile = True
s.render.use_persistent_data = True
s.render.use_motion_blur = False
s.render.use_overwrite = False; s.render.use_placeholder = False
s.render.image_settings.file_format = 'JPEG'; s.render.image_settings.quality = 93
# world volume (morning haze) -> unlink; recreate the haze with a mist pass instead
w = s.world
if w and w.use_nodes:
    out = w.node_tree.nodes.get('World Output')
    for l in list(out.inputs['Volume'].links): w.node_tree.links.remove(l)
    w.mist_settings.start = 0.35; w.mist_settings.depth = 3.2; w.mist_settings.falloff = 'QUADRATIC'
vl = s.view_layers[0]; vl.use_pass_mist = True
s.use_nodes = True
nt = s.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
rl = nt.nodes.new('CompositorNodeRLayers')
haze = nt.nodes.new('CompositorNodeRGB'); haze.outputs[0].default_value = (0.98, 0.88, 0.74, 1)
mr = nt.nodes.new('CompositorNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 1.0
mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = 0.55
mix = nt.nodes.new('CompositorNodeMixRGB'); mix.blend_type = 'MIX'
comp = nt.nodes.new('CompositorNodeComposite')
nt.links.new(rl.outputs['Mist'], mr.inputs['Value'])
nt.links.new(mr.outputs['Value'], mix.inputs['Fac'])
nt.links.new(rl.outputs['Image'], mix.inputs[1]); nt.links.new(haze.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs['Image'], comp.inputs['Image'])
print('CYCLES_HQ ready', c.samples, 'spp')
