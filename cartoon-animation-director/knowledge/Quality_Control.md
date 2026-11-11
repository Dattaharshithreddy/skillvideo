# Quality Control

**Knowledge base document 8 of the master mission (Phase 1).**
Version 1.1, 2026-11-11. Follows documents 1 to 7 in this folder.

Quality control decides whether a drawing, a shot or an episode is good enough to go to the next stage. This document says what is checked, how, by whom, with which tool, and what counts as passing. Its main job is to keep two things apart that are easy to blur: **what a script can prove** and **what only a person can judge**.

## 0. How to read this document

### 0.1 Labels

| Label | Meaning | Status |
|---|---|---|
| **[M]** | Read from our code, or a command run this session | Established project capability |
| **[R]** | My recommendation or a proposed check | Proposed; not built or not tested |
| **[C]** | Craft convention | Established practice |
| **[U]** | Unverified assumption | Check first |

### 0.2 What already exists, and what this document adds

`references/07-qc-rubric.md` holds the 13-line scoring rubric, the bar for sending a shot, and the problem-report format. `templates/qc_report.md` is the report form. `tools/qc_frames.py` and `knowledge/figures/make_cd_figures.py check` are the two automatic checkers. This document does not replace any of them. It adds the map of automated against human checks, the procedures behind each rubric line, acceptance criteria by level, regression testing and release readiness.

### 0.3 Evidence

The ffmpeg commands in section 3.3 were run this session on a synthetic three-second clip to confirm that they work with this build. **No episode was checked for this document.** The worked example in section 17 is a report on a set of stills and says so.

---

## 1. Two kinds of checking

| | Automated validation | Human review |
|---|---|---|
| Answers | Is it technically what was specified? | Is it good? |
| Examples | Size, frame rate, frame count, model size and colour against a baseline, loudness | Appeal, acting, funniness, whether the character is "the same cat", whether a voice sounds right |
| Done by | A script | Eyes, ears, a first-time viewer |
| Repeatable | Exactly | No; that is why notes are written down |
| Can pass a bad film | **Yes** | No |
| Can fail a good film | Yes, on a technicality | Yes, on taste |

**Rule 1.** An automatic pass is reported as "automatic checks passed", never as "passed". `qc_frames.py` already prints its pass line with that qualification [M].

**Rule 2.** A check that needs eyes or ears is never ticked by me on the strength of a script. I can step through frames and look at stills; I cannot watch at full speed or hear (`references/07-qc-rubric.md`).

**Rule 3.** A human judgement is recorded with who made it, on what, and when.

### 1.1 Which check is which

| Area | Automated today [M] | Could be automated [R] | Human only |
|---|---|---|---|
| File and frames | Size, fps, audio present, audio and video length, frame count, numbering, duplicates | Checksums for regression | |
| Stillness and flicker | Per cent of still frames, long holds, big frame-to-frame jumps, near-black frames | | Whether a hold has life; whether a jump is a planned cut |
| Model drift | Size and colour share at the rest pose, six characters | Palette constants check; drift at more poses | Whether a posed drawing is on-model |
| Silhouette | | Overlap measure between figures (as in `Slapstick_Comedy.md` figure 5) | Whether a silhouette reads |
| Proportion and anatomy | | | Digit counts, joints, limb lengths in pose |
| Motion and timing | Frame counts against a plan | Keys lost on held frames (proposal P1); contact parity (P3) | Whether it feels right |
| Continuity | | Position and facing at cut frames | Everything else |
| Audio | Stream, length, loudness, peak, silence ranges | Cue frames against onsets | Everything about how it sounds |
| Comedy and story | | | All of it |
| Safety and originality | | | All of it |

---

## 2. The evidence ladder

Each rung proves more than the one below, and none proves the one above. A report states the highest rung actually reached (lessons learned 22 and 24).

