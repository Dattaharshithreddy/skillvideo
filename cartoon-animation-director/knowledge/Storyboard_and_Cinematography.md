# Storyboard and Cinematography

**Knowledge base document 5 of the master mission (Phase 1).**
Version 1.0, 2026-11-11. Follows `Animation_Fundamentals.md`, `Character_Design_Bible.md`, `Frame_By_Frame_Animation.md` and `Slapstick_Comedy.md`.

Documents 1 to 4 covered how a character moves and how a gag is built. This document covers where the camera is while that happens: which shot, how big, from where, for how long, and how one shot joins the next. It ends with how to plan all of that on paper (the storyboard) and in time (the animatic) before any animation is made.

## 0. How to read this document

### 0.1 Labels

| Label | Meaning | Status |
|---|---|---|
| **[M]** | Read from our code or computed from it this session | Established project capability or fact |
| **[C]** | Craft convention that is widely taught; no primary source opened | Established practice, not verified by me |
| **[R]** | My recommendation or proposed workflow | Proposed; test before trusting |
| **[V]** | Read this session as an excerpt returned by a search | Verified outside fact, at excerpt level |
| **[U]** | Unverified assumption | Check before relying on it |

### 0.2 Evidence

No figure was made for this document and nothing was rendered. Every shot list here is a **plan**. No framing in this document has been looked at on a phone, and no cut has been watched. The three kinds of evidence from `Frame_By_Frame_Animation.md` section 0.2 still apply: poses, timing plans, tested animation.

### 0.3 What is not repeated

Staging inside one shot is in `Slapstick_Comedy.md` section 10. Silhouettes are in `Character_Design_Bible.md`. Timing of a gag is in `Slapstick_Comedy.md` section 6. This document refers to them.

---

## 1. What the camera is for

Every shot answers three questions for the viewer, in this order:

1. **Where am I looking?** One subject, found within a few frames.
2. **What is happening?** One action or one feeling.
3. **What changed since the last shot?** One new piece of information.

A shot that answers none of them should be cut. A shot that answers two different "what is happening" questions should be split. In a silent series this matters more than usual, because no line of dialogue will explain what the picture failed to show.

**The cheapest rule in this document [R]:** change the shot only when the viewer needs to see something they cannot see well enough now. That is the test for every cut and every camera move below.

---

## 2. The frame we have

### 2.1 The picture [M]

- 1080 wide by 1920 tall, 24 frames a second (`toon.py`: `W, H, FPS = 1080, 1920, 24`).
- World coordinates are pixels, y grows downward, the floor line is `GROUND = 1480`.
- The camera is a `Timeline` with four values: `x`, `y`, `zoom`, `shake`. It is keyed with `move` and `set` like any actor.
- `Stage.cut(f, **cam)` makes a hard cut at frame `f`: it jumps the camera and suppresses smears across the cut.
- `Stage.shake(f, amount, dur)` shakes the camera and lets it die away.
- `Show.shot(f, x, z, up, cut)` and `Show.push(f0, f1, x, z, up, ease)` are the episode-level helpers. `Show.cy(z, up)` places the camera so that **the floor sits 600 screen pixels below the centre at any zoom**, which is 360 px above the bottom edge.
- Backgrounds are `Painted` objects wider than the picture (2700 px in the example in `show.py`), so the camera can travel sideways. The camera matrix has a parallax factor for layers.
- `scene.iris` closes or opens a circle on a point; `scene.title_card` makes the opening card. I found **no fade, dissolve or wipe** helper in the engine.
- `Stage.still(f, path, scale)` writes one frame; `Stage.sheet(frames, path, cols, scale)` writes a contact sheet; `Stage.render(out, f0, f1, audio, scale, crf)` renders a range at any scale.

### 2.2 What the ten existing episodes do [M]

Counted from the episode files:

| | Episodes 2 to 10 | Episode 1 |
|---|---|---|
| `ep.shot(...)` calls per episode | 1 to 3 | 0 (older style) |
| `ep.push(...)` calls per episode | 0 to 3 | 0 |
| Direct camera moves | 0 | 5 moves, 1 cut |
| Length | 498 to 846 frames (about 21 to 35 s) | |

