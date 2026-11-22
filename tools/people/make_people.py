"""Blender + MPFB2: generate N realistic CC0 MakeHuman people (Indian devotees), Mixamo-named skeleton, export GLB each.
Run: blender -b -P make_people.py -- OUT N SEED"""
import bpy, sys, os, random, glob, json, traceback
argv = sys.argv[sys.argv.index('--') + 1:]; OUT, N, SEED = argv[0], int(argv[1]), int(argv[2]); os.makedirs(OUT, exist_ok=True)
import importlib
M = lambda n: importlib.import_module('bl_ext.user_default.mpfb.services.' + n)
HumanService = M('humanservice').HumanService; TargetService = M('targetservice').TargetService; LocationService = M('locationservice').LocationService
ClothesService = M('clothesservice').ClothesService; Mhclo = importlib.import_module('bl_ext.user_default.mpfb.entities.clothes.mhclo').Mhclo
roots = [LocationService.get_user_data(), LocationService.get_mpfb_data()]
def assets(kind, ext):
    out = []
    for r in roots: out += glob.glob(os.path.join(r, kind, '**', '*.' + ext), recursive=True)
    return out
skins = assets('skins', 'mhmat'); clothes = assets('clothes', 'mhclo'); hair = assets('hair', 'mhclo'); brows = assets('eyebrows', 'mhclo'); eyes = assets('eyes', 'mhclo')
print('ASSETS skins', len(skins), 'clothes', len(clothes), 'hair', len(hair), flush=True)
print('CLOTHES', [os.path.basename(c) for c in clothes], flush=True); print('SKINS', [os.path.basename(s) for s in skins], flush=True); print('HAIR', [os.path.basename(h) for h in hair], flush=True)
pick = lambda lst, keys: [x for x in lst if any(k in os.path.basename(x).lower() for k in keys)]
rng = random.Random(SEED); manifest = []
CAST = json.load(open(argv[3])) if len(argv) > 3 and os.path.exists(argv[3]) and os.path.getsize(argv[3]) > 2 else None   # optional named characters
if CAST: N = len(CAST)
for i in range(N):
    try:
        for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
        C = CAST[i] if CAST else {}
        male = C.get('male', i % 3 != 2)   # 2 men : 1 woman (most women come from the saree models)
        macro = TargetService.get_default_macro_info_dict()
        macro['gender'] = 1.0 if male else 0.0; macro['age'] = C.get('age', rng.uniform(0.45, 0.85)); macro['muscle'] = C.get('muscle', rng.uniform(0.35, 0.6)); macro['weight'] = C.get('weight', rng.uniform(0.4, 0.75))
        macro['height'] = C.get('height', rng.uniform(0.35, 0.6) if male else rng.uniform(0.25, 0.5))
        if 'race' in macro: macro['race'] = {'african': rng.uniform(0.25, 0.45), 'asian': rng.uniform(0.2, 0.35), 'caucasian': rng.uniform(0.25, 0.45)}
        bm = HumanService.create_human(macro_detail_dict=macro); added = []
        sk = pick(skins, ['middleage', 'young']) or skins
        dark = [s for s in sk if any(k in s.lower() for k in ['dark', 'african', 'brown', 'indian'])] or sk
        if dark: HumanService.set_character_skin(rng.choice(dark), bm)
        for lst in (eyes, brows): 
            if lst: a = rng.choice(lst); added.append((a, HumanService.add_mhclo_asset(a, bm, asset_type='Eyes' if lst is eyes else 'Eyebrows', subdiv_levels=0)))
        hs = pick(hair, C['hair']) if C.get('hair') else (pick(hair, ['short', 'male'] if male else ['long', 'ponytail', 'bob', 'braid']) or hair)
        if hs: a = rng.choice(hs); added.append((a, HumanService.add_mhclo_asset(a, bm, asset_type='Hair', subdiv_levels=0)))
        base = [c for c in clothes if 'shoes' not in c and 'fedora' not in c and 'sport' not in c]
        if male: cs = [c for c in base if os.path.basename(c).startswith('male_') and ('casualsuit' in c or 'worksuit' in c)]
        else: cs = [c for c in base if os.path.basename(c).startswith('female_')]
        cs = cs or clothes; chosen = []
        if C.get('clothes') is False: cs = []
        elif C.get('clothes'): cs = pick(clothes, C['clothes']) or cs
        if cs:
            first = rng.choice(cs); chosen.append(first); added.append((first, HumanService.add_mhclo_asset(first, bm, asset_type='Clothes', subdiv_levels=0)))
        rig = HumanService.add_builtin_rig(bm, 'mixamo')
        for path, obj in added:   # skin every proxy (clothes, hair, brows, eyes) to the rig so they follow poses
            mh = Mhclo(); mh.load(path); ClothesService.set_up_rigging(bm, obj, rig, mh, interpolate_weights=True, import_subrig=False, import_weights=True)
        bpy.ops.object.select_all(action='SELECT')
        p = os.path.join(OUT, f'{C["name"]}.glb' if C.get('name') else f'person_{SEED}_{i:02d}_{"m" if male else "f"}.glb')
        bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True, export_apply=True, export_animations=False, export_skins=True)
        manifest.append({'file': os.path.basename(p), 'male': male, 'clothes': [os.path.basename(c) for c in chosen]}); print('OK', p, flush=True)
    except Exception:
        traceback.print_exc()
json.dump(manifest, open(os.path.join(OUT, f'manifest_{SEED}.json'), 'w'), indent=1)
