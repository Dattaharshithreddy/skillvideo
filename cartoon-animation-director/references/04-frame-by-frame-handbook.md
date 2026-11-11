# Frame-by-frame animation handbook

How to plan and build one action. Written for the `toon-slapstick` engine (24 fps, pose-to-pose keys),
but the method is the traditional one.

Status tags used in this knowledge base:
**[verified]** checked against a source on the date given · **[established]** standard animation teaching, not re-checked today ·
**[measured]** measured by us · **[recommendation]** our working rule · **[estimate]** a guess to be tested.

## 1. The twelve principles, as working rules

The list comes from Frank Thomas and Ollie Johnston's 1981 book *The Illusion of Life: Disney Animation* **[verified 2026-11-11]**.
The working rules below are **[established]** teaching plus **[recommendation]** for this engine.

### 1. Squash and stretch
- **Means:** a form flattens on contact and lengthens in fast travel, while keeping the same volume.
- **Why:** it is what makes a drawing feel made of flesh, with weight.
- **How a professional uses it:** strongest on the contact frame and the one before; gone within a few frames.
- **Example:** Gaju lands from a hop: 2 frames stretched (tall, narrow) falling, 1 frame squashed (wide, low), 6 frames settling.
- **Common mistakes:** volume changes (gets bigger); squash held too long so the character looks like rubber; applied to rigid things like a steel pot.
- **Detect:** freeze the contact frame. Width times height should stay about the same as the rest pose.
- **In the engine:** `sx`, `sy` on the actor, `squash()`; `sx*sy` should stay near 1.0. Use `head_sx/head_sy` for head-only hits.

### 2. Anticipation
- **Means:** a smaller move in the opposite direction before the main move.
- **Why:** it tells the eye where to look and makes the action feel powered.
- **How:** the bigger or faster the action, the longer the anticipation. A throw: 6-10 frames back, 2-3 frames forward.
- **Example:** Bheemu shaking the tree leans away first, weight on the back foot, then pulls.
- **Mistakes:** none at all (action pops from nowhere); anticipation as long as the action (reads as two actions).
- **Detect:** step through the 8 frames before any fast move. If nothing moved the other way, it is missing.
- **In the engine:** a short `move(..., 'out', ...)` the wrong way, then a `'snap'` move. The `antic` ease does a small automatic one.

### 3. Staging
- **Means:** presenting one idea so that it cannot be misread.
- **Why:** a viewer on a phone gets one look at each pose.
- **How:** one action at a time; clear silhouette; the camera as close as the action allows; nothing important behind something else.
- **Example:** a cat drinking milk is staged in profile on the floor so the tongue, the bowl and the whole crouch read.
- **Mistakes:** action hidden behind a prop; two characters acting at once; a small action in a wide shot.
- **Detect:** fill the character black. If the pose no longer reads, restage it.
- **In the engine:** `face`/`yaw` for the view, `ep.shot()`/`cam.move()` for distance; check with a contact sheet.

### 4. Straight ahead and pose to pose
- **Means:** drawing frame after frame as you go, versus planning key poses and filling between.
- **Why:** pose to pose keeps timing and staging under control; straight ahead gives looser, livelier effects.
- **How:** acting is pose to pose. Water, dust, fire, a flapping scarf are straight ahead.
- **In the engine:** actors are pose to pose (`move`, `set`). Effects (`splash`, `puffs`, `sparks`) are generated frame by frame.

### 5. Follow through and overlapping action
- **Means:** parts keep moving after the body stops, and parts start at different times.
- **Why:** a body that starts and stops all at once looks like a cardboard cut-out.
- **How:** loose parts (ears, tail, trunk tip, scarf, belly) lag 2-4 frames behind and overshoot before settling.
- **Example:** Gaju stops running: body stops, ears swing forward and back, trunk tip swings last.
- **Mistakes:** everything keyed on the same frames ("twinning in time").
- **Detect:** list the key frames of the body and of each loose part. If they are identical, there is no overlap.
- **In the engine:** key `ear`, `trunk`, `tail`, `scarf_fly` 2-4 frames after the body, ending with `'elastic'`.

### 6. Slow in and slow out
- **Means:** more drawings near the start and end of a move, fewer in the middle.
- **Why:** real things accelerate and brake.
- **Mistakes:** linear moves (robotic); everything eased the same (floaty).
- **In the engine:** `'io'` for gentle moves, `'out'` to arrive softly, `'in'` to fall, `'snap'` for a pop, `'lin'` only for constant-speed travel.

### 7. Arcs
- **Means:** living things move along curves.
- **Detect:** track one point (a hand, the nose) across frames. It should trace a curve, not a straight line or a zig-zag.
- **In the engine:** a straight `move` of x and y is a straight line. Add a middle key above or below the line, or use `arc()`.

### 8. Secondary action
- **Means:** a smaller action that supports the main one (a tail swishing while drinking).
- **Mistakes:** secondary action that steals attention or happens during the main beat's key moment.

### 9. Timing
- **Means:** the number of frames an action takes.
- **Why:** timing is weight and mood. The same move in 4 frames is a slap; in 16 it is a stroke.
- **Working numbers [measured from classic chase cartoons, 24 fps]:** snap to a pose 2-5 frames; hold 8-20 frames with small life; fast bursts 1-2 frames; a take about 3 frames up, 6 hold; about 14% of frames fully still.

### 10. Exaggeration
- **Means:** push the pose past what is real until it is clearly the idea.
- **Mistakes:** exaggerating everything equally; exaggerating the drawing but not the timing.

