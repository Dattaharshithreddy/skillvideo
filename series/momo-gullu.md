# Momo & Gullu: character + series spec (for Claude Code)

Silent slapstick 3D cartoon Shorts (30–45 s, 1080x1920). Two best friends try everyday tasks and cause glorious disasters. No dialogue: grunts, giggles, trumpets, music, SFX. Warm, kind, nobody gets hurt.

## Momo, the panda ("the expert")
- Body: pear-shaped, soft, big round belly, short stubby legs, small round ears set wide apart. About 2.5x Gullu's height (Momo ~1.6 m, Gullu ~0.65 m).
- Face: black eye patches tilted downward (sleepy-smart), tiny round gold reading glasses low on the nose.
- Outfit: only a bright orange scarf. Nothing that resembles famous cartoon pandas (no shorts, no martial arts).
- Personality: confident, a bit lazy, loves snacks and naps, soft-hearted.
- Signature moves: The Plan (pushes up glasses, taps chin with a bamboo stick, points); Panda Roll (curls into a ball and rolls away); Stress Snack (munches bamboo fast).
- Colours: fur white #F4F1EA, black #1E1E24, scarf orange #FF7A1A, glasses gold #C9A227.

## Gullu, the baby elephant ("the helper")
- Body: small, round, chunky; big head; huge floppy ears (wider than his body); short trunk curling at the tip; tiny tail with a tuft.
- Face: big shiny eyes with long lashes, rosy cheeks, permanent excited smile.
- Outfit: a yellow cap worn backwards, slightly too small.
- Personality: joyful, curious, loyal, copies Momo but bigger; takes instructions literally.
- Signature moves: Trunk Tool (hose, vacuum, hand, trumpet, bat); Ear Fly (flaps ears to hover); Sneeze Blast; Squeeze Hug (glasses pop off Momo).
- Colours: skin grey-blue #8FA3B8, inner ears and cheeks pink #F4A6B8, cap yellow #FFC93C.

Silhouette check: Momo = big pear with two dots on top; Gullu = small ball with two giant fans and a hook.

## Look
Soft, rounded, toy-like 3D cartoon with a slightly fuzzy surface (sheen + fine noise bump, no hair particles except close-ups). Pastel world: sky blue, mint, butter yellow, peach. Soft key + rim light.

## Neighbour
Mr. Kukdu: grumpy, very neat rooster in a cardigan; always the victim of the chaos (running gag).

## Episode formula (30–45 s, new shot every 1.5–2.5 s)
1. Goal (0–4 s): Momo opens the *How To Do Everything* book. 2. First try (4–12 s). 3. Escalation x3 (12–25 s). 4. Disaster, often onto Mr. Kukdu (25–32 s). 5. Button: twist + Squeeze Hug, hard stop.

## Episode 1: Momo & Gullu Make Dosa (35 s, kitchen)
1. Sizzling empty tawa; Momo slaps the book open to a golden dosa. 2. Momo ladles a neat small circle, proud. 3. Gullu sucks the whole batter bucket into his trunk. 4. Gullu sprays: one giant dosa over the tawa, stove and counter. 5. Momo does The Plan, points at a tiny spatula. 6. Gullu's Ear Fly wind lifts the giant dosa. 7. Dosa flips out of the window onto Mr. Kukdu. 8. Kukdu walks out wearing it like a cape, furious. 9. Kukdu tastes it, smiles; all three share it on the doorstep; Squeeze Hug.

## Build order
1. `characters/momo.blend`, `characters/gullu.blend`: code-built (rounded primitives + subdivision/skin modifier), each with a Rigify rig (Gullu: bendy-bone trunk chain + ear flap bones) and face shape keys (blink, smile, frown, mouthOpen, cheekPuff, browsUp, browsDown).
2. Turnaround + expression renders for approval.
3. 5 s test: Gullu's Ear Fly.
4. Episode 1 via cgi-shorts (Blender engine, no narration).