| Rung | Evidence | Proves | Does not prove |
|---|---|---|---|
| 0 | A plan: beat sheet, shot list, cue sheet | Intent | Anything |
| 1 | Stills and key poses | A pose can be read | Motion |
| 2 | Per-frame tables and frame stepping | What is on each frame; arcs and spacing | How it feels at speed |
| 3 | Automatic checks on a rendered file | Technical correctness | Quality |
| 4 | Watched at full speed by a person | Timing | Sound; other viewers |
| 5 | Listened to by a person | Sound | |
| 6 | Shown to a first-time viewer | That it communicates and lands | That it will with every audience |

Everything in knowledge documents 1 to 7 is at rung 0 to 2. Harshith's viewing of the Stage 2 and Stage 3 Laddu tests reached rung 4 for those review clips, and his verdict was "development direction only".

---

## 3. Automated checks we have [M]

### 3.1 `tools/qc_frames.py`

| Command | Checks | Fails when |
|---|---|---|
| `check <frames_dir>` | Frames open; numbering; sizes; identical consecutive frames (holds) | A number is missing or duplicated; a frame cannot be opened; sizes are mixed |
| `video <file.mp4>` | Size 1080 × 1920; 24 fps; audio stream; audio and video lengths; decoded frame count | Wrong size or rate; no audio; lengths differ by more than 0.1 s; frame count mismatch |
| `assemble <frames_dir> out.mp4` | Builds a video from frames after `check` | The frame sequence is not clean |

`video` also **reports without failing**: the share of still frames, the longest hold, holds of 24 frames or more, frame-to-frame jumps above a threshold, and near-black frames. Its wording asks a person to look at each. These are prompts for eyes, not verdicts. Lessons learned records that a "still frames" percentage proved unreliable as evidence because it depends on framing.

### 3.2 The model drift check

```bash
python3 cartoon-animation-director/knowledge/figures/make_cd_figures.py check
```

Compares each of the six approved models, rendered at rest, with `knowledge/model_baseline.json`: size within 2% and colour share within 3 points. It prints PASS or FAIL per character. It last passed for all six on 2026-11-11, before this batch of documents.

What it covers: accidental changes to a model's size or colours. What it does not cover: any pose other than rest, expressions, line quality, digit counts, or anything not drawn by the engine. The `baseline` mode rewrites the baseline and is used **only after explicit approval** (lessons learned 14 and 20).

### 3.3 ffmpeg and ffprobe checks

All run this session on a synthetic clip with ffmpeg 6.1.1 and behaved as described.

```bash
# stream facts and a real frame count
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames -of csv=p=0 ep.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 ep.mp4

# black stretches, frozen stretches, silent stretches
ffmpeg -hide_banner -i ep.mp4 -vf blackdetect=d=0.2:pix_th=0.1 -an -f null -
ffmpeg -hide_banner -i ep.mp4 -vf freezedetect=n=0.001:d=0.5 -an -f null -
ffmpeg -hide_banner -i ep.mp4 -af silencedetect=n=-50dB:d=0.5 -vn -f null -

# loudness and peak
ffmpeg -hide_banner -i ep.mp4 -af ebur128=peak=true -vn -f null -

# regression: is this render the same picture as the reference render?
ffmpeg -hide_banner -i new.mp4 -i reference.mp4 -lavfi ssim -f null -
ffmpeg -v error -i ep.mp4 -map 0:v -f framemd5 -
```

A frozen or silent stretch is not a fault in a cartoon built on holds and pauses. These commands **list** stretches so that each can be matched to a planned hold or a planned silence. An unplanned one is the finding.

### 3.4 Read-only checkers (built and tested 2026-11-11, with Harshith's authorisation)

In `cartoon-animation-director/tools/`. Each reads project files and prints a report. None writes to production files, models, presets or the baseline. `tools/tests/test_checkers.py` runs 14 tests, including one that compares `git status` before and after; all pass.

| Script | Reports |
|---|---|
| `check_keys.py <episode.py> [--contacts f,f] [--all]` | Peak or trough keys that the hold on twos never draws (proposal P1); contacts that fall on a held drawing (P3). A finding is a place to look, not a proven defect |
| `check_safe_area.py episode <episode.py>` / `overlay <video> <out.png>` | Where characters stand against a chosen margin; an overlay picture from a rendered file |
| `check_docs.py` | Broken links, missing paths, section numbering in the Markdown documents |
| `check_protected.py [--drift]` | Protected files against `protected_manifest.json`; uncommitted changes to them; whether the review branch has been merged; optionally the drift check |
| `check_audio.py <files>` | Loudness, range, true peak, silences. Numbers only |

