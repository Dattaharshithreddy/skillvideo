# AI Video Production

**Knowledge base document 6 of the master mission (Phase 1).**
Version 1.0, 2026-11-11. Follows documents 1 to 5 in this folder.

This document explains how AI-assisted tools can and cannot be used to make original cartoon video: what kinds of tool exist, how they differ from our own animation engine, how to keep a character the same across generated shots, how to choose a tool, what goes wrong, and how to check the result.

## 0. How to read this document

### 0.1 The position this project starts from

When the series began, Harshith said he did **not** want fal or other AI video generators to make the videos; the cartoons are to be drawn and animated by our own engine. That position stands unless he changes it. **Nothing in this document adopts a generative workflow for the series.** It is reference knowledge, so that the choice stays an informed one and so that any future test is run properly.

### 0.2 Labels

| Label | Meaning | Status |
|---|---|---|
| **[M]** | Read from our repository or run this session | Established project fact |
| **[T-earlier]** | Recorded in `references/06-pipeline-and-tools.md` as checked or tested on 2026-11-11, before this document | Not re-checked now |
| **[V]** | Read this session as an excerpt returned by a search | Verified at excerpt level, on that date |
| **[R]** | My recommendation or a proposed workflow | Proposed, untested |
| **[U]** | Unverified assumption | Check before relying on it |

### 0.3 The most important warning

**I have not run any generative video model for this project, on our characters or on anything else.** Every statement about what a model does comes from its vendor's or a third party's description, read as an excerpt. Tool features, limits, prices and terms change within months. Before any paid call, read the tool's current documentation for the exact parameter names and limits. The repository's own `references/models.md` already makes this a rule for the fal endpoints it lists.

---

## 1. Three different things that get called "AI video"

| | Our animation engine | Generative image and video models | AI-assisted helpers |
|---|---|---|---|
| Example | `toon-slapstick/engine/` | Text-to-video, image-to-video, first-and-last-frame models | Text-to-speech, in-betweening between two given drawings, upscaling, background painting |
| How a frame is made | Code draws the character from pose numbers | A model samples pixels from a prompt and reference images | A model fills in or converts material we supply |
| Same input twice | **Same output, exactly** [M] | A different result each run unless a seed is fixed, and often even then [U per tool] | Varies |
| Control of timing | To the frame [M] | By prompt and by supplied frames only; not frame-exact | Depends |
| Character consistency | By construction: one model, one palette; a drift check exists [M] | The central problem; managed with reference images, never guaranteed | n/a |
| Text in the picture | Exact (Telugu fonts in `fonts/`) [M] | Often garbled [T-earlier, for ToonCrafter] | n/a |
| What it cannot do | Hand-drawn redrawing, new angles, anything the model has no control for | Repeat itself; obey a frame count; stay on-model reliably | Replace judgement |
| Cost | CPU time; about 3 minutes per 30 s at 1080p [T-earlier] | Per second generated, or a large GPU | Small |

Our engine is not a generated-video tool. When someone asks whether "the AI can make the cartoon", the answer depends entirely on which column they mean. In this project, Claude writes the code that drives the engine in the first column. That is AI-assisted production in a real sense, and it is the only one in use for the series.

---

## 2. What the repository actually contains [M]

| Folder | What it is | Uses generative video? |
|---|---|---|
| `toon-slapstick/` | The 2D engine and the ten Bheemu and Gaju episodes | No |
| `cartoon-animation-director/` | Method, knowledge base, QC tools, review branch | No |
| Repository root (`SKILL.md`, `scripts/run.py`, `references/`) | The earlier **cgi-shorts** skill: 3D explainer shorts. Stages `tts`, `refs`, `images`, `animate`, `assemble` | Yes by default, through fal.ai endpoints listed in `references/models.md`; or Blender rendering with `"engine": "blender"` |
| `blender/` | Headless Blender rendering for cgi-shorts | No |
| `series/momo-gullu/` | An earlier 3D version of the two leads | No |
| `toon-slapstick/tools/tts_telugu.py`, `engine/voice.py` | Telugu speech for the two human characters, made with the AI4Bharat Indic-TTS model | AI speech, not video |

