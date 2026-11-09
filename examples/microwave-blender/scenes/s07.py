import czlib as cz
from common import cloud, jiggle
def build(secs):
    S = cz.S; S.view_settings.view_transform = "Standard"; S.view_settings.look = "None"
    bg = cz.world_studio((0.18, 0.42, 0.78), strength=0.8)
    key = cz.area_light((-4, -5, 6), (0, 0, 0), 1400, 6)
    warm = cz.area_light((3, -3, -2), (0, 0, 0), 0, 4, (1.0, 0.55, 0.2))
    m_o = cz.mat_pbr("hot_o", (0.80, 0.04, 0.05), rough=0.18, coat=1.0, emit=(1.0, 0.28, 0.02), estr=0.0)
    m_h = cz.mat_pbr("hot_h", (0.92, 0.94, 0.97), rough=0.22, coat=1.0, emit=(1.0, 0.6, 0.25), estr=0.0)
    mols = cz.scatter(lambda loc: cz.molecule_h2o(loc, 0.8, m_o, m_h), 40, (-3, -2, -4.5), (3, 4, 4.5), 9)
    jiggle(mols, 0.12, 10.0, 8.0)
    O, H = m_o.node_tree.nodes["Principled BSDF"], m_h.node_tree.nodes["Principled BSDF"]
    def step(t, k, f):
        e = cz.ease(k)
        O.inputs["Emission Strength"].default_value = 1.6 * e; O.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        O.inputs["Base Color"].default_value = (*cz.lerp((0.80, 0.04, 0.05), (1.0, 0.25, 0.0), e), 1); O.inputs["Base Color"].keyframe_insert("default_value", frame=f)
        H.inputs["Emission Strength"].default_value = 0.6 * e; H.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        bg.inputs["Color"].default_value = (*cz.lerp((0.18, 0.42, 0.78), (0.55, 0.10, 0.02), e), 1); bg.inputs["Color"].keyframe_insert("default_value", frame=f)
        bg.inputs["Strength"].default_value = 0.8 - 0.45 * e; bg.inputs["Strength"].keyframe_insert("default_value", frame=f)
        warm.data.energy = 700 * e; warm.data.keyframe_insert("energy", frame=f)
        key.data.energy = 1400 * (1 - 0.75 * e); key.data.keyframe_insert("energy", frame=f)
    cz.animate(step)
    cam = cz.camera(32, fstop=2.0)
    cz.push_in(cam, (0, 0, 0), (0, -4.2, 0.2), (0.4, -8.0, 0.8))
