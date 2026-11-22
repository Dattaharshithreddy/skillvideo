"""Blender + MPFB2: generate N realistic CC0 MakeHuman people (Indian devotees), Mixamo-named skeleton, export GLB each.
Run: blender -b -P make_people.py -- OUT N SEED"""
import bpy, sys, os, random, glob, json, traceback
argv = sys.argv[sys.argv.index('--') + 1:]; OUT, N, SEED = argv[0], int(argv[1]), int(argv[2]); os.makedirs(OUT, exist_ok=True)
import importlib
M = lambda n: importlib.import_module('bl_ext.user_default.mpfb.services.' + n)
HumanService = M('humanservice').HumanService; TargetService = M('targetservice').TargetService; LocationService = M('locationservice').LocationService
roots = [LocationService.get_user_data(), LocationService.get_mpfb_data()]
def assets(kind, ext):
    out = []
    for r in roots: out += glob.glob(os.path.join(r, kind, '**', '*.' + ext), recursive=True)
    return out
skins = assets('skins', 'mhmat'); clothes = assets('clothes', 'mhclo'); hair = assets('hair', 'mhclo'); brows = assets('eyebrows', 'mhclo'); eyes = assets('eyes', 'mhclo')
print('ASSETS skins', len(skins), 'clothes', len(clothes), 'hair', len(hair), flush=True)
print('CLOTHES', [os.path.basename(c) for c in clothes], flush=True); print('SKINS', [os.path.basename(s) for s in skins], flush=True)
pick = lambda lst, keys: [x for x in lst if any(k in os.path.basename(x).lower() for k in keys)]
rng = random.Random(SEED); manifest = []
for i in range(N):
    try:
        for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
        male = i % 2 == 0
        macro = TargetService.get_default_macro_info_dict()
        macro['gender'] = 1.0 if male else 0.0; macro['age'] = rng.uniform(0.45, 0.85); macro['muscle'] = rng.uniform(0.35, 0.6); macro['weight'] = rng.uniform(0.4, 0.75)
        macro['height'] = rng.uniform(0.35, 0.6) if male else rng.uniform(0.25, 0.5)
        if 'race' in macro: macro['race'] = {'african': rng.uniform(0.25, 0.45), 'asian': rng.uniform(0.2, 0.35), 'caucasian': rng.uniform(0.25, 0.45)}
        bm = HumanService.create_human(macro_detail_dict=macro)
        sk = pick(skins, ['middleage', 'young']) or skins
        dark = [s for s in sk if any(k in s.lower() for k in ['dark', 'african', 'brown', 'indian'])] or sk
        if dark: HumanService.set_character_skin(rng.choice(dark), bm)
        for lst in (eyes, brows): 
            if lst: HumanService.add_mhclo_asset(rng.choice(lst), bm, asset_type='Eyes' if lst is eyes else 'Eyebrows', subdiv_levels=0)
        hs = pick(hair, ['short', 'male'] if male else ['long', 'ponytail', 'bob', 'braid']) or hair
        if hs: HumanService.add_mhclo_asset(rng.choice(hs), bm, asset_type='Hair', subdiv_levels=0)
        if male: cs = pick(clothes, ['shirt', 'tshirt', 'pants', 'trousers', 'jeans', 'casualsuit'])
        else: cs = pick(clothes, ['dress', 'skirt', 'long', 'casualsuit', 'female'])
        cs = cs or clothes; chosen = []
        if cs:
            first = rng.choice(cs); chosen.append(first); HumanService.add_mhclo_asset(first, bm, asset_type='Clothes', subdiv_levels=0)
        HumanService.add_builtin_rig(bm, 'mixamo')
        bpy.ops.object.select_all(action='SELECT')
        p = os.path.join(OUT, f'person_{SEED}_{i:02d}_{"m" if male else "f"}.glb')
        bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True, export_apply=True, export_animations=False, export_skins=True)
        manifest.append({'file': os.path.basename(p), 'male': male, 'clothes': [os.path.basename(c) for c in chosen]}); print('OK', p, flush=True)
    except Exception:
        traceback.print_exc()
json.dump(manifest, open(os.path.join(OUT, f'manifest_{SEED}.json'), 'w'), indent=1)
