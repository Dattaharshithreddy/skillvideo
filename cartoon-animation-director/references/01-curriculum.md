# Animation production curriculum

**How this curriculum is used here.** Harshith does not draw; Claude animates with the `toon-slapstick` engine. So the
"student" doing each exercise is the production system (Claude plus the engine), and Harshith is the reviewer. A lesson
is **mastered** only when its exercise has been produced, inspected against the rubric, and accepted by Harshith.
Explaining a concept never counts as mastering it.

Status values: `not started` · `attempted` (exercise made, not yet accepted) · `mastered` (accepted by Harshith, date noted).

## Levels

| Level | Goal |
|---|---|
| 1. Drawing | Characters are solid, consistent and readable in any pose. |
| 2. Motion | Single actions have weight, timing and overlap. |
| 3. Acting | A character thinks, wants and reacts. |
| 4. Comedy | Gags are set up, timed and paid off. |
| 5. Production | A whole episode goes from idea to finished video and passes QC. |

## Lessons

Each lesson: objective, demonstration, exercise, expected output, rubric (see `07-qc-rubric.md` for the scoring scale),
and what to do when it fails.

### Level 1: Drawing

**L1. Readable poses and silhouettes.** `status: attempted (2026-11-11), attempt 1 scored 7/12, not passed; see lessons/L01-silhouettes/report_attempt1.md`
- *Objective:* every key pose reads when filled solid black.
- *Demonstration:* the same action staged badly (arms in front of the body) and well (arms clear of the body).
- *Exercise:* six Bheemu poses (neutral, reach up, wind-up, shock, sitting dazed, run) as a silhouette sheet.
- *Expected output:* one sheet, colour above, silhouette below.
- *Rubric:* each pose scored 0-2 for "can you name the action from the silhouette alone". Pass: 10 of 12.
- *If it fails:* move limbs outside the body outline, tilt the line of action, break left/right symmetry, re-render.

**L2. Construction and volume.** `not started`
- *Objective:* the character is built from simple solid forms that keep their size from every angle.
- *Exercise:* turnaround of one character: front, three-quarter, side, back, with a height grid.
- *Rubric:* head, body and limb sizes within 5% across views; no flat or pasted-on parts.
- *If it fails:* fix the model, not the pose.

**L3. Model sheet and consistency.** `not started`
- *Exercise:* full sheet per `03-character-handbook.md`: views, expressions, mouths, eyes, hands, feet, palette.
- *Rubric:* the consistency checklist in the character handbook, all items yes.

**L4. Expressions.** `not started`
- *Exercise:* twelve expressions per lead, each built from brows, lids, pupils, mouth and head tilt together.
- *Rubric:* a viewer names 10 of 12 emotions without labels.

**L5. Hands, paws, trunk.** `not started`
- *Exercise:* each holds, pinches, points, pushes, pulls and catches a real prop.
- *Rubric:* contact is visible (fingers wrap, object does not float); no extra or missing digits.

### Level 2: Motion

**L6. Weight: the bouncing ball and the sack.** `not started`
- *Exercise:* a light ball and a heavy ball bounce; then Gaju and Bheemu do the same hop.
- *Rubric:* spacing accelerates downward; squash only on contact; the heavy one rises less and settles faster.

**L7. Walks and runs.** `not started`
- *Exercise:* side-view walk and run cycle for Bheemu (heavy) and Gaju (light), plus the cat on four legs.
- *Rubric:* feet do not slide; head bobs at the right moment; arms oppose legs; loops cleanly.

**L8. Anticipation, action, overshoot, settle.** `not started`
- *Exercise:* five single actions: pick up, throw, push, pull, sit down.
- *Rubric:* all four phases present and on different frames for different body parts.

**L9. Overlap and follow-through.** `not started`
- *Exercise:* Gaju runs, stops, turns: ears, trunk and tail overlap.
- *Rubric:* loose parts lag 2-4 frames and overshoot; no two parts share all key frames.

### Level 3: Acting

**L10. Thinking characters.** `not started`
- *Exercise:* "sees it, wants it, checks nobody is looking, takes it": 6 seconds, one character, no props moving by themselves.
- *Rubric:* each thought is a separate pose change led by the eyes; holds have life.

**L11. Animal behaviour study.** `attempted (2026-11-11: milk acting test)`
- *Exercise:* cat lapping milk, staged as in `04-frame-by-frame-handbook.md` section 3.
- *Rubric:* whole-body pose, rhythm of laps, secondary tail and ears, milk reacts.
- *Note:* first attempt staged it wrongly (front view over a table). Redo in profile on the floor.

### Level 4: Comedy

**L12. One gag.** `not started`
- *Exercise:* a 10-second gag with setup, anticipation, surprise, reaction, topper (`05-slapstick-chase-handbook.md`).
- *Rubric:* a first-time viewer can retell it; the reaction is held long enough to read.

**L13. Rule of three and escalation.** `not started`
- *Exercise:* the same attempt three times, each bigger, third one breaks the pattern.

**L14. Chase.** `not started`
- *Exercise:* a 12-second chase with one reversal and one near miss; screen direction stays consistent.

### Level 5: Production

**L15. Storyboard and animatic.** `not started`
- *Exercise:* the pilot (`08-pilot-project.md`) as panels, then as a timed animatic with scratch sound.
- *Rubric:* the story reads from the animatic alone.

**L16. A finished episode.** `not started`
- *Exercise:* the pilot taken through every stage in `06-pipeline-and-tools.md` and through QC.
- *Rubric:* the pilot's acceptance criteria.

**L17. Sound and edit.** `not started`
- *Exercise:* re-score one finished shot three ways: music only, effects only, both with silence before the hit.
- *Rubric:* judged by ear by Harshith (Claude cannot hear audio).

## Order of work

L1 → L5 → L8 → L11 (redo) → L12 → the pilot. Lessons L2-L4, L6, L7, L9, L10 are done when a shot needs them.
