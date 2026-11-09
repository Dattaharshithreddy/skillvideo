"""czlib: helper library for Zack D-style shots in Blender (bpy, Blender 5.x, Cycles).

Import from a shot script run by render.py:
    import czlib as cz
Every helper returns Blender objects so you can tweak anything afterwards.
Units: metres; +Z up; camera looks along its -Z.
"""
import bpy, bmesh, json, math, os, random, urllib.request
from mathutils import Vector, Euler

S = None                      # current scene, set by reset()
FPS = 30
CACHE = os.path.expanduser(os.environ.get("CGI_ASSETS", "~/.cache/cgi-assets"))


# =============================================================== scene / render
def reset():
    global S
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S = bpy.context.scene
    S.render.engine = "CYCLES"
    S.render.fps = FPS
    S.render.resolution_x, S.render.resolution_y = 1080, 1920
    S.render.image_settings.file_format = "PNG"
    S.view_settings.view_transform = "AgX"
    S.view_settings.look = "AgX - Punchy"
    return S


def gpu_setup():
    """Enable OptiX (fastest on RTX/T4/A10G) or CUDA; fall back to CPU. Returns the device type used."""
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == kind]
            if devs:
                for d in prefs.devices:
                    d.use = d.type == kind
                bpy.context.scene.cycles.device = "GPU"
                return kind
        except (TypeError, ValueError):
            continue
    bpy.context.scene.cycles.device = "CPU"
    return "CPU"


def render_preset(quality="final", motion_blur=True):
    """quality: preview (fast look check) | final (delivery)."""
    c = S.cycles
    q = {"preview": (24, 0.5, 4), "final": (128, 1.0, 8)}[quality]
    c.samples, pct, bounces = q
    c.samples = int(os.environ.get("CZ_SAMPLES", c.samples))          # overrides for quick tests
    S.render.resolution_percentage = int(os.environ.get("CZ_RES_PCT", int(pct * 100)))
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.02 if quality == "preview" else 0.01
    c.use_denoising = True
    try:
        c.denoiser = "OPTIX" if c.device == "GPU" else "OPENIMAGEDENOISE"
    except TypeError:
        pass
    c.max_bounces = bounces
    c.transparent_max_bounces = 16
    c.volume_bounces = 1
    S.render.use_persistent_data = True
    S.render.use_motion_blur = motion_blur
    S.render.motion_blur_shutter = 0.5
    return S


def set_frames(seconds):
    S.frame_start, S.frame_end = 1, max(1, int(round(seconds * FPS)))
    return S.frame_end


# =============================================================== materials
def _bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]


def mat_pbr(name, color, rough=0.4, metal=0.0, coat=0.0, sss=0.0, sss_radius=(1.0, 0.4, 0.2), trans=0.0,
            ior=1.45, emit=None, estr=0.0, bump=0.0, bump_scale=40.0, rough_var=0.08, alpha=1.0):
    """Principled material with built-in micro-imperfections: bump noise + roughness variation."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = _bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Subsurface Radius"].default_value = sss_radius
    b.inputs["Transmission Weight"].default_value = trans
    b.inputs["IOR"].default_value = ior
    b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    # roughness variation: real surfaces are never uniformly rough
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = bump_scale * 0.25
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = max(0.0, rough - rough_var)
    mr.inputs["To Max"].default_value = min(1.0, rough + rough_var)
    nt.links.new(n.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    if bump > 0:
        n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = bump_scale; n2.inputs["Detail"].default_value = 10
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.02
        nt.links.new(n2.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_skin(tone=(0.80, 0.58, 0.47), name="skin"):
    """Skin: subsurface scattering, pores, slight sheen. Use on humans/organs."""
    return mat_pbr(name, tone, rough=0.42, sss=0.25, sss_radius=(1.0, 0.35, 0.18), bump=0.12, bump_scale=180, coat=0.05)


def mat_glossy_organ(color=(0.55, 0.05, 0.05), name="organ"):
    """Wet anatomical look (heart, muscle): glossy coat + SSS."""
    return mat_pbr(name, color, rough=0.28, sss=0.3, coat=0.8, bump=0.2, bump_scale=60)


def mat_glass(color=(0.9, 0.97, 1.0), rough=0.02, name="glass"):
    return mat_pbr(name, color, rough=rough, trans=1.0, ior=1.5, rough_var=0.0)


def mat_glow(color, strength=3.0, name="glow"):
    return mat_pbr(name, color, rough=0.3, emit=color, estr=strength, rough_var=0.0)


def mat_xray(edge=(0.2, 0.8, 1.0), strength=4.0, name="xray"):
    """Zack D x-ray body: transparent glass-like body, glowing cyan fresnel edges."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.25
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*edge, 1); em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def setmat(obj, m):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear(); obj.data.materials.append(m)
    for ch in obj.children:
        setmat(ch, m)
    return obj