Two things follow. First, the repository's top-level README describes cgi-shorts, not the cartoon series; a newcomer could read it and assume the cartoons are generated (section 17 lists this as an inconsistency). Second, the model names and prices in `references/models.md` were written for cgi-shorts and say "checked Nov 2026"; I did not re-check them and they are **[U]** here.

AI in-betweening has not been run for this project. `references/06-pipeline-and-tools.md` records that the open models cannot run in Claude's workspace (no GPU, model host blocked) and would need Harshith's GPU server or an online demo [T-earlier].

---

## 3. Where AI assistance could fit, stage by stage

| Stage | Today (established) | Possible AI assistance (proposed, untested) | Main risk |
|---|---|---|---|
| Idea, script, beat sheet | Claude writes | Same | Borrowed gags; run the originality check in `Slapstick_Comedy.md` section 14 |
| Storyboard | Engine stills | Generated thumbnails for poses the models lack | Off-model drawings mistaken for approved designs |
| Backgrounds | Painted in code (`sets.py`, `scene.py`) | Generated painted references, repainted in code or used as plates | Style mismatch with inked characters; Telugu text garbled |
| Character design | Approved models in code | **None.** A generator must never redesign an approved character | Rules 3, 13, 20 of lessons learned |
| Key poses | Engine | Engine | |
| In-betweens | Engine easing | A first-and-last-frame model between two engine keys, for one hero action | Drift between the keys; wrong digit counts; cannot hold on twos |
| Full shots | Engine | Image-to-video from an engine still | Loss of timing control; drift; accessories lost |
| Voices | AI4Bharat TTS for Ammamma and Chintu [T-earlier] | Other TTS, or Harshith's own dubbing tool, which he has named as an option | Quality not yet confirmed by ear |
| Music and effects | Synthesised in `sound.py` | Generated audio | Licence terms; similarity to existing music |
| Edit, encode | ffmpeg | Same | |
| QC | Scripts plus eyes and ears | Same | A model's own "quality" claim is not a check |

---

## 4. Tool selection criteria

Score any candidate on these before spending money. A tool that fails a "must" is out, whatever its demos look like.

| # | Criterion | Why it matters for us | Must or want |
|---|---|---|---|
| 1 | Accepts reference images of a character | Without it there is no consistency at all | Must |
| 2 | Accepts a first frame, and ideally a last frame | Lets our engine supply the poses | Must for workflows B and C |
| 3 | Outputs 9:16 at 1080 × 1920, or cleanly scalable to it | Our delivery format [M] | Must |
| 4 | Holds a flat, inked 2D style without drifting to 3D or painterly | The look of the series | Must; only a test shows it |
| 5 | Clip length and whether it can be extended | Our shots are 1 to 4 seconds; most tools make fixed lengths | Want |
| 6 | Frame rate, and whether it conforms to 24 | Mixing with engine footage | Want |
| 7 | Written commercial-use terms | The channel is meant to earn | Must; read the terms, do not infer |
| 8 | Price per second, including failed takes | Budget is takes × price | Want |
| 9 | API access with documented parameters | Repeatable, scriptable, loggable | Want |
| 10 | Seed or other repeatability control | Regenerating one shot without changing its neighbours | Want |
| 11 | Content rules compatible with family animation | Avoid refusals mid-production | Must |
| 12 | Audio can be switched off | Our sound is made separately | Want |
| 13 | Runs locally on the GPU we have | No per-clip cost, full control | Want; check the memory needed |
| 14 | Stable version naming | So that a shot can be regenerated later | Want |

**Decision rule [R].** Run the same three test shots through every candidate (section 16, exercise 1) and compare with a person's eyes against the model sheets. Do not choose from published samples.

---

## 5. The tool landscape as read on 2026-11-11

**None of these has been tested by us.** Each line gives what a source said and where it came from.

### 5.1 Hosted models

