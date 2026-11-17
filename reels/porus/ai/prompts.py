"""Clip prompts for the AI miniature version (Wan 2.2 TI2V-5B). One list of clips per narration shot.
Every prompt gets the same style prefix so the whole reel reads as one handcrafted tabletop diorama."""
import json
STYLE = ""
NEG = ("cartoon, anime, 2D, illustration, real people, modern objects, text, subtitles, watermark, logo, "
       "oversaturated, yellow tint, green tint, red tint, color cast, washed out, grey sky, empty sky, black background, dark empty background, underexposed, too dark, tiny distant figures, "
       "blurry subject, low quality, jpeg artifacts, deformed, extra limbs, distorted faces, static image, frozen, jerky motion, flicker, morphing")
KF = json.load(open('ai/keyframes.json'))
MOTION = {
 "open_0": "The soldiers march steadily toward the camera, pikes swaying; slow dolly back.",
 "open_1": "He slowly raises his hand; his red cloak moves; slow push-in.",
 "open_2": "The water ripples and flows; the elephants sway their trunks; slow glide over the water.",
 "demand_0": "The messenger's horse trots up and stops; the king turns his head; slow push-in.",
 "ambhi_0": "The gates swing open and the purple-robed king bows low; slow push-in.",
 "ambhi_1": "The soldiers and elephants march out steadily; slow pan.",
 "river_0": "The brown water flows fast; flags flutter; slow lateral pan.",
 "river_1": "The horses rear up and toss their heads; handheld feel.",
 "feint_0": "The horsemen gallop past with flickering torches, flames trailing; tracking shot.",
 "feint_1": "Firelight flickers, soldiers slowly lie down, smoke drifts; slow push-in.",
 "storm_0": "Rain pours, lightning flashes, the boats glide across; slow push-in.",
 "storm_1": "The soldiers wade forward slowly through the water, mist drifting; slow tracking.",
 "son_0": "Wheels spin in the mud, horses strain, horsemen charge in; slow push-in.",
 "son_1": "Rain drops hit the puddles; very slow push-in.",
 "battle_0": "The elephants charge forward, dust billows, pikes thrust; low tracking shot.",
 "battle_1": "Elephants turn and stampede, dust clouds swirl; shaky tracking.",
 "battle_2": "The cavalry gallops in an arc, dust trails grow; slow aerial drift.",
 "king_0": "The tall king lifts his chin; the horse shifts; slow push-in.",
 "king_1": "He slowly raises his head; very slow push-in, soft bokeh shifts.",
 "return_0": "Banners flutter gently, light glows warmer; slow aerial drift.",
 "return_1": "Soldiers sit still, one lowers his head, clouds drift; slow pan.",
 "murder_0": "The fire flickers, the hooded figure creeps closer, then the fire dies down; slow push-in.",
 "legacy_0": "The elephant sways and walks slowly; slow orbit.",
 "legacy_1": "The camera slowly pulls back to reveal the whole diorama on the table."
}
ORDER = ["open_0", "open_1", "open_2", "demand_0", "ambhi_0", "ambhi_1", "river_0", "river_1", "feint_0", "feint_1", "storm_0", "storm_1", "son_0", "son_1", "battle_0", "battle_1", "battle_2", "king_0", "king_1", "return_0", "return_1", "murder_0", "legacy_0", "legacy_1"]
C = {}
for k in ORDER:
    shot = k.rsplit('_', 1)[0]
    C.setdefault(shot, []).append((KF[k].replace('Vertical 9:16 photograph', 'Vertical 9:16 macro video') + ' ' + MOTION[k]))
clips = []
for shot, ps in C.items():
    for k, pr in enumerate(ps): clips.append({'id': f'{shot}_{k}', 'shot': shot, 'prompt': pr})
json.dump({'neg': NEG, 'clips': clips}, open('ai/prompts.json', 'w'), indent=1)
print(len(clips), 'clips')
