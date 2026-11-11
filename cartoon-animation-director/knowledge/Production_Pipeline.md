# Production Pipeline

**Knowledge base document 9 of the master mission (Phase 1).**
Version 1.0, 2026-11-11. Follows documents 1 to 8 in this folder.

This document is the route from an idea to a finished, delivered cartoon: every stage, what goes in, what comes out, who does it, what must be true before the next stage starts, and what to do when a stage fails. It also defines how assets are approved, how versions are kept, and how revisions are handled.

## 0. How to read this document

### 0.1 Labels

| Label | Meaning | Status |
|---|---|---|
| **[M]** | Read from our repository | Established project fact |
| **[T-earlier]** | Recorded as tested in `references/06-pipeline-and-tools.md` | Not re-checked now |
| **[R]** | My proposal | Proposed workflow, untested as a whole |
| **[U]** | Unverified assumption | Check first |

### 0.2 What exists and what this adds

`references/06-pipeline-and-tools.md` already lists thirteen stages in one table, with tools and a one-line acceptance for each, and says who can do what. `tools/new_episode.py` creates the episode folders and a manifest. This document keeps those stage names and folders and adds the gates, responsibilities, failure handling, approval rules, version control and revision process.

**The pipeline as a whole has never been run end to end.** The ten existing episodes were made faster, with fewer stages, and Harshith judged the result basic (lessons learned 11). The pilot in `references/08-pilot-project.md` is the planned first full run. So every gate below is a proposed workflow built from established parts.

---

## 1. Overview

```
 0 Idea ─▶ 1 Script ─▶ 2 Boundary checks ─▶ 3 Asset audit ─▶ 4 Storyboard ─▶ 5 Animatic
                                                  │                              │
                                     (new or changed assets)                 GATE B: timing
                                                  ▼                              │
                                        6 Assets ── GATE A: approval             ▼
                                                                    7 Keys ─▶ 8 In-betweens and effects
                                                                                 │
 14 Retrospective ◀─ 13 Delivery ◀─ GATE D ◀─ 12 Review ◀─ 11 QC ◀─ 10 Edit and render ◀─ 9 Sound
                        (approval to upload)   and revisions   GATE C: candidate
```

Four gates need Harshith: **A** (assets), **B** (animatic), **C/D** (the finished candidate, then upload). Everything between gates can run without stopping, provided nothing touches an approved asset.

---

## 2. Roles

| Role | Who | Does |
|---|---|---|
| **Owner and approver** | Harshith | Approves assets, animatics, candidates and uploads. Watches at full speed. Listens. Decides anything subjective. Uploads |
| **Director and maker** | Claude | Script, boards, engine code, renders, sound, automatic checks, reports. States limits. Never approves its own work |
| **First-time viewer** | Someone who has not seen it | Retell test |
| **Telugu reader and speaker** | Harshith or another | Wall text and spoken lines |
| **Outside help, when wanted** | A human animator or voice actor | Hand-drawn studies; voices |

**Responsibility by stage.** D = does it, A = approves, C = consulted.

| Stage | Claude | Harshith | Viewer |
|---|---|---|---|
| 0 Idea | D | D, A | |
| 1 Script | D | C | |
| 2 Boundary checks | D | A on any doubt | |
| 3 Asset audit | D | | |
| 4 Storyboard | D | C | |
| 5 Animatic | D | **A (gate B)** | C |
| 6 Assets | D (proposals only) | **A (gate A)** | |
| 7-8 Animation | D | | |
| 9 Sound | D | **A by ear** | |
| 10 Edit and render | D | | |
| 11 QC | D (automatic and stills) | D (eyes, ears) | C |
| 12 Review and revisions | D | **A (gate C)** | |
| 13 Delivery | D (file) | **A, D (gate D, upload)** | |
| 14 Retrospective | D | C | |

---

## 3. The stages

Folder names are those created by `tools/new_episode.py` [M]. Knowledge documents are in `cartoon-animation-director/knowledge/`.

