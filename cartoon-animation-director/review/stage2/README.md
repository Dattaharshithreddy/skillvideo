# Stage 2 review package

**Status: REVIEW ONLY. Prepared 2026-11-11. Awaiting Harshith's review. Nothing here is approved or implemented.**

| | Status |
|---|---|
| Approved production models (`toon-slapstick/engine/chars.py`, `cast.py`) | **Unchanged** |
| Existing presets (`show.py`) | **Unchanged**; none added, removed or edited |
| Model baseline (`knowledge/model_baseline.json`) | **Unchanged**; drift check passes for all six characters |
| This folder | Temporary review material on the review branch. Not merged into main |

On every sheet: **green** frame = the approved model exactly as it is (sometimes posed with controls it already has). **Orange** frame = a proposal that exists only here. **Grey** frame = a superseded Stage 1 drawing or a silhouette, for comparison.

Three different kinds of evidence are in this package. They are not the same thing:

| Kind | What it is | What it proves |
|---|---|---|
| Key poses | Still drawings on the sheets | Whether a pose reads. Nothing about motion |
| Timing plans | Frame numbers written under each study and in `life_test.py` | Nothing until played |
| Animation test | `REVIEW_S2_6_laddu_life_test_animation.mp4`, rendered from those poses and that timing | It renders and the frames are as planned. **Whether it feels alive has not been judged by anyone.** I checked individual frames; I cannot judge motion in playback |

Rebuild: `python3 make_stage2.py` (sheets), `python3 make_stage2.py video` (sheets and the animation test). Writes only into this folder.

## Contents, against the seven items requested

| # | Requested | File |
|---|---|---|
| 1 | Revised Laddu profile head, separate head and body | `REVIEW_S2_1_laddu_profile_head_revised.png` |
| 2 | Revised Gaju profile with a subtle pink ear edge | `REVIEW_S2_2_gaju_profile_revised.png` |
| 3 | Refined hiding pose B | `REVIEW_S2_3_gaju_hiding_B_refined.png` |
| 4 | Revised small-hop and fan concepts | `REVIEW_S2_4_gaju_hops_and_fan.png` |
| 5 | Trunk alignment check | Table below; `REVIEW_S2_2b_gaju_trunk_on_revised_profile.png` |
| 6 | Five Laddu Character Life Test studies | `REVIEW_S2_6_1` to `_5_life_*.png`, plus the animation test |
| 7 | Remaining inconsistencies and engine limitations | This file |

## Part A: what changed from Stage 1

**Laddu profile head.** The head is now a separate component placed at the approved head anchor. The body under it is the approved side body with no change at all. Both ears are in the approved main fur colour. The muzzle is 8 shorter, the skull is deeper at the back and flatter on top, and the cheek fur has two points as on the approved head. The construction row shows the body alone, the head alone, and how far the head can move before a gap opens (22 forward is fine; 56 forward opens a gap, which is the D10 limit and is not fixed here).

**Gaju profile.** Same ear size. A narrow rim of the approved inner-ear pink shows along the front edge of the near ear. Both ears' outer surfaces are in the approved main skin colour; the darker tone is used only for the tail, as in the approved model. No new colour.

| Gaju's pink as a share of his area | |
|---|---|
| Approved front | 17% |
| Approved three-quarter | 16% |
| Stage 1 profile | 1% |
| **Revised profile, at rest** | **3%** |
| Revised profile, ear lifted | 11% |

**Movement.** Small hops: six key poses on the approved model with existing controls, volume kept, top of the hop 80 px, proposed 28 frames per hop. Fan: feet on the ground in every pose, no ear enlargement, no lift. Parachute and sail are deferred and not in this package. No new movement control was added.

**Hiding pose B.** Three refinements, all on the approved model with existing controls, upright posture kept, squash now keeps volume (0.82 tall by 1.22 wide).

**Expressions.** Your label-free reading matched all eight intended expressions. Recorded as a visual review by you, not a viewer test. Nothing is claimed to pass.

### Trunk alignment: approved front view against the revised profile

