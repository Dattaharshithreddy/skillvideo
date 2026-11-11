# Engine Change Proposals

**PROPOSALS ONLY. Nothing in this file is approved. Nothing in this file is implemented.**
Version 1.0, 2026-11-11. Kept separate from the knowledge documents at Harshith's instruction (decision register D19 and D21 in `Character_Design_Bible.md`).

The engine (`toon-slapstick/engine/`), the approved models, the presets and the model baseline are unchanged. Each proposal below needs explicit approval before any code is written, and a second approval before anything is merged.

Labels: **[M]** measured in this project. **[R]** my recommendation, untested.

## Summary

| ID | Proposal | Touches engine code? | Changes existing episodes? | Status |
|---|---|---|---|---|
| P1 | Report keys that fall on a held frame | No (a separate read-only checker) | No | Proposed, not approved |
| P2 | Per-frame exposure control | Yes (`Actor.frame_pose`, about ten lines) | No, when the new setting is left empty | Proposed, not approved |
| P3 | Report contacts between an actor on ones and an actor on twos | No (same checker as P1) | No | Proposed, not approved |

---

## P1. Report keys that fall on a held frame

**The problem [M].** `Actor.twos` is on by default. On an odd engine frame the engine shows the pose of the frame before, unless the actor moves 26 px or more in that frame. A pose keyed for one frame on an odd frame is therefore never drawn, and nothing reports it. Measured cases: the hop in document 3 (keyed 0.72 tall, flattest drawing shown 0.83) and the contact test in document 4 (the ball arrives on a head that has not squashed yet).

**Smallest safe change [R].** No engine change at all. A separate script, for example `cartoon-animation-director/tools/check_keys.py`, that reads what the engine already exposes:

1. For each actor with `twos` on, walk `actor.keys` (parameter, then a list of frame, value, ease).
2. For each key on an odd frame, compare `actor.frame_pose(f)` with `actor.pose(f)` for that parameter.
3. If they differ and the value has changed again by frame `f + 1`, print: actor, parameter, frame, value asked for, value shown.

It imports the episode, reads, and prints. It writes nothing and changes no timeline.

**Why this and not a warning inside the engine.** A warning inside `Timeline.move` cannot know whether `twos` will be on at render time, and it would print during every existing episode. A separate checker cannot change a rendered frame.

**Limits.** It reports; it does not fix. It cannot tell an intended soft landing from a lost key, so a person reads the list.

**Test before approval to merge.** Run it on the document 3 hop (must report film frame 20) and on document 4's contact test (must report the odd-frame case and stay silent on the even-frame case). Render one existing episode before and after adding the file and compare the video checksums (must be identical, since no engine file changes).

---

## P2. Per-frame exposure control

**The requirement.** Twos are all-or-nothing per actor per shot, except for the automatic switch on fast travel. A scene often wants twos for acting and ones for a fall, a landing or an impact. Today the only choices are `actor.twos = False` for the whole shot, or planning every contact onto an even frame.

**Minimum design [R].**

- One new optional attribute on `Actor`: `ones = []`, a list of `(first_frame, last_frame)` ranges.
- In `Actor.frame_pose`, one extra condition: if `f` lies inside any range in `ones`, do not fall back to frame `f - 1`.
- One helper to write it: `actor.on_ones(f0, f1)`.
- Nothing else. No change to `Timeline`, to easing, to smears or to rendering.

**Compatibility with existing animations.**

| Case | Behaviour |
|---|---|
| Existing episode, `ones` never set | Identical to today: the list is empty, the new condition is never true |
| `twos = False` | Unchanged: already on ones everywhere |
| Fast travel above 26 px a frame | Unchanged: the automatic switch still applies |
| Props (`Prop.twos = False`) | Unchanged |

**Test before approval to merge.** Render all ten existing episodes before and after and compare checksums frame by frame; every one must be identical. Then show one shot both ways (the document 3 hop with frames 15 to 22 on ones) for playback review. The drift checker must still pass.

**Open design question for Harshith.** Whether ranges belong to the actor (as above) or to the shot (one list for everybody on stage). Per actor is the smaller change. Per shot avoids P3.

---

## P3. Report contacts between an actor on ones and an actor on twos

**The problem [M].** Props are on ones; characters are on twos. When a prop hits a character on an odd frame, the prop is in its contact position while the character still shows the drawing from the frame before. In document 4's test the ball sits 87 px inside the outline of an unsquashed head for one frame.

**Smallest safe change [R].** No engine change. An extra pass in the P1 checker: for a list of contact frames given by the author, report any that are odd while one party is on twos. With P2 approved, the fix is to put both parties on ones around the contact. Without it, the working rule is the one in document 4: key every contact on an even engine frame.

---

## Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.0. Three proposals written. None approved, none implemented, none tested. |
