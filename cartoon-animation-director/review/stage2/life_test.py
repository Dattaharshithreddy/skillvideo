"""REVIEW ONLY. Data for the Laddu Character Life Test: key poses and proposed timing.

Each study is a list of keys. A key is (frame, ease, label, changes); dur gives how many frames each move into a key takes,
so everything before that is a hold. Poses accumulate: every key
keeps everything from the key before it and applies its own changes. Frame numbers are at 24 fps.
Two pseudo-controls: dxw moves the whole cat along the floor, y_up lifts him off it.
PROPOSAL = poses for the review-only acting rig. EXISTING = the best I can do with the approved
model and the controls it already has.
"""

CROUCH = dict(chest=(24.0, 34.0), hip=(6.0, -6.0), shrug=0.6, pawN=(30.0, 0.0), pawF=(34.0, 0.0), hindN=(10.0, 0.0),
              head_dx=28.0, head_dy=22.0, yaw=1.0, tail_a=30.0, tail_b=70.0, tail_tip=40.0)
WARY = dict(CROUCH, eye_open=1.0, happy=0.0, lid=0.55, smile=-0.3, ear_back=0.3, yaw=-0.3, head_rot=-3.0, head_dx=18.0,
            brow_ang=10.0, brow_asym=0.9, pupil=(-0.8, 0.0), tongue=0.0)

