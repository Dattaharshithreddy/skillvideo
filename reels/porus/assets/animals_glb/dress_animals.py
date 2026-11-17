import bpy, bmesh, math, sys, os, mathutils
from mathutils import Vector
SRC='/mnt/user-data/uploads/NOVA/assets/puru/cand/'
OUT='/home/claude/cand/out/'; os.makedirs(OUT,exist_ok=True)
def mat(name,col,rough=0.6,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; return m
def load(name, rotz, height):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC+name+'.glb')
    ms=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in bpy.context.scene.objects: o.select_set(o.type=='MESH')
    bpy.context.view_layer.objects.active=ms[0]
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for o in [o for o in bpy.context.scene.objects if o.type!='MESH']: bpy.data.objects.remove(o)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for o in ms:
        o.data.transform(mathutils.Matrix.Rotation(rotz,4,'Z'))
    vs=[v.co for o in ms for v in o.data.vertices]
    mn=Vector([min(v[i] for v in vs) for i in range(3)]); mx=Vector([max(v[i] for v in vs) for i in range(3)])
    s=height/(mx.z-mn.z); off=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
    for o in ms: o.data.transform(mathutils.Matrix.Scale(s,4)@mathutils.Matrix.Translation(-off))
    vs=[v.co for o in ms for v in o.data.vertices]
    mn=Vector([min(v[i] for v in vs) for i in range(3)]); mx=Vector([max(v[i] for v in vs) for i in range(3)])
    return ms,mn,mx
def cloth(src, region, mats, thick=0.035, push=0.04, border_rings=2, name='cloth'):
    """Duplicate faces of src where region(centroid, normal) is true, push them out, solidify; outer rings get mats[1]."""
    bm=bmesh.new(); bm.from_mesh(src.data)
    keep=[f for f in bm.faces if region(f.calc_center_median(), f.normal)]
    sel=set(keep)
    for f in [f for f in bm.faces if f not in sel]: bm.faces.remove(f)
    for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
    # border band
    ring=set(f for f in bm.faces if any(len(e.link_faces)<2 for e in f.edges))
    band=set(ring)
    for _ in range(border_rings-1):
        band|=set(g for f in list(band) for v in f.verts for g in v.link_faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me)
    me.materials.clear()
    for m in mats: me.materials.append(m)
    for i,f in enumerate(bm.faces): me.polygons[i].material_index=1 if f in band else 0
    bm.free()
    for v in me.vertices: v.co+=v.normal*push
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o)
    sd=o.modifiers.new('s','SOLIDIFY'); sd.thickness=thick; sd.offset=1
    sm=o.modifiers.new('sub','SUBSURF'); sm.levels=1; sm.render_levels=1
    return o

def drape(target, y0, y1, zc, R, amin, amax, mats, nu=48, nv=48, push=0.045, thick=0.03, border=2, name='drape', xc=0.0, mode='PROJECT'):
    """Rectangular cloth: a cylinder patch around an axis along Y, shrink-projected inward onto target."""
    bm=bmesh.new(); rows=[]
    for i in range(nu+1):
        y=y0+(y1-y0)*i/nu; row=[]
        for j in range(nv+1):
            a=math.radians(amin+(amax-amin)*j/nv)
            row.append(bm.verts.new((xc+R*math.sin(a), y, zc+R*math.cos(a))))
        rows.append(row)
    for i in range(nu):
        for j in range(nv):
            f=bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
            f.material_index=1 if (i<border or i>=nu-border or j<border or j>=nv-border) else 0
    bm.normal_update()
    for f in bm.faces:
        c=f.calc_center_median(); out=Vector((c.x-xc,0,c.z-zc))
        if f.normal.dot(out)<0: f.normal_flip()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o)
    sw=o.modifiers.new('sw','SHRINKWRAP'); sw.target=target; sw.wrap_method=mode; sw.offset=push
    if mode=='PROJECT': sw.use_negative_direction=True; sw.use_positive_direction=False
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='sw')
    sd=o.modifiers.new('s','SOLIDIFY'); sd.thickness=thick; sd.offset=1
    sm=o.modifiers.new('sub','SUBSURF'); sm.levels=1; sm.render_levels=1
    o.data.shade_smooth() if hasattr(o.data,'shade_smooth') else None
    return o

def export(path):
    for o in bpy.context.scene.objects: o.select_set(o.type=='MESH')
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True,export_image_format='JPEG',export_jpeg_quality=90)
    print('wrote',path,os.path.getsize(path))
RED=lambda: mat('cloth_red',(0.42,0.03,0.03),0.75)
MAROON=lambda: mat('cloth_maroon',(0.26,0.02,0.05),0.7)
GOLD=lambda: mat('gold',(0.95,0.68,0.25),0.28,1.0)
BRONZE=lambda: mat('bronze',(0.7,0.42,0.2),0.35,1.0)

