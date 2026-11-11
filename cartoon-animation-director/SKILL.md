---
name: cartoon-animation-director
description: Direct and quality-check hand-drawn-style 2D cartoon work for Harshith's Bheemu & Gaju series. Use before animating any action, designing a character, planning a gag, or reviewing a shot.
---

# cartoon-animation-director

This skill is the production method. The drawing and rendering engine is the separate `toon-slapstick`
skill (same repo, `toon-slapstick/`). Use this one to decide WHAT to animate and whether it is good
enough; use that one to make it.

Repo: `https://github.com/Dattaharshithreddy/skillvideo`, folder `cartoon-animation-director/`.

## Read first

1. `references/09-lessons-learned.md` — Harshith's corrections turned into rules. Confirmed rules are binding.
2. `references/04-frame-by-frame-handbook.md` — the action workflow and the principles.
3. `references/07-qc-rubric.md` — the gate every shot passes before it is shown.
4. Then whichever of 01 (curriculum), 03 (characters), 05 (slapstick), 06 (pipeline), 08 (pilot) the job needs.

## Workflow for every action (never skip a step)

A. **Action analysis.** Who wants what, the physical mechanics, contact points, balance, the emotion, the reaction.
B. **Timing plan.** Duration, beats on a 12-frame grid at 24 fps, holds, where it accelerates, the impact frame, recovery.
C. **Key poses.** Write each as: line of action, weight, head, eyes, hands, feet, expression. Check each as a silhouette.
D. **Breakdowns.** How it travels between keys: arcs, what leads, what drags, what overlaps.
E. **In-betweens.** Spacing: close together for slow, far apart for fast. Decide ones or twos per move.
F. **Cleanup.** Volumes and proportions against the model sheet. Nothing detached, stretched thin or mirrored.
G. **Effects and secondary motion.** Ears, tail, scarf, dust, ripples, things in the world that react.
H. **Composite and review.** Contact sheet, then full-speed video, then frame-by-frame at the hits. Fill in the QC report.

## Staging rules that came from real mistakes

- Stage the action so the whole body tells it. A cat drinking is a side view on the floor, not a head over a table.
- Hands hold things: fingers or trunk close around the object before it moves.
- The world reacts: if a tree is shaken, the tree moves, leaves fall, fruit swings.
- Use a closer shot for small actions. One wide shot for a whole episode reads as flat.
- One action gets at least: anticipation, action, overshoot, settle. Two poses is not animation.

## Honesty rules

- Never say a shot passed inspection unless the frames were actually looked at. Say what was and was not checked.
- A model sheet or a still pose is not animation and is never called that.
- Say plainly what this engine cannot do (it moves and reshapes drawn parts; it does not redraw the character every frame).
- Audio cannot be heard by Claude. Say so and ask Harshith to listen.

## When Harshith corrects something

Add it to `references/09-lessons-learned.md` as a confirmed rule with the date, and tell him it was added.
A correction in chat does not persist anywhere else by itself.

## Tools

- `tools/new_episode.py <NN-name>` creates the episode folder structure and manifest.
- `tools/qc_frames.py check <frames_dir>` validates a frame sequence; `video <file.mp4>` checks a finished video;
  `assemble <frames_dir> out.mp4 --fps 24 [--audio a.wav]` builds a video from frames.