| Tool | What sources say | Source type |
|---|---|---|
| **Google Veo 3.1** | Announced with three controls: reference images to guide generation (up to 3, for a character, object or scene), extension of an existing clip, and a transition generated between a first and a last frame [V]. A third-party help page says a first frame and reference images cannot be combined in one request [V]. A third-party model page lists durations of 4, 6 or 8 seconds and 9:16 output [V] | Google developer blog; third-party docs |
| **Kling 3.0** | A hosting provider's page lists text-to-video, image-to-video, start-and-end-frame, "element" referencing to lock a character from reference images, multi-shot storyboarding, native audio and output up to 15 seconds [V]. A third-party guide notes that reference images anchor a character but do not lock every detail [V] | Hosting provider page; third-party guides |
| **Seedance 2.0** | A hosting provider's comparison says its reference-to-video accepts up to 9 images, 3 videos and 3 audio clips [V] | Hosting provider page |

Prices seen on one provider's comparison page that day: about $0.168 per second for Kling 3.0 Pro with audio, and about $0.30 per second for Seedance 2.0 at 720p [V]. Treat prices as a snapshot.

### 5.2 Open models [T-earlier]

From `references/06-pipeline-and-tools.md`, checked earlier on 2026-11-11:

| Tool | Input | Output | Limits recorded |
|---|---|---|---|
| ToonCrafter | Two cartoon stills and a prompt | The motion between them | 512 × 320, up to 16 frames; cannot draw text |
| Wan 2.2 first-last-frame | Two stills | 720p clip; Apache 2.0 | General model; needs a strong GPU |
| AniSora | One still | Anime-style clip; Apache 2.0 | 14B model; large GPU |
| ToonComposer | Keyframe sketches and one colour frame | Finished cartoon clip | About 57 GB of GPU memory for 61 frames at 480p |

Harshith's server is a g4dn.xlarge-class machine. I have not checked whether any of these fits its GPU memory; assume not until measured **[U]**.

### 5.3 What one documented production reported

A provider's FAQ describes a three-minute animated episode made with one of these models: about five generations to lock each character, 164 clips generated in all, an average of three generations per usable shot, and 17 final shots stitched from two or more generations [V]. One anecdote, from a vendor, about a different style. Its use here is the shape of the work: generation is cheap per take and expensive per **accepted** shot.

---

## 6. Prompt design

For the 3D explainer look, the repository already has a tested-in-use guide: `references/prompting.md` (subject and frozen action, framing, backdrop; one idea per shot; a separate motion prompt; avoid text and multiple actions). The points below adapt that to a 2D cartoon and are **[R]**.

### 6.1 Structure of an image prompt

1. **Style block,** identical in every prompt: "flat 2D cartoon, clean dark-brown ink outline of even weight, flat colour fills, soft painted background, no gradients on characters, vertical 9:16".
2. **Character lock block,** identical in every prompt for that character, written from the approved model and nothing else (6.3).
3. **Pose and action, frozen at one instant.**
4. **Framing,** in the vocabulary of `Storyboard_and_Cinematography.md` section 3.
5. **Setting,** from the series bible.
6. **Exclusions:** "no text, no extra characters, no 3D shading".

### 6.2 Structure of a motion prompt

- One action per clip. A clip is one beat of `Slapstick_Comedy.md` section 2.
- Say what the camera does, usually "locked camera".
- Say what must not change: "glasses stay on, scarf stays orange, cap stays on".
- Describe speed in words ("snaps", "holds still, then"). Frame counts in a prompt are not obeyed [U; assume not].

### 6.3 The character lock block

Written once per character from `Character_Design_Bible.md` and `toon-slapstick/series/bheemu-gaju.md`, then pasted byte-for-byte. A third-party guide makes the same point for one tool: paraphrasing the block between generations lets drift back in [V]. Example for a test, original to our cast:

> "Bheemu, a big calm panda standing upright, round body, white belly, black arms and legs, black ears and eye patches, round thin gold-rimmed glasses, short orange scarf, four toes on each paw, friendly closed-mouth smile."

Digit counts come from the decision register (D1) and are part of the block because extra or missing digits are a known failure.

### 6.4 What a prompt must never contain

- The name of any existing cartoon, character, studio or artist, or "in the style of" any of them (lessons learned 18 and 32).
- Real people.
- A request to "improve" or "redesign" an approved character.

### 6.5 Prompts are not specifications

A prompt asks; a model answers with something. The specification is the approved model sheet. Every generated frame is judged against the sheet, not against the prompt.

---

