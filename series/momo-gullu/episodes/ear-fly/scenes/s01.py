"""Shot 1 (2.5s): wide. Momo reads a small book; Gullu waddles in beside him, bored. Slow push-in."""
import eplib as ep
import czlib as cz


def build(seconds):
    f_end = ep.F(seconds)
    ep.stage(target=(0, 0, 0.85))
    momo = ep.build_momo.build(loc=(-0.32, 0, 0))
    momo["root"].rotation_euler.z = 0.12           # slightly toward Gullu's entrance
    gullu = ep.build_gullu.build(loc=(1.35, 0, 0))

    # momo reads: book on palm, head tipped down, eyes down, slow breath, one blink
    ep.give_book(momo, yaw=0.12)
    ep.kb(momo["arm"], "head", 1, rot=(14, 0, -5))
    ep.kx(momo["face"], 1, pupilSmall=0.55, lidSquint=0.3)
    ep.breathe(momo["arm"], 1, f_end)
    ep.blink(momo["face"], ep.F(1.15))
    # tiny page-nod
    ep.kb(momo["arm"], "head", ep.F(1.8), rot=(13, 0, 6))
    ep.kb(momo["arm"], "head", ep.F(2.0), rot=(16, 0, 5))
    ep.kb(momo["arm"], "head", ep.F(2.3), rot=(13.5, 0, 6))

    # gullu waddles in and stops beside momo, bored
    ep.kx(gullu["face"], 1, lidSleepy=0.35, browsDown=0.18)
    ep.waddle(gullu, 1, ep.F(1.9), 1.35, 0.46)
    ep.ear_settle(gullu["arm"], ep.F(1.9), droop=-14, amp0=10, dur=10)
    ep.ko(gullu["root"], ep.F(2.05), loc=(0.46, 0, 0.006))
    ep.ko(gullu["root"], ep.F(2.2), loc=(0.46, 0, 0))
    ep.blink(gullu["face"], ep.F(2.25))
    # bored sigh: little squash
    s = 0.936
    ep.ko(gullu["root"], ep.F(2.3), scale=(s, s, s))
    ep.ko(gullu["root"], ep.F(2.5), scale=(s * 1.01, s * 1.01, s * 0.97))
    ep.ko(gullu["root"], ep.F(2.75), scale=(s, s, s))

    cam = cz.camera(lens=50)
    cz.move_camera(cam, ((0, -3.85, 1.04), (0, -3.1, 0.99)), (0, 0, 0.84), ease_kind="inout")