### Stage 0. Idea

| | |
|---|---|
| Purpose | One situation worth 20 to 40 seconds |
| Input | The series bible (`toon-slapstick/series/bheemu-gaju.md`); the cast; a place; an object two characters want |
| Output | One sentence: "X wants A, does B, and gets C instead" |
| Gate | The sentence exists and needs "and then" no more than once |
| Fails when | It needs dialogue to work; it is a known gag; it needs a character to be mean |
| Then | Change the mechanism or drop it. Ideas are cheap |
| See | `Slapstick_Comedy.md` section 2 |

### Stage 1. Script and beat sheet

| | |
|---|---|
| Input | The sentence |
| Output | `script/`: cause and effect chain as arrows; beat sheet with frame ranges on a 12-frame grid; reactions assigned per character |
| Gate | Setup, wait, hold and reaction each have a stated length; three chain links or fewer |
| Fails when | Too many ideas; reaction has no room |
| Then | Cut to one object and one want |
| See | `Slapstick_Comedy.md` sections 2 to 9 and 16 |

### Stage 2. Boundary checks

| | |
|---|---|
| Input | Script |
| Output | A short note in `script/`: imitation test result, series rules, originality check |
| Gate | All three pass. Any doubt goes to Harshith before more work is done |
| Fails when | A child could copy it and be hurt; it resembles a known scene; someone is humiliated |
| Then | Keep the structure, change the mechanism |
| See | `Slapstick_Comedy.md` sections 13 and 14 |

### Stage 3. Asset audit and minimum reference package

| | |
|---|---|
| Purpose | Find out, before boarding, what the episode needs that does not exist |
| Input | Script; the approved models and their controls; existing props and sets |
| Output | `research/`: a table of every character, pose, view, expression, prop, set and effect needed, each marked **exists / exists with a limitation / missing** |
| Gate | Every "missing" item has a decision: restage to avoid it, propose it as a new asset (stage 6), or drop the beat |
| Fails when | The gag depends on a pose or view the models cannot make |
| Then | State the limitation and show what existing controls can do (lessons learned 25). Do not approximate silently |
| See | `Character_Design_Bible.md` 13.5 (per-shot minimum reference package). Do not block work on references a shot does not need (lessons learned 21) |

### Stage 4. Storyboard

| | |
|---|---|
| Input | Beat sheet; asset audit |
| Output | `storyboard/`: floor plan, shot list, panels (engine stills), hook-up frames for each cut |
| Gate | The story reads from pictures alone, judged by a person; continuity list clean |
| Fails when | Action hidden; wrong shot size; line crossed |
| Then | Restage at thumbnail level |
| See | `Storyboard_and_Cinematography.md` |

### Stage 5. Animatic (GATE B)

| | |
|---|---|
| Input | Board; scratch sound |
| Output | `animatic/`: a small real-time render with scratch sound |
| Gate | Automatic file checks pass; **Harshith has watched and listened**; a first-time viewer retold it; shot lengths frozen and recorded |
| Fails when | Holds too short; the wait too long or too short; a cut confuses |
| Then | Change lengths and render again. Compare alternatives in playback, never from stills (lessons learned 29) |
| See | `Storyboard_and_Cinematography.md` section 12 |

### Stage 6. Assets (GATE A)

Only entered when stage 3 found something missing or changed.

| | |
|---|---|
| Input | The list of proposed assets |
| Output | Review sheets marked **REVIEW ONLY / PROPOSAL**, on the review branch; a list of inconsistencies with the approved model |
| Gate | Harshith reviews the sheet. **Approval to prepare or accept a sheet is not approval to alter the production model.** A separate explicit approval is needed to implement, and another to merge |
| Fails when | The proposal changes something that was not asked; a rig does not reproduce the approved drawing at rest |
| Then | Revise the sheet. The production model is untouched throughout |
| See | Section 5 of this document; `Character_Design_Bible.md` section 13 |

