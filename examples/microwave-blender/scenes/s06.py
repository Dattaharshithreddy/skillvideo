import random
import czlib as cz
from common import cloud, jiggle
def build(secs):
    cz.world_studio((0.18, 0.42, 0.78), top=(0.70, 0.86, 1.0), strength=0.8); cz.studio_rig(scale=1.4, key=1300)
    mols = cloud(26, (-1.8, -1.2, -2.4), (1.8, 1.8, 2.4), 0.85, seed=5); jiggle(mols, 0.18, 9.0, 8.0)
    sparks = cz.glow_particles(12, (-1.6, -1.0, -2.0), (1.6, 1.4, 2.0), (1.0, 0.45, 0.05), 0.05, 5)
    for s in sparks:
        s.cycles.use_motion_blur = False  # they teleport each frame; blur would smear the jump
    def step(t, k, f):
        rnd = random.Random(f)
        for s in sparks:
            sc = rnd.uniform(0.0, 1.8) if rnd.random() < 0.6 else 0.0
            cz.key_obj(s, f, loc=(rnd.uniform(-1.6, 1.6), rnd.uniform(-1.0, 1.4), rnd.uniform(-2, 2)), scale=(sc, sc, sc), step=True)
    cz.animate(step)
    cam = cz.camera(35, fstop=2.0)
    cz.push_in(cam, (0, 0, 0), (0, -5.2, 0.4), (0, -4.2, 0.2), shake=0.04)