STUDIES = [
    dict(n=1, name='Curiosity', dur=[4, 6, 4, 12], intent='He is idling. Something at the edge of his eye: milk.', start_dx=-130, end=56, level=1.0,
         proposal=[
             (0, 'lin', 'START idle, mid-step, looking away',
              dict(yaw=-0.2, pupil=(-0.3, 0.1), tail_a=-8.0, tail_b=55.0, tail_tip=20.0, pawN=(16.0, -12.0), wristN=24.0, chest=(-4.0, 0.0), head_rot=-3.0)),
             (16, 'out', 'ANTICIPATION eyes go first, ears flick, he stops',
              dict(pupil=(0.95, 0.0), earflick=1.0, chest=(-8.0, 2.0), head_dx=-2.0, lid=0.2)),
             (22, 'snap', 'ACTION head turns and tilts, chest leans, tail hooks',
              dict(yaw=0.95, head_rot=15.0, head_dx=24.0, head_dy=8.0, lid=0.0, eye_pop=1.15, brow=8.0, chest=(22.0, 6.0), hip=(4.0, -2.0),
                   tail_a=55.0, tail_b=30.0, tail_tip=95.0, earflick=0.0, pupil=(0.6, 0.2))),
             (26, 'out', 'OVERSHOOT leans too far, rump lifts',
              dict(chest=(34.0, 12.0), head_dx=34.0, head_dy=12.0, hip=(10.0, -12.0), tail_tip=140.0, head_rot=19.0)),
             (38, 'over', 'SETTLE eases back, head tilts the other way, paw comes down',
              dict(chest=(14.0, 2.0), head_dx=16.0, head_dy=0.0, head_rot=-11.0, hip=(0.0, 0.0), pawN=(30.0, 0.0), wristN=0.0, tail_tip=110.0, eye_pop=1.05, lid=0.1)),
         ],
         existing=[
             dict(yaw=-0.2, pupil=(-0.3, 0.1), tail=-0.5, armR=(10.0, -10.0)),
             dict(pupil=(0.95, 0.0), ear_back=0.3),
             dict(yaw=0.95, head_rot=10.0, head_dx=12.0, lid=0.0, eye_pop=1.15, brow=8.0, tail=1.0, ear_back=0.0),
             dict(head_dx=18.0, rot=3.0),
             dict(head_rot=-8.0, head_dx=10.0, armR=(16.0, 0.0), rot=0.0),
         ],
         face_only=dict(yaw=0.95, lid=0.0, eye_pop=1.15, brow=8.0),
         timing='hold 1-12 (tail sways) | eyes dart 13-14 on ones, body stops by 16 | head turn 17-22 (6 f) | overshoot 23-26 | settle 27-38 | '
                'moving hold to 56 with one ear flick at 46. Tail follows the head by 3 frames.',
         alive='The eyes move before the head, and the head before the chest. One paw hangs in the air while he decides. '
               'The tail asks the question (hook), then answers late.'),
    dict(n=2, name='Greed', dur=[8, 10, 6, 12], intent='He pretends not to care. His nose does not agree.', start_dx=-130, end=66, level=1.0,
         proposal=[
             (0, 'lin', 'START plays it cool, eyes away from the bowl', dict(yaw=0.5, lid=0.4, pupil=(-0.4, 0.0), head_rot=-4.0, tail_a=20.0, tail_b=80.0)),
             (18, 'io', 'ANTICIPATION nose lifts, sniffs, eyes half shut',
              dict(head_dy=-12.0, head_rot=-12.0, chest=(-8.0, -4.0), yaw=0.9, lid=0.55, pupil=(0.5, -0.3), tail_tip=30.0)),
             (34, 'in', 'ACTION the nose pulls him: head and chest go, hind feet stay',
              dict(head_dx=30.0, head_dy=16.0, head_rot=12.0, chest=(26.0, 10.0), pawN=(46.0, 0.0), eye_pop=1.25, pupil_s=1.35, lid=0.0,
                   pupil=(0.7, 0.4), tongue=0.2, tail_a=4.0, tail_b=8.0, tail_tip=0.0, yaw=1.0)),
             (40, 'out', 'REACTION hindquarters catch up, shoulders rise: the stalk',
              dict(dxw=70.0, hip=(8.0, -10.0), chest=(20.0, 30.0), shrug=0.9, pawN=(30.0, 0.0), pawF=(34.0, 0.0), hindN=(10.0, 0.0),
                   head_dx=22.0, head_dy=18.0, tail_b=20.0)),
             (52, 'over', 'SETTLE at the rim, chest low, tail tip gives him away',
              dict(dxw=130.0, chest=(24.0, 34.0), hip=(6.0, -6.0), head_dx=28.0, head_dy=22.0, lid=0.3, tongue=0.45, tail_tip=70.0,
                   eye_pop=1.0, pupil_s=1.1, shrug=0.6)),
         ],
         existing=[
             dict(yaw=0.5, lid=0.4, pupil=(-0.4, 0.0)),
             dict(head_dy=-10.0, head_rot=-10.0, yaw=0.9, lid=0.55),
             dict(head_dx=20.0, head_dy=10.0, head_rot=10.0, armR=(30.0, 0.0), eye_pop=1.25, pupil_s=1.35, lid=0.0, tongue=0.2, sx=1.06, sy=0.95, yaw=1.0),
             dict(dxw=70.0, sy=0.86, sx=1.14),
             dict(dxw=130.0, tongue=0.45, lid=0.3, eye_pop=1.0),
         ],
         face_only=dict(yaw=1.0, eye_pop=1.25, pupil_s=1.35, lid=0.0, tongue=0.2),
         timing='hold 1-10 | nose lifts 11-18, two small sniffs on twos 19-24 | pulled forward 25-34, slow start then fast | '
                'hind end catches up 35-40 | settle 41-52 | hold to 66 with the tail tip twitching every 6 frames.',
         alive='The body stretches because the front leaves before the back agrees. The stretch is in the spine, not in a scale. '
               'Shoulders rise above the back line in the stalk. Hind feet stay planted for 10 frames.'),
    dict(n=3, name='Suspicion', dur=[2, 20, 8, 14], intent='Mid-drink, he feels watched.', start_dx=0, end=80, level=0.7,
         proposal=[
             (0, 'lin', 'START drinking, eyes shut', dict(CROUCH, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5)),
             (14, 'snap', 'ANTICIPATION freeze: eyes open, ears back, tongue forgotten',
              dict(eye_open=1.0, happy=0.0, lid=0.0, smile=0.2, ear_back=0.5, pupil=(0.0, 0.6), breath=0.0)),
             (44, 'io', 'ACTION only the head turns. Body, paws and tongue do not move',
              dict(yaw=-0.85, head_rot=-8.0, head_dx=18.0, lid=0.45, brow_ang=10.0, brow_asym=0.9, pupil=(-0.9, 0.1), smile=-0.3)),
             (52, 'io', 'REACTION eyes slide further, tongue slips back in, tail tip starts',
              dict(pupil=(-0.95, -0.2), lid=0.55, tongue=0.0, tail_tip=90.0)),
             (66, 'io', 'SETTLE head comes half-way back, still wary', dict(yaw=-0.3, pupil=(-0.8, 0.0), head_rot=-3.0, tail_tip=40.0, ear_back=0.3, breath=1.0)),
         ],
         existing=[
             dict(sy=0.86, sx=1.14, head_dx=18.0, head_dy=16.0, yaw=1.0, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5),
             dict(eye_open=1.0, happy=0.0, lid=0.0, ear_back=0.5, smile=0.2),
             dict(yaw=-0.85, head_rot=-8.0, lid=0.45, brow_ang=10.0, brow_asym=0.9, pupil=(-0.9, 0.1), smile=-0.3),
             dict(lid=0.55, tongue=0.0, tail=1.0),
             dict(yaw=-0.3),
         ],
         face_only=dict(lid=0.45, brow_ang=10.0, brow_asym=0.9, pupil=(-0.9, 0.1), smile=-0.3),
         timing='lapping hold 1-12 | freeze in 2 frames 13-14, then a dead hold 15-24 | slow head turn 25-44 (20 f, on twos) | '
                'eyes slide 45-52 | settle 53-66 | hold to 80, tail tip only.',
         alive='Contrast: everything stops except one part. The stillness of the body is the acting. '
               'The tongue left hanging says he forgot what he was doing.'),
    dict(n=4, name='Sudden shock', dur=[2, 3, 3, 24], intent='Something touches him.', start_dx=0, end=56, level=0.7,
         proposal=[
             (0, 'lin', 'START wary crouch', dict(WARY)),
             (10, 'out', 'ANTICIPATION two frames only: he flattens', dict(chest=(24.0, 44.0), hip=(6.0, 6.0), sy=0.9, sx=1.11)),
             (13, 'snap', 'ACTION straight up, back arched, legs stiff. The tail has not reacted yet',
              dict(y_up=46.0, sy=1.08, sx=0.93, arch=34.0, chest=(4.0, -6.0), hip=(2.0, -4.0), shrug=0.0, pawN=(20.0, 10.0), pawF=(26.0, 8.0),
                   hindN=(-18.0, 8.0), hindF=(-14.0, 6.0), head_dx=6.0, head_dy=-18.0, head_rot=-6.0, yaw=0.3, lid=0.0, eye_pop=1.5, pupil_s=0.5,
                   brow=16.0, mouth_open=0.85, ear_back=0.0, pupil=(0.0, 0.0), bristle=1.0, brow_ang=0.0, brow_asym=0.0, smile=-0.2)),
             (20, 'out', 'REACTION lands; four frames late the tail shoots up and puffs',
              dict(y_up=0.0, sy=0.94, sx=1.06, arch=26.0, chest=(4.0, 6.0), pawN=(20.0, 0.0), pawF=(26.0, 0.0), hindN=(-18.0, 0.0), hindF=(-14.0, 0.0),
                   tail_a=88.0, tail_b=4.0, tail_tip=0.0, tail_puff=1.0)),
             (44, 'io', 'SETTLE comes down slowly; the tail deflates last',
              dict(sy=1.0, sx=1.0, arch=16.0, chest=(0.0, 0.0), head_dy=-8.0, mouth_open=0.2, eye_pop=1.3, tail_puff=0.55, tail_b=20.0, bristle=0.4, hindN=(-26.0, 0.0))),
         ],
         existing=[
             dict(sy=0.86, sx=1.14, head_dx=18.0, head_dy=16.0, yaw=-0.3, lid=0.55, brow_ang=10.0, brow_asym=0.9, pupil=(-0.8, 0.0), smile=-0.3),
             dict(sy=0.78, sx=1.24),
             dict(y_up=46.0, sy=1.15, sx=0.88, eye_pop=1.5, pupil_s=0.5, lid=0.0, mouth_open=0.85, head_dy=-12.0, head_dx=6.0, yaw=0.3, ear_back=0.0,
                  brow=16.0, brow_ang=0.0, brow_asym=0.0, pupil=(0.0, 0.0)),
             dict(y_up=0.0, sy=0.9, sx=1.1, tail=1.5),
             dict(sy=1.0, sx=1.0, mouth_open=0.2, eye_pop=1.3),
         ],
         face_only=dict(eye_pop=1.5, pupil_s=0.5, lid=0.0, mouth_open=0.85, brow=16.0),
         timing='hold 1-8 | flatten 9-10 (2 f, ones) | up 11-13 (3 f, ones) | hang 14-17 | land 18-20 | the tail only starts at 21 and is straight up and '
                'fully puffed at 23, after he has landed | slow come-down 21-44, tail deflates last.',
         alive='Fast against slow: 5 frames up, 24 frames down. The body reacts first and the tail 4 frames later, so the shock travels through him. '
               'The arch is in the spine; the legs go stiff and straight.'),
    dict(n=5, name='Satisfaction', dur=[12, 12, 8, 24], intent='The bowl is empty. Nothing left to want.', start_dx=0, end=84, level=0.06,
         proposal=[
             (0, 'lin', 'START last lick, eyes shut', dict(CROUCH, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5)),
             (20, 'io', 'ANTICIPATION lifts his chest and head: a breath in',
              dict(chest=(10.0, 4.0), hip=(4.0, -2.0), shrug=0.2, head_dx=8.0, head_dy=-14.0, head_rot=-12.0, tongue=0.0)),
             (32, 'out', 'ACTION sits back on his haunches, breath out, belly rounds',
              dict(hip=(-2.0, 36.0), chest=(-40.0, -34.0), hindN=(46.0, 0.0), hindF=(46.0, 0.0), pawN=(-6.0, 0.0), pawF=(-2.0, 0.0), head_dx=-26.0, head_dy=6.0,
                   head_rot=8.0, belly=0.6, tongue=0.35, yaw=0.7, tail_a=-28.0, tail_b=30.0, tail_tip=0.0, shrug=0.0)),
             (40, 'out', 'OVERSHOOT sinks past the pose, tail tip curls up last',
              dict(chest=(-44.0, -24.0), head_dy=14.0, belly=1.0, sy=0.97, sx=1.03, tongue=0.0, tail_tip=75.0)),
             (64, 'over', 'SETTLE lifts a little, eyes half open, done',
              dict(chest=(-42.0, -30.0), head_dy=8.0, head_rot=-5.0, belly=0.7, sy=1.0, sx=1.0, eye_open=1.0, happy=0.0, lid=0.65, pupil=(0.2, 0.3), smile=0.8, tail_tip=40.0)),
         ],
         existing=[
             dict(sy=0.86, sx=1.14, head_dx=18.0, head_dy=16.0, yaw=1.0, eye_open=0.0, happy=1.0, smile=1.0, tongue=0.5),
             dict(sy=0.95, sx=1.04, head_dy=-10.0, head_rot=-12.0, tongue=0.0),
             dict(face=0.0, sy=1.0, sx=1.0, head_dx=0.0, head_dy=0.0, head_rot=8.0, yaw=0.0, tongue=0.35),
             dict(sy=0.96, sx=1.04, tongue=0.0),
             dict(sy=1.0, sx=1.0, head_rot=-5.0, eye_open=1.0, happy=0.0, lid=0.65, smile=0.8),
         ],
         face_only=dict(eye_open=0.0, happy=1.0, smile=1.0),
         timing='hold 1-8 | chest lifts 9-20 (slow) | sits back 21-32 | sinks 33-40 | settles 41-64 | slow blink 70-78, hold to 84.',
         alive='Weight moves from the front feet to the haunches, then keeps going past the pose and comes back. '
               'The belly rounds as he breathes out. The tail is the last thing to arrive.'),
]

LAG = dict(tail_a=3, tail_b=3, tail_tip=4, tail_puff=3, ear_back=2, earflick=0)     # follow-through: frames these controls trail the body by


def cumulative(keys):
    """Full pose at each key: every key keeps what came before."""
    out, cur = [], {}
    for k in keys:
        ch = k[3] if isinstance(k, tuple) else k
        cur = dict(cur); cur.update(ch)
        out.append(cur)
    return out