New props, backgrounds and effects that touch no approved character are lighter: they are new code in a new file or function, shown as stills before use.

### Stage 7. Key animation

| | |
|---|---|
| Input | Frozen animatic; approved assets |
| Output | `keyframes/`: the episode file with key poses; a silhouette sheet |
| Gate | Each key reads as a silhouette (a person scores it); every contact on a drawn frame |
| Fails when | Weak or mirrored poses; twins; a key lost on a held frame |
| Then | Re-pose; move the key to an even engine frame |
| See | `Frame_By_Frame_Animation.md` sections 3 to 6; `Slapstick_Comedy.md` 11.2 |

### Stage 8. Breakdowns, in-betweens, effects and secondary motion

| | |
|---|---|
| Input | Keys |
| Output | `inbetweens/`, `clean/`, `colour/` as needed: full motion with arcs, overlap, effects, and a living motion in every hold |
| Gate | Moves stepped; per-frame tables read at every contact; four phases in every action |
| Fails when | Even spacing; sliding; dead holds; effects that steal attention |
| Then | Add breakdowns; offset loose parts by 2 to 4 frames; key a blink or an ear in each hold |
| See | `Frame_By_Frame_Animation.md` sections 5, 8, 9 and 12. Generated in-betweens are a separate, unadopted test (`AI_Video_Production.md` 8.1) |

### Stage 9. Sound

| | |
|---|---|
| Input | Picture with frozen lengths |
| Output | `sound/effects/`, `sound/music_dialogue/`: cue sheet, voice files, the mixed WAV, the licence log |
| Gate | Automatic: stream, length, loudness recorded. **Real gate: Harshith listens** |
| Fails when | A hit is early; music never stops; a borrowed sound |
| Then | Fix the cue sheet, not the mix by hand |
| See | `Sound_Design.md` |

### Stage 10. Edit and render

| | |
|---|---|
| Input | Shots, audio |
| Output | `comp/`, `renders/`: the full-size render and the delivery encode, version-numbered |
| Gate | `qc_frames.py video` passes |
| Fails when | Wrong size or rate; audio length mismatch |
| Then | Fix and re-render; never patch a file by hand |
| Facts | Render is CPU only, about 3 minutes per 30 s at 1080p [T-earlier]. Delivery encode: H.264, CRF 22, `-preset slow -tune animation`, AAC 160 kbps, `+faststart`, written by `Show.main` in `final` mode as `bheemu_gaju_epNN_slug.mp4` [M] |

### Stage 11. Quality control

| | |
|---|---|
| Input | The candidate file |
| Output | `qc/`: the QC report |
| Gate | No rubric line at 0, total at least 20 of 26, no blocker; the report lists what was and was not inspected |
| Fails when | Any of the above is not met |
| Then | Section 8 of this document |
| See | `Quality_Control.md`; `references/07-qc-rubric.md` |

### Stage 12. Review and revisions (GATE C)

| | |
|---|---|
| Input | Candidate plus QC report |
| Output | Harshith's notes, or his approval of the candidate |
| Gate | Explicit approval in words |
| Then | Section 7 (revisions) |

### Stage 13. Delivery (GATE D)

| | |
|---|---|
| Input | Approved candidate |
| Output | The uploaded video; the file, episode code and report pushed to GitHub |
| Gate | Release checklist complete (`Quality_Control.md` section 14); explicit approval to upload. Upload is Harshith's, or done through a browser only with his approval for that upload |
| Platform choices | Title, description, audience setting, any required disclosure: Harshith's decisions **[U]** on current platform rules |

### Stage 14. Retrospective

| | |
|---|---|
| Input | Everything that went wrong; viewer reactions; channel data when available |
| Output | New or changed rules in `references/09-lessons-learned.md`; unresolved items added to the decision register |
| Gate | Harshith is told what was added |

---

## 4. The gates in detail