def elephant(royal):
    ms,mn,mx=load('ir_elephant_nature',0.0,3.1)
    el=ms[0]; L=mx.y-mn.y; H=mx.z
    yh=mn.y  # head end (-Y)
    def fr(y): return (y-yh)/L
    # blanket over back and flanks
    drape(el, yh+0.55*L, yh+0.87*L, 2.0, 2.0, -104, 104, [MAROON() if royal else RED(), GOLD()], name='caparison')
    if royal:
        # back top for howdah
        back=[v.co for v in el.data.vertices if 0.62<fr(v.co.y)<0.78 and abs(v.co.x)<0.3]
        zt=max(v.z for v in back)-0.12; yc=sum(v.y for v in back)/len(back)
        g=GOLD(); red=mat('cushion',(0.55,0.05,0.05),0.8)
        def box(sx,sy,sz,loc,m):
            bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.scale=(sx/2,sy/2,sz/2); o.data.materials.append(m); bpy.ops.object.transform_apply(scale=True); return o
        W,D=1.25,1.35
        box(W,D,0.22,(0,yc,zt+0.11),g)
        box(W-0.12,D-0.12,0.12,(0,yc,zt+0.28),red)
        for sx in (-1,1):
            box(0.06,D,0.32,(sx*(W/2-0.03),yc,zt+0.38),g)
        for sy in (-1,1):
            box(W,0.06,0.32,(0,yc+sy*(D/2-0.03),zt+0.38),g)
        for sx in (-1,1):
            for sy in (-1,1):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.045,depth=0.85,location=(sx*(W/2-0.06),yc+sy*(D/2-0.06),zt+0.22+0.425)); bpy.context.object.data.materials.append(g)
        bpy.ops.mesh.primitive_cube_add(location=(0,yc,zt+1.12)); c=bpy.context.object; c.scale=(W/2+0.08,D/2+0.08,0.05); c.data.materials.append(g)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,location=(0,yc,zt+1.16),segments=32,ring_count=16); d=bpy.context.object; d.scale=(W*0.46,D*0.46,0.42)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
        for v in d.data.vertices: v.select = v.co.z<0
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT'); d.data.materials.append(g)
        bpy.ops.mesh.primitive_cone_add(radius1=0.08,depth=0.35,location=(0,yc,zt+1.75)); bpy.context.object.data.materials.append(g)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07,location=(0,yc,zt+1.6)); bpy.context.object.data.materials.append(g)
        print('HOWDAH_SEAT_Z',round(zt+0.34,3),'Y',round(yc,3))
    export(OUT+('puru_elephant.glb' if royal else 'war_elephant.glb'))

def horse():
    ms,mn,mx=load('ir_horse',math.pi/2,2.25)
    body=[o for o in ms if 'hair' not in o.name][0]; hair=[o for o in ms if 'hair' in o.name][0]
    L=mx.y-mn.y; H=mx.z; yh=mn.y
    import numpy as np
    def recolor(img, k, dark):
        if img is None or img.size[0]==0: return
        n=img.size[0]*img.size[1]; px=np.empty(n*4,dtype=np.float32); img.pixels.foreach_get(px); px=px.reshape(-1,4)
        lum=(0.3*px[:,0]+0.59*px[:,1]+0.11*px[:,2])*k
        px[:,0]=lum*dark[0]; px[:,1]=lum*dark[1]; px[:,2]=lum*dark[2]
        img.pixels.foreach_set(px.ravel()); img.update()
        if img.packed_file: img.unpack(method='WRITE_LOCAL')
        p=f'/home/claude/cand/tex_{abs(hash(img.name))}.png'; img.filepath_raw=p; img.file_format='PNG'; img.save()
    done=set()
    for o,k in ((body,0.30),(hair,0.12)):
        for m in o.data.materials:
            b=m.node_tree.nodes['Principled BSDF']; bc=b.inputs['Base Color']
            if bc.is_linked and bc.links[0].from_node.type=='TEX_IMAGE':
                im=bc.links[0].from_node.image
                if im.name not in done: recolor(im,k,(1.0,1.0,1.08)); done.add(im.name)
            else: bc.default_value=(0.02,0.02,0.02,1)
    def fr(y): return (y-yh)/L
    drape(body, yh+0.40*L, yh+0.60*L, 1.15, 1.0, -70, 70, [mat('saddle_red',(0.5,0.04,0.04),0.7), GOLD()], nu=24, nv=32, push=0.025, thick=0.02, name='saddlecloth', mode='NEAREST_SURFACEPOINT')
    export(OUT+'horse.glb')
which=sys.argv[sys.argv.index('--')+1:]
if 'war' in which: elephant(False)
if 'royal' in which: elephant(True)
if 'horse' in which: horse()
