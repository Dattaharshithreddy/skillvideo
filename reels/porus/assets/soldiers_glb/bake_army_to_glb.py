import bpy, os, sys, re
TEX=int(os.environ.get('TEX','2048'))
bpy.ops.wm.open_mainfile(filepath="/mnt/user-data/uploads/NOVA/assets/puru/army.blend")
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=4
s.render.bake.use_pass_direct=False; s.render.bake.use_pass_indirect=False; s.render.bake.use_pass_color=True
s.render.bake.margin=int(os.environ.get('BM','4'))
def skin_group(nt):
    # procedural skin: base tone with soft mottling, slightly redder ears/lips
    N=nt.nodes; L=nt.links
    tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=180; nz.inputs['Detail'].default_value=6
    nz2=N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=12
    ramp=N.new('ShaderNodeValToRGB'); e=ramp.color_ramp.elements
    e[0].position=0.35; e[0].color=(0.33,0.18,0.11,1); e[1].position=0.7; e[1].color=(0.47,0.28,0.18,1)
    mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs['Factor'].default_value=0.25
    L.new(tc.outputs['Object'],nz.inputs['Vector']); L.new(tc.outputs['Object'],nz2.inputs['Vector'])
    L.new(nz2.outputs['Fac'],ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'],mix.inputs['A']); L.new(nz.outputs['Color'],mix.inputs['B'])
    return mix.outputs['Result']
def prep(m):
    nt=m.node_tree; N=nt.nodes
    out=next((n for n in N if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
    src=out.inputs['Surface'].links[0].from_node if out and out.inputs['Surface'].links else None
    name=m.name.lower()
    if src is None or src.type!='BSDF_PRINCIPLED':
        b=N.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value=0.5
        nt.links.new(b.outputs[0],out.inputs['Surface']); src=b
        col=skin_group(nt)
        if 'lips' in name: b.inputs['Base Color'].default_value=(0.32,0.12,0.09,1)
        elif 'nail' in name: b.inputs['Base Color'].default_value=(0.55,0.38,0.30,1)
        else: nt.links.new(col,b.inputs['Base Color'])
    bc=src.inputs['Base Color']
    for n in N:
        if n.type=='TEX_IMAGE' and n.image and not n.image.has_data:
            # missing external texture: break its links and substitute a flat colour
            for o in n.outputs:
                for l in list(o.links):
                    sock=l.to_socket; nt.links.remove(l)
                    if sock.type=='RGBA':
                        c=(0.04,0.03,0.02,1) if 'eyebrow' in name else (0.85,0.85,0.83,1) if 'high-poly' in name else (0.30,0.18,0.09,1)
                        try: sock.default_value=c
                        except: pass
    if 'king_silk' in name and not bc.is_linked: bc.default_value=(0.36,0.04,0.06,1)
    return src
os.makedirs('/home/claude/conv/glb2',exist_ok=True)
only=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for c in bpy.data.collections:
    if not c.name.startswith('A_'): continue
    v=c.name[2:]
    if only and v not in only: continue
    ob=c.all_objects[0]
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.hide_set(False); ob.hide_render=False; ob.select_set(True); bpy.context.view_layer.objects.active=ob
    me=ob.data
    uv=me.uv_layers.new(name='bake'); me.uv_layers.active=uv
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=float(os.environ.get('IM','0.003')))
    bpy.ops.object.mode_set(mode='OBJECT')
    img=bpy.data.images.new(v+'_albedo',TEX,TEX); img.generated_color=(0.6,0.55,0.5,1); img.colorspace_settings.name='sRGB'
    mats=[sl.material for sl in ob.material_slots if sl.material]
    nodes={}
    meta={}
    for m in set(mats):
        b=prep(m)
        mi=b.inputs['Metallic']; ro=b.inputs['Roughness']
        nm=m.name.lower(); metal=any(k in nm for k in ('gold','bronze','steel','brass','silver','iron','metal'))
        meta[m]=(1.0 if metal or (not mi.is_linked and mi.default_value>0.5) else 0.0,
                 (0.35 if metal else 0.6) if ro.is_linked else ro.default_value)
        for l in list(mi.links): m.node_tree.links.remove(l)
        mi.default_value=0.0
        t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=img; m.node_tree.nodes.active=t; nodes[m]=(t,b)
    bpy.ops.object.bake(type='DIFFUSE', uv_layer='bake')
    path=f'/home/claude/conv/glb2/{v}_albedo.png'; img.filepath_raw=path; img.file_format='PNG'; img.save()
    # rewire: baked texture -> base color through the bake UV
    for m,(t,b) in nodes.items():
        nt=m.node_tree; uvn=nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map='bake'
        nt.links.new(uvn.outputs['UV'],t.inputs['Vector'])
        for l in list(b.inputs['Base Color'].links): nt.links.remove(l)
        nt.links.new(t.outputs['Color'],b.inputs['Base Color'])
        for k in ('Roughness','Metallic'):
            for l in list(b.inputs[k].links): nt.links.remove(l)
        b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value = meta[m]
        for k in ('Normal',):
            for l in list(b.inputs[k].links): nt.links.remove(l)
    # keep only the bake UV for export
    for u in [u for u in me.uv_layers if u.name!='bake']: me.uv_layers.remove(u)
    out=f'/home/claude/conv/glb2/{v}.glb'
    bpy.ops.export_scene.gltf(filepath=out,use_selection=True,export_format='GLB',export_apply=True,export_image_format='JPEG',export_jpeg_quality=88)
    print('wrote',out,os.path.getsize(out),flush=True)
