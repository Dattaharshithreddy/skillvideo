import bpy, sys, importlib, os, glob, math
def imp(pkg, key):
    for m in list(sys.modules):
        if m.endswith(pkg): return getattr(importlib.import_module(m), key)
    raise ImportError(pkg)
HumanService = imp('mpfb.services.humanservice', 'HumanService')
AssetService = imp('mpfb.services.assetservice', 'AssetService')
AnimationService = imp('mpfb.services.animationservice', 'AnimationService')
TargetService = imp('mpfb.services.targetservice', 'TargetService')
bpy.ops.wm.read_factory_settings(use_empty=True)
macro = TargetService.get_default_macro_info_dict()
macro.update({'gender': 1.0, 'age': 0.86, 'muscle': 0.42, 'weight': 0.62, 'height': 0.45, 'proportions': 0.5})
macro['race'] = {'asian': 0.25, 'caucasian': 0.42, 'african': 0.33}
human = HumanService.create_human(macro_detail_dict=macro)
human.name = 'raju_body'
def find(name, sub):
    p = AssetService.find_asset_absolute_path(name, asset_subdir=sub)
    print('ASSET', name, p); return p
skin = find('old_african_male.mhmat', 'skins')
if skin: HumanService.set_character_skin(skin, human, skin_type='MAKESKIN')
TD = os.path.join(os.path.dirname(sys.modules[[m for m in sys.modules if m.endswith('mpfb.services.targetservice')][0]].__file__), '..', 'data', 'targets', 'eyes')
for side in ('l', 'r'):
    for t_, w_ in (('eye-height1-decr', 0.6), ('eye-height2-decr', 0.35), ('eye-height3-decr', 0.15), ('eye-eyefold-down', 0.5), ('eye-bag-height-incr', 0.5)):
        p_ = os.path.join(TD, f'{side}-{t_}.target.gz')
        try: TargetService.load_target(human, p_, weight=w_); print('TGT', t_)
        except Exception as e: print('TGTFAIL', t_, e)
rig = HumanService.add_builtin_rig(human, 'default'); rig.name = 'raju_rig'
for sub, fn, typ in [('eyes', 'high-poly.mhclo', 'Eyes'), ('eyebrows', 'eyebrow006.mhclo', 'Eyebrows'), ('eyelashes', 'eyelashes02.mhclo', 'Eyelashes'),
                     ('teeth', 'teeth_base.mhclo', 'Teeth'), ('hair', 'short02.mhclo', 'Hair'),
                     ('clothes', 'namuhekam_male_polo_shirt.mhclo', 'Clothes'), ('clothes', 'toigo_wool_pants.mhclo', 'Clothes'), ('clothes', 'shoes02.mhclo', 'Clothes')]:
    p = find(fn, sub)
    if p:
        try: HumanService.add_mhclo_asset(p, human, asset_type=typ)
        except Exception as e: print('FAIL', fn, e)
pose = glob.glob(os.path.join(os.path.dirname(os.path.dirname(skin)), '..', 'poses', 'standing02', '*.bvh')) if skin else []
print('POSE', pose)
if pose:
    try: AnimationService.import_bvh_file_as_pose(rig, pose[0])
    except Exception as e: print('POSEFAIL', e)
print('BONES', [b.name for b in rig.pose.bones][:80])
import mathutils
for side, sgn in (('L', 1), ('R', -1)):
    pb = rig.pose.bones.get('upperarm01.' + side)
    if pb:
        Rb = pb.bone.matrix_local.to_3x3().to_quaternion()
        Rarm = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(42 * sgn))
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Rb.inverted() @ Rarm @ Rb
        print('ARM', side, tuple(round(x, 3) for x in pb.rotation_quaternion))
bpy.context.view_layer.update()
# grey hair / eyebrows
for o in bpy.data.objects:
    if o.type == 'MESH' and any(k in o.name.lower() for k in ('short02', 'eyebrow')):
        for m in o.data.materials:
            if m and m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED':
                        n.inputs['Base Color'].default_value = (0.55, 0.55, 0.55, 1)
                    if n.type == 'TEX_IMAGE' and n.image: n.image.colorspace_settings.name = 'sRGB'
print('OBJS', [(o.name, o.type) for o in bpy.data.objects])
bpy.ops.wm.save_as_mainfile(filepath='/opt/reel/raju.blend')
# quick look render
sc = bpy.context.scene
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
from mathutils import Vector
def shot(loc, tgt, lens, path):
    cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); cd.lens = lens
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)
for loc, e, col in (((1.5, -2.5, 2.4), 400, (1, .92, .85)), ((-2, 1.5, 2), 250, (.6, .7, 1)), ((-1, -3, 1.2), 120, (1, 1, 1))):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.data.energy = e; l.data.size = 1.5; l.data.color = col
    l.rotation_euler = (Vector((0, 0, 1.2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.cycles.use_denoising = True
pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
for d in pr.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'
sc.render.resolution_x, sc.render.resolution_y = 540, 960; sc.view_settings.view_transform = 'AgX'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 80
shot((0.6, -3.2, 1.2), (0, 0, 0.95), 40, '/opt/reel/raju_full.jpg')
shot((0.25, -0.9, 1.6), (0, 0, 1.55), 60, '/opt/reel/raju_face.jpg')
print('DONE')