### 11. Solid drawing
- **Means:** forms have volume, weight and balance; no "twins" (left and right sides mirroring each other) **[verified 2026-11-11: Thomas and Johnston warned against twins]**.
- **Detect:** arms, legs, eyebrows and ears doing exactly the same thing on both sides.
- **In the engine:** always offset `armL` from `armR`, tilt the head, use `brow_asym`.

### 12. Appeal
- **Means:** a design and a performance people want to watch.
- **How:** simple readable shapes, clear personality in every pose, eyes that look at something.

## 2. The drawings in an action

| Drawing | What it is | Who decides it |
|---|---|---|
| **Key / extreme** | The storytelling poses: start, anticipation, contact, extreme, settle. | Planned first. |
| **Breakdown** | The pose between two keys that decides HOW it travels: which part leads, the arc. | Planned second. |
| **In-between** | The drawings that fill the rest. Their spacing gives the speed. | The engine's easing, or an AI in-betweener. |
| **Hold** | A pose kept on screen. Needs a little life (a blink, a breath) or it dies. | Planned with the timing. |

**Ones and twos:** on ones there is a new drawing every frame (fast action, camera moves); on twos a drawing is held for
two frames (most acting). The engine can render on twos automatically; fast moves should stay on ones. **[established]**

**Exposure sheet (x-sheet):** a table with one row per frame: action notes, the drawing number for each level, camera notes,
sound. Template: `templates/xsheet.csv`.

## 3. The action workflow (A to H), worked example

**Action: Laddu the cat laps milk from a bowl on the floor (original staging, side view).**

**A. Analysis.** He wants the milk and thinks nobody is watching. Mechanics: crouch, chest low, rump high, weight on the
front paws; the head dips, the tongue reaches forward and down, curls back with milk, the jaw closes. Contact points:
four paws on the floor, tongue on the milk. Emotion: greedy, then blissful.

**B. Timing (24 fps).** Approach 24 frames. Sniff 2 x 6 frames. Crouch 8 frames with a 4-frame settle.
Lap cycle 6 frames (4 laps a second), 5 laps, then eyes close and 5 more. Hold in bliss 12 frames. Total about 110 frames.

**C. Key poses.**
1. *Arrive:* standing in profile, head up, eyes on the bowl, tail high with a hook. Line of action: a low S from tail tip to nose.
2. *Sniff:* neck stretched forward, nose over the bowl, front legs braced, rump still high.
3. *Crouch:* elbows bend out, chest drops to just above the floor, rump stays up, tail starts to wave.
4. *Lap down:* head dips 10 px, tongue fully out touching the milk, eyes half shut.
5. *Lap back:* head lifts 6 px, tongue curled in, a drop on the chin.
6. *Bliss:* eyes shut in happy arcs, ears relaxed outward, tail in slow wide waves.

**D. Breakdowns.** Into the crouch the chest leads and the rump follows 2 frames later. In the lap the tongue leads down, the
head follows 1 frame later; coming back the head leads and the tongue trails.

**E. In-betweens.** Crouch: slow out, fast middle, soft landing with a 3-frame overshoot. Laps on ones (they are fast).

**F. Cleanup.** Check the neck stays attached and the same thickness in poses 2 to 5. Check all four paws stay planted.

**G. Secondary.** Tail waves on a 20-frame cycle, never in step with the laps. Ears flick every third lap. Rings spread on
the milk from each touch. Two or three drops fly on the first laps. The milk level falls slowly.

**H. Review.** Contact sheet of the six keys as silhouettes; video at full speed; frame-by-frame through two lap cycles.

## 4. Recipes (starting points, adjust to the character's weight)

| Action | Frames at 24 fps | Notes |
|---|---|---|
| Walk, relaxed | 12 per step (light), 16 (heavy) | Contact, down, passing, up. Head lowest just after contact. |
| Sneak | 16-24 per step | Body leans back on the reach, forward on the plant. |
| Run | 6-8 per step, on ones | Both feet off the ground at one point. Lean into it. |
| Zip off | 6-8 wind-up, 1-3 exit | Leave dust and a smear; hold the empty frame 4. |
| Jump | 6 crouch, 2 stretch off, air on arcs, 1 squash, 6-8 settle | The crouch is the anticipation. |
| Fall | accelerates: spacing grows each frame | Stretch on the way down. |
| Impact | 1 frame contact squash, 2-4 shake, 8-12 recovery | Silence just before; biggest sound on the contact frame. |
| Take (surprise) | 3 squash down, 3 stretch up with eyes wide, 6 hold, settle | Blink before it. |
| Double take | look, look away, 4-frame pause, snap back, take | The pause is the joke. |
| Slip | 4 frames foot shoots forward, body hangs 2, then drops | The hang in the air is the laugh. |
| Blink | 2 closing, 1-2 shut, 2 opening | Blink on head turns and before takes. |

## 5. Mistakes we have actually made, and the fix

| Mistake | How it showed | Fix |
|---|---|---|
| Two or three poses per action | Movement looked like sliding between stickers | Minimum four: anticipation, action, overshoot, settle |
| Objects jumping to a hand | Things teleported | Reach, close the fingers or trunk, then lift, each as its own pose |
| Static world | Tree did not shake, milk did not move | Anything touched becomes a prop that can move |
| One wide shot | Small actions unreadable | Cut closer for small actions |
| Head sliding off the body | Stretched neck | Move the chest with the head; limit head offset |
| All keys on the same frames | Stiff stops | Offset ears, tail, trunk, scarf by 2-4 frames |