| Gate | What is shown | What approval means | What it does **not** mean |
|---|---|---|---|
| **A. Assets** | Review sheets with a red REVIEW ONLY banner; list of differences from the approved model | "This direction is acceptable" or "implement this" | Sheet approval is not model approval. Implementation and merge each need their own words |
| **B. Animatic** | A real-time rough with scratch sound | Timing and shot plan are frozen | That the finished animation will be accepted |
| **C. Candidate** | The finished render with its QC report | This version is good enough | That it may be uploaded |
| **D. Upload** | The release checklist | Publish this file | Anything about the next episode |

**Reading an approval.** Take it at its narrowest meaning. "Approved as a development direction only" (the Stage 3 Laddu decision) approves a direction and nothing else. If the scope of an approval is unclear, ask before acting on the wider reading.

**When Harshith is not available.** Work continues up to the next gate and stops there. Preparatory work for the stage beyond the gate may be done if it touches nothing approved and is labelled as waiting.

---

## 5. Asset approval and change control

### 5.1 What is protected [M]

| Protected | Where |
|---|---|
| Production character code | `toon-slapstick/engine/chars.py`, `cast.py` |
| Engine behaviour | `toon-slapstick/engine/toon.py` and the other engine modules |
| Existing presets | `toon-slapstick/engine/show.py` (`CALM` to `SLEEP`) |
| The model baseline | `cartoon-animation-director/knowledge/model_baseline.json` |
| Episode 1 | `toon-slapstick/episodes/01-dosa-snatch/` |
| Approved decisions | `Character_Design_Bible.md` section 13 |

None of these is edited without explicit approval for that specific change.

### 5.2 Status words

From the decision register: **Approved** (settled). **Provisional** (in force until reviewed). **Prepare sheet** (a proposal sheet may be made; the model stays untouched). **Investigate** (tests may be run and shown; nothing implemented). **Deferred.** Add to these for assets: **Review only** (exists on the review branch) and **Development direction** (a direction to keep exploring; not usable in production).

### 5.3 The path of a character change

1. A need is found (stage 3) or Harshith asks.
2. A sheet is prepared on the review branch, every image marked REVIEW ONLY / PROPOSAL, with a list of inconsistencies with the approved model.
3. Harshith reviews. Outcomes: revise, keep as a development direction, or approve for implementation.
4. If, and only if, implementation is approved: the change is made on a branch, new presets are added without altering existing ones (rule R3), the drift check is run, and regression is run (`Quality_Control.md` section 13).
5. Results are shown. A character also needs a passed life test before production use (lessons learned 23).
6. Merge only on a further explicit approval. The baseline is rewritten only on explicit approval.
7. The decision is recorded in the register with its date and exact scope.

### 5.4 The review branch [M]

- Branch `review/stage1-character-refs` holds all review material (Stages 1 to 3 of the character review). It exists on the remote and is not merged.
- In the working clone used so far, the folder `cartoon-animation-director/review/` is in Git's local exclude file, so review files are not committed to `main` by accident. That exclude is local to a clone and is not stored in the repository; a fresh clone must set it again or take the same care by hand.
- Review files are added to the branch through a separate worktree, with a forced add because of that exclude.
- Character-review stages are closed unless a specific unresolved issue blocks a knowledge document (decision of 2026-11-11).

### 5.5 Engine changes

An engine limitation is documented as known and unresolved. The smallest safe change is written up separately in `Engine_Change_Proposals.md` and waits for review. Nothing is implemented with the finding (lessons learned 30). Three proposals are on file (P1 to P3); none is approved.

---

## 6. Version control

### 6.1 What is in the repository [M]

`github.com/Dattaharshithreddy/skillvideo`, default branch `main`, plus the review branch. `main` holds the engine, the episodes' code, the method and knowledge base, and tools.

### 6.2 Rules

