import czlib as cz
from common import cloud, jiggle
def build(secs):
    cz.world_studio((0.18, 0.42, 0.78), top=(0.70, 0.86, 1.0), strength=0.8); cz.studio_rig(scale=1.6, key=1300)
    mols = cloud(46, (-3, -2, -4), (3, 9, 4)); jiggle(mols, 0.08, 0.6, 1.5)
    cam = cz.camera(30, fstop=1.6)
    cz.move_camera(cam, ((0.3, -6, 0.2), (0.3, -1, 0.2)), lambda e: (0, e * 5 - 1, 0), roll=lambda e: 0.08 * e)
    cam.data.dof.focus_distance = 2.6
