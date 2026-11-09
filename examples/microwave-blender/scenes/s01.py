import bpy, bmesh
import czlib as cz
from common import bowl_with_soup
def build(secs):
    cz.world_studio((0.02, 0.025, 0.03), strength=0.3)
    cav = cz.box((5.0, 7.0, 3.0), (0, -1.2, 0.9), None, bevel=0)
    bm = bmesh.new(); bm.from_mesh(cav.data); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(cav.data); bm.free()
    m = cz.mat_pbr("cavity", (0.78, 0.78, 0.76), rough=0.35, metal=0.6, bump=0.15, bump_scale=25)
    nt = m.node_tree; vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 30
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.12; ramp.color_ramp.elements[1].position = 0.16
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"]); cz.setmat(cav, m)
    tt = cz.cylinder(1.75, 0.06, (0, 0.2, -0.55), cz.mat_glass(), 128)
    bowl, soup = bowl_with_soup((0, 0.2, 0.08), 1.0)
    cz.area_light((-1.6, -1.0, 2.3), (0, 0.2, 0), 260, 1.2, (1.0, 0.82, 0.55))
    cz.area_light((2.0, -2.0, 1.2), (0, 0.2, 0), 60, 2.0, (0.6, 0.75, 1.0))
    for o in (bowl, soup, tt):  # turntable spins
        cz.key_obj(o, 1, rot=(0, 0, 0)); cz.key_obj(o, cz.S.frame_end, rot=(0, 0, 0.35 * secs))
    cam = cz.camera(28, fstop=2.8)
    cz.push_in(cam, (0, 0.25, -0.05), (1.1, -3.3, 1.35), (0.55, -2.25, 0.95))
