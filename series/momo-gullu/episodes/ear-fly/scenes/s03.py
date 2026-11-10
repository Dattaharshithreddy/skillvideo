"""Shot 3 (2.5s): medium. Flapping gets faster, Gullu lifts off past Momo's face.
Momo's eyes follow him up, surprised; glasses slip."""
import eplib as ep
import czlib as cz


def build(seconds):
    f_end = ep.F(seconds)
    ep.stage(target=(0, 0, 0.9))
    momo = ep.build_momo.build(loc=(-0.44, 0, 0))
    momo["root"].rotation_euler.z = 0.14
    gullu = ep.build_gullu.build(loc=(0.46, 0, 0))
    arm, face, root = gullu["arm"], gullu["face"], gullu["root"]
    marm, mface = momo["arm"], momo["face"]

    # momo reading at first
    ep.give_book(momo, yaw=0.14)
    ep.kb(marm, "head", 1, rot=(13, 0, -8))
    ep.kx(mface, 1, pupilSmall=0.55, lidSquint=0.3)
    ep.blink(mface, ep.F(0.4))
    ep.breathe(marm, 1, ep.F(0.8))

    # gullu: fast flap, squash anticipation, then liftoff with a stretch
    s = 0.936
    ep.kx(face, 1, smile=0.8, lidSquint=0.4)
    ep.flap(arm, 1, f_end, 4.5, 7.0, amp0=45, amp1=58, droop0=-5)
    ep.ko(root, ep.F(0.1), scale=(s, s, s))
    ep.ko(root, ep.F(0.3), scale=(s * 1.05, s * 1.05, s * 0.88))
    ep.ko(root, ep.F(0.55), scale=(s * 0.96, s * 0.96, s * 1.07))
    ep.ko(root, ep.F(0.9), scale=(s, s, s))
    for t, z, x in ((0.0, 0.0, 0.46), (0.45, 0.02, 0.46), (0.8, 0.16, 0.44), (1.3, 0.46, 0.41),
                    (1.9, 0.76, 0.38), (2.5, 0.93, 0.36), (seconds, 0.99, 0.36)):
        ep.ko(root, ep.F(t), loc=(x, 0, z))
    # legs dangle once airborne
    ep.kb(arm, "leg.L", ep.F(0.8), rot=(0, 0, 0))
    ep.kb(arm, "leg.R", ep.F(0.8), rot=(0, 0, 0))
    ep.kb(arm, "leg.L", ep.F(1.3), rot=(-24, 0, 0))
    ep.kb(arm, "leg.R", ep.F(1.3), rot=(-19, 0, 0))
    ep.kb(arm, "leg.L", ep.F(1.8), rot=(-17, 0, 0))
    ep.kb(arm, "leg.R", ep.F(1.8), rot=(-23, 0, 0))
    # happy glance down at momo near the top
    ep.kx(face, ep.F(1.7), smile=1.0, lidSquint=0.2)
    ep.kx(face, ep.F(2.1), smile=1.0, pupilSmall=0.5)
    ep.kb(arm, "head", ep.F(1.8), rot=(0, 0, 0))
    ep.kb(arm, "head", ep.F(2.2), rot=(10, -8, 0))

    # momo notices, eyes follow up, jaw drops, glasses slip
    ep.kb(marm, "head", ep.F(0.8), rot=(13, 0, -8))
    ep.kb(marm, "head", ep.F(1.05), rot=(4, 0, 16))        # turn toward gullu
    ep.kb(marm, "head", ep.F(1.5), rot=(-12, 0, 12))       # tilt back, following
    ep.kb(marm, "head", ep.F(2.2), rot=(-26, 0, 8))
    ep.kx(mface, ep.F(0.95), pupilSmall=0.0, lidSquint=0.0, browsUp=0.6)
    ep.kx(mface, ep.F(1.3), browsUp=1.0, eyesWide=1.0)
    ep.kx(mface, ep.F(1.7), browsUp=1.0, eyesWide=1.0, mouthOpen=0.55)
    # book arm sinks as he forgets it
    ep.kb(marm, "upperarm.L", ep.F(1.2), rot=(-16, 0, -58))
    ep.kb(marm, "forearm.L", ep.F(1.2), rot=(-62, 0, 8))
    ep.kb(marm, "upperarm.L", ep.F(2.0), rot=(-8, 0, -32))
    ep.kb(marm, "forearm.L", ep.F(2.0), rot=(-30, 0, 4))
    # glasses slip down the nose, tiny catch at the end (offsets from the rest location)
    gl = momo["glasses"]
    from mathutils import Vector as V
    G0 = V(gl.location)
    ep.ko(gl, ep.F(1.55), loc=G0)
    ep.ko(gl, ep.F(1.72), loc=G0 + V((0, -0.007, -0.020)))
    ep.ko(gl, ep.F(1.80), loc=G0 + V((0, -0.006, -0.016)))
    ep.ko(gl, ep.F(1.95), loc=G0 + V((0, -0.007, -0.024)))

    cam = cz.camera(lens=50)
    cz.move_camera(cam, ((0.04, -2.85, 0.96), (0.02, -2.78, 0.98)),
                   lambda e: (0, 0, 0.82 + 0.20 * cz.ease(max(0.0, (e - 0.25) / 0.75), "inout")),
                   ease_kind="linear")
