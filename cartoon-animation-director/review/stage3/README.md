# Stage 3: Laddu Character Life Test, revised

**Status: REVIEW ONLY. Prepared 2026-11-11. Awaiting Harshith's review. Nothing is approved, merged or implemented.**

Production character code, existing presets, approved models and `model_baseline.json` are unchanged. The drift check passes for all six characters. Everything here is on the review branch.

Colours on the sheets: **grey** = the current version you reviewed (Stage 2). **Orange** = the revised proposal. **Green** = the approved production model.

Three kinds of evidence, kept apart:

| Kind | Where | Status |
|---|---|---|
| Key poses | The comparison sheets. Tiles are frames taken from the animation test | Proposals |
| Timing | Frame numbers on each sheet and in `life_test3.py` | Proposals |
| Animation tests | The two videos | Rendered and checked frame by frame by me. **Not judged in motion by anyone yet** |

## Files

| File | Shows |
|---|---|
| `REVIEW_S3_laddu_life_test_current_vs_revised.mp4` | Side by side: current on the left, revised on the right, all five studies, 1080 × 960, 500 frames, 20.8 s, silent |
| `REVIEW_S3_laddu_life_test_revised.mp4` | Revised only, 540 × 960 |
| `REVIEW_S3_0_identity_and_proportion_fixes.png` | The outline and foreleg investigations |
| `REVIEW_S3_1` to `_5_*_current_vs_revised.png` | One comparison sheet per study, with your direction, what changed, and timing notes |

In the side-by-side video the shorter clip holds its last frame while the longer one finishes.

## The two investigations

| | Approved side model | Stage 2 rig | Stage 3 rig |
|---|---|---|---|
| Height × length at rest | 256 × 322 | 256 × 346 | 256 × 322 |
| Outline overlap with the approved model | 100% | 86% | **98%** |
| Foreleg length when sitting, against natural | | 133% | **97%** |

**Outline.** The Stage 2 rig drew a new tube-shaped body. The Stage 3 rig carries the approved body outline, its belly patch and its three stripes on a spine. With the spine at rest it is the approved drawing; when the spine bends, that same outline bends. The remaining 2% is the foreleg, which now has an elbow, and the breathing.

**Forelegs.** I had raised his chest when he sat, so the legs had to stretch. A sitting cat keeps its shoulders at about standing height and drops its hips. Corrected. Across all labelled keys the longest reach is now 115%, for three frames in the shock recoil where the legs are thrown out stiff. Everything else is at or under natural length. Say if you want that capped too.

The head is a separate component laid over the body, as before.

## What changed in each study

| Study | Your direction | What I changed | Frames |
|---|---|---|---|
| 1 Curiosity | Revise: notice, pause, tilt, cautious shift | Eyes-only notice (2 f); a 10-frame pause with the weight rocked back and one paw in the air; the head turns before the body moves; a separate head tilt; a 12-frame creep with the spine stretching; hesitation; recovery | 96, was 56 |
| 2 Greed | Keep; more anticipation and involuntary movement | Before he gives in: a sneaked glance, looking away, sniffing, a lip lick with a paw lifting by itself, pulling himself back | 98, was 66 |
| 3 Suspicion | Keep; clear freeze, slow head turn | 11 dead frames with breathing stopped; then only the ears; then only the eyes; then a 26-frame head turn. Nothing in the body is keyed after the freeze | 106, was 80 |
| 4 Sudden shock | Keep; recoil, landing, delayed tail | He jumps backwards as well as up; lands with legs wide, sinks, rebounds; the tail starts 4 frames after the landing, whips past upright and returns; then he looks back | 74, was 56 |
| 5 Satisfaction | Keep; release of tension, staggered settle | He checks the empty bowl and tries one more lick; then hips at frame 56, shoulders at 66, head at 74, tail tip at 86 | 126, was 84 |

## Timing notes (frame each key is reached, 24 fps)

| Study | Keys |
|---|---|
| 1 | 1 start · 15 notice · 19 pause, held to 28 · 35 look · 47 think · 65 cautious shift · 71 hesitate · 83 recover · ear flick 89-93 · end 96 |
| 2 | 1 start · 11 glance · 19 deny · 31 sniff, four small bobs to 39 · 43 tell · 53 resist · 67 gives in · 73 catch up · 85 settle · end 98 |
| 3 | 1 start, lapping · 16 freeze, dead hold to 26 · 29 listen · 41 eyes first · 69 slow turn (26 f) · 77 stare · 99 recover · end 106 |
| 4 | 1 start · 11 flinch (2 f) · 14 recoil (3 f) · 21 land · 25 rebound · 30 tail · 37 look · 63 recover · end 74 |
| 5 | 1 start · 15 check · 23 hope · 43 breath in · 57 sit · 67 shoulders · 75 head · 87 tail · 109 settle · blink 113-122 · end 126 |

The engine holds drawings for two frames and switches to single frames on fast moves, so the flinch and recoil play on ones.

## Existing controls or engine change?

| Movement used in the revised studies | Existing approved controls | Needs an engine change |
|---|---|---|
| Eyes move before the head; pupils, lids, brows | Yes | |
| Head turn, tilt, nod | Yes | |
| Holds, pauses, dead freeze, all timing | Yes | |
| Tail and ears arriving late | Yes (key them later) | |
| Tongue, mouth, blink | Yes | |
| One fore paw lifted or stepping | Yes | |
| Jump, backward recoil, whole-body squash and stretch | Yes | |
| Weight rocking back or forward (chest and hips separately) | | Yes |
| Spine stretching, arching, rounding | | Yes |
| Chest low with rump high (the stalk) | | Yes |
| Shoulders rising above the back | | Yes |
| Sitting down in side view | | Yes (today: a cut to the front drawing) |
| Hind feet planted or stepping one at a time | | Yes |
| Foreleg folding at an elbow | | Yes |
| Tail hook, straight quiver, upright, puff | | Yes (today: one swing value) |
| One ear at a time | | Yes; not used here either, both ears still move together |
| Fur standing on end | | Yes |
| Breathing, belly rounding | | Yes |

Roughly: the thinking (notice, pause, look, hesitate) is timing and head acting and needs no engine change. The weight and the body (shift, stalk, sit, arch, tail) do.

## Still inconsistent or unresolved

1. Stripes ride on the spine and stretch or bunch with it. At rest they are now in their approved positions.
2. Shock recoil: forelegs at 115% for three frames (above).
3. The head is the approved front-facing head turned with `yaw`, so he looks at the bowl three-quarter, not in profile. The revised profile head is still a separate proposal and is not used here.
4. Both ears share one control.
5. During the whole-body squash on the flinch and landing, the head squashes too. It lasts 2 to 3 frames.
6. No expression or study has been shown to a viewer without labels.
7. The earlier still-frame measure is not reliable for this framing; I have not used it as evidence.

## Questions for this review

1. Side by side, is the revised Laddu more convincing in each study? Which still fail?
2. Suspicion: is the freeze long enough, and the head turn slow enough, in playback?
3. Shock: is the tail delay readable, and is the brief leg stretch acceptable?
4. Does he remain unmistakably the same cat throughout?
