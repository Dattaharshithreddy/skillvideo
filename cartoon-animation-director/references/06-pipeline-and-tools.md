# Video production pipeline and tools

Tags: **[verified 2026-11-11]** checked by web search that day · **[established]** widely known, not re-checked today ·
**[tested]** run by us · **[recommendation]** our choice.

## 1. Who can do what

| | Claude directly | Needs a connected tool | Needs Harshith or outside software |
|---|---|---|---|
| Script, gag design, shot list, timing plan | yes | | |
| Drawing characters and backgrounds | yes, as code in the engine (parametric drawings, not free-hand) | image-generation tool for painted references | hand drawing in Krita or OpenToonz |
| Animating | yes, pose-to-pose in the engine | GPU for AI in-betweening | frame-by-frame drawing by a human animator |
| Watching reference video | | the desktop browser | |
| Rendering and encoding | yes (CPU, about 3 min per 30 s) | | |
| Music and effects | yes, synthesised | | recorded instruments, licensed libraries |
| Voices | yes, free Telugu TTS model [tested] | | a human voice actor |
| Hearing the result | no | | Harshith |
| Judging if it is funny | partly | | Harshith and a test audience |
| Uploading to YouTube | | browser, with his approval | Harshith |

## 2. The stages

| # | Stage | Input | Output | Tool | Common failure | Accepted when |
|---|---|---|---|---|---|---|
| 1 | Script | Idea | One page: want, obstacle, beats, ending | Claude | Too many ideas | Retold in two sentences |
| 2 | Storyboard | Script | One panel per pose change, with shot size and screen direction | Engine stills or sketches | Action hidden, wrong shot size | Story reads from panels alone |
| 3 | Animatic | Panels | Panels timed to scratch sound, real duration | Engine + ffmpeg | Holds too short | Timing feels right at full speed |
| 4 | Assets | Board | Model sheets, props, backgrounds | Engine (`chars.py`, `cast.py`, `sets.py`) | Off-model, static things that must move | Consistency checklist passes |
| 5 | Key animation | Animatic | Key poses per shot | Engine `move`/`set` | Weak silhouettes, twins | Silhouette sheet reads |
| 6 | In-betweens | Keys | Full motion | Engine easing, or AI in-betweener | Even spacing, sliding | Arcs and spacing checked |
| 7 | Cleanup and colour | Motion | Final line and colour | Engine | Detached parts, flicker | No unintended flicker |
| 8 | Background compositing | Layers | Character over background, shadows | Engine `Stage` | Characters floating | Contact shadows present |
| 9 | Effects | Composite | Dust, water, impact, secondary motion | Engine fx | Effects stealing attention | Support the action only |
| 10 | Sound | Timing | Music, effects, voice | `sound.py`, `voice.py` | Late or early hits | Hits within 1 frame of the picture |
| 11 | Editing | Shots | Cut sequence | Engine cuts, ffmpeg | Jumps in position between shots | Continuity checklist passes |
| 12 | Rendering | Edit | 1080x1920, 24 fps, H.264 + AAC MP4 | Engine + ffmpeg | Huge files, wrong fps | `qc_frames.py video` passes |
| 13 | QA | Video | QC report | `tools/qc_frames.py` + eyes | Claiming a pass without looking | Rubric score at or above the bar |

## 3. Tool comparison

### Drawing and frame-by-frame animation

| Tool | What it is | Cost / licence | Good for | Limits for us |
|---|---|---|---|---|
| **toon-slapstick engine** (ours) | Code-drawn characters, pose-to-pose, CPU render | Ours | Claude can run the whole thing alone; fast | Puppet-style: parts move, they are not redrawn. Not hand-drawn quality. [tested] |
| **OpenToonz** | Full 2D pipeline: drawing, scan cleanup, timeline, compositing, render in one app. Based on the Toonz software used by Studio Ghibli. | Free for commercial and non-commercial use [verified 2026-11-11] | True frame-by-frame production | Needs a human animator at the desktop |
| **Krita** | Painting program with an animation timeline | Free [verified 2026-11-11]; open source (GPL) [established] | Hand-drawn frames, backgrounds | Needs a human; no compositing pipeline |
| **Blender Grease Pencil** | 2D stroke animation inside Blender's timeline, layer based, mixes with 3D | Free [verified 2026-11-11]; open source (GPL) [established] | 2D drawn animation with 3D cameras; scriptable in Python | Heavier to learn than a 2D-only tool [verified 2026-11-11] |
| **Pencil2D** | Light frame-by-frame tool | Free, open source [verified 2026-11-11] | Pencil tests | Few production features |
| **Synfig Studio** | Vector tweening | Free [verified 2026-11-11] | Cut-out style | Same puppet look as our engine |
| Toon Boom Harmony, Moho, Adobe Animate | Industry rigging and frame-by-frame tools | Paid [established] | Studio work | Cost; need a human |

### AI in-betweening and video generation (open models)

| Tool | Input | Output | Limits |
|---|---|---|---|
| **ToonCrafter** | Two cartoon stills + a prompt | The motion between them | 512x320, up to 16 frames; success not guaranteed; cannot draw text [verified 2026-11-11] |
| **Wan 2.2 first-last-frame** | Two stills | 720p clip; Apache 2.0 [verified 2026-11-11] | General model, style can drift; needs a strong GPU |
| **AniSora** | One still | Anime-style clip; Apache 2.0 [verified 2026-11-11] | 14B model, large GPU |
| **ToonComposer** | Keyframe sketches + one colour frame | Finished cartoon clip | About 57 GB GPU memory for 61 frames at 480p [verified 2026-11-11] |

None of these can be run in Claude's workspace (no GPU, model host blocked). They run on Harshith's GPU server or in online demos.

### Sound and voice

| Need | Tool | Status |
|---|---|---|
| Music and effects | `engine/sound.py` (synthesised tabla, bansuri, veena, effects) | [tested]; not heard by Claude |
| Telugu voice | AI4Bharat Indic-TTS, female speaker; pitched for Ammamma and Chintu | [tested]; quality not confirmed by Harshith |
| Real animal sounds | Recorded files supplied by Harshith | Not available yet |

### Editing and delivery

ffmpeg for encoding: H.264, CRF 20-22, `-tune animation`, AAC 160 kbps, `+faststart`. 1080x1920 at 24 fps. [tested]

## 4. Recommended pipeline today [recommendation]

1. Script, board and animatic in the engine (fast, Claude alone).
2. Key poses in the engine, checked as silhouettes.
3. In-betweens: engine easing for most shots. For hero actions, test AI in-betweening between engine keys on the GPU server.
4. Signs and Telugu text composited by the engine after any AI step (AI models garble text).
5. Sound in the engine; Harshith listens.
6. QC with the rubric before anything is sent.

If hand-drawn quality is required beyond what this gives, the honest options are a human animator in OpenToonz or Krita,
or commercial AI video models with our character sheets as references.