# =============================================================== primitives
def _new(op, **kw):
    op(**kw); o = bpy.context.object
    if o.type == "MESH":
        bpy.ops.object.shade_smooth()
    return o


def sphere(r, loc, m=None, seg=64):
    o = _new(bpy.ops.mesh.primitive_uv_sphere_add, radius=r, location=loc, segments=seg, ring_count=seg // 2)
    return setmat(o, m) if m else o


def cylinder(r, depth, loc, m=None, verts=64):
    o = _new(bpy.ops.mesh.primitive_cylinder_add, radius=r, depth=depth, location=loc, vertices=verts)
    return setmat(o, m) if m else o


def box(size, loc, m=None, bevel=0.01):
    o = _new(bpy.ops.mesh.primitive_cube_add, size=1, location=loc)
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:  # real objects never have perfectly sharp edges
        bv = o.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 3
    return setmat(o, m) if m else o


def plane(size, loc, m=None):
    o = _new(bpy.ops.mesh.primitive_plane_add, size=size, location=loc)
    return setmat(o, m) if m else o


def empty(loc=(0, 0, 0)):
    bpy.ops.object.empty_add(location=loc); return bpy.context.object


def parent(child, par):
    child.parent = par; child.matrix_parent_inverse = par.matrix_world.inverted(); return child


def text3d(body, loc, size=0.3, m=None, extrude=0.02):
    bpy.ops.object.text_add(location=loc); t = bpy.context.object
    t.data.body = body; t.data.size = size; t.data.extrude = extrude; t.data.align_x = "CENTER"
    return setmat(t, m) if m else t


def arrow(loc, length=1.0, m=None, r=0.04):
    root = empty(loc)
    sh = cylinder(r, length * 0.75, (loc[0], loc[1], loc[2] - length * 0.125), m, 32)
    hd = _new(bpy.ops.mesh.primitive_cone_add, radius1=r * 2.6, depth=length * 0.25,
              location=(loc[0], loc[1], loc[2] + length * 0.375), vertices=32)
    if m: setmat(hd, m)
    parent(sh, root); parent(hd, root)
    return root


def porthole(target, center, radius, depth_axis="Y", rim_mat=None):
    """Clean circular cutaway through `target` (shirt, skin, wall) at world `center`. Returns the cutter."""
    rot = {"X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0), "Z": (0, 0, 0)}[depth_axis]
    c = _new(bpy.ops.mesh.primitive_cylinder_add, radius=radius, depth=4, location=center, rotation=rot, vertices=96)
    c.display_type = "WIRE"; c.hide_render = True
    mod = target.modifiers.new("porthole", "BOOLEAN"); mod.object = c; mod.operation = "DIFFERENCE"; mod.solver = "EXACT"
    if not any(md.type == "SOLIDIFY" for md in target.modifiers):  # give the cut edge visible thickness
        target.modifiers.new("thick", "SOLIDIFY").thickness = 0.01
    if rim_mat:
        target.data.materials.append(rim_mat)
    return c


# =============================================================== world & light
def world_studio(color, top=None, strength=1.0):
    """Plain studio backdrop (look A/C): flat colour or vertical gradient."""
    w = bpy.data.worlds.new("studio"); S.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    if top:
        tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -1
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        e = ramp.color_ramp.elements; e[0].position, e[0].color = 0.35, (*color, 1); e[1].position, e[1].color = 0.75, (*top, 1)
        nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    else:
        bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength
    return bg


def world_hdri(path, strength=1.0, rotation_deg=0.0, background=None):
    """Realistic image-based lighting (look B). `background` colour hides the HDRI from camera but keeps its light."""
    w = bpy.data.worlds.new("hdri"); S.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(path)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value[2] = math.radians(rotation_deg)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = strength
    if background:
        out = [n for n in nt.nodes if n.type == "OUTPUT_WORLD"][0]
        lp = nt.nodes.new("ShaderNodeLightPath"); bg2 = nt.nodes.new("ShaderNodeBackground")
        bg2.inputs["Color"].default_value = (*background, 1); mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(bg.outputs[0], mix.inputs[1]); nt.links.new(bg2.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return bg


def area_light(loc, target, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object; l.data.energy = energy; l.data.size = size; l.data.color = color
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return l


def studio_rig(target=(0, 0, 0), scale=1.0, key=1200, warm_key=True, rim_color=(0.75, 0.88, 1.0)):
    """Soft key (large, upper-left), fill (opposite, weak), rim (behind) = the reference's soft wrap light."""
    t = Vector(target); s = scale
    k = area_light(t + Vector((-3.5, -4, 4)) * s, t, key * s * s, 4 * s, (1.0, 0.96, 0.9) if warm_key else (1, 1, 1))
    f = area_light(t + Vector((4, -3, 1)) * s, t, key * 0.25 * s * s, 5 * s, (0.9, 0.95, 1.0))
    r = area_light(t + Vector((1.5, 5, 3)) * s, t, key * 0.8 * s * s, 2 * s, rim_color)
    return k, f, r


def fog(density=0.02, color=(0.8, 0.9, 1.0), size=40):
    """Atmospheric depth (god rays from area/spot lights). Costly: keep density low."""
    v = box((size, size, size), (0, 0, size / 2 - 2), bevel=0)
    m = bpy.data.materials.new("fog"); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(_bsdf(m)); out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    pv = nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = density
    pv.inputs["Color"].default_value = (*color, 1)
    nt.links.new(pv.outputs[0], out.inputs["Volume"]); setmat(v, m)
    return v


# =============================================================== camera & motion
def camera(lens=35, fstop=None, sensor=36):
    bpy.ops.object.camera_add(); c = bpy.context.object; S.camera = c
    c.data.lens = lens; c.data.sensor_width = sensor
    c.data.clip_start = 0.01
    if fstop:
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop
    return c


def aim(cam, loc, target, roll=0.0):
    cam.location = Vector(loc)
    e = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    e.rotate_axis("Z", roll); cam.rotation_euler = e
    if cam.data.dof.use_dof:
        cam.data.dof.focus_distance = (Vector(target) - Vector(loc)).length
    return cam


def ease(x, kind="inout"):
    x = max(0.0, min(1.0, x))
    return {"inout": x * x * (3 - 2 * x), "out": 1 - (1 - x) ** 3, "in": x ** 3, "linear": x}[kind]


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def _keycam(cam, f):
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
    if cam.data.dof.use_dof:
        cam.data.dof.keyframe_insert("focus_distance", frame=f)


def animate(fn, f0=None, f1=None):
    """Call fn(t_seconds, k_0to1, frame) every frame and let fn set + keyframe anything. Dense keys = exact control."""
    f0 = f0 or S.frame_start; f1 = f1 or S.frame_end
    for f in range(f0, f1 + 1):
        S.frame_set(f)
        fn((f - S.frame_start) / FPS, (f - f0) / max(1, f1 - f0), f)


def move_camera(cam, path, target, ease_kind="inout", roll=None, shake=0.0, f0=None, f1=None):
    """path: (start, end) locations or a function k->location. target: point or function k->point or an object.
    shake: handheld amplitude in metres (0.01 subtle, 0.04 impact)."""
    rnd = random.Random(1)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]

    def step(t, k, f):
        e = ease(k, ease_kind)
        loc = path(e) if callable(path) else lerp(path[0], path[1], e)
        tg = target(e) if callable(target) else (target.matrix_world.translation if hasattr(target, "matrix_world") else target)
        if shake:
            loc = Vector(loc) + Vector([shake * math.sin(t * (11 + i * 3.7) + ph[i]) for i in range(3)])
        aim(cam, loc, tg, (roll(e) if callable(roll) else (roll or 0.0)))
        _keycam(cam, f)
    animate(step, f0, f1)


def push_in(cam, target, start, end, **kw):
    move_camera(cam, (start, end), target, **kw)


def orbit(cam, target, radius, height, deg0, deg1, **kw):
    tg = Vector(target)
    move_camera(cam, lambda e: tg + Vector((radius * math.sin(math.radians(deg0 + (deg1 - deg0) * e)),
                                            -radius * math.cos(math.radians(deg0 + (deg1 - deg0) * e)), height)), tg, **kw)


def follow(cam, obj, offset=(0, -3, 0.6), **kw):
    """Follow-cam: chases a moving object (heart, wrench, helmet). Animate the object first."""
    def p(e):
        return obj.matrix_world.translation + Vector(offset)
    move_camera(cam, p, obj, ease_kind="linear", **kw)


def whip(cam, f_mid, frames=8):
    """Fast 0.25 s whip: big yaw swing centred on f_mid; motion blur turns it into a transition.
    Call AFTER the main camera move; it overrides rotation keys around f_mid."""
    for f in range(f_mid - frames // 2, f_mid + frames // 2 + 1):
        S.frame_set(f)
        x = (f - f_mid) / (frames / 2)
        cam.rotation_euler.rotate_axis("Y", 0.35 * math.copysign(1 - abs(x), x) if x else 0)
        cam.keyframe_insert("rotation_euler", frame=f)


def key_obj(obj, f, loc=None, rot=None, scale=None, step=False):
    """step=True requests stepped keys. For objects that teleport between frames, also set
    obj.cycles.use_motion_blur = False, or motion blur will smear the jump."""
    pe = bpy.context.preferences.edit
    old = pe.keyframe_new_interpolation_type
    if step:
        pe.keyframe_new_interpolation_type = "CONSTANT"
    _key_obj(obj, f, loc, rot, scale)
    pe.keyframe_new_interpolation_type = old


def _key_obj(obj, f, loc, rot, scale):
    if loc is not None: obj.location = loc; obj.keyframe_insert("location", frame=f)
    if rot is not None: obj.rotation_euler = rot; obj.keyframe_insert("rotation_euler", frame=f)
    if scale is not None: obj.scale = scale; obj.keyframe_insert("scale", frame=f)


# =============================================================== assets (Poly Haven, CC0) & import
def _get(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest):
        req = urllib.request.Request(url, headers={"User-Agent": "cgi-shorts/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            f.write(r.read())
    return dest


def _ph_files(asset_id):
    req = urllib.request.Request(f"https://api.polyhaven.com/files/{asset_id}", headers={"User-Agent": "cgi-shorts/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def ph_search(kind="hdris", query=""):
    """List Poly Haven asset ids. kind: hdris | textures | models. Filters by id/name/tags containing query."""
    req = urllib.request.Request(f"https://api.polyhaven.com/assets?t={kind}", headers={"User-Agent": "cgi-shorts/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    q = query.lower()
    return [k for k, v in data.items() if q in k or q in v.get("name", "").lower() or any(q in t for t in v.get("tags", []))]


def ph_hdri(asset_id, res="2k", **world_kw):
    """Download a Poly Haven HDRI (e.g. 'studio_small_09', 'kloofendal_48d_partly_cloudy') and light the scene with it."""
    url = _ph_files(asset_id)["hdri"][res]["hdr"]["url"]
    return world_hdri(_get(url, f"{CACHE}/hdri/{asset_id}_{res}.hdr"), **world_kw)


def ph_material(asset_id, res="2k", scale=1.0):
    """Poly Haven PBR texture set (e.g. 'brick_wall_001', 'wood_floor_deck', 'concrete_floor_02') as a material."""
    files = _ph_files(asset_id)
    maps = {"Diffuse": "Base Color", "Rough": "Roughness", "nor_gl": "Normal", "Displacement": "Disp", "arm": None}
    m = bpy.data.materials.new(asset_id); m.use_nodes = True; nt = m.node_tree; b = _bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale); nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    for key, sock in maps.items():
        if key not in files or sock is None:
            continue
        info = files[key].get(res) or next(iter(files[key].values()))
        fmt = "jpg" if "jpg" in info else next(iter(info))
        path = _get(info[fmt]["url"], f"{CACHE}/tex/{asset_id}/{key}_{res}.{fmt}")
        im = nt.nodes.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(path)
        if key != "Diffuse":
            im.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
        if sock == "Normal":
            nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(im.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
        elif sock == "Disp":
            dp = nt.nodes.new("ShaderNodeDisplacement"); dp.inputs["Scale"].default_value = 0.02
            nt.links.new(im.outputs["Color"], dp.inputs["Height"])
            out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]; nt.links.new(dp.outputs[0], out.inputs["Displacement"])
        else:
            nt.links.new(im.outputs["Color"], b.inputs[sock])
    return m


def ph_model(asset_id, res="2k", loc=(0, 0, 0), scale=1.0):
    """Import a Poly Haven model (glTF) e.g. 'ceramic_vase_01', 'wooden_table_02', 'food_apple_01'. Returns a root empty."""
    files = _ph_files(asset_id)
    g = files["gltf"][res]["gltf"]
    base = f"{CACHE}/models/{asset_id}_{res}"
    main = _get(g["url"], f"{base}/{os.path.basename(g['url'])}")
    for rel, inc in g.get("include", {}).items():
        _get(inc["url"], f"{base}/{rel}")
    return import_model(main, loc, scale)


def import_model(path, loc=(0, 0, 0), scale=1.0):
    """Import .glb/.gltf/.fbx/.obj/.blend (Mixamo characters, Sketchfab CC models, BodyParts3D .obj...).
    Returns an empty parented over everything imported."""
    before = set(bpy.data.objects)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".blend":
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = src.objects
        for o in dst.objects:
            if o: S.collection.objects.link(o)
    else:
        raise ValueError(f"unsupported model type {ext}")
    new = [o for o in bpy.data.objects if o not in before]
    root = empty(loc)
    for o in new:
        if o.parent is None:
            parent(o, root)
    root.scale = (scale, scale, scale)
    return root


def shape_key(obj, name, value, frame=None):
    """Drive a face blend shape (ARKit-style names like 'jawOpen', 'eyeBlinkLeft', 'mouthSmileLeft')."""
    keys = obj.data.shape_keys.key_blocks if obj.data.shape_keys else {}
    kb = next((k for k in keys if k.name.lower() == name.lower()), None)
    if kb is None:
        return False
    kb.value = value
    if frame is not None:
        kb.keyframe_insert("value", frame=frame)
    return True


# =============================================================== science / micro helpers
def molecule_h2o(loc, scale=1.0, m_o=None, m_h=None):
    m_o = m_o or mat_pbr("oxygen", (0.80, 0.04, 0.05), rough=0.18, coat=1.0, bump=0.04, bump_scale=60)
    m_h = m_h or mat_pbr("hydrogen", (0.92, 0.94, 0.97), rough=0.22, coat=1.0, bump=0.03, bump_scale=60)
    root = empty(loc)
    parent(sphere(0.30 * scale, loc, m_o, 48), root)
    a = math.radians(104.5 / 2)
    for s in (-1, 1):
        parent(sphere(0.19 * scale, Vector(loc) + Vector((math.sin(a) * s, 0, -math.cos(a))) * 0.36 * scale, m_h, 32), root)
    return root


def scatter(make, n, box_min, box_max, seed=1):
    rnd = random.Random(seed); out = []
    for _ in range(n):
        loc = [rnd.uniform(box_min[i], box_max[i]) for i in range(3)]
        o = make(loc); o.rotation_euler = Euler([rnd.uniform(0, 6.28) for _ in range(3)]); out.append(o)
    return out


def glow_particles(n, box_min, box_max, color=(0.2, 1.0, 0.3), r=0.02, strength=6, seed=2, shape="sphere"):
    """Invisible agents made visible (bacteria = shape 'rod', energy = 'sphere')."""
    m = mat_glow(color, strength, f"glow_{color}")
    def mk(loc):
        if shape == "rod":
            o = _new(bpy.ops.mesh.primitive_cylinder_add, radius=r, depth=r * 5, location=loc, vertices=16)
            bv = o.modifiers.new("round", "BEVEL"); bv.width = r * 0.9; bv.segments = 6
            return setmat(o, m)
        return sphere(r, loc, m, 16)
    return scatter(mk, n, box_min, box_max, seed)
