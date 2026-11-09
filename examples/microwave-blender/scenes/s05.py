import math
import czlib as cz
from common import cloud, jiggle
def build(secs):
    cz.world_studio((0.18, 0.42, 0.78), top=(0.70, 0.86, 1.0), strength=0.8); cz.studio_rig(scale=1.2, key=1300)
    hero = cz.molecule_h2o((0, 0, 0), 1.0)
    bg = cloud(18, (-4, 3, -4), (4, 9, 4), seed=11); jiggle(bg, 0.05, 3.0, 2.0)
    m = cz.mat_pbr("arrow", (0.02, 0.35, 1.0), rough=0.15, coat=1, emit=(0.0, 0.35, 1.0), estr=0.9)
    arrows = [cz.arrow((x, 2.2, -0.2), 1.6, m, 0.06) for x in (-2.0, -1.0, 1.0, 2.0)]
    def step(t, k, f):
        up = (f // 4) % 2
        for a in arrows: cz.key_obj(a, f, rot=(0 if up else math.pi, 0, 0))
        cz.key_obj(hero, f, rot=(0.3, 9.0 * t, 0.4 * math.sin(t * 5)))
    cz.animate(step)
    cam = cz.camera(50, fstop=2.0)
    cz.orbit(cam, (0, 0, 0), 3.3, 0.5, -12, 8)