| Rule | Source |
|---|---|
| Push every successful render to GitHub immediately | Lessons learned 1 (renders were lost when a server was replaced) |
| Never overwrite an approved version; versions are `v001`, `v002`... | `tools/new_episode.py` |
| Frames are named `<episode>_<shot>_<stage>_f00001.png` | Same |
| Episode folders are `NN-short-name`; shots `s01`, `s02`... | Same |
| `manifest.json` in each episode lists every asset and the status of each stage | Same |
| Review work stays on the review branch | Lessons learned 26 |
| Run the drift check before any commit touching character code | Lessons learned 14 |
| Pull with rebase before pushing `main` | Working practice in this project |
| One commit says what changed and, for documentation commits, that no code, model, preset or baseline changed | Working practice |

### 6.3 Commit hygiene [R]

- Documentation, engine code and character code go in separate commits, so that a reviewer can see at once whether anything protected moved.
- `git status` and `git diff --stat -- toon-slapstick` are checked before every documentation commit; the second must be empty.
- Secrets never go in the repository or the chat: keys and login codes are typed only in the terminal.

### 6.4 Large files [U]

Rule 1 puts renders in Git. I have not checked the repository's size or whether large-file storage is set up. At some number of episodes this will need a decision; it is listed as an open question.

---

## 7. Revisions

| Step | Do |
|---|---|
| 1. Capture | Write each note as given, with the frame or timestamp |
| 2. Classify | Local or global; blocker, major or minor (`Quality_Control.md` 12.1). Which stage does it send the work back to? |
| 3. Scope | State exactly what will change. **Change only what was asked** (lessons learned 3) |
| 4. Route | A note on timing returns to stage 5; on a pose, stage 7; on a design, stage 6 with its gate; on sound, stage 9 |
| 5. Fix | Make the change as a new version; the previous version stays |
| 6. Re-check | The changed shot from the top, plus the cuts on both sides, plus anything downstream (sound cues after a re-time) |
| 7. Report | What changed, what did not, what was re-checked |
| 8. Learn | If the note is a principle and not a one-off, add it to lessons learned and say so |

**How far back a change reaches.**

| Change to | Redo |
|---|---|
| A sound level | Stage 9 mix, 10, 11 |
| One pose | 7 for that shot, 8, 10, 11; check sound sync |
| A shot's length | 5 for that shot, then 7 to 11 and **all later sound cues** |
| The shot order | 4, 5, then everything |
| A character design | 6 with gate A, then every shot the character is in, plus regression |
| The idea | Start again; keep the retrospective |

This table is why the gates are where they are: the further back a change reaches, the earlier it should be caught.

---

## 8. Failure handling

### 8.1 By type

| Failure | Detected by | Response | Decided by |
|---|---|---|---|
| A needed pose or view does not exist | Asset audit | Restage, or propose an asset, or drop the beat. State the limitation | Claude proposes; Harshith chooses if an asset is proposed |
| The engine cannot express an action | Trying it | Say so; show what existing controls give; write a proposal if warranted | Harshith |
| A key is lost on a held frame | Per-frame table | Move the key to an even engine frame, or note both timing options for playback | Claude; Harshith for a timing choice |
| Automatic check fails | `qc_frames.py` | Fix the cause; re-render | Claude |
| Drift check fails | The drift check | **Stop.** Find the unintended change; revert it. Never rewrite the baseline to pass | Claude reverts; Harshith for anything else |
| A rubric line scores 0 | QC | Blocker: fix before showing | Claude |
| A safety or originality doubt | Stage 2, or anyone at any time | Stop the gag; change the mechanism; ask if unsure | Harshith |
| Harshith rejects the animatic | Gate B | Back to stage 4 or 5 | Harshith |
| Harshith rejects the candidate | Gate C | Section 7 | Harshith |
| A render is lost | A missing file | Re-render from the episode code, which is in Git. This is why rule 1 exists | Claude |
| A tool is unavailable | An error | Say which, and what could not be done; do not substitute silently | |
| I cannot verify something | Always possible | Say "not verified" and why | |

### 8.2 Stop conditions

Stop and report, without trying to work round it, when:

