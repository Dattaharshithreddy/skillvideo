---
name: cgi-shorts
description: Make Zack D Films-style vertical shorts: 30-second 3D/CGI explainers and true stories with porthole/x-ray cutaways, a calm flowing narrator, a cut every 1-2 seconds and small lowercase captions. Use for a "Zack D style" short, a 3D what-if/fact short, or a CGI story reel.
---

# CGI Shorts (Zack D Films style)

Topic → script → word-timed narration → shot stills → image-to-video clips → captions + SFX + music → 1080x1920 MP4, 27–37 s.

Everything lives in one project folder. Every stage is re-runnable and skips finished work.

**Two engines.** `"engine": "blender"` in shots.json renders real 3D scenes in Blender on your own GPU, written as code with `blender/czlib.py`. There's no AI video and no per-clip cost; read `references/blender-mode.md` first. Leave `engine` unset to use AI images and video via fal.ai (below).

## 0. Setup (once)
```bash
pip install fal-client requests edge-tts      # add --break-system-packages if pip refuses
# ffmpeg + ffprobe on PATH
export FAL_KEY=...                            # stills + video (fal.ai)
export ELEVENLABS_API_KEY=...                 # narration (optional; edge-tts fallback)
```
Optional: put a bold rounded font (e.g. Nunito ExtraBold, free from Google Fonts) in `project/fonts/` and set `"captions": {"font": "Nunito ExtraBold"}` in `project/config.json`.

`--free` runs with no paid APIs (edge-tts voice, your own or placeholder stills, slow zoom on stills). Use it for drafts and timing checks; its renders will fail the motion check in `analyze.py`, because the reference footage moves far more than a zoom on a still.

## 1. Workflow
1. **Read `references/style-guide.md`**, then pick the look (A bright explainer / B realistic story / C science).
2. **Write the script** with `references/script-formulas.md`: 80–110 words, flowing sentences, hook in the first words, hard stop on the payoff. Verify every fact and number with a web search.
3. **Split into shot fragments** of 3–6 words (18–25 shots). Fragments may cut mid-sentence; joined with spaces they must equal the script.
4. **Write `shots.json`** (schema below) using `references/prompting.md` and `references/detail-rubric.md`. Every `image` prompt uses the 5-layer detail stack (subject+action, materials, imperfections, light, simple backdrop). Model the shot list on the closest breakdown in `references/shot-breakdowns.md`. Define recurring characters once.
5. **Check endpoints** before the first paid call each session: fetch `https://fal.ai/models/<endpoint-id>/llms.txt` for each endpoint in the config and fix parameter names in `config.json` if they changed (`references/models.md`).
6. **Run**
   ```bash
   python scripts/run.py PROJECT --stage tts      # check words/s in the log: aim 2.7-3.1
   python scripts/run.py PROJECT --stage refs
   python scripts/run.py PROJECT --stage images   # then grade EVERY still with the rubric (score <8/10 → fix prompt, --only sNN --force)
   python scripts/run.py PROJECT --stage animate  # the expensive step
   python scripts/run.py PROJECT --stage assemble
   ```
   A `--free` full run first is a cheap way to check pacing.
7. **Frame-by-frame QC:**
   ```bash
   python scripts/analyze.py PROJECT/out/final.mp4 --look A    # or B / C
   ```
   It detects every cut, measures shot lengths, camera motion, brightness, saturation and contrast against targets measured from the reference channel, and writes `analysis/report.md` plus first/last-frame contact sheets per shot (`analysis/shots_XX.png`). Open each sheet:
   - first ≈ last frame means a static shot: strengthen the motion prompt or regenerate the clip;
   - any shot over 2.5 s needs splitting.
   Fix every WARN, re-run the affected stages, re-analyze. Deliver only when pacing is all PASS and the look is PASS or explained. Report `out/cost.txt`.
8. **Study any reference** the user supplies the same way: `python scripts/analyze.py their_video.mp4` gives its cut list and sheets. Read them before writing the shot list.

## 2. Project layout
```
project/
  shots.json   config.json (optional overrides)   music.mp3 (optional, light bed)
  sfx/         whoosh.mp3, impact.mp3 ... referenced by name
  fonts/       optional caption font
  refs/ audio/ images/ clips/ out/     generated
```

## 3. shots.json
```json
{
  "title": "What if you had eagle eyes",
  "look": "A",
  "voice": {"provider": "elevenlabs", "voice_id": "pNInz6obpgDQGcFmaJgB", "stability": 0.5, "style": 0.1, "speed": 1.08},
  "style": "high-end 3D CGI render, glossy saturated colours, realistic but slightly stylised like a modern video game cinematic, soft even studio lighting, plain pastel backdrop, vertical 9:16",
  "characters": {
    "guy": {"description": "friendly bald man in his 30s, plain mustard-yellow t-shirt, blue jeans, slim build, light stubble"}
  },
  "shots": [
    {"id": "s01", "line": "If you swapped your eyes",
     "image": "blue nitrile gloved hands holding forceps that lift a glistening eagle eye toward the guy's face, macro, plain lavender backdrop",
     "motion": "slow push-in as the eye moves toward camera", "characters": ["guy"], "sfx": "whoosh"},
    {"id": "s02", "line": "for an eagle's,",
     "image": "majestic golden eagle head in profile, piercing eye, plain sky-blue backdrop",
     "motion": "eagle turns its head sharply toward camera"}
  ]
}
```
- `line`: the narration fragment for this shot (3–6 words). The shot lasts from its first word to the next shot's first word.
- `image`: the still. The global `style` is appended automatically.
- `motion`: what happens in the first ~2 s of the clip.
- `characters`: ids whose reference sheet is used, for consistency.
- `sfx`: optional sound in `sfx/`, played at the shot's first word.
- `still: true`: skip AI video and use a slow zoom on the still instead (cheap).
- `clip_start`: seconds into the generated clip to start from (pick the best moment).

## 4. Quality bar
- First frame already shows the action; the first words state the hook.
- Average shot ~1.7 s, no shot over ~2.5 s (one 4 s hold allowed); `analyze.py` pacing all PASS.
- Every still scores ≥ 8/10 on the rubric in `references/detail-rubric.md`.
- Captions: 1–3 words, lowercase as spoken, bold white with a soft shadow, at ~78% height (the default config does this).
- Bright, clean explainers (not dark and moody); at least 3 cutaway/x-ray/macro shots.
- Ends on the payoff or a gag; no outro, no call to action.
- Your own mascot and designs. No real people, logos, copyrighted characters or gore.

## References
- `references/blender-mode.md`: Blender engine on a GPU server: setup, scene-script contract, czlib cheat sheet, free assets, realism checklist, render budget (example: `examples/microwave-blender/`)
- `references/shot-breakdowns.md`: per-shot tables of 5 reference videos + measured numbers
- `references/detail-rubric.md`: the 5-layer detail stack, FX, anatomy, still-grading rubric, numeric targets
- `references/style-guide.md`: looks, devices, rhythm (from frame-by-frame study of the channel)
- `references/script-formulas.md`: openers, connectors, structures, worked example
- `references/prompting.md`: style presets, image/motion prompts, cutaway recipes
- `references/models.md`: endpoints, costs, config keys, Blender alternative
