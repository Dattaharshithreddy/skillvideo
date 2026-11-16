# What do I need? -> where to get it

First choice is listed first. "fetch" = `python3 scripts/atlas.py fetch <id>`.

| Subject | Stylised / low-poly | Realistic | Notes |
|---|---|---|---|
| **Trains, wagons, track** | Kenney *Train Kit*; Quaternius *Modular Trains* (both CC0, manual download) | BlenderKit search "locomotive"; Sketchfab (check licence per model) | No good train pack lives on GitHub. Real track routes: Blosm imports railways from OpenStreetMap. |
| **Humans (any age/build)** | fetch `kaykit-adventurers`; Quaternius *Animated Men/Women*, *Posed Humans* | **MPFB2** - generate, dress, rig | MPFB2 output is CC0 and scriptable, so it is the base for recurring characters. |
| **Kings, queens, soldiers** | fetch `kaykit-adventurers` (knight, barbarian, mage); Quaternius *Animated Knight*, *RPG Characters* | MPFB2 body + your own costume/crown; Sketchfab CC0 museum statues for stone/bronze royals | **Gap:** there is no free ready-made Indian king/queen set. Build once (MPFB2 + clothes, or an AI model generator) and reuse. |
| **Temples, statues, idols, artifacts** | Polygonal Mind `tomb-chaser-1` (Egypt), `tomb-chaser-2` (pagoda), `lunar-year` | Sketchfab CC0 heritage (e.g. Minneapolis Institute of Art Chola bronzes); Smithsonian Open Access | Filter Sketchfab by Downloadable + CC0. Other Sketchfab models are usually CC-BY: credit required. |
| **Castles, forts, medieval towns** | fetch `kaykit-medieval`; Quaternius *Medieval Village MegaKit*; Kenney *Castle Kit* | BlenderKit | |
| **Modern buildings, city streets, cars** | fetch `kaykit-city`; Kenney *City Kits*, *Car Kit* | **Blosm** (real city from a place name); Building Tools (procedural) | |
| **A real location** (town, ghat road, river) | - | **Blosm** (buildings, roads, rail, rivers) + **BlenderGIS** (real elevation + satellite image) | This is how to do "fly from A to B over real terrain". |
| **Hills, mountains, terrain** | fetch `kaykit-medieval` (hill and mountain pieces) | BlenderGIS (real DEM); A.N.T. Landscape (built into Blender extensions); Infinigen | |
| **Rocks, boulders, cliffs** | Quaternius *Stylized Nature MegaKit* | `atlas.py polyhaven search rock`; Blender Extra Mesh Objects rock generator | Poly Haven rocks are photoscans with 8k textures: pick `--res 2k` for reels. |
| **Trees, plants, grass, forest** | Quaternius *Stylized Nature MegaKit*; `gn-trees` | Modular Tree; tree-gen; Poly Haven plants; Infinigen whole forests | |
| **Skies and lighting** | - | `atlas.py polyhaven search <mood> --type hdris` | One HDRI = instant believable lighting. |
| **Ground, wall, rock materials** | - | Poly Haven textures; BlenderKit materials | |
| **Human anatomy (organs, bones, vessels)** | - | fetch `z-anatomy` (whole body, labelled) | CC BY-SA 4.0: credit Z-Anatomy in the caption. |
| **Drugs, proteins, receptors, DNA** | - | Molecular Nodes (loads real PDB structures) | |
| **Neurons, brain cells** | - | NeuroMorphoVis | |
| **Space, rockets, satellites, astronaut** | fetch `kaykit-space` | fetch `nasa` | |
| **Aircraft** | fetch `fr24-aircraft` (GPL-2.0, read LICENSES.md) | BlenderKit | |
| **Animals, creatures** | Quaternius *Farm Animals*, *Dinosaurs*; Polygonal Mind `xyz` | Infinigen creatures; Smithsonian fossils | |
| **Rooms, furniture, kitchens, food** | fetch `kaykit-furniture`, `kaykit-restaurant`, `pmndrs-market` | Infinigen Indoors; Poly Haven props | |
| **Egypt / Japan / park / station sets** | fetch `polygonal-mind --set tomb-chaser-1 / tomb-chaser-2 / momuspark / transit` | - | |
| **Character animation clips** | Quaternius *Universal Animation Library* (CC0); KayKit characters ship with clips | MPFB2 + Rigify | |
| **Anything else** | 3dassets.dev search | BlenderKit, then Objaverse filtered to CC0/CC-BY | Last resort: generate it. |

## Do not mix styles in one reel

Low-poly packs (KayKit, Kenney, Quaternius) match each other. Photoreal sources (Poly Haven,
MPFB2, Infinigen, scans) match each other. A scanned rock next to a KayKit castle looks wrong.
Pick one column per video.
