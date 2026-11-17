"""Keyframe prompts (ElevenLabs gpt-image, 9:16) for the AI miniature reel; Wan 2.2 animates each still."""
import json
B = ("Vertical 9:16 photograph of a handcrafted museum-quality miniature diorama, tiny hand-painted figurines, macro lens tilt-shift, "
     "shallow depth of field, crisp detail on the main figurines, natural rich colors, warm side light, dark studio and table edge far behind, no sky. ")
PURU = "a very tall Indian king figurine with dark skin, black beard, golden turban with a jewel, white dhoti, saffron sash, gold armlets and a long sword"
ALEX = "a young clean-shaven Greek king figurine with curly hair, bronze helmet with a tall white plume, red cloak and bronze cuirass, on a black horse"
PHAL = "Macedonian phalanx figurines with bronze helmets, round bronze shields with a star emblem, red tunics and very long sarissa pikes"
INDI = "Indian soldier figurines in white tunics and turbans with tall bamboo longbows"
ELEP = "Indian war elephants with red and gold caparisons and wooden howdahs carrying archers"
K = {
 'open_0': f"A column of {PHAL} marches toward the camera across a dusty ochre plain, filling the frame; behind them {ALEX}. Golden morning light.",
 'open_1': f"Close-up of {ALEX} raising his right hand to command, rows of {PHAL} behind him.",
 'open_2': f"Low view across a wide resin river: on the far bank a long line of {ELEP}; foreground water ripples.",
 'demand_0': f"A tiny Greek messenger on horseback arrives at the gate of an ancient Indian mud-brick fort with saffron flags; in front of the gate {PURU} sits on a richly decorated war elephant, {INDI} on guard.",
 'ambhi_0': f"The tall wooden gates of a walled ancient Indian city stand open; a king figurine in a purple robe and purple turban bows low before {ALEX}.",
 'ambhi_1': f"Indian soldier figurines in purple turbans and two war elephants march out of the city gate to join rows of {PHAL}.",
 'river_0': f"A wide flooded muddy resin river in monsoon; on the near bank a Greek camp of small red tents and {PHAL}; on the far bank a long line of {ELEP} and {INDI}.",
 'river_1': f"Close-up of Greek cavalry horse figurines rearing in panic at the riverbank; blurred war elephants across the water.",
 'feint_0': f"Night scene: Greek horseman figurines carrying burning torches gallop along the riverbank, torchlight reflecting in the dark resin water, blue moonlight.",
 'feint_1': f"Night scene in an Indian army camp: {INDI} sit tired around small glowing campfires, some lying down, blue moonlight.",
 'storm_0': f"Night thunderstorm over the miniature river, lightning flash, heavy rain, small wooden boats crowded with {PHAL} secretly crossing the dark water.",
 'storm_1': f"Misty dawn: {PHAL} wade chest-deep through the river from a small island, holding round shields above their heads.",
 'son_0': f"Indian two-horse war chariot figurines stuck in deep brown mud after rain, wheels sinking, Greek horsemen charging toward them.",
 'son_1': f"Close-up of a young Indian prince figurine in a small golden turban fallen in the mud beside a stuck chariot wheel, rain puddles.",
 'battle_0': f"{ELEP} charge into a dense block of {PHAL} with pikes lowered, dust rising, dramatic low angle.",
 'battle_1': f"Battle chaos: wounded war elephants turn around and trample {INDI}, dust, fallen figurines.",
 'battle_2': f"Elevated view: Greek cavalry figurines sweep in a wide arc around the flank of the Indian army, dust trails across the diorama plain.",
 'king_0': f"{PURU}, wounded, stands proudly before {ALEX}; {PHAL} around them; golden evening light.",
 'king_1': f"Extreme close-up of {PURU}, head raised with dignity, golden evening light, soft bokeh.",
 'return_0': f"Elevated view of the diorama: a kingdom between two rivers with tiny villages and saffron banners, glowing in golden light.",
 'return_1': f"Tired Greek soldier figurines sit on a riverbank under grey monsoon clouds, banners lowered, pikes lying on the ground.",
 'murder_0': f"Night: {PURU} alone by a small fire in front of a red tent; a dark hooded figurine with a dagger approaches from behind.",
 'legacy_0': f"Close-up of {PURU} riding a richly decorated war elephant, warm sunset light.",
 'legacy_1': f"{PURU} on a decorated war elephant on a hilltop, silhouetted against a golden backdrop; the whole miniature diorama on a wooden table around it.",
}
json.dump({k: B + v for k, v in K.items()}, open('keyframes.json', 'w'), indent=1)
print(len(K))
