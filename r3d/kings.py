# Royal outfit sheet: 3 researched king looks + queen + mantri, standing, front-lit.
import bpy, sys, os, math, random, traceback
sys.path.insert(0, os.path.dirname(__file__))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
from kitlib import *
random.seed(5)
SHIRT = G('toigo_fisherman_sweater') or G('janexx_old_female_sweater'); PANTS = G('elvs_disco_pants_skinny') or G('punkduck_female_tight_jeans')
WHITE_ROSE = brocade('kabayi_white', (0.93, 0.91, 0.85), scale=22, dot=0.12)           # Vijayanagara: white silk, gold roses
RED_JAMA = brocade('jama_red', (0.3, 0.015, 0.025), scale=26, dot=0.12)               # court: red brocade choga
GREEN_PATKA = cloth('patka_green2', (0.03, 0.2, 0.09), bw=0.12, sheen=0.4)
GOLD_PATKA = cloth('patka_gold2', (0.75, 0.55, 0.22), border=(0.5, 0.03, 0.05), bw=0.12, sheen=0.4, metal_border=False)
CAP = brocade('kullayi_brocade', (0.88, 0.8, 0.6), motif=(1.0, 0.75, 0.35), scale=40, dot=0.12, hem=0)
PAGDI_SAFF = turban_mat('pagdi_saffron2', (0.85, 0.28, 0.02), band=(0.95, 0.55, 0.08)); PAGDI_W = cloth('pagdi_white', (0.95, 0.93, 0.88), bw=0, sheen=0.3)
CHURI = cloth('churidar_white', (0.92, 0.9, 0.85), bw=0)
SILK = cloth('king_silk', (0.16, 0.004, 0.012), bw=0.08); KUTT = cloth('king_utt', (0.95, 0.72, 0.3), mode='edge', sheen=0.4); JN = cloth('janeu', (0.95, 0.94, 0.9), bw=0, metal_border=False)
QS = brocade('queen_pattu', (0.25, 0.01, 0.06), scale=30, dot=0.1, hem=0.1); QP = cloth('queen_pallu', (0.25, 0.01, 0.06), mode='edge', bw=0.06, sheen=0.3); QB = brocade('queen_blouse', (0.6, 0.38, 0.05), scale=50, dot=0.1, hem=0)
MW = cloth('mantri_dhoti', (0.92, 0.9, 0.84), bw=0.05); MU = cloth('mantri_utt', (0.9, 0.86, 0.72), mode='edge'); MT = turban_mat('mantri_turban2', (0.95, 0.93, 0.86), band=(0.98, 0.96, 0.9), bump=0.6)
cast = []
def look(name, fn):
    try: fn(); cast.append(name); print('LOOK', name, 'ok')
    except Exception: traceback.print_exc(limit=4); print('LOOK', name, 'FAIL')
def vijayanagara():   # Krishnadevaraya style
    bm, rig, P = person(-2.6, 0, 0, True, [('ind_jama_long', WHITE_ROSE), ('ind_patka', GOLD_PATKA)], muscle=0.6, weight=0.6, hair=False)
    add(SHIRT, bm, 'Clothes', WHITE_ROSE); add(G('ind_uttariya_diag'), bm, 'Clothes', brocade('flap_white', (0.95, 0.93, 0.87), scale=22, dot=0.12, hem=0)); bpy.context.view_layer.update(); P = body_pts(bm)
    kullayi(P, rig, CAP); pearl_ropes(bm, rig, 2); earrings(P, rig); moustache(bm, rig, P); tilak(P, rig)
    w = bone_pos(rig, 'wrist.L'); attach([merge(kit('sword_khanda', (w.x, w.y - 0.03, w.z - 0.98), 0.95))], rig, 'wrist.L')
