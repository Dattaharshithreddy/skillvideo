# kitiki-style test: realistic MPFB humans (Indian skin tones, white dhoti, turban) + procedural temple, bright daylight, Cycles CPU
import bpy, glob, os, random, math, sys, traceback
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.locationservice import LocationService
UD = LocationService.get_user_data(); SD = LocationService.get_mpfb_data()
def find(kind, pat):
    r = []
    for root in (UD, SD): r += glob.glob(os.path.join(root, kind, '**', pat), recursive=True)
    return sorted(r)
skins = [s for s in find('skins', '*.mhmat') if any(k in s.lower() for k in ('middleage', 'young', 'brown', 'african', 'asian', 'indian', 'latin'))] or find('skins', '*.mhmat')
eyes = find('eyes', '*.mhclo'); brows = find('eyebrows', '*.mhclo'); hair = find('hair', '*.mhclo')
print('ASSETS', len(skins), len(eyes), len(brows), len(hair)); print('SKINS', [os.path.basename(s) for s in skins][:12])
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
random.seed(4)
def mat(name, col, rough=0.6, metal=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
WHITE = mat('cotton', (0.85, 0.83, 0.78), 0.9); SAFF = mat('saffron', (0.9, 0.38, 0.05), 0.8); STONE = mat('stone', (0.62, 0.56, 0.47), 0.85)
GOLD = mat('gold', (1.0, 0.72, 0.25), 0.25, 1.0); GROUND = mat('ground', (0.55, 0.48, 0.38), 0.95); TURB = mat('turban', (0.75, 0.1, 0.08), 0.8)
def human(x, y, rot, i):
    macro = {'gender': random.choice([0.0, 1.0]) if i % 3 else 1.0, 'age': random.uniform(0.4, 0.6), 'muscle': random.uniform(0.45, 0.65),
             'weight': random.uniform(0.4, 0.6), 'height': random.uniform(0.4, 0.6), 'proportions': 0.6, 'cupsize': 0.5, 'firmness': 0.5,
             'race': {'african': 0.25, 'asian': 0.35, 'caucasian': 0.4}}
    try:
        bm = HumanService.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    except TypeError:
        bm = HumanService.create_human(); 
    for fn, args in ((HumanService.set_character_skin, (random.choice(skins), bm)),):
        try: fn(*args, skin_type='ENHANCED_SSS')
        except Exception: traceback.print_exc(limit=1)
    for lst, typ in ((eyes, 'Eyes'), (brows, 'Eyebrows'), (hair, 'Hair')):
        if lst and not (typ == 'Hair' and macro['gender'] > 0.5):
            try: HumanService.add_mhclo_asset(lst[0] if typ != 'Hair' else random.choice(lst), bm, asset_type=typ, subdiv_levels=0, material_type='MAKESKIN')
            except Exception: traceback.print_exc(limit=1)
    bm.location = (x, y, 0); bm.rotation_euler[2] = rot
    h = bm.dimensions.z
    # dhoti / saree drape: tapered cylinder hip->ankle; turban for men
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.26, radius2=0.19, depth=h * 0.5, location=(x, y, h * 0.27))
    d = bpy.context.object; d.data.materials.append(WHITE if macro['gender'] > 0.5 else SAFF)
    bpy.ops.object.shade_smooth()
    if macro['gender'] > 0.5:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.05, location=(x, y, h * 0.96))
        t = bpy.context.object; t.scale = (1, 1.15, 1.4); t.data.materials.append(TURB if i % 2 else SAFF)
    return bm
# ground + temple: stepped gopuram tiers, gold kalasams, prakaram wall
bpy.ops.mesh.primitive_plane_add(size=200); bpy.context.object.data.materials.append(GROUND)
GX, GY = 0, 22
for k in range(9):
    w = 14 - k * 1.25; hgt = 2.2
    bpy.ops.mesh.primitive_cube_add(location=(GX, GY, 1.1 + k * hgt)); c = bpy.context.object
    c.scale = (w / 2, (8 - k * 0.6) / 2, hgt / 2); c.data.materials.append(STONE)
    bpy.ops.object.modifier_add(type='BEVEL'); c.modifiers[-1].width = 0.12
    for j in range(int(w)):  # niche pillars per tier
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=hgt * 0.8, location=(GX - w / 2 + 0.5 + j, GY - (8 - k * 0.6) / 2 - 0.1, 1.1 + k * hgt))
        bpy.context.object.data.materials.append(STONE)
bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=1.5, location=(GX, GY, 9 * 2.2 + 0.75)); bpy.context.object.data.materials.append(STONE)
for j in range(-2, 3):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(GX + j * 1.1, GY, 9 * 2.2 + 1.9)); bpy.context.object.data.materials.append(GOLD)
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, depth=0.8, location=(GX + j * 1.1, GY, 9 * 2.2 + 2.5)); bpy.context.object.data.materials.append(GOLD)
bpy.ops.mesh.primitive_cube_add(location=(GX, GY - 0.2, 2.5)); door = bpy.context.object; door.scale = (1.6, 4.3, 2.5)
dm = mat('dark', (0.05, 0.04, 0.03)); door.data.materials.append(dm)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(location=(GX + sx * 25, GY, 2.5)); w = bpy.context.object; w.scale = (18, 0.8, 2.5); w.data.materials.append(STONE)
# crowd walking toward the gopuram
n = 0
for r in range(4):
    for cidx in range(6):
        x = -6 + cidx * 2.4 + random.uniform(-0.6, 0.6); y = -2 + r * 3.2 + random.uniform(-0.8, 0.8)
        try: human(x, y, math.pi + random.uniform(-0.4, 0.4), n); n += 1
        except Exception: traceback.print_exc(limit=2)
print('HUMANS', n)
# light: bright sky + sun, filmic
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(200)
w.node_tree.links.new(sky.outputs[0], w.node_tree.nodes['Background'].inputs[0]); w.node_tree.nodes['Background'].inputs[1].default_value = 0.35
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(52), 0, math.radians(200))); bpy.context.object.data.energy = 4; bpy.context.object.data.angle = math.radians(3)
bpy.ops.object.camera_add(location=(1.5, -13, 3.2), rotation=(math.radians(84), 0, math.radians(4))); cam = bpy.context.object
cam.data.lens = 28; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 11; cam.data.dof.aperture_fstop = 5.6
s = bpy.context.scene; s.camera = cam; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 48))
s.cycles.use_denoising = True; s.render.resolution_x, s.render.resolution_y = 1080, 1920; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
s.render.filepath = '/opt/r3d/out/test.png'; os.makedirs('/opt/r3d/out', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/test.blend')
bpy.ops.render.render(write_still=True); print('RENDER_DONE')