| Measure | Approved front | Revised profile | Result |
|---|---|---|---|
| Root height below head centre | 6 | 8 | Within 2 |
| Radius at the root, at the tip | 31, 12 | 31, 12 | Same drawing |
| Rest length along the centre line | 117 | 114 | 2% shorter |
| Lowest point of the rest trunk below head centre | 103 | 94 | Profile rest trunk hangs 9 higher |
| Wrinkle rings, nostrils, gripping finger | 8, 2, 1 | 8, 2, 1 | Same drawing |

The root was 10 too low in Stage 1; it is now within 2. To clear the eye it sits 8 further forward on the face.

## Part B: Laddu Character Life Test

Each study sheet has four rows:

1. **Model-sheet look** (green): the approved side model at rest, and the Stage 1 method of changing only the face.
2. **Existing controls only** (green): the most I could get from the approved model with the controls it already has.
3. **Proposed acting rig** (orange): five keys. Start, anticipation, action, reaction or overshoot, settle.
4. **Silhouettes** of row 3.

The acting rig is review-only. It keeps the approved head drawing, paws, tail stripes, colours and line weight. What is new is the body underneath: a spine that can curve, a chest and hips that move independently, legs with joints that reach for a paw position, shoulders that can rise above the back, and a tail with separate direction, curl and puff. The head remains a separate component laid over the body.

### What makes the proposed poses more alive, specifically

| Principle | Model-sheet look | Proposed poses |
|---|---|---|
| Line of action | Spine is a fixed horizontal block | Spine stretches (greed), arches (shock), goes upright (satisfaction) |
| Weight | Always evenly on four straight legs | Forward onto the front feet (curiosity, greed); back onto the haunches (satisfaction) |
| Asymmetry | Legs in matched pairs | One paw held in the air while he decides; one hind foot steps back after the shock |
| Lead and follow | Everything changes together | Eyes, then head, then chest; tail and ears 2 to 4 frames later |
| Contrast | Whole body or nothing | Suspicion: only the head moves, the rest is frozen |
| Tail as acting | One sway value | Low and loose, hooked like a question, straight and quivering, straight up and puffed |
| Involuntary movement | None | Breathing all the time; ear flick; tongue forgotten; tail tip twitch |

### Measured: how much of the outline changes between START and ACTION

| Study | Face only (Stage 1 method) | Approved model, existing controls | Proposed rig |
|---|---|---|---|
| 1 Curiosity | 7% | 21% | 47% |
| 2 Greed | 8% | 34% | 48% |
| 3 Suspicion | 0% | 10% | 10% |
| 4 Sudden shock | 1% | 83% | 84% |
| 5 Satisfaction | 0% | 64% | 69% |

Read this with care. It counts any outline change, including simply moving through space: the shock scores high in both columns because he leaves the ground. Suspicion is low by design. It shows that face-only acting barely moves the outline; it does not measure quality.

### My own assessment of the stills

- **Strongest:** greed (the stretch and the stalk), sudden shock (delayed tail), satisfaction (the sit and the sink).
- **Weakest:** curiosity. The lean is clearer than in the first draft but still modest.
- **Cannot be judged in stills:** suspicion. It depends entirely on the hold and the slow turn.
- The existing controls did better than I expected for crouching, by squashing the whole character. The cost is that the head and stripes squash too, which is off-model.

### Proposed timing (24 fps)

| Study | Total | Plan |
|---|---|---|
| 1 Curiosity | 56 f | hold 1-12; eyes dart 13-14; body stops by 16; head turn 17-22; overshoot 23-26; settle 27-38; hold to 56 with one ear flick at 46 |
| 2 Greed | 66 f | hold 1-10; nose lifts 11-18; two small sniffs 19-24; pulled forward 25-34, slow then fast; hind end catches up 35-40; settle 41-52; hold to 66 |
| 3 Suspicion | 80 f | lapping hold 1-12; freeze in 2 frames 13-14; dead hold 15-24; slow head turn 25-44; eyes slide 45-52; settle 53-66; hold to 80 |
| 4 Sudden shock | 56 f | hold 1-8; flatten 9-10; up 11-13; hang 14-17; land 18-20; tail starts at 21 and is fully up and puffed at 23, after he has landed; slow come-down to 44 |
| 5 Satisfaction | 84 f | hold 1-8; chest lifts 9-20; sits back 21-32; sinks 33-40; settles 41-64; slow blink 70-78 |