## 7. Reference-image consistency

**Principle [R]: the approved engine models are the only source of reference images.** Not a generated "character sheet", not a model's own redraw. The engine can render any approved character at any existing pose and size with `Stage.still`, on a plain background, exactly on-model [M].

A reference package for one character, made from the engine:

| Image | Purpose |
|---|---|
| Front, neutral, full body, plain background | Identity |
| Three-quarter head (`yaw`), full body | The only other view the models have |
| The shot's start pose, in the shot's framing | First frame for image-to-video |
| The shot's end pose | Last frame, where the tool accepts one |
| Each approved expression preset needed in the shot | Face reference |
| A flat palette strip with the named colours | Colour reference for the human checker |

Limits to state plainly:

- Our models have no true profile or back view (`Character_Design_Bible.md` section 12). A generator asked for a side view will invent one. An invented view of an approved character is a design change and needs the review path, not a prompt.
- Review-branch drawings (profile heads, the acting rig) are **REVIEW ONLY** and must not be used as references for anything meant for production.
- Reference images anchor; they do not lock [V]. Expect to reject takes.

---

## 8. Workflows

| ID | Workflow | Status |
|---|---|---|
| **A** | Engine only: keys, easing, sound, encode | **Established.** All ten episodes [M] |
| **B** | Engine keys, AI in-betweens for one hero action | Proposed, untested |
| **C** | Engine still as first frame, image-to-video for the shot | Proposed, untested |
| **D** | Reference sheets in, whole shots generated from prompts | Not in line with the starting position (0.1); documented for completeness |
| **E** | AI for background references only | Proposed, untested |
| **F** | AI speech for human characters | Established for two characters; quality unconfirmed by ear [T-earlier] |

### 8.1 Workflow B, step by step (a test design, not a method in use)

1. Pick **one** action that the engine does badly and that matters: for example the cat's lap in the pilot.
2. Make the two key poses in the engine with approved models; render each as a still at the shot's framing.
3. Check both stills against the model sheet. They are on-model by construction; confirm the framing matches between them.
4. Send the pair to a first-and-last-frame model with a one-action motion prompt and the lock block.
5. Generate a fixed, small number of takes (say five). Log each (section 9).
6. Reject on sight any take with a wrong digit count, missing accessory, colour shift, changed proportions or a style change.
7. Conform the survivor to 24 fps and 1080 × 1920. Compare its first and last frames with the engine stills.
8. Cut it into the engine-rendered shot. Check the joins as hook-up frames (`Storyboard_and_Cinematography.md` 7.3).
9. Add any Telugu text and all sound from the engine, never from the model.
10. Run the QC of section 14 and send it for viewing, labelled as a test.

**Gate.** A generated in-between replaces an engine one only if Harshith, having seen both side by side at full speed, prefers it and finds the character unchanged.

### 8.2 Workflow C

As B, with only a first frame. Less control over where the action ends, so the join into the next engine shot is the weak point. Use it only for a shot that ends on a cut.

### 8.3 Workflow E

Generate a painted background reference, then either repaint it in `sets.py` style or use it as a plate. All wall text is added by the engine afterwards. A new background is a new asset and takes the asset path in `Production_Pipeline.md`.

---

## 9. Generating shots: the take loop

| Step | Do | Record |
|---|---|---|
| 1 | Fix the inputs: references, prompt, model name and version, settings | All of them, verbatim |
| 2 | Decide the number of takes and the budget before starting | The cap |
| 3 | Generate | File name per take; seed if the tool exposes one |
| 4 | First pass: reject on hard failures (7 in section 12) | Reason per rejected take |
| 5 | Second pass: compare survivors with the model sheet at three frames: first, middle, last | Notes |
| 6 | Choose, or stop | The choice and why |
| 7 | If nothing survives, go to failure recovery (section 13), not to more takes of the same thing | |

Keep every prompt and setting in the episode folder (`research/` or a `gen/` subfolder; `tools/new_episode.py` creates the standard folders [M]). A shot that cannot be regenerated is a shot that cannot be revised.

---

## 10. Continuity across generated shots