So most episodes are one or two camera set-ups for half a minute. `cartoon-animation-director/SKILL.md` already records the consequence as a rule from a real mistake: one wide shot for a whole episode reads as flat, and small actions need a closer shot. This document is the method for fixing that. Episode 1 is not to be changed (lessons learned 10).

### 2.3 What zoom gives [M, arithmetic]

Visible world area is 1080/zoom by 1920/zoom.

| Zoom | Visible width × height (world px) | What fits [R] |
|---|---|---|
| 1.0 | 1080 × 1920 | Everything; much empty space above the cast |
| 1.1 (the helper's default) | 982 × 1745 | Bheemu and Gaju side by side with room above |
| 1.5 | 720 × 1280 | One big character full length, or two close together |
| 2.0 | 540 × 960 | Bheemu full length, alone |
| 2.5 | 432 × 768 | Bheemu from the knees up; Gaju full length with room |
| 3.0 | 360 × 640 | Bheemu's head and chest; Gaju full length, tight |
| 4.0 | 270 × 480 | A face; a prop; Gaju's head and trunk |

Reference sizes: Bheemu is 580 px tall, Ammamma 560, Chintu 390, Bujji 300, Gaju 250, Laddu 250 [M, model `HEIGHT` constants]. In `Slapstick_Comedy.md` example 1 Bheemu and Gaju stand 430 px apart and the pair needs about 940 px of width.

**The main consequence of a vertical picture:** a two-shot of our leads is always a wide shot (zoom about 1.1). Anything closer is a single. The gap between "both in frame" and "one in frame" has no middle, so the choice of who is on screen during a reaction is a real decision every time.

### 2.4 Where the phone's own buttons sit [V, U]

Shorts and similar apps draw their interface over the picture. The margins quoted for a 1080 × 1920 frame differ widely between sources I read: top 120 to 380 px, bottom 300 to 672 px, right 96 to 192 px, left 40 to 60 px [V]. One source says the figures are measured from the app and not published constants [V]. I could not confirm an official figure, so treat all of these as **[U]**.

What this means for us [M, arithmetic]: with `Show.shot`, the floor is 360 px above the bottom edge. Under the smaller quoted bottom margins (300 to 390 px) the characters' feet are just clear. Under the largest (672 px, starting at screen y 1248) Gaju, who is about 275 screen pixels tall at zoom 1.1, would stand almost entirely inside the covered band. **This needs one check on a real phone** with an existing episode (section 18). Nothing has been changed.

---

## 3. Shot sizes

Shot size is how much of the subject fills the frame. Names follow live-action convention [C].

| Shot | Shows | Use it for | With our cast [R] |
|---|---|---|---|
| Extreme wide / establishing | The whole place; figures small | Where are we? | Zoom 1.0, cast in the lower third; the first shot of a new location |
| Wide (long) | Whole bodies plus surroundings | Physical action, chases, relationships in space | Zoom 1.0 to 1.2. The only two-shot of Bheemu and Gaju |
| Full | One body, head to feet | A body gag: a hop, a fall, a take | 2.0 for Bheemu, 2.5 to 3.0 for Gaju |
| Medium | Waist or knees up | Acting with arms and face | 2.5 to 3.0 for Bheemu |
| Medium close | Chest up | A reaction that needs the eyes | 3.0 to 3.5 |
| Close-up | The face | A thought; a slow burn; a decision | 4.0 |
| Extreme close-up | Eyes, a paw, a trunk tip | One tiny action the story turns on | 5.0 and up; line quality must be checked at this size |
| Insert | An object, no face | Plant a prop; show the milk level | 4.0 on the object |
| Over-the-shoulder | One character past another | Who is looking at whom | Limited: there is no back view of any model (section 4) |

**Decision rules [R].**

1. **Size follows the size of the action.** If the action is in the whole body, use a full or wide shot. If it is in the eyes, a close-up. A cat lapping milk in a wide shot is a rule already learned the hard way.
2. **Establish, then go in.** The first shot of a scene is wide enough to show geography; closer shots borrow that knowledge.
3. **The gag in wide, the reaction closer.** The cause and the victim share the frame at impact (`Slapstick_Comedy.md` section 10); the reaction may then be a single.
4. **Change size by a clear step.** Cutting from zoom 2.0 to 2.3 looks like a mistake. Change by at least half as much again (2.0 to 3.0), or do not cut [C: the "30 per cent" or "30 degree" convention, adapted].
5. **Closer is stronger; use it less.** If every beat is a close-up, the close-up has no force left for the slow burn.
6. **Check the drawing at that size.** Our models were approved at roughly zoom 1 to 2. At zoom 4 a line is four times as thick on screen. A close-up of an approved model is the same model, but whether it holds up is an eyes check, not an assumption.

---

## 4. Camera angles

In live action the angle is where the camera stands: eye level, high (looking down, makes the subject small), low (looking up, makes it imposing), bird's-eye, worm's-eye, and tilted ("Dutch") for unease [C].

**What our engine can do [M].** The camera slides and zooms over flat drawings. It cannot look up or down at a character, because that needs a different drawing of the character. The models have a front view, a three-quarter head through `yaw`, and no true profile or back view (`Character_Design_Bible.md` section 12).

**So angle is a design job, not a camera setting.** A real high or low angle needs new drawings, which is a character-asset change and goes through review. What can be done today with existing controls [R]:

| Wanted effect | Without a new drawing |
|---|---|
| Subject looks small or alone | Wide shot, subject low and small in the frame, empty space above |
| Subject looks big | Frame it tall: full height of the picture, head near the top |
| Unease | Not available honestly. Camera `rot` does not exist; do not fake it |
| Looking up at something | The other character's eyes and head tilt up; show the thing in the top of the frame |
| Looking down | Put the camera's `y` higher so the floor shows; the drawing itself does not change |

Eye level for a small character is low. Framing Gaju's shots with the camera centred on **his** eye line, not Bheemu's, is the 2D equivalent of getting down to a child's height [R].

---

## 5. Composition

Composition is where things sit inside the rectangle.

- **Thirds [C].** Divide the frame into three each way. In our picture the lines are at x = 360 and 720, y = 640 and 1280. A subject on a line or crossing reads as placed; dead centre reads as formal or static, which suits a deadpan hold.
- **Headroom.** A little space above the head. Too much and the character sinks; none and the head feels cut. For a single, about a tenth of the frame height [R].
- **Looking room.** More space in front of the face than behind it. A character looking right sits left of centre. Breaking this on purpose makes the viewer expect something behind the character.
- **Lead room.** The same for movement: space ahead of the direction of travel.
- **Depth in layers.** Foreground, middle and background. Our stage has actor `z` for draw order and painted backgrounds [M]; a foreground object (a pot edge, a leaf) at the bottom or side gives depth and a place to hide things.
- **Contrast finds the subject.** The eye goes to the strongest contrast in value or colour, then to faces, then to whatever moves. Put the subject where the background is plainest and most different in value (`Character_Design_Bible.md`, rule R4: fix contrast by staging and lighting before any design change).
- **Lines point.** A wall top, a clothesline, an eyeline or a trunk can aim at the subject.
- **Empty space is a tool.** In a vertical frame the top half is often empty. Use it deliberately: it is where things fall from, fly to, or appear (`Slapstick_Comedy.md` example 1).
- **Edges.** A character cut by the frame edge at a joint (neck, wrist, ankle) looks amputated. Cut mid-limb or not at all. No body part should touch the edge by accident.
- **One subject per frame.** If two things compete, one is made smaller, darker, stiller or moved out.

**How to check a composition [R].** Shrink the still to thumbnail size and squint. If the subject is still the first thing seen, it works. Then make it a silhouette (`Slapstick_Comedy.md` figure 5 shows the method). Both are stills checks.

---

## 6. Blocking across shots

Staging one moment is in document 4. Blocking is where characters move over a whole scene.

- **Draw a floor plan first.** One top-down sketch: doors, furniture, where each character starts and ends, where the camera looks from. Every shot is then a view of the same plan, which is what keeps geography consistent.
- **Give each character a home position.** Bheemu left, Gaju right, for example. The audience learns it in the first wide shot, and a swap later means something.
- **Move for a reason.** A character crosses the frame because they want something on the other side.
- **Keep the stage line** (section 7) between the two leads for the whole scene.
- **Use height.** Floor, cot, wall top, tree. A vertical picture rewards blocking that travels up and down.

---

## 7. Screen direction and continuity

### 7.1 Screen direction [C]

- A character travelling left to right keeps travelling left to right in the next shot, until a turn is shown on screen or a head-on shot resets it.
- Two characters facing each other define a line between them. **Keep the camera on one side of that line** (the 180 degree rule). Cross it and they appear to swap sides.
- A chaser and the chased move in the same screen direction. Two characters heading for a collision move in opposite directions.
- In our series the rule is easy to keep because the camera never truly moves round the cast. It is easy to break by flipping a character's `face` or swapping x positions between shots without showing the move.

### 7.2 Eyelines

A character looking off-screen right, followed by a shot of an object, tells the viewer the object is what they see. The next character should look back left. Eyeline height matters too: Gaju looks up at Bheemu; Bheemu looks down.

### 7.3 Continuity list

Check these across every cut inside a scene.

| Kind | Question | Where the truth lives |
|---|---|---|
| Position | Is everyone where the last shot left them? | Floor plan; actor `x`, `y` at the cut frame |
| Direction | Facing and travelling the same way? | `face`, `yaw` |
| Pose | Does the pose at the start of shot B match the end of shot A? | The hook-up frame (below) |
| Props | Same hand or trunk, same state (full, empty, broken)? | Prop keys |
| Accessories | Glasses, scarf, cap present and the right way round? | Approved model |
| Expression | No unexplained jump in mood | Presets at the cut |
| Time and light | Same time of day, same background | The `Painted` set |
| Sound | Ambience and music carry across | `Sound_Design.md` |

**The hook-up frame [R].** For each cut, print the outgoing frame and the incoming frame side by side with `Stage.sheet`. This is the fastest continuity check we have and it uses an existing function.

### 7.4 Cutting on action [C]

A cut hides best inside a movement: start the move in shot A, finish it in shot B. Overlap by two or three frames so the action is not shortened. Cutting between two still poses makes the cut itself the event, which is right for a smash cut and wrong almost everywhere else.

---

## 8. Camera movement

| Move | What it is | Use it for | Engine [M] |
|---|---|---|---|
| Lock-off | No movement | Most shots; every gag | Default |
| Push-in | Zoom rises slowly | A realisation; growing attention | `push` or `cam.move(..., zoom=)` |
| Pull-out | Zoom falls | A reveal: what the character had not seen | Same |
| Pan / track | Camera `x` travels | Following a walk or a chase | `cam.move(..., x=)`; wide backgrounds allow it |
| Tilt / crane | Camera `y` travels | Following something up or down | `cam.move(..., y=)` |
| Shake | Brief random offset | A heavy impact | `Stage.shake` |
| Whip | A very fast pan between two subjects | A sudden look across | Possible as a 3 to 4 frame move; blur is not provided |

**Rules.**

- **Every move has a motive [C]:** follow, reveal, or emphasise. If none applies, lock it.
- **Lock the camera from the anticipation to the end of the hold** of any gag (`Slapstick_Comedy.md` section 10).
- **Ease in and out** (`io`) unless following a snap.
- **A follow leads slightly.** Keep lead room ahead of the runner.
- **Push-ins are slow.** A push that is noticed as a move is too fast: 48 frames or more for a small change of zoom [R].
- **Shake is rationed.** One or two per episode, and only for the heaviest event. It also conflicts with clarity on the contact frame, so start it the frame after contact [R].
- **Do not move and cut at once.** Let a move finish before the cut, or cut on the action inside it.

---

## 9. Shot transitions

| Transition | Meaning to the viewer [C] | Available in the engine [M] |
|---|---|---|
| Cut | Same time, new view | Yes, `Stage.cut` |
| Cut on action | Continuous movement | Yes, by timing the cut |
| Match cut | Two similar shapes or moves join two scenes | Yes, by design |
| Cutaway / insert | "Meanwhile, look at this" | Yes |
| Smash cut | Sudden contrast: calm to chaos | Yes |
| Jump cut | Time skipped in the same framing | Yes; rarely right for us |
| Iris in / out | Classic cartoon open and close | Yes, `scene.iris`; `Show.close` uses it at the end |
| Title card | Opening | Yes, `scene.title_card` |
| Fade to black | End of a chapter; time passes | Not found. Could be done at encode time with ffmpeg, which changes no engine code [R] |
| Dissolve | Time passes gently | Not found |
| Wipe | Scene change with energy | Not found |

**Rules [R].** Inside a scene, use cuts. Between scenes or for the passing of time, use the iris, which is ours already. One kind of scene transition per episode keeps the style consistent. A missing fade or dissolve is an engine limitation to state, not to build around silently (lessons learned 25).

---

## 10. Pacing

Pacing is how long each shot stays and how the lengths vary.

- **A shot lasts as long as it takes to read, plus a beat.** Rough reading times [R]: an insert 18 to 24 frames; a close-up reaction 24 to 48; a full shot with one action 36 to 72; a wide establishing shot 48 to 96. New or complicated pictures need more.
- **Vary the lengths.** Three shots of equal length feel mechanical. Short, short, long is a rhythm.
- **Shots get shorter as tension rises** and long again at the release. This is the escalation rule of `Slapstick_Comedy.md` section 7 applied to editing.
- **Cut on the 12-frame grid where it costs nothing.** The music beat is 12 frames [M]; cuts on beats feel intended.
- **Do not cut during a hold that is the joke.** The slow burn is one unbroken shot.
- **Average shot length for a 30 second episode [R].** Six to ten shots is a reasonable target against the present one to three. That is a proposal to test on one episode, not a standard.
- **The first two seconds.** In a feed, the opening picture decides whether the viewer stays [C]. Open on a clear, readable image with a character in it. The existing title card takes the first 36 frames by default (`Show(..., intro=36)`) [M]; whether that costs viewers is a question for Harshith's channel data, not for me [U].

---

## 11. Storyboards

A storyboard is the film as a row of drawings, made before animation so that mistakes are cheap.

### 11.1 What one panel carries

| Field | Example |
|---|---|
| Shot and panel number | S03 P2 |
| Drawing | The key pose, in frame |
| Shot size and zoom | Medium close, zoom 3.0 |
| Camera | Lock-off / push to 3.5 over 48 frames |
| Action | "Bheemu's eyes slide right" |
| Arrows | Character movement (solid), camera movement (outlined) |
| Length | 24 frames |
| Sound | "dry tick on the eye move" |
| Transition out | Cut |

One panel per pose change that the story needs, not per frame. A 30 second episode is usually 20 to 40 panels [R].

### 11.2 The stages [C]

1. **Thumbnails.** Tiny, fast, many versions. Solve the staging here.
2. **Rough board.** One readable panel per beat, with the fields above.
3. **Clean board.** On-model drawings for anything that will be reviewed.
4. **Shot list.** The table that the animation is built from.

### 11.3 Boards with our engine [M for the functions, R for the method]

I cannot sketch freehand. Two honest routes:

- **Engine stills as panels.** Pose the approved models with existing controls, set the camera, and write panels with `Stage.still` or a whole board with `Stage.sheet`. This is how figure 1 of `Slapstick_Comedy.md` was made. The panels are on-model by construction. The limit is that a board can only show what the models can already do; a pose they cannot make is reported as a limitation, not approximated.
- **Hand thumbnails by Harshith or another person,** photographed, when the idea needs a pose the models lack. Decision D22 allows a small labelled hand-drawn study only when it answers a specific question.

### 11.4 Shot list template

| Shot | Frames | Size / zoom | Camera | Who | Action | Sound | Cut in / out | Continuity note |
|---|---|---|---|---|---|---|---|---|
| S01 | 1-48 | Wide / 1.1 | Lock | B, G | ... | ... | Iris in / cut | Home positions set |

### 11.5 How to check a board

- Read it without the notes. Does the story come through from pictures alone? (This is the acceptance test already written in `references/06-pipeline-and-tools.md`, stage 2.)
- Cover each panel in turn. If nothing is lost, cut it.
- Check every cut against section 7.3.
- Count shot sizes. If one size makes up more than about half the board, look for the shots that are the wrong size.

---

## 12. Animatics

An animatic is the storyboard played in real time with rough sound. It answers one question the board cannot: **is the timing right?**

### 12.1 How to build one here [M for the tools, R for the method]

1. Key only the main poses and camera for each shot, with `step` or `snap` eases so that poses pop from one to the next.
2. Add scratch sound: the hit on the contact frame, one tick per beat, the music bed (`Sound_Design.md`).
3. Render small: `Stage.render(out, scale=0.25)` or `0.5`. A render exists to be watched, not admired.
4. Check the file with `tools/qc_frames.py video` so length, frame rate and audio are right.
5. Send it to be **watched and listened to**. I can step through frames; I cannot watch at speed or hear (`references/07-qc-rubric.md`).

### 12.2 What is judged at the animatic

- Is each shot on screen long enough to read, and no longer?
- Do the pauses of `Slapstick_Comedy.md` section 6 feel right?
- Does any cut confuse geography or direction?
- Can a first-time viewer retell it?

### 12.3 The gate

Nothing is animated in detail until the animatic is accepted. Changing a shot's length at the animatic costs one number; changing it after in-betweens and sound costs the shot. Where two timings are in doubt, both are rendered and compared in playback (lessons learned 29).

---

## 13. Worked examples (plans only)

### 13.1 "The ball that went up", re-boarded from one shot to six

`Slapstick_Comedy.md` example 1 was posed as a single wide shot of 240 frames. Here is the same gag as a shot list. The beat lengths are unchanged; only the camera is new. **Nothing here has been rendered or watched.**

| Shot | Film frames | Size / zoom | Camera | Action | Why this shot |
|---|---|---|---|---|---|
| S01 | 1-48 | Wide / 1.1 | Lock | Bheemu dozing left, Gaju right with the ball. Gaju's sly look | Establish geography and home positions; both needed in frame |
| S02 | 49-76 | Full on Gaju / 2.5 | Lock | Bounces 1 and 2 | The action is small and in Gaju's body and trunk |
| S03 | 77-134 | Wide / 1.1, camera `y` raised to show more sky | Lock | Bounce 3; the ball leaves the top; the wait; Gaju relaxes | The empty space above Bheemu must be visible for the wait to work |
| S04 | 135-152 | Same as S03 (no cut) | Lock | The fall, the impact, the hold | Cause and victim in one frame; no cut near a hit |
| S05 | 153-184 | Medium close on Bheemu / 3.0, then cut to medium on Gaju / 3.0 at 165 | Lock | Slow burn; then Gaju's guilt | Eyes carry it. Two singles because a two-shot cannot be this close (section 2.3) |
| S06 | 185-240 | Wide / 1.1 | Lock, iris out | Topper on Gaju; both laugh | Back to both for the reconciliation |

**Continuity notes.** Bheemu stays left and Gaju right in every shot. In S05 Bheemu looks right and Gaju looks left, so their eyelines meet across the cut. S03 and S04 are deliberately one shot of 76 frames: the wait and the hit must not be cut. S02 to S03 is a cut on action, on the wind-up for the big bounce.

**What I would test first.** Whether S02 is worth the cut at all. It adds a set-up and removes Bheemu from view during the bounces, which may weaken the audience's sense of where the danger is. That is a playback question.

### 13.2 "The hand pump", opening four shots

From `Slapstick_Comedy.md` example 2 (a written plan; the pump prop and water effect do not exist).

| Shot | Frames | Size | Action | Why |
|---|---|---|---|---|
| S01 | 1-36 | Extreme wide | Garden, hot afternoon; Gaju small, tongue out; Bujji far right | Where, who, heat |
| S02 | 37-48 | Insert | The pump spout: one drop hangs | Plant the object |
| S03 | 49-80 | Full on Gaju and pump | Attempts 1 and 2 | Body action |
| S04 | 81-104 | Close on Gaju's face under the spout, eyes up | He looks up the spout | The audience now knows where the water will go |

### 13.3 The pilot

`references/08-pilot-project.md` ("The Milk Bowl") already specifies three shots with sizes: wide, close side view, medium with a pull back. It is the standing example of rule 3.1: the drink is a close, floor-level shot because the action is small. Its side view depends on a profile that is still review-only material.

---

## 14. Implementation steps

1. Start from the beat sheet (`Slapstick_Comedy.md` section 16, step 5).
2. Draw the floor plan and fix home positions and the stage line.
3. For each beat, ask the three questions of section 1 and choose the shot size by the rules of section 3.
4. Write the shot list (11.4). Mark every cut as cut-on-action, cutaway or scene change.
5. Check the list against 7.3 and count the shot sizes.
6. Make the board from engine stills; print hook-up frames for every cut.
7. Check each panel as a thumbnail and as a silhouette.
8. State any shot that needs a pose, view, prop or transition the engine lacks. Do not approximate it silently.
9. Build the animatic (section 12) and send it for watching and listening.
10. Record the verdict and any change of length; only then start detailed animation.

---

## 15. Exercises

None has been done.

| # | Exercise | Trains | Buildable today? |
|---|---|---|---|
| 1 | One action, four sizes: Gaju's hop as wide, full, medium and close. Which reads best, and why? | Size follows action | Yes |
| 2 | Board `Slapstick_Comedy.md` example 1 twice: one shot, and the six shots of 13.1. Render both as animatics | Whether cutting helps | Yes |
| 3 | Hook-up sheet: print outgoing and incoming frames for five cuts and mark every continuity error | Continuity | Yes |
| 4 | Cross the line on purpose in a two-character scene, then fix it | Screen direction | Yes |
| 5 | The same reaction with headroom at 0, 10 and 25 per cent of frame height | Composition | Yes |
| 6 | One push-in at 24, 48 and 96 frames | Motivated movement | Yes |
| 7 | Take an existing episode's file and write the shot list it would need at eight shots, without changing the episode | Pacing | Paper only |
| 8 | Phone check: watch one existing episode in the Shorts player and note what the interface covers | Safe areas | Needs Harshith's phone |

---

## 16. Common mistakes

| Mistake | How to detect | Fix |
|---|---|---|
| One wide shot for everything | One or two camera set-ups in 30 s | Board it; go closer for small actions and reactions |
| Close-up of a body action | The action leaves the frame | Use a full or wide shot |
| Wide shot of a face action | The eyes are a few pixels | Cut to a medium close or close-up |
| Cut near the hit | A cut within 6 frames of contact | Hold the shot from anticipation to the end of the hold |
| Crossing the line | Characters swap sides across a cut | Keep home positions; show any crossing |
| Weak size change | Two consecutive zooms within 30 per cent | Change by half again or do not cut |
| Unmotivated move | Cannot name follow, reveal or emphasise | Lock it |
| Subject not found | Thumbnail test fails | Simplify the background, raise contrast, clear the space |
| Amputating edge | Frame edge at a joint | Reframe |
| No lead or looking room | Face or travel direction against the edge | Shift the subject back |
| Continuity jump | Hook-up sheet shows a pose, prop or accessory change | Match the incoming key to the outgoing frame |
| Animating before the animatic | Detailed keys exist and timing is still changing | Stop; return to the animatic |
| Important action under the phone's buttons | Not yet measurable (2.4) | Phone check, then decide |
| Every beat a new shot | More than about 12 cuts in 30 s with no reason | Merge shots that answer the same question |

---

## 17. Checklist for a storyboard and animatic

**Board**
- [ ] Floor plan drawn; home positions and stage line fixed
- [ ] First shot of each location establishes geography
- [ ] Each shot answers one "what is happening"
- [ ] Shot size chosen by the size of the action
- [ ] Cause and victim share the frame at every impact
- [ ] No cut and no camera move from anticipation to the end of the hold
- [ ] Every cut classified; size changes are clear steps
- [ ] Screen direction and eyelines consistent
- [ ] Hook-up frames printed for every cut and checked against 7.3
- [ ] Panels read as thumbnails and silhouettes (eyes)
- [ ] Anything the engine cannot show is listed as a limitation
- [ ] The story reads from pictures alone (a person, not me)

**Animatic**
- [ ] Rendered at real length with scratch sound
- [ ] `qc_frames.py video` run
- [ ] Watched at full speed and listened to (Harshith)
- [ ] First-time viewer retold it
- [ ] Shot lengths frozen and recorded before animation starts

---

## 18. Limitations and open questions

**Limitations [M].**

- The camera slides and zooms only. No rotation, no real change of angle, no depth of field, no motion blur.
- No fade, dissolve or wipe helper.
- No profile or back view of any model, so over-the-shoulder shots and true side-on staging are not available from approved assets.
- A two-shot of the leads is always wide in a vertical frame.
- Close-ups enlarge approved line work; whether it holds at zoom 4 and above has not been looked at.

**Open questions for Harshith.**

1. **Phone safe area.** Does the Shorts interface cover the characters' lower bodies in the existing episodes? One look on a phone settles it. If it does, the fix is a staging decision, and I would bring options, not make the change.
2. **Target number of shots** for a 30 second episode. I propose six to ten for a test.
3. **Scene transition.** Keep the iris as the only scene transition, or do you want fades? A fade can be added at encode time without engine code; inside the engine it would be a new helper needing approval.
4. **The title card.** Keep 36 frames at the start, or open on action? Your channel's retention data should decide.
5. **Close-up quality.** Do you want a review-only sheet of each approved model at zoom 3, 4 and 5 to judge line weight? It would change nothing; it would only show.

---

## 19. References

No outside source was opened for the craft sections of this document. They are standard film grammar as taught in the books below, tagged **[book]** because I have not opened them this session.

- Joseph V. Mascelli, *The Five C's of Cinematography* **[book]**
- Steven D. Katz, *Film Directing Shot by Shot* **[book]**
- Bruce Block, *The Visual Story* **[book]**
- Francis Glebas, *Directing the Story* **[book]**
- Mark Simon, *Storyboards: Motion in Art* **[book]**

**Safe-area figures (excerpts from a search; they disagree with each other; none is an official source):** https://www.hopperhq.com/blog/youtube-shorts-dimensions/ ; https://www.socialync.io/tools/safe-zones/youtube-shorts ; https://www.poster.ly/tools/youtube-shorts-safe-zone-checker ; https://www.admakeai.com/blog/vertical-video-dimensions-2026 **[excerpt]**

**Our own material**
- `toon-slapstick/engine/toon.py` (`Camera`, `Stage.cut`, `shake`, `still`, `sheet`, `render`), `show.py` (`Show.shot`, `push`, `cy`), `scene.py` (`Painted`, `iris`, `title_card`)
- `toon-slapstick/episodes/*/episode.py` (shot counts)
- `cartoon-animation-director/SKILL.md`, `references/06-pipeline-and-tools.md`, `references/07-qc-rubric.md`, `references/08-pilot-project.md`, `references/09-lessons-learned.md`
- `Slapstick_Comedy.md`, `Character_Design_Bible.md`, `Frame_By_Frame_Animation.md`

---

## 20. Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.0. No figures. Camera capabilities read from the engine; shot counts of the ten episodes counted from their files. Two shot lists written as plans. Nothing rendered, watched or checked on a phone. Not reviewed by Harshith. |