### 3.5 Tables printed by the figure scripts

`make_fb_figures.py` and `make_sc_figures.py` print what the engine shows on every frame of a move. Reading such a table is how the lost landing squash (document 3) and the late contact squash (document 4) were found. It is a manual read of automatic output.

---

## 4. Automated checks that are proposed, not built [R]

None of these exists. Each would be a new script outside the engine; anything touching engine code needs approval first.

| Proposal | What it would report | Notes |
|---|---|---|
| Keys on held frames | **Built: `check_keys.py`** (section 3.4) | `Engine_Change_Proposals.md` P1 |
| Contact parity | **Built: `check_keys.py --contacts`** | P3 |
| Regression checksums | Whether any existing episode's frames changed after a code change | Uses `framemd5` or `ssim`; needs reference renders kept |
| Palette constants | Any drawn colour not in the named palette | Follows rule R7 |
| Edge and safe-area report | Frames where a character's bounding box touches the frame edge or a chosen margin | Margin value is unsettled (`Storyboard_and_Cinematography.md` 2.4) |
| Cue against picture | A sound cue whose frame differs from the picture's contact frame | Needs contact frames listed by the author |
| Hook-up sheets | Outgoing and incoming frame pairs for every cut | `Stage.sheet` already exists; this only automates the list |

A proposed check is never cited as a result.

---

## 5. Character consistency and model drift

**What drift is.** A character's look changing without a decision: a little taller, a slightly different orange, an ear that moved, a fifth toe.

**Where it comes from.** Edits to character code for one purpose that change something else; new poses built outside the approved model; a review rig promoted without checking it against the approved drawing; generated footage (`AI_Video_Production.md`).

**Checks.**

| Check | Kind | How |
|---|---|---|
| Size and colour at rest | Automated | The drift check (3.2), before any commit that touches character code |
| Rest pose against the approved drawing | Measured | Outline overlap, as done for the Stage 3 review rig (98% at rest). A rig must reproduce the approved drawing at rest (lessons learned 28) |
| Limb lengths in pose | Measured | Same source: natural lengths kept; report the percentage |
| Digit counts | Human | Count against the decision register: Bheemu four toes, Gaju three nails, humans four fingers and a thumb, Laddu four visible toes, Bujji three (D1, provisional) |
| Accessories | Human | Glasses, scarf, cap, bindi, bangles present and correct in every shot |
| Markings and face | Human | Side by side with the model sheet |
| Expressions | Human | Only approved presets, or new ones added without changing existing ones (rule R3) |
| Mirroring | Human | Asymmetric details do not flip when the character turns |

**The governing rule.** A consistent model sheet does not make a character production-ready; it must also act convincingly in a life test (lessons learned 23). Consistency is necessary and not sufficient.

---

## 6. Silhouettes, proportion and anatomy

All human checks; scripts only prepare the pictures.

**Silhouette procedure.**
1. Pull the key poses of the shot.
2. Convert to solid black on white (`Slapstick_Comedy.md` figure 5 shows a script doing this).
3. Ask of each: can a person say who it is and what they are doing? Score 0, 1 or 2 as in the rubric.
4. A person scores it. My own score is labelled as mine.

**Proportion.** Compare head height to body height, and limb length to body, with the model sheet, at the extreme poses, since that is where stretching hides. Squash and stretch keep volume: taller means narrower.

**Anatomy.** Joints bend the right way; nothing is detached or stretched thin; hands hold things with fingers or the trunk closed round them; feet are planted when they should be (lessons learned 2; `cartoon-animation-director/SKILL.md` staging rules).

---

## 7. Motion readability and timing