In the animation test the tail trails the body by 3 to 4 frames and the ears by 2. Characters are held on twos by the engine and switch to ones on fast moves.

### The animation test

`REVIEW_S2_6_laddu_life_test_animation.mp4`: 540 × 960, 24 fps, 342 frames, 14.25 s, silent, all five studies in order, with a REVIEW ONLY banner, study name, current key and frame counter burned in.

What I checked: it renders; the key frames match the sheets; the holds and moves fall on the planned frames; the tail in the shock study starts only after he has landed. What I did not and cannot check: whether it feels alive in motion. The automatic still-frame measure reads 66%, but the cat fills only a small part of a tall frame, which makes that measure unreliable here; no two consecutive frames are exactly identical.

## Engine limitations (approved Laddu model, existing controls)

| Wanted | Possible today? | What is possible instead |
|---|---|---|
| Curve the spine | No | Tilt or squash the whole character |
| Lower the chest while the rump stays up | No | Whole-body squash, which also squashes the head and stripes |
| Shift weight forward or back | No | Slide the whole character |
| Sit down in side view | No | Cut to the approved front sitting drawing; it pops between two drawings (study 5, row 2) |
| Pose hind legs one at a time in side view | No | Walk cycle only |
| Fold a foreleg at the elbow | No | Move the paw; the leg stays a soft curve |
| Tail direction, curl, puff | No | One swing value |
| Move one ear | No | Both ears share one control |
| Head far forward on a stretched neck | Limited | Gap opens beyond about 40 to 56 forward (D10) |
| Fur standing up | No | |
| Breathing | No | |
| Head turn, tilt, nod | **Yes** | `yaw`, `head_rot`, `pitch` |
| Eyes, lids, brows, pupils, mouth, tongue | **Yes** | |
| One fore paw lifted | **Yes** | `armL`, `armR` |
| Overlap in time (tail and ears late) | **Yes** | Key them on later frames |

So: timing, lead-and-follow, head acting and face acting need no engine change. Body acting does.

## Remaining inconsistencies

### Stripe movement
1. On the acting rig the three back stripes ride on the spine, so they slide when it bends. At rest they sit up to 10 units from their approved positions.
2. With existing controls, a whole-body squash squashes the stripes and the head with it.

### Paw and limb proportions
3. All paws use the approved paw drawing and size, four visible toes.
4. The Stage 1 "pressing" paw (24 × 9 against the approved 19 × 11) was not revised and is still off-model.
5. **On the rig the forelegs change length.** Sitting, the shoulder-to-paw reach is 125 against a natural 92, so the leg is drawn about a third longer. Either this stretch is accepted as cartoon licence, or the sitting pose must bring the chest lower.
6. At rest the rig is the same height as the approved side model (256) but 346 long against 322, and its outline overlaps the approved one by 85%. The body is a new drawing, not the approved body.

### Far-side colour
7. Fixed: both of Laddu's ears are in the main fur colour; both of Gaju's ears are in the main skin colour.
8. Laddu's far legs still use the approved darker far-side fur, as the approved side model does.
9. Gaju's far arm and far leg are now the same colour as the near ones, which follows the approved front model but gives less depth in profile. Your call.

### Head
10. The approved head is a front-facing drawing. On the side body with `yaw` at full it becomes a three-quarter head with the features bunched at one edge. In the life test he therefore looks towards the bowl with a three-quarter head, not a profile.
11. The revised profile head is still a proposal and was not used in the life test.

### Expression readability
12. Your reading matched all eight Stage 1 expressions. That is one informed reviewer, not a blind test.
13. Suspicion is weaker in profile, because a one-brow expression needs two eyes.
14. None of the life-test poses has been shown to anyone without labels.

### Gaju
15. The profile body depth (124) is still my estimate.
16. The rest trunk hangs 9 higher in profile than in the front view.
17. Row 3 of the fan sheet depends on the profile, which is not approved.

## Questions for this review

1. Watching the animation test: does Laddu think, hesitate and react, or is he still a toy? Which study works and which does not?
2. Is the acting rig recognisably the same cat?
3. Foreleg stretch when sitting: acceptable or not?
4. Gaju's pink rim: enough, too much, or too little?
5. Hiding: B1, B2 or B3?
6. Gaju's far limbs in profile: same colour as near, or darker?