- the next step would edit a protected file (5.1) without explicit approval;
- the drift check fails;
- a gag fails the imitation test and no safe mechanism is found;
- an approval's scope is unclear;
- two instructions conflict;
- a result would have to be claimed without having been tested.

---

## 9. Choosing the workflow

Not every job needs all fourteen stages.

| Job | Stages | Gates |
|---|---|---|
| **A timing or acting test** (one action, plain background) | 1, 7, 8, 10, a short QC note | Shown as a test; no approval implied |
| **A character life test** | 1, 6 (review only), 7, 8, 10, review | Gate A logic: review only, never merged without approval |
| **A reference sheet** | 6 only | Review; sheet approval is not model approval |
| **A single gag** (10 s) | 0 to 5, 7 to 12 | B and C |
| **The pilot** | All, in full | All four |
| **An episode** | All | All four |
| **A revision** | Section 7 | The gate of the stage it returns to |
| **A knowledge document** | Research, write, validate, commit to `main`, report | Harshith's review of the document |
| **An engine or model change** | Proposal file, approval, branch, drift check, regression, show, approval, merge | Two explicit approvals |
| **A generated-video test** | `AI_Video_Production.md` section 8, as a labelled test | Approval before any paid call |

**Decision rule.** Use the smallest workflow that answers the question being asked, and say which one was used. Never use a small workflow to slip past a gate that the full one would have had.

---

## 10. Worked example: where "The ball that went up" stands

| Stage | State | Evidence |
|---|---|---|
| 0 Idea | Done | One sentence in `Slapstick_Comedy.md` 15.1 |
| 1 Script | Done | Beat sheet, chain, reactions |
| 2 Boundary checks | Done by me; not reviewed | Soft ball, no intent, recovery on screen. My originality check passed; a person has not looked |
| 3 Asset audit | Done | Uses approved models, presets and the existing `ball` prop. Limitations listed: no "dawning" expression, no slump, trunk does not reach the ball |
| 4 Storyboard | Partly | Twelve key frames as one shot; a six-shot list written in `Storyboard_and_Cinematography.md` 13.1, not boarded |
| 5 Animatic | **Not done** | Nothing rendered. Gate B not reached |
| 6 Assets | Not needed | No new asset proposed |
| 7 to 13 | Not started | |

The next action that would produce evidence is stage 5: a small render with scratch sound for Harshith to watch and hear. It has not been asked for.

---

## 11. Common mistakes

| Mistake | How to detect | Fix |
|---|---|---|
| Skipping the animatic | Detailed keys exist; timing still changing | Go back to stage 5 |
| Starting sound before lengths are frozen | Cues re-timed more than once | Freeze at gate B |
| Reading a sheet approval as a model approval | Character code changed after a sheet review | Revert; ask |
| Fixing a global problem inside one shot | A protected file changed in a shot commit | Revert; report; propose |
| Quantity over one piece done properly | Several episodes at rubric scores under the bar | One pilot through every gate first |
| Silent substitution | A different tool, pose or method used with no note | Say what was substituted and why |
| Overwriting a version | No previous file to compare with | New version number every time |
| Not pushing | A render exists only on one machine | Push at once |
| Asset audit after boarding | A board that needs a pose nobody has | Audit first |
| Treating my QC as approval | "Passed" with no person named | Gate C is Harshith's |
| A revision that changes more than was asked | The diff touches other shots | Revert the extra; re-check neighbours |

---

## 12. Checklists

**Start of an episode**
- [ ] `tools/new_episode.py NN-name` run; manifest created
- [ ] One-sentence idea written
- [ ] Lessons learned read; confirmed rules are binding

**Before gate B**
- [ ] Beat sheet, boundary note, asset audit, shot list and board in their folders
- [ ] Every missing asset has a decision
- [ ] Animatic rendered small with scratch sound; automatic checks run

