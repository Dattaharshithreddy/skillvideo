"""Shot 5 (2.5s): Gullu tires, ears droop, drops onto Momo's belly, bounces; both end up
sitting on the floor. Momo annoyed, then happy. Hold at the end."""
import eplib as ep
import czlib as cz


def build(seconds):
    f_end = ep.F(seconds)
    ep.stage(target=(0, 0, 0.7))
    momo = ep.build_momo.build(loc=(-0.10, 0, 0))
    gullu = ep.build_gullu.build(loc=(0.42, 0.02, 0))
    arm, face, root = gullu["arm"], gullu["face"], gullu["root"]
    marm, mface = momo["arm"], momo["face"]
    mroot = momo["root"]
    momo["glasses"].location.y -= 0.006; momo["glasses"].location.z -= 0.018
    s = 0.936

    # gullu runs out of flap: slower, lower, sleepier
    ep.flap(arm, 1, ep.F(0.85), 5.0, 1.6, amp0=42, amp1=12, droop0=0, droop1=-28)
    ep.kx(face, ep.F(0.1), smile=0.6)
    ep.kx(face, ep.F(0.5), smile=0.0, lidSleepy=0.7, browsSad=0.3)
    ep.kx(face, ep.F(0.8), lidSleepy=1.0, browsSad=0.45, frown=0.25)
    for t, x, z in ((0.0, 0.42, 1.26), (0.4, 0.30, 1.22), (0.7, 0.18, 1.16), (0.85, 0.12, 1.10)):
        ep.ko(root, ep.F(t), loc=(x, -0.06, z))
    # the drop: stretch falling, squash on the belly FRONT, bounce away, floor
    ep.ko(root, ep.F(0.95), loc=(0.07, -0.16, 0.98), scale=(s * 0.97, s * 0.97, s * 1.07))
    ep.ko(root, ep.F(1.12), loc=(0.04, -0.26, 0.80), scale=(s * 1.06, s * 1.06, s * 0.80))  # belly!
    ep.ko(root, ep.F(1.3), loc=(0.18, -0.24, 0.98), scale=(s * 0.97, s * 0.97, s * 1.05))   # bounce
    ep.ko(root, ep.F(1.55), loc=(0.38, -0.16, 0.38), scale=(s, s, s))
    ep.ko(root, ep.F(1.7), loc=(0.47, -0.10, 0.03), scale=(s * 1.05, s * 1.05, s * 0.90))   # floor
    ep.ko(root, ep.F(1.85), loc=(0.47, -0.10, 0.0), scale=(s, s, s))
    ep.ear_settle(arm, ep.F(1.12), droop=-34, amp0=26, dur=10)
    ep.ear_settle(arm, ep.F(1.7), droop=-42, amp0=20, dur=16)
    ep.trunk_flop(arm, ep.F(1.12), kick=24, dur=12)
    ep.trunk_flop(arm, ep.F(1.7), kick=18, dur=14)
    # sitting: legs out front
    ep.kb(arm, "leg.L", ep.F(1.55), rot=(-20, 0, 0))
    ep.kb(arm, "leg.R", ep.F(1.55), rot=(-16, 0, 0))
    ep.kb(arm, "leg.L", ep.F(1.85), rot=(-62, 0, 0))
    ep.kb(arm, "leg.R", ep.F(1.85), rot=(-58, 0, 0))
    # dizzy -> giggly
    ep.kx(face, ep.F(1.5), lidSleepy=1.0, browsSad=0.3)
    ep.blink(face, ep.F(1.95))
    ep.expr(face, ep.F(2.15), "laugh", 0.85)
    ep.kb(arm, "head", ep.F(2.0), rot=(0, 0, 0))
    ep.kb(arm, "head", ep.F(2.3), rot=(-10, 6, 0))        # looks up at momo

    # momo: hit, knocked onto his bottom, annoyed... then melts
    ep.breathe(marm, 1, ep.F(0.9))
    ep.kb(marm, "head", 1, rot=(-10, 0, 16))              # watching gullu sputter (up-right)
    ep.kx(mface, 1, browsUp=0.4)
    ep.kb(marm, "upperarm.L", 1, rot=(0, 0, -10))         # rest arms until the impact
    ep.kb(marm, "upperarm.R", 1, rot=(0, 0, 10))
    ep.kb(marm, "upperarm.L", ep.F(1.0), rot=(0, 0, -10))
    ep.kb(marm, "upperarm.R", ep.F(1.0), rot=(0, 0, 10))
    ep.ko(mroot, ep.F(1.0), loc=(-0.10, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1))
    ep.ko(mroot, ep.F(1.12), loc=(-0.10, 0.02, -0.03), rot=(-7, 0, 0), scale=(1.05, 1.05, 0.93))
    ep.ko(mroot, ep.F(1.3), loc=(-0.10, 0.05, -0.06), rot=(-5, 0, 0), scale=(0.98, 0.98, 1.03))
    ep.ko(mroot, ep.F(1.6), loc=(-0.10, 0.07, -0.15), rot=(-4, 0, 0), scale=(1, 1, 1))     # sits
    ep.kb(marm, "thigh.L", ep.F(1.2), rot=(0, 0, 0))
    ep.kb(marm, "thigh.R", ep.F(1.2), rot=(0, 0, 0))
    ep.kb(marm, "thigh.L", ep.F(1.6), rot=(-74, 0, -8))
    ep.kb(marm, "thigh.R", ep.F(1.6), rot=(-70, 0, 8))
    # belly jiggle on impact + arm flail
    ep.kb(marm, "spine", ep.F(1.05), scale=(1, 1, 1))
    ep.kb(marm, "spine", ep.F(1.17), scale=(1.07, 0.95, 1.07))
    ep.kb(marm, "spine", ep.F(1.32), scale=(0.96, 1.04, 0.96))
    ep.kb(marm, "spine", ep.F(1.5), scale=(1, 1, 1))
    ep.kb(marm, "upperarm.L", ep.F(1.12), rot=(-30, 0, -70))
    ep.kb(marm, "upperarm.R", ep.F(1.12), rot=(-30, 0, 70))
    ep.kb(marm, "upperarm.L", ep.F(1.6), rot=(-14, 0, -30))
    ep.kb(marm, "upperarm.R", ep.F(1.6), rot=(-14, 0, 30))
    # face: shock -> annoyed -> happy
    ep.kx(mface, ep.F(1.1), eyesWide=1.0, mouthOpen=0.7, browsUp=1.0)
    ep.kx(mface, ep.F(1.45), eyesWide=0.0, mouthOpen=0.0, browsUp=0.0,
          browsDown=1.0, frown=0.9, lidNarrow=1.0)
    ep.kb(marm, "head", ep.F(1.4), rot=(14, 0, 14))       # glares down at gullu
    ep.kx(mface, ep.F(1.95), browsDown=1.0, frown=0.9, lidNarrow=1.0)
    ep.blink(mface, ep.F(2.05))
    ep.kx(mface, ep.F(2.3), browsDown=0.0, frown=0.0, lidNarrow=0.0,
          smile=1.0, browsUp=0.5, lidSquint=0.5)
    ep.kb(marm, "head", ep.F(2.3), rot=(10, 0, 10))
    # held ending: breathing, a late blink each
    ep.breathe(marm, ep.F(2.3), f_end)
    ep.blink(mface, ep.F(2.62))
    ep.blink(face, ep.F(2.5))
    ep.kb(arm, "ear.L", ep.F(2.55), rot=(-42, 0, 0))
    ep.kb(arm, "ear.L", ep.F(2.65), rot=(-30, 0, 0))
    ep.kb(arm, "ear.L", ep.F(2.75), rot=(-40, 0, 0))

    cam = cz.camera(lens=50)
    cz.move_camera(cam, ((0, -3.35, 0.82), (0, -3.25, 0.80)), (0.05, 0, 0.64), ease_kind="inout")