def court_king():     # red brocade jama, patka, churidar, royal pagdi with sarpech + kalgi, pearls
    bm, rig, P = person(-1.3, 0, 0, True, [('ind_jama_skirt', RED_JAMA), ('ind_patka', GREEN_PATKA)], muscle=0.65, hair=False)
    add(SHIRT, bm, 'Clothes', RED_JAMA); add(G('ind_uttariya_diag'), bm, 'Clothes', brocade('flap_red', (0.34, 0.02, 0.03), scale=26, dot=0.12, hem=0)); add(PANTS, bm, 'Clothes', CHURI); bpy.context.view_layer.update(); P = body_pts(bm)
    turban2(P, rig, PAGDI_SAFF, 'pagdi'); pearl_ropes(bm, rig, 4); earrings(P, rig); moustache(bm, rig, P, 0.009); armlets(rig)
def ancient_king():   # Chola/ancient: bare chest, silk dhoti, uttariya, kireetam
    bm, rig, P = person(0.0, 0, 0, True, [('ind_kingdhoti', SILK), ('ind_uttariya_diag', KUTT), ('ind_janeu', JN)], muscle=0.75, hair=False)
    top, r, hd = head_info(P); attach([merge(kit('crown_kireetam', (top.x, top.y, top.z - 0.06 - 1.3 * 0.9), 0.9))], rig, 'head')
    necklace(bm, rig); armlets(rig); earrings(P, rig); moustache(bm, rig, P); tilak(P, rig)
def queen():
    bm, rig, P = person(1.3, 0, 0, False, [('ind_sareeskirt', QS), ('toigo_camisole_top', QB), ('ind_pallu', QP)])
    top, r, hd = head_info(P); attach([merge(kit('crown_kireetam', (top.x, top.y, top.z - 0.045 - 1.3 * 0.42), 0.42))], rig, 'head')
    necklace(bm, rig, layers=((0.06, 0.075, 30), (0.12, 0.09, 40), (0.18, 0.1, 48))); armlets(rig); earrings(P, rig); tilak(P, rig)
def mantri():
    bm, rig, P = person(2.6, 0, 0, True, [('ind_dhoti', MW), ('ind_uttariya_diag', MU), ('ind_janeu', JN)], age=0.75, weight=0.6, hair=False)
    turban2(P, rig, MT, 'mantri', jewel=True, kalgi=False, pearls=False); moustache(bm, rig, P, 0.006); tilak(P, rig, (0.9, 0.9, 0.85))
for n, f in (('vijayanagara', vijayanagara), ('court_king', court_king), ('ancient_king', ancient_king), ('queen', queen), ('mantri', mantri)): look(n, f)
print('CAST', cast)
# backdrop: warm palace wall + floor
bpy.ops.mesh.primitive_plane_add(size=40); bpy.context.object.data.materials.append(solid('floor_s', (0.5, 0.42, 0.34), 0.3, tex='ground', tscale=0.3))
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 3.5, 5), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(solid('wall_s', (0.85, 0.72, 0.58), 0.8, tex='plaster', tscale=0.5))
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.45, 0.4, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.4
for loc, e, sz, col in (((-2.5, -5, 4), 1400, 5, (1, 0.9, 0.78)), ((3.5, -3, 2.5), 500, 3, (0.85, 0.9, 1.0)), ((0, 2, 3.5), 600, 4, (1, 0.8, 0.6))):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = e; L.data.size = sz; L.data.color = col
    k = L.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=(0, 0, 1.2)); k.target = bpy.context.object; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 96)); s.cycles.use_denoising = True
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = float(os.environ.get('EV', -0.5))
shots = [('sheet', (0, -7.6, 1.1), (0, 0, 0.95), 35, 1920, 1080)] + [(f'close_{n}', (x, -2.2, 1.55), (x, 0, 1.4), 50, 1080, 1920) for n, x in (('vijayanagara', -2.6), ('court_king', -1.3), ('queen', 1.3))]
for name, loc, tgt, lens, rx, ry in shots:
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
    c = cam.constraints.new('TRACK_TO'); c.target = e; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; cam.data.lens = lens
    s.camera = cam; s.render.resolution_x, s.render.resolution_y = rx, ry; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
    s.render.filepath = f'/opt/r3d/out/kings_{name}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/kings.blend'); print('KINGS_DONE')