- **Carry the frame.** Use the last frame of one clip as the first frame of the next where the action continues. One guide recommends this for one tool [V].
- **One background plate per location,** generated or painted once and reused. Never let each shot invent the room.
- **Home positions and screen direction** as in `Storyboard_and_Cinematography.md` section 7. A generator has no memory of where anyone stood.
- **Props keep their state.** If the bowl is half empty in shot 3, the first frame of shot 4 says so, because it came from the engine.
- **Colour.** Sample the character's main colours in the first and last frame of each clip and compare with the named palette constants (rule R7).
- **Frame rate and size.** Conform every clip to 24 fps and 1080 × 1920 before judging it.
- **The look on twos.** Engine characters hold drawings for two frames by default [M]. Generated motion is on ones. A cut between the two will show a change in texture of movement. I do not know how visible that is **[U]**; it needs watching.

---

## 11. Editing generated material

- Trim to the usable part. Most clips are longer than our shots.
- Never use generated audio. Sound is built in `sound.py` and locked to frames (`Sound_Design.md`).
- Composite all text in the engine after generation.
- Do not upscale or sharpen a clip to hide softness next to engine footage; match the engine footage to the clip, or drop the clip.
- Keep the generated clip, the engine stills it came from, and the log together and versioned (`Production_Pipeline.md` section 6).

---

## 12. Limitations and failure modes

| # | Failure | What it looks like | Why it matters here |
|---|---|---|---|
| 1 | Identity drift | Face shape, proportions or markings change over the clip | The cast must be unmistakably the same |
| 2 | Wrong digits | Five toes, three fingers, a second trunk tip | Digit counts are approved decisions (D1) |
| 3 | Accessory loss | Glasses vanish or fuse; scarf changes colour; cap gone | Accessories are part of the model |
| 4 | Style drift | 3D shading, painterly texture, line weight changes | Breaks the look against engine shots |
| 5 | Morphing | Shapes melt between poses instead of moving | Reads as a glitch, not animation |
| 6 | No timing control | The hit lands when the model likes | Slapstick is timed to the frame (`Slapstick_Comedy.md` section 6) |
| 7 | Cannot hold | A "still" character keeps wobbling | Pauses are the comedy |
| 8 | Text garbled | Telugu on walls becomes nonsense | Standing rule: text is scenery and must be correct |
| 9 | Invented views | A profile or back view that was never approved | A design change by accident |
| 10 | Physics errors | Objects pass through each other | Cause and effect must be readable |
| 11 | Unrepeatable | The same request gives a different shot | Revisions change more than was asked (rule 3) |
| 12 | Content refusal | A harmless bonk is refused as violence | Unpredictable production stops |
| 13 | Version churn | The model is replaced or withdrawn | Old shots cannot be matched |
| 14 | Cost creep | Many takes per accepted shot | See 5.3 |

Failures 1 to 5 can be caught by eye against a sheet. Failures 6 and 7 are structural: they are why workflow A exists and why the engine supplies the keys in B and C.

---

## 13. Failure recovery

Work down this list and stop at the first step that gives an acceptable shot.

1. **Same inputs, more takes,** up to the cap. Variation alone sometimes fixes it.
2. **Shorten the action.** Half the movement per clip.
3. **Add the last frame,** if only a first frame was given.
4. **Tighten the framing** so that the failing part (hands, feet) is out of the picture. This is a staging change; note it.
5. **Split the shot** into two clips with an engine pose between them.
6. **Change the tool,** with the same references and prompt.
7. **Fall back to the engine.** Always available; always on-model. State the limitation that sent you looking in the first place.

Never "fix" a failed take by accepting a slightly different character. Never retouch a generated frame into an approved design by hand without saying so.

---

## 14. Quality checks for generated footage

| Check | How | Automated? |
|---|---|---|
| File: size, frame rate, length, audio stream | `tools/qc_frames.py video` [M] | Yes |
| Frozen or black stretches | Same tool; ffmpeg `freezedetect`, `blackdetect` (`Quality_Control.md`) [M] | Yes |
| Identity against the model sheet | Side-by-side stills at first, middle and last frame | **No. Eyes** |
| Digit counts | Count on those three frames and any frame where hands or feet move | **No. Eyes** |
| Accessories and palette | Look; sample colours and compare with the constants | Sampling can be scripted [R]; judging cannot |
| Style match with engine shots | Watch the cut in both directions | **No. Eyes** |
| Hook-up frames | `Stage.sheet` for the engine side; extracted frames for the clip | Printing yes, judging no |
| Timing against the beat sheet | Count frames to the contact | Yes, once a person marks the contact frame |
| Sound | Built separately; ears | **No. Ears** |

