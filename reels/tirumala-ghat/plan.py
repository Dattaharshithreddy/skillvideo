import json
L = [
 ("Every day, a river of buses and cars climbs these hills to Tirumala, on a road built more than eighty years ago.",
  "Every day, a river of buses and cars climbs these hills to Tirumala... on a road built more than eighty years ago.", ["Tirumala,", "eighty"], "open"),
 ("And here's the strange part. This old road survives every monsoon, while the newer road beside it keeps breaking.",
  "And here's the strange part. This old road survives every monsoon... while the newer road beside it keeps breaking.", ["survives", "breaking."], "two_roads"),
 ("Before 1944, there was no motor road here. Pilgrims walked, or rode bullock carts up a winding track.",
  "Before nineteen forty-four, there was no motor road here. Pilgrims walked, or rode bullock carts, up a winding track.", ["1944,", "bullock"], "cart_track"),
 ("The plan for a motor road is credited to Sir M. Visvesvaraya, India's legendary engineer. Engineer A. Nageswara Iyer led the work, and Gannon Dunkerley built it.",
  "The plan for a motor road is credited to Sir M. Visvesvaraya, India's legendary engineer. Engineer A. Nageswara Iyer led the work, and Gannon Dunkerley built it.", ["Visvesvaraya,", "Iyer"], "people"),
 ("Their smartest decision? They didn't fight the mountain. They followed the old cart track, keeping the slope gentle all the way up.",
  "Their smartest decision? They didn't fight the mountain. They followed the old cart track... keeping the slope gentle, all the way up.", ["fight", "gentle"], "lay_road"),
 ("Going straight up would be far too steep for any vehicle.",
  "Going straight up, would be far too steep for any vehicle.", ["straight", "steep"], "straight"),
 ("So wherever the hill turns steep, the road folds back on itself. Hairpin bends. The road gets longer, but every stretch stays gentle.",
  "So wherever the hill turns steep, the road folds back on itself. Hairpin bends. The road gets longer... but every stretch stays gentle.", ["Hairpin", "longer,"], "hairpins"),
 ("Opened in 1944, this one road carried every vehicle, up and down, for thirty years.",
  "Opened in nineteen forty-four, this one road carried every vehicle, up and down, for thirty years.", ["1944,", "thirty"], "traffic"),
 ("In 1974, a second road opened for the climb. But between kilometre eleven and seventeen, it was cut steeply through the rock.",
  "In nineteen seventy-four, a second road opened for the climb. But between kilometre eleven and seventeen, it was cut steeply through the rock.", ["1974,", "rock."], "second_road"),
 ("That cut left fractured rock behind. In heavy rain, boulders fall, and the road has to close.",
  "That cut left fractured rock behind. In heavy rain, boulders fall... and the road has to close.", ["fractured", "close."], "rockfall"),
 ("The old road, laid along the hill's own path, keeps running.",
  "The old road, laid along the hill's own path... keeps running.", ["old", "running."], "old_runs"),
 ("Same hills. Two roads. Great engineering works with nature, not against it.",
  "Same hills. Two roads. Great engineering works with nature... not against it.", ["nature,"], "finale"),
]
lines = [{"text": t, "tts": s, "keywords": k, "shot": sh, "audio": f"audio/l{i+1:02d}.wav"} for i, (t, s, k, sh) in enumerate(L)]
json.dump({"gap": 0.05, "lines": lines}, open('brief/plan.json', 'w'), indent=1, ensure_ascii=False)
print(len(lines), sum(len(l['tts'].split()) for l in lines))
