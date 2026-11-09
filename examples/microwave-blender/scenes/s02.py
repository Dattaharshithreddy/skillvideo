import math
import czlib as cz
from common import lab_world, bowl_with_soup, field_arrows
def build(secs):
    lab_world(); bowl_with_soup((0, 0, -1.6), 1.6); arrows = field_arrows()
    def step(t, k, f):
        flip = cz.ease((t - 0.55) / 0.3)
        for a in arrows: cz.key_obj(a, f, rot=(math.pi * flip, 0, 0))
    cz.animate(step)
    cam = cz.camera(32, fstop=3.5)
    cz.orbit(cam, (0, 0.3, 0.1), 6.2, 1.5, -20, 5)
