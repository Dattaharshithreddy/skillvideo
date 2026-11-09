# Prompting guide

## Global `style` presets (pick one, matching the look in style-guide.md)
- **A bright explainer:** `high-end 3D CGI render, glossy saturated colours, realistic but slightly stylised like a modern video game cinematic, soft even studio lighting, plain pastel backdrop, crisp detail, medical-illustration quality anatomy, vertical 9:16`
- **B realistic story:** `realistic 3D CGI render, naturalistic lighting, real-world location detail, slight motion blur, accurate costume and props, cinematic but not dark, vertical 9:16`
- **C science:** `clean 3D CGI render, white and lab-blue colour palette, soft diffused lighting, macro photography depth of field, glowing particles, vertical 9:16`

## Image prompt (`image` field)
Order: **subject + action frozen mid-moment → framing → backdrop → special device**. Keep it to one idea, since the shot is on screen for under 2 seconds.

Examples:
- `blue nitrile gloved hand holding forceps that lift a tiny glowing red heart out of a hummingbird's open chest, macro close-up, plain lavender backdrop`
- `the mascot standing on a blue running track, a circular porthole cut in his yellow t-shirt revealing hundreds of tiny beating hearts inside his chest, medium shot, bright sky`
- `x-ray view of a human torso, dark navy background, body outline glowing cyan with fresnel edges, only the heart in full red colour`
- `flight-deck crewman in yellow jumpsuit and helmet being pulled feet-first toward a jet engine intake, night carrier deck, motion blur`
- `macro view of two green grapes touching on a microwave turntable, a bright violet spark glowing exactly where they meet`
- `field-line arrows flowing through air between floating glowing molecules, bokeh background, white and blue palette`

### Cutaway recipes
- **Porthole:** `a clean circular hole cut through his [shirt/skin/jeans] revealing [inside] in full detail`
- **X-ray:** `dark navy background, translucent body glowing cyan at the edges, [organ] in full colour`
- **Transparent object:** `semi-transparent [machine/wall] showing [subject] inside`
- **Macro → molecule:** `extreme macro`, then `molecular scale, glowing spheres for atoms`

### Consistency
- Define each recurring character in `characters` with 4–6 fixed traits (head/hair, shirt colour, trousers, build, one distinctive feature). `--stage refs` makes a reference sheet, and every shot listing the character is generated from it.
- Same backdrop colour for all studio shots in a video.

## Motion prompt (`motion` field)
Shots last ~1.5 s but clips are 5 s, so describe motion that reads within the **first 2 seconds**. Use `clip_start` in shots.json to pick a later section if the best moment comes later.
- `slow push-in as the forceps lift the heart out`
- `camera drifts right, tiny hearts pulse rapidly`
- `the crewman slides toward the intake, strong motion blur, slight camera shake`
- `spark flares between the grapes, camera slowly pushes in`
- `slow orbit around the glowing torso`

Avoid: scene changes, new characters entering, text, lip-sync, multiple actions.

## Negative cues (models that accept them)
`text, watermark, logo, blurry, deformed hands, extra fingers, distorted face, morphing, cartoon, anime, low poly, gore`
