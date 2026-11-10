"""Shot 4 (2.5s): low angle. Gullu hovers proudly, trunk waving; Momo jumps for him and misses."""
import math
import eplib as ep
import czlib as cz


def build(seconds):
    f_end = ep.F(seconds)
    ep.stage(target=(0, 0, 1.0))
    momo = ep.build_momo.build(loc=(-0.40, 0.04, 0))
    momo["root"].rotation_euler.z = 0.10
    gullu = ep.build_gullu.build(loc=(0.14, 0.02, 0))
    arm, face, root = gullu["arm"], gullu["face"], gullu["root"]
    marm, mface = momo["arm"], momo["face"]
    momo["glasses"].location.y -= 0.006; momo["glasses"].location.z -= 0.018   # glasses sit low

    # gullu hovers with a proud laugh, bobbing, trunk waving
    ep.flap(arm, 1, f_end, 6.0, 6.2, amp0=46, droop0=-4)
    base = 1.24
    for f in range(1, f_end + 1):
        t = (f - 1) / cz.FPS
        dodge = 0.15 * cz.ease(min(1.0, max(0.0, (t - 0.9) / 0.28)), "out") * (1 if t < 1.5 else max(0.3, 1 - (t - 1.5) * 0.6))
        ep.ko(root, f, loc=(0.14, 0.02, base + 0.06 * math.sin(2 * math.pi * 1.1 * t) + dodge))
    ep.expr(face, 1, "laugh", 0.9)
    for t, mo in ((0.5, 0.9), (0.9, 0.55), (1.3, 0.9), (1.8, 0.6), (2.3, 0.9)):
        ep.kx(face, ep.F(t), mouthOpen=mo)
    for f in range(1, f_end + 1, 2):                      # trunk waves with whip overlap
        t = (f - 1) / cz.FPS
        ep.kb(arm, "trunk.2", f, rot=(14 * math.sin(2 * math.pi * 1.3 * t), 0, 0))
        ep.kb(arm, "trunk.3", f, rot=(20 * math.sin(2 * math.pi * 1.3 * t - 0.7), 0, 0))
        ep.kb(arm, "trunk.4", f, rot=(26 * math.sin(2 * math.pi * 1.3 * t - 1.4), 0, 0))
    ep.kb(arm, "leg.L", 1, rot=(-20, 0, 0))
    ep.kb(arm, "leg.R", 1, rot=(-16, 0, 0))

    # momo: crouch, leap, grab, miss, land, fume
    mroot = momo["root"]
    ep.kb(marm, "head", 1, rot=(-18, 0, 6))               # watching him up there
    ep.kb(marm, "upperarm.L", 1, rot=(0, 0, -10))
    ep.kb(marm, "upperarm.R", 1, rot=(0, 0, 10))
    ep.kb(marm, "forearm.L", 1, rot=(-8, 0, 0))
    ep.kb(marm, "forearm.R", 1, rot=(-8, 0, 0))
    ep.kx(mface, 1, browsDown=0.7, mouthOpen=0.35, lidNarrow=0.4)
    ep.ko(mroot, 1, loc=(-0.40, 0.04, 0), scale=(1, 1, 1))
    ep.ko(mroot, ep.F(0.25), loc=(-0.40, 0.04, -0.09), scale=(1.04, 1.04, 0.92))   # crouch
    ep.ko(mroot, ep.F(0.42), loc=(-0.40, 0.04, 0.02), scale=(0.97, 0.97, 1.06))
    ep.ko(mroot, ep.F(0.75), loc=(-0.36, 0.03, 0.56), scale=(1, 1, 1))             # apex
    ep.ko(mroot, ep.F(1.05), loc=(-0.34, 0.03, 0.10))
    ep.ko(mroot, ep.F(1.18), loc=(-0.34, 0.03, 0.0), scale=(1.05, 1.05, 0.91))     # land squash
    ep.ko(mroot, ep.F(1.4), loc=(-0.35, 0.03, 0), scale=(1, 1, 1))
    # arms reach overhead during the leap, drop after
    ep.kb(marm, "upperarm.L", ep.F(0.2), rot=(0, 0, -20))
    ep.kb(marm, "upperarm.R", ep.F(0.2), rot=(0, 0, 20))
    ep.kb(marm, "upperarm.L", ep.F(0.55), rot=(0, 0, -150))
    ep.kb(marm, "upperarm.R", ep.F(0.55), rot=(0, 0, 150))
    ep.kb(marm, "forearm.L", ep.F(0.55), rot=(0, 0, -20))
    ep.kb(marm, "forearm.R", ep.F(0.55), rot=(0, 0, 20))
    ep.key_hand(marm, "L", "open", ep.F(0.55))
    ep.key_hand(marm, "R", "open", ep.F(0.55))
    ep.kb(marm, "head", ep.F(0.3), rot=(-24, 0, 10))
    ep.kb(marm, "upperarm.L", ep.F(1.5), rot=(-10, 0, -35))
    ep.kb(marm, "upperarm.R", ep.F(1.5), rot=(-10, 0, 35))
    ep.kb(marm, "forearm.L", ep.F(1.5), rot=(-20, 0, 0))
    ep.kb(marm, "forearm.R", ep.F(1.5), rot=(-20, 0, 0))
    ep.key_hand(marm, "L", "relax", ep.F(1.5))
    ep.key_hand(marm, "R", "relax", ep.F(1.5))
    # after the miss: glare up, second small frustrated hop
    ep.kx(mface, ep.F(1.3), browsDown=1.0, frown=0.7, lidNarrow=0.8, mouthOpen=0.0)
    ep.ko(mroot, ep.F(1.8), loc=(-0.35, 0.03, 0))
    ep.ko(mroot, ep.F(1.95), loc=(-0.35, 0.03, 0.10))
    ep.ko(mroot, ep.F(2.12), loc=(-0.35, 0.03, 0), scale=(1.03, 1.03, 0.95))
    ep.ko(mroot, ep.F(2.3), loc=(-0.35, 0.03, 0), scale=(1, 1, 1))
    ep.kb(marm, "upperarm.R", ep.F(1.95), rot=(0, 0, 120))
    ep.kb(marm, "upperarm.R", ep.F(2.25), rot=(-10, 0, 40))
    ep.blink(mface, ep.F(1.45))

    cam = cz.camera(lens=40)
    cz.move_camera(cam, ((0.02, -2.4, 0.28), (0.02, -2.32, 0.31)), (0.0, 0.03, 1.02), ease_kind="inout")