| Method | Shows | Who |
|---|---|---|
| Contact sheet | Poses and staging; nothing about motion | Me or anyone |
| Stills at takes and hits | The extremes | Me or anyone |
| Frame stepping | Arcs, spacing, overlap, the exact contact frame | Me or anyone |
| Per-frame table | Numbers for each frame: height, squash, held or new | Script, read by me |
| Full-speed viewing | Timing, weight, whether it feels alive | **A person** |
| Viewing without sound, then with | Whether the picture alone reads | **A person** |

What to look for when stepping: every action has anticipation, action, overshoot and settle; arcs are curved; spacing is close for slow and wide for fast; loose parts arrive late; no key is lost on a held frame; contacts are on drawn frames; holds have one small living motion (`Frame_By_Frame_Animation.md`, `Slapstick_Comedy.md` sections 6 and 11).

Timing choices between two versions are compared in playback and never decided from stills (lessons learned 29).

---

## 8. Continuity

Checked across every cut with a hook-up sheet (`Storyboard_and_Cinematography.md` 7.3): position, direction, pose, props and their state, accessories, expression, time and light, sound. Across episodes: the house, the cast's relationships, and the Telugu wall lines stay as the series bible has them (`toon-slapstick/series/bheemu-gaju.md`).

---

## 9. Visual defects

| Defect | Looks like | Found by |
|---|---|---|
| Flicker or popping | A part appears, vanishes or jumps for one frame | Jump list from `qc_frames.py video`, then eyes |
| Morphing | A shape changes when it should move | Stepping |
| Detached part | Head off the neck; hand off the arm | Stepping the extremes |
| Clipping | One thing passing through another | Stepping |
| Floating | Feet not on the ground; no contact shadow | Stills |
| Draw-order error | A hand behind the thing it holds | Stills |
| Edge cut | A character sliced by the frame at a joint | Every fourth frame, as the pilot's criteria specify |
| Line weight jump | Lines thicken or thin between shots | Compare shots at different zoom |
| Text error | Telugu misspelt, mirrored or cut off | **A Telugu reader** |
| Banding or blockiness | Gradients in steps; compression squares | The encoded file, on a phone |
| Wrong colour | A palette colour off | Sampling plus eyes |
| Smear across a cut | A streak on the first frame of a shot | The engine suppresses smears at `Stage.cut` frames [M]; check any cut made another way |

---

## 10. Audio and synchronisation

| Check | Kind |
|---|---|
| Audio stream present; length within 0.1 s of the video | Automated (`qc_frames.py video`) |
| Loudness and true peak recorded | Automated (`ebur128`); the target is a decision, `Sound_Design.md` 13.3 |
| Silent ranges match planned silences | Automated list, compared with the cue sheet |
| Each hit cue is on the drawn contact frame | Comparison of cue sheet with per-frame table |
| Hits feel in sync | **Eyes and ears** |
| Levels: the hit, then dialogue, then the rest | **Ears** |
| Voices intelligible; Telugu correct | **Ears; a Telugu speaker** |
| Reads on a phone speaker | **Ears** |
| Every outside sound has a licence log entry | Document check |

The rubric's bar: sound events within one frame of the picture event. `Slapstick_Comedy.md` adds: never early.

---

## 11. Human review

### 11.1 Who

| Reviewer | Judges |
|---|---|
| Harshith | Everything subjective; final approval; all sound |
| A first-time viewer | Whether it communicates: the retell test |
| A Telugu reader and speaker | Text on walls; spoken lines |
| A person who knows cartoons well | Originality (`Slapstick_Comedy.md` section 14) |
| Me | Stills, stepped frames, tables, scripts. Labelled as mine |

### 11.2 Protocol [R]

1. **First viewing is clean.** Once, at full speed, with sound, on a phone, before reading any notes. First impressions cannot be recovered later.
2. **Second viewing without sound.** Does the story still read?
3. **Then step.** Only now look frame by frame at whatever felt wrong.
4. **Notes use the problem format** in `references/07-qc-rubric.md`: what, where (frame), likely cause, correction, corrected instruction, scope (local or global).
5. **Score the rubric.** Tick in the report only the inspection methods actually used.

### 11.3 Tests with other people

