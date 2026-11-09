"""Shared builders for the microwave short (look C: white / lab blue, glossy molecules)."""
import math, random
from mathutils import Vector, Euler
import czlib as cz

def lab_world():
    cz.world_studio((0.62, 0.74, 0.92), top=(0.92, 0.95, 1.0), strength=0.9)
    cz.studio_rig(scale=1.4, key=1100)

def bowl_with_soup(loc, r=1.0):
    import bpy, bmesh
    b = cz.sphere(r, loc, None, 96)
    bm = bmesh.new(); bm.from_mesh(b.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > -0.05 * r], context="VERTS")
    bm.to_mesh(b.data); bm.free()
    b.modifiers.new("s", "SOLIDIFY").thickness = 0.06 * r
    b.modifiers.new("sub", "SUBSURF").levels = 2
    cz.setmat(b, cz.mat_pbr("ceramic", (0.93, 0.93, 0.95), rough=0.12, coat=1.0, bump=0.01, bump_scale=150))
    b.scale.z = 0.62
    soup = cz.cylinder(r * 0.93, 0.02, (loc[0], loc[1], loc[2] - 0.18 * r), cz.mat_pbr(
        "soup", (0.85, 0.30, 0.05), rough=0.10, coat=0.6, sss=0.4, bump=0.4, bump_scale=5))
    return b, soup

def field_arrows(m=None):
    m = m or cz.mat_pbr("arrow", (0.02, 0.35, 1.0), rough=0.15, coat=1, emit=(0.0, 0.35, 1.0), estr=0.9)
    return [cz.arrow((ix * 0.75, iy * 0.75 + 0.4, iz * 1.25 - 0.1), 0.9, m)
            for ix in range(-2, 3) for iy in range(-1, 2) for iz in range(0, 2)]

def cloud(n, lo, hi, scale=0.8, seed=3):
    return cz.scatter(lambda loc: cz.molecule_h2o(loc, scale), n, lo, hi, seed)

def jiggle(mols, amp=0.1, spin=1.0, speed=3.0, seed=5):
    rnd = random.Random(seed)
    data = [(Vector(m.location), Vector(m.rotation_euler), Vector([rnd.uniform(-1, 1) for _ in range(3)]), rnd.uniform(0, 6.3)) for m in mols]
    def step(t, k, f):
        for m, (b, r, w, ph) in zip(mols, data):
            cz.key_obj(m, f, loc=b + Vector((amp * math.sin(t * speed * 2 + ph), amp * math.sin(t * speed * 1.6 + 2 * ph),
                                                amp * math.cos(t * speed * 2.3 + ph))), rot=Euler(r + w * t * spin))
    cz.animate(step)
