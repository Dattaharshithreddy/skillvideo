# Pilot project: "The Milk Bowl"

A small original test of the whole pipeline. About 20 seconds, vertical 1080x1920, 24 fps, silent with music and effects.
It replaces quantity with one piece made properly.

## Story (three shots)

1. **Setup (wide, 4 s).** Evening in Ammamma's kitchen. A steel bowl of milk on the floor by the stove. A note on the wall:
   a funny original Telugu line about the milk being counted. Laddu the cat strolls in, in profile.
2. **The drink (close, side view, 10 s).** He sniffs, crouches, laps. Bliss. From off-screen, the tip of Gaju's trunk creeps
   along the floor, dips into the far side of the bowl, and the milk level starts to fall faster than the cat can lap.
   The cat notices the level, follows the trunk with his eyes, slow burn, then puts one paw on the trunk. The trunk freezes.
3. **Pay-off (medium, 6 s).** Pull back: Gaju is "hiding" behind a pot far too small. Take. The trunk sneezes the milk back
   all over the cat. Both freeze, look at the empty bowl, then at the door, where Bheemu's shadow appears. They share one
   look and both point at each other. Iris out.

## What it tests

| Stage | Tested by |
|---|---|
| Character consistency | Cat and elephant in new poses (crouch, hiding) |
| Staging | Profile floor shot for drinking; closer shot for small action |
| Key poses and silhouettes | Crouch, lap, slow burn, take |
| Overlap and secondary motion | Tail, ears, trunk, milk surface |
| Slapstick structure | Setup, intention, unexpected, reaction, topper, warm end |
| Sound | Rhythm of laps, silence before the sneeze |
| QC | Full rubric and report |

## New drawings needed

- Cat crouching pose in profile (chest low, rump high, elbows out) and a lean control so the head never detaches.
- Bowl prop with milk level and ripples.
- Gaju squeezed behind a small pot (hiding pose).
- Kitchen floor-level background framing.

## Acceptance criteria (all measurable)

1. `qc_frames.py video` passes: 1080x1920, 24 fps, audio and video within 0.1 s, no missing frames.
2. Rubric total at least 23 of 26, no zeros (`07-qc-rubric.md`).
3. Silhouette sheet of the six key poses: each scored 2 by Harshith or by a second reviewer.
4. No frame where a character is cut by the frame edge or has a detached part (checked by stepping every 4th frame).
5. Every action has at least four phases (anticipation, action, overshoot, settle); verified from the key list.
6. Loose parts (tail, ears, trunk) have key frames offset from the body by 2-4 frames; verified from the key list.
7. Lap rhythm between 3 and 5 laps per second.
8. The reaction pose after the sneeze is held at least 12 frames.
9. A first-time viewer retells the story in one or two sentences (Harshith tests this on one person).
10. Harshith judges the sound acceptable by ear.

## Automated, tool-dependent, human

| Automated by Claude | Needs a connected tool | Needs a human |
|---|---|---|
| Script, timing plan, x-sheet | Reference study (desktop browser) | Judging appeal and funniness (criteria 3, 9) |
| Drawing new poses in the engine | AI in-betweening test (GPU server) | Listening to the sound (criterion 10) |
| Animation, render, encode | | Final approval |
| Criteria 1, 4, 5, 6, 7, 8 checks | | |
| QC report | | |

## Order of work

1. Reference study 1 and 2 from `02-research-references.md` (cat lapping).
2. Draw the crouch pose; silhouette sheet; show Harshith.
3. Animatic of the three shots.
4. Key animation, then in-betweens, effects, sound.
5. QC report; send with the report.
