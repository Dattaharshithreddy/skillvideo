# Character design and consistency handbook

Tags: **[established]** standard teaching · **[recommendation]** our rule · **[measured]** from our own files.

## 1. What makes a design work [established]

- **Silhouette first.** The character is recognisable as a black shape. Bheemu: round head, two round ears, pear body.
  Gaju: big ears, trunk, cap. If two characters share a silhouette, change one.
- **Simple forms.** Build from spheres, pears, cylinders and beans. A form has a front, sides and a back; a flat shape does not.
- **Contrast between characters.** Big and small, round and pointed, slow and quick. Bheemu is heavy and calm; Gaju is small and busy.
- **Proportion in heads.** Measure the body in head-heights and keep it. Cute characters are 2 to 3 heads tall; adults 5 to 6.
- **Line of action.** One curve through the whole pose. A straight vertical line is a dead pose.
- **Weight and balance.** The weight sits over the supporting foot. If the head leans out, the hips go the other way.
- **No twins.** Left and right sides never mirror each other in a pose.

## 2. The pipeline for a new character

Do these in order and get step 5 looked at before going further (lesson learned #4).

1. **Brief.** Name, species, age, what they want, how they move, one flaw, relationship to the leads.
2. **Silhouettes.** Six to ten black shapes. Pick the one that reads fastest.
3. **Construction.** The chosen shape rebuilt from simple forms, with a centre line and eye line on the head.
4. **Proportion and anatomy guide.** Height in heads, limb lengths, where joints are. For animals, study the real skeleton:
   which way the knee and hock bend, how many toes, how the animal sits.
5. **Model sheet.** Clean final drawing.
6. **Turnaround.** Front, three-quarter, side, back at the same height on a grid.
7. **Expression sheet.** At least twelve, each using brows, lids, pupils, mouth and head tilt together.
8. **Mouths and eyes.** Closed, smile, open small, open wide, "oo", teeth; eye shapes for wide, half, shut happy, shut tight.
9. **Hands, feet, special parts.** Relaxed, open, fist, point, grip, pinch; feet from front and side; trunk, tail, ears in three positions.
10. **Action poses.** Neutral, walk, run, jump, fall, reaction, sitting, sleeping.
11. **Colour and shading guide.** Named colours with values, ink colour, where shadows go.
12. **Consistency checklist** (below), filled in.

A sheet of four views is reference, not animation. New poses are drawn whenever the action needs them.

## 3. Our cast, as built [measured from the engine]

| Character | Class | Height (engine units) | Fixed features |
|---|---|---|---|
| Bheemu | `chars.Bheemu` | 580 | Round head, oval eye patches, gold round glasses, small orange scarf, long pear body, arms from behind the shoulders, 4-toed paws |
| Gaju | `chars.Gaju` | 250 | Yellow cap, big pink-lined ears, thick trunk with wrinkles and a nostril tip, column legs with toenails, no fingers |
| Ammamma | `cast.Ammamma` | 560 | Green cotton saree with gold border, maroon blouse, silver bun, red bindi, bangles, bare feet |
| Chintu | `cast.Chintu` | 390 | Red and yellow striped shirt, blue shorts, hair tuft, bare feet |
| Laddu | `cast.Laddu` | 250 | Orange tabby, cream bib and paws, green almond eyes with slit pupils |
| Bujji | `cast.Bujji` | 300 | White, long leaf ears with pink inside, big hind feet, front paws at the chest |

Approved and frozen: Bheemu's face, Bheemu's and Gaju's limbs and body (lesson learned #3). Do not alter without being asked.

## 4. Consistency checklist (every new pose, every shot)

- [ ] Same number of heads tall as the model sheet.
- [ ] Head, eye and ear sizes unchanged; eyes on the eye line.
- [ ] Markings in the same place (eye patches, stripes, bib).
- [ ] Clothing and accessories present and the right way round (glasses, scarf, cap, bindi, bangles).
- [ ] Digit count right on every hand, paw and foot.
- [ ] Limbs attach where the model says; nothing floating or detached.
- [ ] Limb thickness and length unchanged unless deliberately stretched for 1-3 frames.
- [ ] Colours from the palette only.
- [ ] Line weight the same as neighbouring shots.
- [ ] Left and right not mirrored.

## 5. Common mistakes and how to catch them

| Mistake | How to detect | Correction |
|---|---|---|
| Limbs built from separate shapes with visible joins | Zoom to 300% on shoulders, wrists, ankles | One outline per limb, with the hand or paw unioned into it |
| "Toy" look: limbs stuck on the outside of the body | Arms start at the widest part of the torso | Start arms behind the shoulder line; overlap the body outline |
| Proportions drifting between shots | Overlay the model sheet at the same scale | Fix the pose, never rescale the character per shot |
| Anatomy from imagination | Compare with a photo or a skeleton diagram | Study the real animal first (which way joints bend, how it sits) |
| Face redesigned while fixing something else | Diff against the approved sheet | Change only what was asked |
| Sitting or lying poses invented by squashing the standing pose | Looks deflated | Draw a dedicated pose for it |

## 6. Using image-generation tools for references

When a tool is available, generate reference sheets, then inspect for: wrong digit counts, duplicated limbs, glasses or cap
changing shape, markings moving, proportions changing between views. Reject and regenerate rather than "fixing in animation".
A generated sheet is still only reference: the engine's model must be made to match it by hand.
Claude cannot generate images directly in this workspace; it draws through the engine's code.
