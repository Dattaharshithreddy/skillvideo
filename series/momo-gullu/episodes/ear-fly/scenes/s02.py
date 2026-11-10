"""Shot 2 (2s): close on Gullu. He notices his own ears, goes cheeky, starts flapping."""
import eplib as ep
import czlib as cz


def build(seconds):
    f_end = ep.F(seconds)
    ep.stage(target=(0, 0, 0.45), scale=0.6, key=640)
    gullu = ep.build_gullu.build(loc=(0, 0, 0))
    arm, face, root = gullu["arm"], gullu["face"], gullu["root"]

    # bored at first
    ep.kx(face, 1, lidSleepy=0.35, browsDown=0.18)
    ep.kb(arm, "ear.L", 1, rot=(-12, 0, 0))
    ep.kb(arm, "ear.R", 1, rot=(-12, 0, 0))
    ep.blink(face, ep.F(0.25))

    # notices an ear: head turns, one brow up, that ear flicks twice
    ep.kb(arm, "head", ep.F(0.3), rot=(0, 0, 0))
    ep.kb(arm, "head", ep.F(0.55), rot=(-4, 18, 0))
    ep.kx(face, ep.F(0.35), lidSleepy=0.35, browsDown=0.18)
    ep.kx(face, ep.F(0.6), lidSleepy=0.0, browsDown=0.0, browOneUp=1.0, eyesWide=0.5)
    for i, (df, a) in enumerate(((0.0, -12), (0.08, 14), (0.16, -10), (0.26, 16), (0.36, -12))):
        ep.kb(arm, "ear.L", ep.F(0.6 + df), rot=(a, 0, 0))

    # the idea lands: cheeky smirk to camera, little head tilt
    ep.kb(arm, "head", ep.F(1.0), rot=(-2, 4, 9))
    ep.kx(face, ep.F(0.95), eyesWide=0.0)
    ep.kx(face, ep.F(1.1), smirk=1.0, browOneUp=1.0, lidSquint=0.7)

    # flapping starts, ramping up; body bounces with it, trunk curls with excitement
    ep.kb(arm, "ear.R", ep.F(0.95), rot=(-12, 0, 0))
    ep.flap(arm, ep.F(1.1), f_end, 1.8, 4.4, amp0=16, amp1=44, droop0=-8, droop1=-4, root=root, bob=0.006)
    ep.kb(arm, "trunk.3", ep.F(1.1), rot=(0, 0, 0))
    ep.kb(arm, "trunk.4", ep.F(1.1), rot=(0, 0, 0))
    ep.kb(arm, "trunk.3", f_end, rot=(-22, 0, 0))
    ep.kb(arm, "trunk.4", f_end, rot=(-30, 0, 0))
    ep.kx(face, ep.F(1.7), smirk=1.0, browOneUp=1.0, lidSquint=0.5, smile=0.4)

    cam = cz.camera(lens=40)
    cz.move_camera(cam, ((0.08, -1.86, 0.56), (0.06, -1.68, 0.53)), (0.0, 0, 0.45), ease_kind="inout")
