"""REVIEW ONLY. Stage 3 revision of the Laddu Character Life Test: moves and timing (24 fps).

A move is (end_frame, length, ease, label, changes). The change is reached at end_frame and takes
`length` frames; before it starts the previous value is held. Moves may overlap when they drive
different parts: that is how the eyes lead and the tail follows. Moves with a label are the key
poses shown on the comparison sheets. dxw slides the cat along the floor, y_up lifts him.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stage2'))
from life_test import CROUCH, WARY                                                   # noqa: E402

S3 = [
    dict(n=1, name='Curiosity', start_dx=-130, end=96, level=1.0,
         start=dict(yaw=-0.2, pupil=(-0.3, 0.1), tail_a=-8.0, tail_b=55.0, tail_tip=20.0, pawN=(16.0, -12.0), wristN=24.0, chest=(-4.0, 0.0), head_rot=-3.0),
         start_label='START idle, mid-step, looking away',
         moves=[
             (14, 2, 'snap', 'NOTICE eyes only: a flick to the side', dict(pupil=(0.95, 0.0), earflick=1.0)),
             (18, 3, 'out', 'PAUSE he stops dead, weight rocks back, paw stays in the air', dict(chest=(-12.0, 2.0), hip=(-5.0, 3.0), arch=5.0, head_dx=-5.0, lid=0.12, tail_tip=0.0, earflick=0.0, ear_back=0.25)),
             (34, 6, 'io', 'LOOK the head turns; the body has not moved', dict(yaw=0.95, head_dx=4.0, head_dy=2.0, lid=0.0, eye_pop=1.15, brow=8.0, pupil=(0.6, 0.2), ear_back=0.0)),
             (46, 7, 'io', 'THINK head tilts, tail curls into a hook', dict(head_rot=17.0)),
             (49, 7, 'over', None, dict(tail_a=55.0, tail_b=30.0, tail_tip=95.0)),
             (64, 12, 'io', 'CAUTIOUS SHIFT spine stretches, chest and one paw creep forward', dict(chest=(22.0, 9.0), hip=(4.0, -2.0), arch=-5.0, head_dx=22.0, head_dy=8.0, pawN=(36.0, -7.0), wristN=30.0)),
             (70, 4, 'out', 'HESITATE goes a little too far, rump lifts', dict(chest=(30.0, 12.0), hip=(9.0, -9.0), head_dx=30.0, head_rot=20.0)),
             (73, 4, 'over', None, dict(tail_tip=140.0)),
             (82, 10, 'over', 'RECOVER eases back, paw touches down, head tilts the other way', dict(chest=(12.0, 3.0), hip=(0.0, 0.0), arch=0.0, head_dx=14.0, head_dy=0.0, head_rot=-11.0, pawN=(30.0, 0.0), wristN=0.0, eye_pop=1.05, lid=0.1)),
             (86, 8, 'over', None, dict(tail_tip=110.0)),
             (90, 2, 'out', None, dict(earflick=1.0)), (93, 3, 'out', None, dict(earflick=0.0)),
         ]),
    dict(n=2, name='Greed', start_dx=-130, end=98, level=1.0,
         start=dict(yaw=0.5, lid=0.4, pupil=(-0.4, 0.0), head_rot=-4.0, tail_a=20.0, tail_b=80.0),
         start_label='START plays it cool',
         moves=[
             (10, 3, 'snap', 'GLANCE the eyes sneak to the bowl', dict(pupil=(0.9, 0.15))),
             (18, 4, 'out', 'DENY looks away, nose in the air', dict(pupil=(-0.6, -0.1), yaw=0.25, head_rot=-9.0, lid=0.5)),
             (30, 8, 'io', 'SNIFF the nose turns back on its own', dict(head_dy=-12.0, head_rot=-12.0, chest=(-8.0, -4.0), yaw=0.9, lid=0.55, pupil=(0.5, -0.3))),
             (32, 2, 'io', None, dict(head_dy=-17.0)), (34, 2, 'io', None, dict(head_dy=-12.0)), (36, 2, 'io', None, dict(head_dy=-16.0)), (38, 2, 'io', None, dict(head_dy=-12.0)),
             (34, 6, 'over', None, dict(tail_tip=30.0)),
             (42, 3, 'out', 'TELL he licks his lips; a paw lifts by itself', dict(tongue=0.3, pawN=(10.0, -10.0), wristN=22.0)),
             (46, 3, 'out', None, dict(tongue=0.0)), (46, 4, 'over', None, dict(tail_tip=85.0)),
             (52, 4, 'out', 'RESIST pulls himself back, brows down', dict(chest=(-14.0, 0.0), hip=(-5.0, 3.0), arch=4.0, head_dx=-5.0, lid=0.2, brow_ang=9.0, pawN=(0.0, 0.0), wristN=0.0)),
             (66, 10, 'in', 'GIVES IN the nose pulls him; hind feet stay planted', dict(head_dx=30.0, head_dy=16.0, head_rot=12.0, chest=(26.0, 10.0), hip=(0.0, 0.0), arch=-7.0, pawN=(46.0, 0.0), eye_pop=1.25, pupil_s=1.35, lid=0.0,
                                                                                    pupil=(0.7, 0.4), tongue=0.2, yaw=1.0, brow_ang=0.0)),
             (69, 8, 'out', None, dict(tail_a=4.0, tail_b=8.0, tail_tip=0.0)),
             (72, 6, 'out', 'CATCH UP hindquarters arrive, shoulders rise', dict(dxw=70.0, hip=(8.0, -10.0), chest=(20.0, 30.0), shrug=0.9, arch=6.0, pawN=(30.0, 0.0), pawF=(34.0, 0.0), hindN=(10.0, 0.0), head_dx=22.0, head_dy=18.0)),
             (84, 12, 'over', 'SETTLE at the rim; the tail tip gives him away', dict(dxw=130.0, chest=(24.0, 34.0), hip=(6.0, -6.0), arch=2.0, head_dx=28.0, head_dy=22.0, lid=0.3, tongue=0.45, eye_pop=1.0, pupil_s=1.1, shrug=0.6)),
             (88, 10, 'over', None, dict(tail_b=20.0, tail_tip=70.0)),
         ]),
    dict(n=3, name='Suspicion', start_dx=0, end=106, level=0.7,
         start=dict(CROUCH, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5), start_label='START drinking, eyes shut',
         moves=[
             (4, 3, 'io', None, dict(tongue=0.1)), (8, 3, 'io', None, dict(tongue=0.5)), (12, 3, 'io', None, dict(tongue=0.1)), (13, 1, 'lin', None, dict(tongue=0.5)),
             (15, 2, 'snap', 'FREEZE eyes open, ears back, tongue forgotten. Breathing stops', dict(eye_open=1.0, happy=0.0, lid=0.0, smile=0.2, ear_back=0.5, pupil=(0.0, 0.6), breath=0.0)),
             (28, 2, 'out', 'LISTEN after 11 dead frames only the ears move', dict(ear_back=0.8)),
             (40, 6, 'io', 'EYES FIRST pupils slide; head and body still frozen', dict(pupil=(-0.9, 0.1), lid=0.35)),
             (68, 26, 'io', 'SLOW TURN only the head turns. Body, paws and tongue do not move', dict(yaw=-0.85, head_rot=-8.0, head_dx=18.0, lid=0.45, brow_ang=10.0, brow_asym=0.9, smile=-0.3)),
             (76, 6, 'io', 'STARE eyes go further than the head', dict(pupil=(-0.95, -0.2), lid=0.55)),
             (82, 5, 'io', None, dict(tongue=0.0)), (84, 6, 'over', None, dict(tail_tip=90.0)),
             (98, 12, 'io', 'RECOVER head comes half-way back; breathing starts again', dict(yaw=-0.3, pupil=(-0.8, 0.0), head_rot=-3.0, ear_back=0.3, breath=1.0)),
             (100, 8, 'over', None, dict(tail_tip=40.0)),
         ]),
    dict(n=4, name='Sudden shock', start_dx=0, end=74, level=0.7,
         start=dict(WARY), start_label='START wary crouch',
         moves=[
             (10, 2, 'out', 'FLINCH two frames: he flattens, eyes pop', dict(chest=(24.0, 44.0), hip=(6.0, 6.0), sy=0.9, sx=1.11, eye_pop=1.3, lid=0.0, pupil=(0.0, 0.0), brow_ang=0.0, brow_asym=0.0)),
             (13, 3, 'snap', 'RECOIL up and backwards, back arched, legs stiff. Tail not yet', dict(y_up=52.0, dxw=-34.0, rot=-7.0, sy=1.08, sx=0.93, arch=44.0, chest=(4.0, -6.0), hip=(2.0, -4.0), shrug=0.0, pawN=(22.0, 10.0), pawF=(28.0, 8.0),
                                                                                                    hindN=(-20.0, 8.0), hindF=(-16.0, 6.0), head_dx=6.0, head_dy=-18.0, head_rot=-6.0, yaw=0.3, eye_pop=1.5, pupil_s=0.5, brow=16.0,
                                                                                                    mouth_open=0.85, ear_back=0.0, bristle=1.0, smile=-0.2)),
             (20, 3, 'in', 'LAND legs wide, body sinks', dict(y_up=0.0, dxw=-48.0, rot=0.0, sy=0.9, sx=1.11, arch=28.0, chest=(4.0, 12.0), hip=(2.0, 10.0), pawN=(28.0, 0.0), pawF=(32.0, 0.0), hindN=(-26.0, 0.0), hindF=(-20.0, 0.0), head_dy=-6.0)),
             (24, 4, 'out', 'REBOUND comes up out of the landing', dict(sy=1.03, sx=0.97, arch=36.0, chest=(2.0, -2.0), hip=(0.0, -4.0), head_dy=-14.0)),
             (24, 4, 'snap', None, dict(tail_a=104.0, tail_b=0.0, tail_tip=0.0, tail_puff=1.0)),
             (29, 5, 'io', 'TAIL arrives 4 frames after the landing, whips past upright and comes back', dict(tail_a=86.0, tail_b=6.0)),
             (36, 5, 'io', 'LOOK what was that? head turns back to see', dict(yaw=-0.6, pupil=(-0.8, 0.0), mouth_open=0.3, head_rot=-10.0)),
             (62, 24, 'io', 'RECOVER comes down slowly; the tail deflates last', dict(sy=1.0, sx=1.0, arch=14.0, chest=(0.0, 0.0), hip=(0.0, 0.0), head_dy=-8.0, mouth_open=0.1, eye_pop=1.25, bristle=0.3, hindN=(-32.0, 0.0), yaw=-0.2, head_rot=-4.0)),
             (70, 26, 'io', None, dict(tail_puff=0.4, tail_b=22.0)),
         ]),
    dict(n=5, name='Satisfaction', start_dx=0, end=126, level=0.06,
         start=dict(CROUCH, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5), start_label='START last lick, eyes shut',
         moves=[
             (6, 3, 'io', None, dict(tongue=0.0)),
             (14, 4, 'out', 'CHECK opens his eyes and looks into the empty bowl', dict(eye_open=1.0, happy=0.0, lid=0.3, pupil=(0.3, 0.7), smile=0.3)),
             (22, 3, 'io', 'HOPE one more lick, just in case', dict(tongue=0.45)), (26, 3, 'io', None, dict(tongue=0.0)),
             (42, 12, 'io', 'BREATH IN chest and head lift, back rounds', dict(chest=(10.0, -2.0), hip=(4.0, -2.0), shrug=0.2, arch=6.0, head_dx=8.0, head_dy=-14.0, head_rot=-12.0, eye_open=0.0, happy=1.0, smile=1.0)),
             (56, 12, 'out', 'SIT hips go down first; forelegs stay their natural length', dict(hip=(0.0, 36.0), chest=(-40.0, -2.0), arch=10.0, hindN=(44.0, 0.0), hindF=(44.0, 0.0), pawN=(-40.0, 0.0), pawF=(-38.0, 0.0), head_dx=-22.0, head_dy=2.0,
                                                                                                    head_rot=6.0, yaw=0.7, shrug=0.0)),
             (60, 12, 'over', None, dict(tail_a=-28.0, tail_b=30.0, tail_tip=0.0)),
             (66, 8, 'out', 'SHOULDERS sink next, belly rounds as he breathes out', dict(chest=(-42.0, 7.0), shrug=0.35, belly=1.0, arch=14.0)),
             (74, 8, 'out', 'HEAD drops after the shoulders', dict(head_dy=15.0, head_rot=11.0)),
             (78, 3, 'io', None, dict(tongue=0.35)), (83, 4, 'io', None, dict(tongue=0.0)),
             (86, 8, 'over', 'TAIL the tip curls up last', dict(tail_tip=75.0)),
             (108, 20, 'over', 'SETTLE lifts a little, eyes half open', dict(chest=(-41.0, 2.0), head_dy=8.0, head_rot=-5.0, belly=0.7, arch=10.0, shrug=0.1, eye_open=1.0, happy=0.0, lid=0.65, pupil=(0.2, 0.3), smile=0.8)),
             (110, 10, 'over', None, dict(tail_tip=40.0)),
             (116, 4, 'io', None, dict(lid=1.0)), (122, 5, 'io', None, dict(lid=0.65)),
         ]),
]

VERDICT = {1: 'Revise: strengthen noticing, the pause, the head tilt and the cautious weight shift',
           2: 'Keep direction: more anticipation and small involuntary movements before he gives in',
           3: 'Keep concept: body must freeze clearly while the head turns slowly',
           4: 'Keep concept: refine the recoil, the landing and the delayed tail',
           5: 'Keep concept: release of tension; head, shoulders and tail settle one after another'}
CHANGES = {1: 'New beats: eyes-only notice (2 f), a 10-frame pause with the weight rocked back, the head turn before any body move, a separate head tilt, then a 12-frame creep with the spine stretching. 96 frames, was 56.',
           2: 'New beats before he gives in: a sneaked glance, looking away, sniffing, lip lick with a paw lifting by itself, and pulling himself back. 98 frames, was 66.',
           3: 'The freeze is now 11 dead frames with breathing stopped, then only the ears, then only the eyes, then a 26-frame head turn. Nothing in the body is keyed after the freeze. 106 frames, was 80.',
           4: 'He now jumps backwards as well as up, lands with legs wide, sinks and rebounds. The tail starts 4 frames after the landing, whips past upright and returns. He then looks back. 74 frames, was 56.',
           5: 'He checks the empty bowl and tries one more lick first. Then hips at frame 56, shoulders at 66, head at 74, tail tip at 86. Forelegs stay natural length. 126 frames, was 84.'}
