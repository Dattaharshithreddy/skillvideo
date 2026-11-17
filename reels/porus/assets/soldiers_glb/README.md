# Puru vs Alexander assets for NOVA

## Soldiers (GLB, converted from army.blend)
One static posed figure per type, ~44-47k triangles each, Y-up, metres, feet at origin.
- ind_spear_white / ind_spear_saffron / ind_spear_red: Indian spearmen (turban colour), dhal shield, bhala spear
- ind_sword: Indian swordsman
- greek_white / greek_red: Macedonian soldiers, bronze helmet and round shield
- alexander, puru (puru wears the tall crown)

Skin, cloth weave, pleats and borders are baked into one 4096 albedo texture per figure (JPEG inside the GLB); metal parts keep metallic=1. Skin is a procedural mottled tone (the original MPFB skin images were not packed in army.blend). No skeleton: figures are posed statues, fine for miniature crowds; use instancing.

## Not here yet
War elephant, Puru's royal elephant, horse: Model Forge GLBs exist only on the stopped GPU server. Use stand-ins until AWS is unblocked.

## ref/
Blender Cycles reference for the side-by-side test (GPU A10G, 24 samples, 540x960 stills):
- blender_clip_A/B/C.mp4: A aerial crane, B dolly to Puru, C orbit Alexander (5 s each)
- still_A/B/C.jpg: frame 60 of each shot
- army_sheet.jpg: lineup of all soldier types
Camera setups (cam position, target, f-stop), keyframed start -> end over 150 frames:
- A: (-9,-52,32)->(5,-30,11), target (0,2,0)->(0,-3,0.5), f/1.6 -> f/1.1
- B: (-15,-6.6,1.3)->(1.2,-7.0,1.9), target (-9,-11,1.0)->(0,-10.4,1.6), f/2.0 -> f/1.4
- C: (2.4,7.3,0.55)->(-1.6,7.5,0.7), target (0.5,9.4,0.5) -> (0.5,9.4,0.55), f/1.2
Coordinates are Blender Z-up. Layout: river y = 2.5*sin(0.07x); Greeks y 11..22, Indians y -22..-13, elephants y about -11, Alexander + horse near (0.6, 9.4), Puru on elephant near (0,-10.4). Soldiers scaled 0.4 (miniature).
