# Stage 1 character reference review

**Status: REVIEW ONLY. Prepared 2026-11-11. Awaiting Harshith's review. Nothing here is approved.**

Everything in this folder is a temporary review image or the code that draws it. None of it is a production asset.

| | Where | Status |
|---|---|---|
| Approved production models | `toon-slapstick/engine/chars.py`, `cast.py`, `show.py` | **Unchanged.** Not edited in this stage |
| Model baseline | `knowledge/model_baseline.json` | **Unchanged.** Drift check passes for all six characters |
| Existing presets | `show.py` (CALM … SLEEP) | **Unchanged.** No preset added, removed or edited |
| Review sheets | `REVIEW_S1_*.png` in this folder | Temporary. Every sheet carries a red REVIEW ONLY banner |
| Proposal drawing code | `review_models.py`, `sheetkit.py`, `make_stage1.py` in this folder | Temporary. Subclasses the production classes; does not modify them |

On every sheet a **green** frame marked PRODUCTION is the approved model exactly as it is today (sometimes posed with controls it already has). An **orange** frame marked PROPOSAL is a new drawing that exists only here.

Rebuild: `python3 make_stage1.py` (writes only into this folder).

## The sheets

| File | Shows |
|---|---|
| `REVIEW_S1_1a_laddu_profile_head.png` | Approved front head, today's side view, proposed true profile head, with guide lines |
| `REVIEW_S1_1b_laddu_crouch_lap.png` | Five key poses: walk in, sniff, crouch, lap out, lap in |
| `REVIEW_S1_1c_laddu_paws.png` | Six paw shapes, four visible toes each |
| `REVIEW_S1_2a_gaju_views.png` | Approved front and three-quarter, proposed upright profile, all-fours alternative |
| `REVIEW_S1_2b_gaju_trunk.png` | Nine trunk positions on the proposed profile |
| `REVIEW_S1_2c_gaju_hiding.png` | Three ways to "hide" behind a pot that is far too small |
| `REVIEW_S1_3_gaju_movement.png` | Fan, parachute, sail, small hops |
| `REVIEW_S1_4_pilot_expressions.png` | Bliss, suspicion, slow burn, take for Laddu; four pilot beats for Gaju |

These are key poses and reference stills. They are not animation, and they do not show that any of this moves well.

## Measurements against the approved model

| Check | Approved | Proposal | Result |
|---|---|---|---|
| Laddu standing height, side | 256 | 256 | Same |
| Laddu length, side | 322 | 368 | Longer: the muzzle and whiskers now point forward |
| Gaju standing height | 282 | 282 | Same |
| Gaju width | 346 (front, ears out) | 266 (profile) | Narrower, as expected side-on |
| Share of pixels in the character's named colours, Laddu | 91% | 93% | Same palette |
| Share of pixels in named colours, Gaju | 89% | 88% | Same palette |
| Gaju's pink as a share of his area | 17% front, 16% three-quarter | **1% in profile at rest**, 10% with the ear lifted | **Large difference** |
| `GajuReview` with ear size 1 against production Gaju | | | Identical outline |
| Digit counts | Laddu four toes, Gaju three nails | Same on every proposal | Consistent |

## Inconsistencies with the approved model

### Laddu
1. There is no approved side-view head, so the whole profile outline is new: skull shape, muzzle length, cheek fur shown only at the back of the jaw.
2. The far ear is drawn in the darker "far side" fur colour. The approved head draws both ears in the main fur colour.
3. The neck is drawn as one outline with the body. In the approved model the head is a separate piece laid over the body. This is the idea behind the D10 fix, but it is itself unapproved.
4. In the crouch the forelegs fold at a visible elbow. The approved side body only has straight forelegs. Back stripes slide as the spine drops.
5. The paw underside with pads is new information; the approved model never shows a sole.
6. The pressing paw is wider and flatter than the model paw (24 × 9 against 19 × 11). Intended as a squash, but it is off-model.
7. With one eye visible, a one-brow expression loses its asymmetry. Suspicion reads weaker in profile than from the front.

### Gaju
1. **Pink almost disappears in profile** (1% against 17%). The near ear shows its plain outer side. His pink ears are a large part of how he is recognised.
2. The far ear is drawn in the darker skin tone. The approved model draws both ears in the main skin colour and uses the darker tone only for the tail.
3. The mouth is visible in profile. In the approved front view the trunk hides it. This helps acting but it is a difference.
4. Body depth in profile (124 wide) is my estimate. There is no approved side reference to check it against.
5. The trunk root sits 10 units lower on the face than in the front view, so that it clears the eye.
6. Parachute and sail enlarge the ears to 1.35 to 1.4 times. That is off-model on purpose and would need a rule for how long it may last.
7. The all-fours alternative is not the approved posture. The approved Gaju stands upright with his front legs hanging like arms. My first profile draft put him on all fours; I corrected it and kept the all-fours version only as a labelled alternative.
8. Hiding poses A and B and the hop poses use the approved model only, but their squash values do not keep volume exactly (width × height between 0.78 and 1.05).

### Expressions
9. None has been tested on anyone. No expression here is claimed to pass.
10. Laddu's approved head rests with half-lowered lids. Every recipe sets the lids explicitly; the preset values are untouched.

## Corrections to my earlier documents

1. **View audit.** I reported that heads always face the camera. That was incomplete: the approved models already have a head-turn control (`yaw`) that gives a three-quarter head. I had only tested the body-turn control. What is really missing is a true profile and a back view.
2. **Twos.** `Animation_Fundamentals.md` said the engine has no "on twos" option. It does: characters hold each pose for two frames by default and switch to single frames on fast moves.

Both documents have been corrected.

## Questions for the review

1. Laddu's profile head: is it recognisably the same cat?
2. Gaju in profile: acceptable with the pink hidden, or should the near ear show some pink at rest?
3. Movement: which of fan, parachute, sail and small hops should become his style? Any to drop?
4. Hiding: A, B or C?
5. Expressions: can you name each one with the labels covered?
