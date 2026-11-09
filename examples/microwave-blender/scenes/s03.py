import math
import czlib as cz
from common import lab_world, bowl_with_soup, field_arrows
def build(secs):
    lab_world(); bowl_with_soup((0, 0, -1.6), 1.6); arrows = field_arrows()
    def step(t, k, f):  # strobe flip every 2 frames = "billions of times a second"
        for i, a in enumerate(arrows):
            cz.key_obj(a, f, rot=(math.pi * ((f // 2) % 2) + 0.25 * math.sin(t * 40 + i), 0, 0))
    cz.animate(step)
    cam = cz.camera(40, fstop=2.2)
    cz.push_in(cam, (0, 0.4, 0.4), (2.5, -5.0, 1.1), (1.1, -2.6, 0.7), shake=0.01)
