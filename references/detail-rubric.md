# Detail rubric: how detailed is "Zack D detailed"

What frame-by-frame study shows: every frame works as a still image. The detail lives in **materials, micro-imperfections, purposeful light, FX that show forces, and accurate props**. Use this rubric to write prompts and to grade every still before animating.

## 1. The detail stack (put all 5 layers in every `image` prompt)
| Layer | What to specify | Reference examples |
|---|---|---|
| **1. Subject + frozen action** | Who/what, mid-motion, with a readable pose or expression | forceps lifting a heart; man bracing, body leaning 30°; cheeks pushed by wind |
| **2. Materials** | Name each material and its finish | iridescent feathers with individual barbs; wet glossy heart; matte blue nitrile glove; brushed steel with micro-scratches; translucent bone; denim fibres |
| **3. Micro-imperfections** | 1–2 small real-world flaws | moles and pores on skin; scuffed helmet paint; scratched ear cups; worn stitching; condensation |
| **4. Light** | Soft key + rim, and one motivated accent | soft wrap studio light; cyan fresnel rim on x-ray bodies; warm practical light; glowing element as its own light source |
| **5. Environment** | Simple and uncluttered, one colour family, shallow depth of field | lavender wall with one darker stripe; blurred blue kitchen tiles; night carrier deck with distant lights |

Template:
`[subject + frozen action], [framing/lens], [material 1 with finish], [material 2], [1–2 imperfections], [light: soft key + rim + accent], [simple backdrop, colour], shallow depth of field`

## 2. FX that show forces (use when anything moves fast or is invisible)
- **Airflow/suction:** translucent wind streaks and haze flowing into the opening.
- **Speed:** directional motion blur on the background, streak lines.
- **Invisible agents:** glowing colour-coded particles (bacteria green rods, energy violet sparks, oxygen blue spheres), the same colour in every shot.
- **Paths:** motion trails that draw the trajectory.
- **Impact:** small debris, dust puffs, a camera shake in the motion prompt.

## 3. Anatomy and cutaways (look A)
- Medical-atlas fidelity: glossy red muscle fibres with striations, blue veins and red arteries as smooth glossy tubes, cream translucent bone.
- X-ray: dark navy background, body as translucent glass with cyan fresnel edges, one organ in full colour.
- Porthole: a perfectly clean-edged hole (circle or rectangle) through clothing and skin, with the material's thickness visible at the edge (denim fibres, skin layers).

## 4. People
- Realistic proportions with a slightly polished, game-cinematic finish; never cartoon.
- Expressive acting: strain, shock, dizziness, disgust. Faces deform with forces (wind, g-force).
- Clothing has cloth folds and flapping in motion; occupation-accurate gear.
- Recurring mascot: identical outfit every shot.

## 5. Camera and motion (for `motion` prompts)
- Something always moves: slow push-in, orbit, lateral track, follow-cam.
- At the start or end of a shot, use a fast whip/arc (0.3 s, blurred) to a new framing. This doubles as a transition.
- Macro shots: slow push with focus fall-off. Wide shots: lateral track. Reveals: slow push into the porthole.

## 6. Grading a still (score each 0–2; regenerate below 8/10)
| Check | 0 | 1 | 2 |
|---|---|---|---|
| Readable at phone size in 1.5 s | cluttered | ok | instantly clear |
| Materials distinct | plastic/same-y | some | every surface reads |
| Micro-detail | none | some | imperfections visible up close |
| Light | flat or harsh | ok | soft key + rim + accent |
| Consistency | character/palette drifts | minor | matches refs and palette |
Also reject: text/logos baked in (except intended labels), extra fingers, warped faces, gore.

## 7. Numeric targets for the final video (checked by `scripts/analyze.py`)
- Average shot 1.2–2.2 s, longest ≤ 4.5 s, total 25–48 s.
- Camera near-still in ≤ 25% of moments.
- Look A: luma 0.45–0.72, saturation 0.40–0.65, contrast 0.12–0.22.
- Look B: luma 0.33–0.55, saturation 0.25–0.48, contrast 0.17–0.32.
- Look C: luma 0.55–0.75, saturation 0.25–0.45, contrast 0.10–0.18.
