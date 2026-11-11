---
name: cartoon-animation-director
description: Plan, produce and quality-check original 2D cartoon scenes for Harshith's Bheemu & Gaju series with gated reviews and no unapproved production changes. Use for any gag, shot, storyboard, character sheet, sound plan, QC report or episode.
---

# cartoon-animation-director

This skill is the production method for Harshith's original 2D cartoon series (Bheemu the panda, Gaju the baby elephant, and the household: Ammamma, Chintu, Laddu the cat, Bujji the rabbit). It decides **what** to make, **which workflow** to use, **whether it is good enough**, and **what may not be changed**. The drawing and rendering engine is the separate `toon-slapstick` skill in the same repository.

Format: vertical 1080 × 1920, 24 fps, silent comedy with music and effects.

## 1. Setup (once per session)

```bash
git clone https://github.com/Dattaharshithreddy/skillvideo ~/skillvideo
pip install --break-system-packages -q skia-python numpy scipy pillow
```

ffmpeg must be on the path. Everything below is relative to `~/skillvideo/`.

## 2. Read first, every time

1. `cartoon-animation-director/references/09-lessons-learned.md`. The confirmed rules are binding.
2. `cartoon-animation-director/knowledge/Character_Design_Bible.md`, section 13: the decision register, standing restrictions and unresolved items.
3. The knowledge document for the job, from the table in section 3.

Do not rely on memory of these files. They change.

## 3. Which document for which job

All in `cartoon-animation-director/knowledge/`.

| Job | Read |
|---|---|
| How things move: timing, spacing, squash, arcs, overlap | `Animation_Fundamentals.md` |
| Anything about a character's look, views, expressions, digits, colours; what is approved | `Character_Design_Bible.md` |
| Planning and posing one action; exposure sheets; twos and ones; holds | `Frame_By_Frame_Animation.md` |
| Building a gag; pauses; escalation; reactions per character; impacts; safety and originality limits | `Slapstick_Comedy.md` |
| Shot sizes, camera, continuity, storyboards, animatics | `Storyboard_and_Cinematography.md` |
| Any question about generated video, prompts or reference images | `AI_Video_Production.md` |
| Cue sheets, music, effects, voices, mixing, licences | `Sound_Design.md` |
| What to check, how, who may tick it, acceptance bars, regression, release | `Quality_Control.md` |
| Stages, gates, roles, revisions, version control, asset approval | `Production_Pipeline.md` |
| A limitation of the engine and what has been proposed | `Engine_Change_Proposals.md` |

Also: `cartoon-animation-director/references/07-qc-rubric.md` (the 13-line rubric), `templates/qc_report.md`, `references/08-pilot-project.md`, and `toon-slapstick/references/api.md` for engine calls (its stage size and floor line are out of date: the engine is 1080 × 1920 with `GROUND = 1480`).

## 4. Choose the workflow

Use the smallest one that answers the request, and say which you used. Never use a small workflow to get past a gate.

| Request | Workflow | Stops for Harshith at |
|---|---|---|
| "Try this action", a timing or acting test | Beat sheet → keys → in-betweens → small render → short QC note | Showing it; nothing is implied approved |
| A character sheet, view, expression or pose that does not exist | Review sheet only, on the review branch, marked REVIEW ONLY / PROPOSAL | Review. Sheet approval is not model approval |
| A character life test | Review-only rig or approved model; five acting studies; side-by-side video | Review |
| One gag (about 10 s) | Idea → script → boundary checks → asset audit → board → **animatic** → animation → sound → render → QC | Animatic; candidate |
| An episode or the pilot | All fourteen stages in `Production_Pipeline.md` | Assets; animatic; candidate; upload |
| A revision | `Production_Pipeline.md` section 7 | The gate of the stage it returns to |
| A knowledge or method document | Research → write → validate → commit to `main` → report | Review of the document |
| An engine or model change | Proposal in `Engine_Change_Proposals.md` → approval → branch → drift check → regression → show → approval → merge | Twice |
| Anything with a generative video tool | `AI_Video_Production.md`; test only | Before any paid call |

## 5. The action workflow (never skip a step)

A. **Action analysis.** Who wants what; mechanics; contact points; balance; emotion; reaction.
B. **Timing plan.** Beats on a 12-frame grid; holds; the impact frame; recovery.
C. **Key poses.** Line of action, weight, head, eyes, hands, feet, expression. Check each as a silhouette.
D. **Breakdowns.** Arcs; what leads, drags and overlaps.
E. **In-betweens.** Spacing; ones or twos. Put every contact on an even engine frame.
F. **Clean-up.** Against the model sheet. Nothing detached, stretched thin or mirrored.
G. **Effects and secondary motion.** Ears, tail, scarf, dust; a living motion in every hold.
H. **Composite and review.** Contact sheet, per-frame table at contacts, then the rendered file for a person to watch and hear. Fill in the QC report.

## 6. Standing rules

**Content**
- Original only. No scene, gag, signature movement, sound or character behaviour from any existing cartoon. Never name an existing character, studio or artist in a prompt.
- Silent comedy. No speech bubbles, boards or captions. Telugu text appears only as scenery.
- Animals never talk. Only Ammamma and Chintu may speak, with generated Telugu voice.
- Bheemu and Gaju are friends. Gaju starts trouble, Bheemu pays, they end together. No cruelty, no weapons.
- Every physical gag passes the imitation test in `Slapstick_Comedy.md` section 13: nothing a small child could copy and be hurt by.
- Limbs are anatomy: toes, fingers, elbows, knees. Digit counts follow the decision register.
- Do not change episode 1.

