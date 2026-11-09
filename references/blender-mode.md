# Blender mode: real 3D renders on your own GPU (no AI video)

Set `"engine": "blender"` in shots.json. Each shot gets a scene script (`scenes/sNN.py`) written with `blender/czlib.py`, and `run.py --stage animate` renders every shot headless on the GPU into `clips/sNN.mp4`. Voice, captions, SFX, assembly and `analyze.py` QC are unchanged.

## One-time server setup (Ubuntu 22.04 NVIDIA GPU server, e.g. AWS Deep Learning Base OSS AMI)
```bash
bash cgi-shorts/blender/setup_server.sh      # Blender 5.2, ffmpeg, Kokoro voice, GPU test render
```
It prints the GPU (OptiX on RTX/T4/A10G/L4) and a render time. If it says `device: CPU`, the driver isn't visible: check `nvidia-smi`.

## Workflow for each video
1. Script → shot fragments → `shots.json` with `"engine": "blender"`, each shot `"scene": "scenes/sNN.py"`. Steps 1–3 of SKILL.md still apply.
2. `python scripts/run.py PROJECT --stage tts`, which fixes every shot's exact duration.
3. Write one scene script per shot (contract below). Shared builders go in `scenes/common.py`.
4. **Look check, cheap:** one still per shot
   `blender -b --factory-startup -P blender/render.py -- scenes/s04.py /tmp/s04.png 2.0 --quality preview --still 1.0`
   Grade each against `detail-rubric.md`; fix until ≥ 8/10.
5. **Preview video:** `python scripts/run.py PROJECT --stage animate --preview` then `--stage assemble` and `analyze.py`. Fix motion/pacing WARNs.
6. **Final:** `python scripts/run.py PROJECT --stage animate --force` (full res, 128 samples), then assemble + analyze.

## Scene script contract
```python
import czlib as cz            # cz.reset(), gpu_setup(), render_preset(), set_frames() are already done
def build(secs):               # secs = shot length incl. 0.35 s handle; frames 1..cz.S.frame_end at 30 fps
    cz.world_studio((0.62, 0.68, 0.95), top=(0.85, 0.88, 1.0))
    cz.studio_rig()
    heart = cz.sphere(0.3, (0, 0, 0), cz.mat_glossy_organ())
    cz.key_obj(heart, 1, scale=(1, 1, 1)); cz.key_obj(heart, 8, scale=(1.15, 1.15, 1.15))
    cam = cz.camera(50, fstop=2.0)
    cz.push_in(cam, (0, 0, 0), (0, -4, 0.6), (0, -2.5, 0.3))
```
Everything that moves must be **keyframed** (helpers do it). That is how motion blur and the final render see it.

## czlib cheat sheet
| Area | Helpers |
|---|---|
| Materials | `mat_pbr` (roughness variation + bump imperfections built in), `mat_skin` (SSS, pores), `mat_glossy_organ`, `mat_glass`, `mat_glow`, `mat_xray` (cyan fresnel x-ray body), `ph_material('brick_wall_001')` |
| Worlds/light | `world_studio` (look A/C backdrop), `ph_hdri('studio_small_09')` / `world_hdri` (look B realism; `background=` hides the HDRI but keeps its light), `studio_rig` (soft key + fill + rim), `area_light`, `fog` |
| Objects | `sphere`, `cylinder`, `box` (bevelled edges), `plane`, `text3d`, `arrow`, `molecule_h2o`, `scatter`, `glow_particles(shape='rod')` for bacteria, `porthole(target, center, r)` cutaway, `import_model`, `ph_model('food_apple_01')`, `shape_key(face, 'jawOpen', 0.6, frame)` |
| Camera | `camera(lens, fstop)`, `push_in`, `orbit`, `follow(cam, obj)`, `move_camera(path_fn, target_fn, shake=)`, `whip(cam, frame)` (0.25 s transition) |
| Animation | `key_obj(obj, frame, loc/rot/scale)`, `animate(fn(t, k, frame))` for per-frame logic, `ease()` |

## Assets (free; downloaded and cached on the server in `~/.cache/cgi-assets`)
- **Poly Haven (CC0):** HDRIs, PBR textures, models via `ph_hdri/ph_material/ph_model`; `cz.ph_search('models', 'food')` lists ids.
- **Humans:** MPFB (the MakeHuman plugin for Blender) exports CC0 realistic humans; Mixamo (free Adobe login) gives rigged characters and animations as FBX → `import_model`. For lip/expressions use a character with ARKit-style shape keys (`jawOpen`, `eyeBlinkLeft`, `mouthSmileLeft`…) and `shape_key()`.
- **Anatomy:** BodyParts3D (CC BY-SA, credit it in the description) gives real scanned bones and organs as OBJ → `import_model`.
- **Earth/space:** NASA Visible Earth / Blue Marble textures (public domain) on a sphere.
- Credit every CC BY-SA source in the video description.

## Realism checklist (what separates "3D" from "looks real")
1. **Light like a photographer:** large soft key, weaker fill, strong rim; or a real HDRI. Never a single point light.
2. **No perfect surfaces:** roughness variation + micro-bump (on by default in `mat_pbr`), bevelled edges (`box` does it), dust/scratches on hero props.
3. **Skin and organs need subsurface scattering** (`mat_skin`, `mat_glossy_organ`).
4. **Real scale:** model in metres; a 1.8 m human, a 0.3 m skull. Wrong scale breaks DOF and light falloff.
5. **Depth of field** on every macro and close shot (`camera(fstop=1.6–2.8)`); focus on the subject.
6. **Motion blur on** (render preset) and **camera never static** (push/orbit/follow; `shake=0.01` handheld, `0.04` impacts).
7. **Atmosphere:** subtle `fog(0.01)` for depth in large scenes; volumetric god rays only where they motivate the light.
8. **Colour:** AgX Punchy for most shots; Standard view for saturated glowing FX (heat, energy). Keep one palette per video.
9. **Film finish:** the render driver adds subtle grain + vignette (`CZ_POST` env to change or disable).
10. **Composition for 9:16:** subject in the upper 55%; captions own ~78% height.

## Render budget (estimates; measure with `setup_server.sh`)
| GPU | Final (1080x1920, 128 spp) per frame | 10 s video (300 frames) |
|---|---|---|
| NVIDIA T4 (AWS g4dn) | ~3–8 s | ~15–40 min |
| A10G (AWS g5) | ~1–3 s | ~5–15 min |
| RTX 4090 / L40S | ~0.5–1.5 s | ~3–8 min |
Heavy scenes (glass, volumes, many lights) cost 2–5x more. Use `--preview` until the look is final.
