"""Clip prompts for the AI miniature version (Wan 2.2 TI2V-5B). One list of clips per narration shot.
Every prompt gets the same style prefix so the whole reel reads as one handcrafted tabletop diorama."""
import json
STYLE = ("Tilt-shift macro photograph of a handcrafted miniature diorama on a tabletop, tiny hand-painted figurines, "
         "model trees and flock grass, resin river, shallow depth of field with soft blurred foreground and background, "
         "warm cinematic light, highly detailed, ancient India 326 BC. ")
NEG = ("cartoon, anime, 2D, illustration, real people, photograph of real life, modern objects, text, subtitles, watermark, logo, "
       "blurry subject, low quality, jpeg artifacts, deformed, extra limbs, distorted faces, static, frozen, flicker")
C = {
 'open': [
  "A long column of tiny Macedonian phalanx soldiers with bronze helmets, round shields and very long upright pikes marches across a dusty plain, slow camera dolly alongside them, golden morning light.",
  "A figurine of a young Greek king on a black horse, red cloak and white crested helmet, at the head of his tiny army, camera slowly pushes in, golden light.",
  "Across a wide miniature river, a long line of Indian war elephants with red and gold caparisons and wooden howdahs stands on the far bank, camera glides low over the water toward them."],
 'demand': [
  "A tiny horseman gallops up to the gate of an ancient Indian mud-brick fort with saffron flags; in front of the gate a regal Indian king figurine with a golden turban sits on a decorated war elephant, guards with long bows around him."],
 'ambhi': [
  "The tall wooden gates of an ancient Indian walled city slowly swing open; a king figurine in purple robes and turban bows low to a Greek general on horseback, slow push-in.",
  "Tiny Indian soldiers in purple turbans and two war elephants march out of the city gate to join rows of Greek soldiers with long pikes, slow pan."],
 'river': [
  "A wide swollen muddy river in monsoon flood flows fast through the miniature landscape; on the near bank a Greek camp of small red tents; on the far bank a long line of war elephants and Indian archers in white, slow pan.",
  "Close macro shot of tiny Greek cavalry horses rearing and panicking at the riverbank, war elephants blurred across the water."],
 'feint': [
  "Night on the miniature riverbank: tiny horsemen carrying burning torches gallop back and forth along the bank, torchlight reflecting in the dark water, blue moonlight.",
  "Night in a miniature Indian army camp: tiny soldiers in white sit around small campfires, tired, some lying down, the fires slowly dying, blue moonlight."],
 'storm': [
  "A violent thunderstorm at night over the miniature river: heavy rain, flashes of lightning, small wooden boats full of tiny soldiers secretly crossing the dark water.",
  "Misty dawn on the miniature river: tiny soldiers wade chest-deep through the water from a small island, holding round shields above their heads."],
 'son': [
  "Ancient Indian two-horse war chariots stuck in deep brown mud after rain, wheels sinking, tiny drivers whipping the horses, Greek horsemen charging in, a young prince figurine falling, slow push-in.",
  "Close macro of a young Indian prince figurine with a small golden turban falling from his stuck chariot into the mud, rain drops, slow motion."],
 'battle': [
  "Epic miniature battle: armored Indian war elephants with howdahs and archers charge into a dense phalanx of tiny soldiers holding very long pikes, dust rising, low macro tracking shot.",
  "Miniature battle chaos: wounded war elephants turn around in panic and trample their own Indian infantry, dust and fallen figurines.",
  "Tiny Greek cavalry gallops around the flank of the Indian army in a wide arc across the miniature plain, dust trails, aerial view."],
 'king': [
  "Close macro of figurines in golden evening light: a very tall wounded Indian king with a golden turban stands proudly, facing a young Greek king seated on a black horse, soldiers with pikes around them, shallow depth of field.",
  "Extreme close-up of the tall Indian king figurine slowly raising his head with dignity, golden light, soft bokeh."],
 'return': [
  "A miniature diorama landscape seen from above: a kingdom between two rivers glowing in warm golden light, tiny villages and saffron banners, slow aerial drift.",
  "Tired tiny Greek soldiers sit on the bank of a river under grey monsoon clouds, banners lowered, pikes lying on the ground, refusing to march on."],
 'murder': [
  "Dark miniature scene at night: an Indian king figurine alone by a small fire in front of a red tent; a shadowy figure with a dagger slowly approaches from behind; the fire flickers and goes out."],
 'legacy': [
  "Close macro of a regal Indian king figurine with a golden turban riding a richly decorated war elephant, golden sunset light, slow push-in, soft bokeh.",
  "At sunset a regal Indian king on a richly decorated war elephant stands on a hilltop, silhouetted against a golden sky, the camera slowly pulls back to reveal the whole miniature diorama on a wooden table with warm bokeh lights behind."],
}
clips = []
for shot, ps in C.items():
    for k, pr in enumerate(ps): clips.append({'id': f'{shot}_{k}', 'shot': shot, 'prompt': STYLE + pr})
json.dump({'neg': NEG, 'clips': clips}, open('ai/prompts.json', 'w'), indent=1)
print(len(clips), 'clips')