- **Retell test.** A first-time viewer watches once and says what happened in one or two sentences. Pass: the sentence matches the one written at the start (`Slapstick_Comedy.md` section 2).
- **Blind expression test.** Show an expression with no label and ask what the character feels. Harshith's label-free reading of the Stage 1 expressions is on record as a visual review, not as this test (decision D18).
- **Reaction point.** Note where the viewer smiles or laughs. It should be at the reaction beat.

Do not explain the gag first, do not ask leading questions, and record the answer as given.

---

## 12. Acceptance criteria

### 12.1 Severity [R]

| Class | Meaning | Examples | Consequence |
|---|---|---|---|
| Blocker | Must not be shown | Off-model character; wrong digit count; safety rule broken; borrowed gag or sound; wrong size or frame rate; no audio; Telugu error | Fix before any review |
| Major | A casual viewer notices | Detached part; lost contact drawing; hit out of sync; unreadable silhouette; dead hold | Fix before sending as a candidate |
| Minor | A careful viewer notices | A slightly even spacing; a hold one beat long | Log; fix if cheap |

### 12.2 By level

| Level | Passes when |
|---|---|
| **A plan** (beat sheet, board, cue sheet) | Complete; passes the safety and originality checks; nothing in it claims a result |
| **A character sheet or reference** | Marked REVIEW ONLY or PROPOSAL; inconsistencies with the approved model listed; Harshith has reviewed it. Approval of a sheet is not approval to change the model |
| **A character for production** | Approved sheets **and** a passed life test by Harshith's viewing; drift check passes; decision recorded in the register |
| **An animatic** | Automatic checks pass; watched and listened to; retold by a first-time viewer; lengths frozen |
| **A shot, to be sent** | No rubric line at 0 and a total of at least 20 of 26 [M, `references/07-qc-rubric.md`]; no blocker; report lists what was and was not inspected |
| **A lesson, mastered** | At least 23 of 26 and Harshith accepts it [M] |
| **An episode** | Every shot at the bar; continuity checked across all cuts; audio checks done and listened to; release checklist (section 14) complete |
| **A knowledge document** | Links and paths resolve; numbers match their source; states its own evidence level; reviewed by Harshith |
| **An engine or model change** | Approved before coding; drift check and regression (section 13) pass; approved again before merge |

A score I give on a human-only rubric line is a provisional score. The bar is met only when a person has scored those lines.

---

## 13. Regression testing

**Purpose.** To show that a change did only what it was meant to do.

**What must not change without a decision.**

- The six approved models: guarded by the drift check and `model_baseline.json`.
- Existing presets in `show.py`.
- The rendered frames of existing episodes, above all episode 1 (lessons learned 10).
- Approved figures in the knowledge base: each has a script that regenerates it.

**Procedure for any future code change [R; not yet run, since no engine change has been approved].**

1. Before the change: render the reference set and store either the files or their `framemd5` lists. The set is all ten episodes for an engine change, or the affected ones for a narrower change.
2. Make the change on a branch.
3. Run the drift check.
4. Render the same set and compare: `framemd5` for "identical", `ssim` to measure any difference.
5. Every difference is either intended and listed, or a regression.
6. Run the figure scripts and confirm that the tables in the documents still match.
7. Report: what changed, what did not, what was not tested.

**What exists today.** Step 3 and step 6. The final encodes of all ten episodes are in the repository under each episode's `out/` folder [M, verified 2026-11-11 with `git ls-files`], so reference renders exist. `check_protected.py` adds a hash check of the protected files.

**A caution on "identical".** Renders may differ between machines or library versions without any code change **[U]**. Establish that two renders of the same code on the same machine are identical before treating a difference as a regression.

---

## 14. Release readiness

An episode is ready to upload when every line is true. Lines marked (H) are Harshith's.

**Technical (automated)**
- [ ] 1080 × 1920, 24 fps, H.264, AAC audio, `+faststart` (the delivery settings in `references/06-pipeline-and-tools.md` and `show.py`); pixel format read with ffprobe and recorded
- [ ] `qc_frames.py video` passes
- [ ] No unplanned black, frozen or silent stretch
- [ ] Loudness and peak measured and recorded
- [ ] File named by the project convention (`bheemu_gaju_epNN_slug.mp4`, as `show.py` writes it)