**The existing drift check does not apply.** `knowledge/figures/make_cd_figures.py check` measures the engine's own models against `model_baseline.json` [M]. It cannot read a generated video. For generated footage, character consistency is a human check until something better is built and approved.

**Acceptance for a test [R].** No hard failure (1 to 5, 8, 9 of section 12) in any frame stepped through; the shot scores no zero on the 13-line rubric in `references/07-qc-rubric.md`; and Harshith has watched it.

---

## 15. Rights, disclosure and safety

I am not a lawyer; this is what to check, not advice.

- **Licence of the output.** Read each tool's current terms for commercial use. A hosting provider's marketing line that outputs may be used commercially [V] is not the same as reading the terms.
- **Disclosure on YouTube.** Creators must disclose realistic content that is meaningfully altered or synthetically generated; the help page lists clearly unrealistic content, such as animation, among things that do not need it [V]. A news report notes that this leaves AI-generated children's cartoons outside the labelling rule [V]. Policies change: check the upload form on the day.
- **Originality.** A generator can reproduce protected characters or styles without being asked. The check in `Slapstick_Comedy.md` section 14 applies to generated pictures as well as written gags, and a person who knows cartoons should look.
- **Family audience.** The rules of `Slapstick_Comedy.md` section 13 apply whatever made the picture.
- **Honesty in reports.** A generated shot is described as generated, with the tool and date. It is never described as animated by the engine, and the reverse.

---

## 16. Exercises

None has been done. All need Harshith's approval before any paid call or GPU time.

| # | Exercise | Answers |
|---|---|---|
| 1 | **Three-shot bake-off.** The same three engine stills (Bheemu neutral; Gaju mid-hop; Laddu sitting) through each candidate tool with a locked camera and a tiny motion. Five takes each | Which tool, if any, holds our style and models |
| 2 | **In-between test (workflow B)** on one action from the pilot | Whether generated in-betweens beat engine easing for a hero move |
| 3 | **Hold test.** Ask for two seconds of a character standing still | Whether a tool can hold at all |
| 4 | **Digit audit.** Count digits on every frame of five accepted takes | The real failure rate for our cast |
| 5 | **Cut test.** Engine shot, generated shot, engine shot; watch the joins | Whether ones against twos shows |
| 6 | **Prompt discipline.** Regenerate one shot with the lock block paraphrased | How sensitive consistency is to wording |
| 7 | **Cost log.** For exercise 1, record takes, accepted shots and spend | The real price per accepted second |

---

## 17. Common mistakes

| Mistake | How to detect | Fix |
|---|---|---|
| Calling the engine "AI-generated", or a generated clip "our animation" | Read the report | Name the method for each shot |
| Choosing a tool from its demo reel | No test on our characters exists | Run the bake-off |
| Letting a generator make the character sheet | The reference images did not come from the engine | Rebuild references from approved models |
| Paraphrasing the lock block | Prompts differ between shots | Paste it; diff the prompts |
| Several actions in one clip | The motion prompt has "then" in it twice | One beat per clip |
| Accepting "close enough" | Side-by-side with the sheet shows a difference | Reject; the sheet is the specification |
| Using generated audio | The clip arrived with sound | Strip it; build sound in the engine |
| Generated text in the picture | Signs are unreadable | Composite text in the engine |
| No log | A shot cannot be regenerated | Log inputs before generating |
| Quoting last year's features or prices | The statement has no date | Re-read the documentation; date every claim |
| Using review-branch art as a reference | The reference has a REVIEW ONLY banner | Use approved assets only |

---

## 18. Checklist for any generated shot

