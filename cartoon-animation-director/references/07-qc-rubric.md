# Quality-control rubric

Every shot is scored before it is shown. Score each line 0, 1 or 2.

- **0** = fails; visible to a casual viewer.
- **1** = weak; a careful viewer notices.
- **2** = good.

**Bar to send a shot:** no 0 anywhere, and at least 20 of 26.
**Bar to call a lesson mastered:** at least 23 of 26, and Harshith accepts it.

## The thirteen checks

| # | Check | How it is inspected | Auto or eyes |
|---|---|---|---|
| 1 | Character identity and model consistency | Compare stills with the model sheet: markings, accessories, colours | Eyes |
| 2 | Anatomy and perspective | Digit counts, joints bending the right way, nothing detached or stretched thin | Eyes |
| 3 | Clear silhouettes and readable poses | Silhouette sheet of the key poses | Eyes (sheet made automatically) |
| 4 | Arcs | Track hand, head and prop positions across frames | Eyes; path can be plotted from the engine |
| 5 | Timing and spacing | Frame counts against the timing plan; no mid-speed mush | Partly auto (hold/burst statistics) |
| 6 | Weight and contact | Feet planted, contact shadows, objects held not floating | Eyes |
| 7 | Transitions between poses | Step through each move; anticipation → action → overshoot → settle all present | Eyes |
| 8 | Anticipation and follow-through | Loose parts lag and overshoot; keys not all on the same frames | Partly auto (key-frame lists) |
| 9 | Background and camera consistency | Nobody cut off or hidden; no jumps in position across cuts | Eyes |
| 10 | No flicker or morphing | Frame-difference spikes outside planned cuts and hits | Auto, then eyes |
| 11 | Audio sync | Sound events within 1 frame of the picture event; audio and video the same length | Auto for length; ears for sync (Harshith) |
| 12 | Frame integrity | No missing, duplicated-by-mistake or misordered frames; right size and frame rate | Auto (`qc_frames.py`) |
| 13 | Story and comedy | A first-time viewer can retell it; the reaction is held | Harshith |

## What "inspected" means

- **Contact sheet** shows poses and staging. It does not show motion.
- **Stills** at takes and hits show the extremes.
- **Frame stepping** through a move shows arcs, spacing and overlap.
- **Full-speed viewing** shows timing. Claude cannot watch at full speed; it steps through frames. Say so.
- **Listening** is always Harshith.

The report must list which of these were actually done. Never write "passed" for a check that was not inspected.

## Problem report format

For each problem:

1. **Observed issue:** what is wrong, in plain words.
2. **Where:** shot, frame number or timestamp.
3. **Likely cause:** which pose, key or setting produced it.
4. **Recommended correction.**
5. **Corrected instruction:** the new pose, timing or code change.
6. **Scope:** local (this shot) or global (the character, the engine, every episode).

Example:

> 1. Cat's head separates from the body when he leans over the pot.
> 2. Milk acting test, frames 100-130.
> 3. `head_dx=-118` moves only the head; the chest stays put.
> 4. Lean the whole body.
> 5. Rotate the body about the hips by 14° and limit `head_dx` to ±50.
> 6. Global: add a lean control to the cat; add a rule to lessons learned.

## QC report template

See `templates/qc_report.md`. One report per shot or per episode, saved in the episode's `qc/` folder.
`tools/qc_frames.py` writes the automatic part; the eyes part is filled in by whoever looked.