**Picture (eyes)**
- [ ] Every shot at the rubric bar; no blocker or major defect open
- [ ] Characters on-model in every shot; digits and accessories checked
- [ ] Continuity checked on every cut
- [ ] Telugu text read by a Telugu reader
- [ ] Watched on a phone in the real player; nothing important under the interface (H)

**Sound (ears)**
- [ ] Listened to on a phone speaker and earphones (H)
- [ ] Licence log complete

**Content (people)**
- [ ] Passes the safety rules and the imitation test (`Slapstick_Comedy.md` section 13)
- [ ] Passes the originality check; looked at by someone who knows cartoons
- [ ] Retell test passed
- [ ] Ends with the cast reconciled

**Records**
- [ ] QC report saved in the episode's `qc/` folder
- [ ] Episode file, render and report committed and pushed (lessons learned 1)
- [ ] Platform settings chosen: audience setting, any disclosure the platform requires (`AI_Video_Production.md` section 15) (H)
- [ ] Explicit approval to upload (H)

---

## 15. Reporting honestly

- Tick only the inspection methods that were used. The report form has the list.
- Write "not inspected" with the reason for anything skipped.
- State the highest rung of the evidence ladder reached.
- Separate proposed key poses, timing plans and tested animation (lessons learned 24).
- A number is reported with how it was obtained.
- An automatic pass is called an automatic pass.
- "Looks good to me" from me is a statement about stills.

---

## 16. When something fails

1. Write the problem in the six-part format.
2. Classify the severity (12.1) and the scope: **local** (this shot) or **global** (the character, the engine, every episode).
3. A local fix is made, and the shot is checked again from the top: the fix can break something else.
4. A global cause is **not** fixed on the spot if it touches character code, a preset, the baseline or the engine. It is reported, with what the existing controls can do instead (lessons learned 25), and where relevant written up in `Engine_Change_Proposals.md`.
5. A correction from Harshith becomes a rule in `references/09-lessons-learned.md`, with the date, and he is told it was added.
6. Change only what was asked (lessons learned 3). Re-check that nothing else moved: that is regression at small scale.

---

## 17. Worked example: an honest report on something that is not finished

The subject is worked example 1 of `Slapstick_Comedy.md` ("The ball that went up") as it stands: 240 frames posed in the engine, five figures, no render, no sound.

**How it was inspected**

- [ ] Automatic checks (`qc_frames.py`): **not run; there is no rendered file**
- [x] Contact sheet: 12 key frames (figure 1)
- [x] Stills at hits: frames 133 to 148, every frame (figure 2)
- [x] Per-frame table: fall and impact
- [ ] Frame stepping through all moves: **only the impact**
- [ ] Full-speed viewing: **nobody**
- [ ] Listening: **no sound exists**

**Scores (mine, from stills; provisional)**

| # | Check | Score | Note |
|---|---|---|---|
| 1 | Character identity | 2 | Approved models and presets only; drift check passes |
| 2 | Anatomy | 2 | Nothing detached in the 28 frames looked at |
| 3 | Silhouettes | 1 | Clear layout reads to me; a person has not scored it |
| 4 | Arcs | not inspected | The ball's path was plotted; character arcs were not stepped |
| 5 | Timing and spacing | not inspected | A plan; never played |
| 6 | Weight and contact | 1 | Contact drawing shown on the right frame; the trunk never touches the ball |
| 7 | Transitions | not inspected | |
| 8 | Anticipation and follow-through | 1 | Present as keys; ears and scarf not offset |
| 9 | Background and camera | not applicable | Plain background, one locked shot |
| 10 | Flicker | not inspected | No render |
| 11 | Audio sync | not inspected | No audio |
| 12 | Frame integrity | not inspected | No render |
| 13 | Story and comedy | not inspected | No viewer |

**Verdict.** Not a candidate for sending. It is at rung 2 of the evidence ladder. The next step that would produce evidence is a rendered preview with sound, watched and listened to by Harshith.