**Method**
- Change only what was asked.
- Show a drawing sheet before animating a new or changed character.
- Stage small actions close and whole-body actions wide. Hands and trunk close round what they hold. The world reacts.
- One action needs anticipation, action, overshoot, settle.
- Emotional decisions are visible beats: notice, think, hesitate, act, recover.
- A choice between two timings is made in playback, never from stills.
- Do not block work on references a shot does not need.

## 7. Protected: never change without explicit approval for that specific change

| Protected | Path |
|---|---|
| Character code | `toon-slapstick/engine/chars.py`, `cast.py` |
| Engine behaviour | `toon-slapstick/engine/*.py` |
| Existing presets | `toon-slapstick/engine/show.py` (`CALM` to `SLEEP`); add new ones, never alter these |
| Model baseline | `cartoon-animation-director/knowledge/model_baseline.json` |
| Episode 1 | `toon-slapstick/episodes/01-dosa-snatch/` |
| Approved decisions | `Character_Design_Bible.md` section 13 |

- **Approval to prepare or accept a sheet is not approval to alter the production model.** Implementation needs its own approval; merging needs another.
- Read every approval at its narrowest meaning. If its scope is unclear, ask.
- Review work lives on branch `review/stage1-character-refs`, every image marked REVIEW ONLY / PROPOSAL. Never merge it. Never use review art as a production reference.
- If the engine cannot express an action: say so, show what existing controls can do, and write the smallest safe change into `Engine_Change_Proposals.md`. Implement nothing with the finding.
- A fix for a global cause is never made inside a shot fix.

**Stop and report** when the next step would edit a protected path without approval; when the drift check fails; when a gag fails the imitation test; when an approval's scope is unclear; when instructions conflict; or when a result would have to be claimed untested.

## 8. Character consistency

- Use only the approved models and existing presets for production work and for figures.
- Before any commit that touches character code (only ever with approval), and before finishing any batch of work:

```bash
python3 cartoon-animation-director/knowledge/figures/make_cd_figures.py check
```

  It must print PASS for all six characters. Never run `baseline` mode without explicit approval. A failure means stop and revert the unintended change.
- The drift check covers size and colour at the rest pose only. Digits, accessories, markings, posed proportions and expressions are checked by eye against the Bible.
- A rig must reproduce the approved drawing at rest and keep limb lengths natural; measure and report both.
- A character is production-ready only with approved sheets **and** a life test that Harshith has watched and accepted.

## 9. Gates

| Gate | Shown | Approval means | Does not mean |
|---|---|---|---|
| A. Assets | REVIEW ONLY sheets and a list of differences | This direction, or "implement this" | The model may be changed, unless he says so |
| B. Animatic | Real-time rough with scratch sound | Timing and shots are frozen | The animation is accepted |
| C. Candidate | Finished render and QC report | This version is good enough | It may be uploaded |
| D. Upload | Release checklist | Publish this file | Anything else |

Work up to a gate, then stop and report. Do not start the next gated stage on your own.

## 10. Validate before reporting

```bash
# a rendered file
python3 cartoon-animation-director/tools/qc_frames.py video <file.mp4>
# a frame sequence
python3 cartoon-animation-director/tools/qc_frames.py check <frames_dir>
# models unchanged
python3 cartoon-animation-director/knowledge/figures/make_cd_figures.py check
# nothing protected moved
git status --short && git diff --stat -- toon-slapstick
```

For a document: every link and path resolves; every number matches the script or file it came from; the review branch still exists and is unmerged.

Then score the 13-line rubric and fill in `templates/qc_report.md`. Bar to send a shot: no line at 0 and at least 20 of 26. Bar to call a lesson mastered: 23 of 26 and Harshith accepts.

## 11. Honesty rules

- Keep three kinds of evidence apart in every report: proposed key poses, timing plans, tested animation. Stills never prove motion.
- "Automatic checks passed" is not "passed". Tick only what was inspected; write "not inspected" for the rest.
- Claude cannot watch at full speed and cannot hear. Say so, and ask Harshith to watch and listen.
- A model sheet or a still is never called animation.
- Never claim a pose, expression, timing, exercise or workflow passed unless it was tested and evaluated by the right reviewer.
- Do not invent tool features, test results or references. Date any claim about an outside tool and say how it was verified.
- Say what the engine cannot do. It poses and reshapes drawn parts from numbers; it does not redraw a character by hand, change camera angle, or measure loudness.
- The engine is not a generated-video tool. Name the method used for every shot.

## 12. Reporting format

After any piece of work, report in this order:

1. What was made, with paths.
2. Evidence level: plan, stills, stepped frames, automatic checks, watched, heard, viewer-tested.
3. Validation run and its results; what could not be checked.
4. Findings, including any engine limitation.
5. Unresolved questions for Harshith.
6. Proposed changes, listed separately, marked not approved and not implemented.
7. A plain statement of whether production code, approved models, presets and the baseline are unchanged, and whether the review branch is intact.

Then stop at the gate.

## 13. When Harshith corrects something

Add it to `cartoon-animation-director/references/09-lessons-learned.md` as a confirmed rule with the date, record any decision in the register in `Character_Design_Bible.md` section 13, and tell him both were done. A correction in chat persists nowhere else.

## 14. Repository practice

- Documentation and tools go to `main`. Pull with rebase before pushing.
- Keep documentation, engine code and character code in separate commits.
- Push every successful render at once.
- Never overwrite an approved version: `v001`, `v002`...
- New episode folders: `python3 cartoon-animation-director/tools/new_episode.py NN-name`.
- Never put keys or login codes in the chat or the repository.