- [ ] Harshith has approved the test and its budget
- [ ] Tool documentation read today; parameter names and limits confirmed
- [ ] Licence terms read; commercial use confirmed in writing by the terms
- [ ] References rendered from approved engine models only
- [ ] Style block and lock block pasted unchanged
- [ ] One action; camera stated; exclusions stated
- [ ] No existing character, studio or artist named
- [ ] Inputs logged before generation; takes capped
- [ ] Hard-failure pass done on every take (eyes)
- [ ] First, middle and last frames compared with the model sheet (eyes)
- [ ] Digits counted (eyes)
- [ ] Conformed to 24 fps and 1080 × 1920; `qc_frames.py video` run
- [ ] Text and sound added by the engine
- [ ] Hook-up frames checked on both sides
- [ ] Watched at full speed (Harshith)
- [ ] Reported as generated, with tool, version and date

---

## 19. Open questions and inconsistencies found

**For Harshith.**

1. Does the starting position (no AI video generators for the series) still stand? If yes, sections 8.1 to 10 remain reference only.
2. If a test is wanted, which is acceptable: a hosted paid tool, or only models that run on your own GPU?
3. May engine stills of the approved characters be uploaded to a third-party service as references? That sends your designs to an outside company.
4. Is Workflow F (TTS voices) accepted as it is, once you have listened?

**Inconsistencies in the repository (reported, not changed).**

- The root `README.md` and `SKILL.md` describe cgi-shorts and say AI video through fal.ai is the default. They do not mention the 2D series or the starting position in 0.1.
- `references/models.md` lists endpoints and prices as "checked Nov 2026". I did not re-check them.

---

## 20. References

Tags: **[excerpt]** read this session as an excerpt from a search; the full page was not opened. **[own]** our repository.

**Hosted models**
- Google Developers Blog, "Introducing Veo 3.1 and new creative capabilities in the Gemini API": https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/ **[excerpt]**
- Scenario help, "Veo 3.1 - The Essentials" (first frame and reference images not combined): https://help.scenario.com/articles/1049410120-veo-3-1-the-essentials **[excerpt]**
- Pletor docs, Veo 3.1 model page (durations, ratios): https://docs.pletor.ai/ai-model-library/video-models/google-veo3.1 **[excerpt]**
- fal.ai, Kling 3.0 page: https://fal.ai/kling-3 ; "Seedance 2.0 vs. Kling 3.0": https://fal.ai/learn/tools/seedance-2-0-vs-kling-3-0 **[excerpt]**
- Magic Hour, "Kling 3.0 Reference Guide": https://magichour.ai/blog/kling-30-reference-guide **[excerpt]**
- Atlas Cloud, "How to Use Kling 3.0 for Character Consistency": https://www.atlascloud.ai/blog/guides/how-to-use-kling-3.0-for-character-consistency **[excerpt]**
- invideo FAQ, Seedance 2.0 against Kling 3.0 (the documented production): https://invideo.io/faq/seedance-20-vs-kling-30-which-ai-video-model-is-better/ **[excerpt]**

**Disclosure**
- YouTube Help, "Disclosing use of GenAI content": https://support.google.com/youtube/answer/14328491 **[excerpt]**
- YouTube blog, "How we're helping creators disclose altered or synthetic content": https://blog.youtube/news-and-events/disclosing-ai-generated-content **[excerpt]**
- Wired, on the exemption for animation (mirror): https://wirednews.pages.dev/story/kids-cartoons-free-pass-youtube-deepfake-disclosure-rules **[excerpt]**

**Our own material [own]**
- `references/06-pipeline-and-tools.md` (open models, who can do what), `references/07-qc-rubric.md`, `references/09-lessons-learned.md`
- Root `README.md`, `SKILL.md`, `references/models.md`, `references/prompting.md`, `scripts/run.py`
- `toon-slapstick/engine/`, `toon-slapstick/tools/tts_telugu.py`, `toon-slapstick/series/bheemu-gaju.md`
- `Character_Design_Bible.md`, `Slapstick_Comedy.md`, `Storyboard_and_Cinematography.md`, `Sound_Design.md`, `Quality_Control.md`, `Production_Pipeline.md`

---

## 21. Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.0. No generative tool was run. Hosted-tool statements are excerpts read today; open-model statements are carried from `references/06-pipeline-and-tools.md`. All workflows other than A and F are proposals. Not reviewed by Harshith. |