This is what a report looks like when most of the work has not been checked. It is more useful than a full table of 2s.

---

## 18. Common mistakes

| Mistake | How to detect | Fix |
|---|---|---|
| "Passed" on automatic checks alone | The report has no named viewer | Say "automatic checks passed" |
| Ticking a human-only line myself | No person named against it | Leave it "not inspected", or mark the score provisional |
| Stills offered as proof of motion | The evidence is a contact sheet | State the rung |
| Skipping the clean first viewing | Notes exist before a full-speed viewing | Watch first |
| Treating a hold as a defect | `freezedetect` output pasted as a fault list | Match each stretch to the plan |
| Fixing a global cause locally and silently | Character or engine code changed inside a shot fix | Stop; report; propose |
| No regression after a change | Only the changed shot was re-rendered | Compare the reference set |
| Rewriting the baseline to make a check pass | `baseline` mode run without approval | Never; revert |
| Checking only the shot that was asked about | A neighbour's continuity broke | Check the cuts on both sides |
| Scoring from memory | No frame numbers in the notes | Cite frames |
| One reviewer for everything | Telugu text checked by a non-reader | Use the right reviewer |

---

## 19. Checklists

**Before any commit that touches character code**
- [ ] Explicit approval exists for this change
- [ ] Drift check run; result pasted in the commit message or report
- [ ] Baseline not rewritten
- [ ] Reference renders compared (section 13)

**Before showing a shot**
- [ ] `qc_frames.py video` run on the file
- [ ] Contact sheet and stills at hits looked at
- [ ] Moves stepped; per-frame table read at each contact
- [ ] Hook-up frames checked for each cut
- [ ] QC report filled in; uninspected lines say so
- [ ] Evidence rung stated

**Before calling anything approved**
- [ ] A named person approved it, in words, for this specific thing
- [ ] The decision is in the register (`Character_Design_Bible.md` section 13) or in lessons learned
- [ ] Approval of a sheet has not been read as approval of a model change

---

## 20. Limitations and open questions

**Limitations.**

- The drift check covers the rest pose only.
- No automatic check exists for digits, silhouettes, continuity, lost keys or sync.
- I cannot watch at speed or hear, so rubric lines 5, 11 and 13 can never be completed by me.
- No reference renders are known to be stored for regression.

**Open questions for Harshith.**

1. May I build the read-only checkers in section 4 as separate scripts in `tools/`? They change no engine or character code. The key-on-held-frame checker is the most useful.
2. Should reference renders of the ten episodes be stored for regression, and where?
3. Is the severity scale in 12.1 right, and is "Telugu error" correctly a blocker?
4. Who are the first-time viewer and the Telugu reader for the tests in 11.3?
5. Should the pilot's acceptance criteria (`references/08-pilot-project.md`) be the template for every episode?

---

## 21. References

- `references/07-qc-rubric.md`, `templates/qc_report.md`, `tools/qc_frames.py`
- `knowledge/figures/make_cd_figures.py`, `knowledge/model_baseline.json`
- `references/08-pilot-project.md` (acceptance criteria), `references/09-lessons-learned.md`
- `Character_Design_Bible.md` (decision register, digit counts), `Frame_By_Frame_Animation.md`, `Slapstick_Comedy.md`, `Storyboard_and_Cinematography.md`, `AI_Video_Production.md`, `Sound_Design.md`, `Production_Pipeline.md`, `Engine_Change_Proposals.md`
- ffmpeg filters used: `blackdetect`, `freezedetect`, `silencedetect`, `ebur128`, `ssim`, and the `framemd5` muxer; confirmed present in the local build with `ffmpeg -filters` and by running each command

No outside source was opened for this document.

---

## 22. Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.1. Section 3.4 added for the five read-only checkers; section 4 and 13 updated with verified facts (checkers built; episode renders are in the repository). |
| 2026-11-11 | Version 1.0. Existing tools read and described. Eight ffmpeg and ffprobe commands run on a synthetic clip. No episode checked. One worked report on unfinished work. Not reviewed by Harshith. |