**Before gate C**
- [ ] All shots keyed, in-betweened, with living holds
- [ ] Sound built from the cue sheet; licence log complete
- [ ] Full render and delivery encode made as a new version
- [ ] QC report complete and honest
- [ ] Pushed to GitHub

**Before gate D**
- [ ] Release checklist in `Quality_Control.md` section 14 complete
- [ ] Explicit approval to upload, in words

**After**
- [ ] Retrospective written; rules added; Harshith told

**Every documentation or tooling commit**
- [ ] `git diff --stat -- toon-slapstick` is empty
- [ ] Drift check passes
- [ ] Review branch untouched and unmerged
- [ ] Commit message says what did and did not change

---

## 13. Open questions and inconsistencies found

**For Harshith.**

1. Are the four gates the ones you want, and is the animatic gate (B) acceptable as a hard stop before detailed animation?
2. The pilot ("The Milk Bowl") needs a cat profile and crouch that are review-only. Should the pilot wait for those, or be restaged with approved assets, or should a different pilot be chosen that needs none (worked example 1 needs none)?
3. Renders in Git: keep rule 1 as it is, or move renders to release assets or other storage as the series grows?
4. Who is the first-time viewer, and who checks Telugu?
5. The ten existing episodes: leave as published work, or bring any back through this pipeline? Episode 1 is not to be changed in either case.

**Inconsistencies in the repository (reported, not changed).**

- `toon-slapstick/references/api.md` says the stage is 1920 × 1080 with `GROUND = 900`. The engine is 1080 × 1920 with `GROUND = 1480`.
- `cartoon-animation-director/SKILL.md` points only to `references/` and does not mention the `knowledge/` documents. `Animation_Skill.md` is written to replace it, if approved.
- The master mission text is not stored in the repository; it exists only as an uploaded file in the working session.
- The root `README.md` describes the cgi-shorts skill only.

**Points where documents 3 and 4 are incomplete or overstated (reported; those documents are unchanged).**

- `Frame_By_Frame_Animation.md` section 19 says there is no moving hold except line boil. Line boil is off unless a stage sets `boil`, and no episode sets it. Separately, `acting.py` has helpers that write small keyed motions for holds (`bob`, `blink`); documents 3 and 4 do not mention them. The engine still has no automatic moving hold, so the conclusion stands, but the helpers should have been named.
- `Slapstick_Comedy.md` section 20.1 says the trunk and hands cannot be aimed at a point. The engine has `Stage.probe` (the world position of an anchor), `attach` (a prop rides on a hand or trunk anchor), and offset controls for arms and trunk. Aiming is possible by hand with these; what is missing is automatic reach. The statement is too strong.
- `Slapstick_Comedy.md` section 13.3 proposes no dizzy-star injury effects. `scene.stars` exists and is called in six episode files, and `acting.take` draws surprise marks. The proposed rule conflicts with existing episodes and needs Harshith's decision before it can be a rule.

---

## 14. References

- `references/06-pipeline-and-tools.md` (stages, tools, who can do what), `07-qc-rubric.md`, `08-pilot-project.md`, `09-lessons-learned.md`
- `tools/new_episode.py`, `tools/qc_frames.py`, `templates/qc_report.md`
- `toon-slapstick/engine/show.py` (`Show.main`, delivery encode), `toon-slapstick/SKILL.md`, `toon-slapstick/series/bheemu-gaju.md`
- `Character_Design_Bible.md` section 13 (decision register), `Engine_Change_Proposals.md`
- `Animation_Fundamentals.md`, `Frame_By_Frame_Animation.md`, `Slapstick_Comedy.md`, `Storyboard_and_Cinematography.md`, `AI_Video_Production.md`, `Sound_Design.md`, `Quality_Control.md`, `Animation_Skill.md`

No outside source was opened for this document.

---

## 15. Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.0. Stages taken from `references/06-pipeline-and-tools.md` and extended with gates, roles, failure handling, approval and version rules. The pipeline has not been run end to end. Not reviewed by Harshith. |
