# Licence rules for a monetised channel

Not legal advice: this is what each licence text says. When a source says "check per model", check.

| Licence | Use in monetised reels | Credit | Watch out for |
|---|---|---|---|
| **CC0** (KayKit, Kenney, Quaternius, Poly Haven, Polygonal Mind, MPFB2 output, museum CC0 scans) | Yes | Not required | Nothing. Default to these. |
| **CC BY 4.0** (most Sketchfab downloads, most of Objaverse, many glTF samples) | Yes | **Required**: creator name + source + licence, in the caption or pinned comment | Keep the model's page URL when you download it. |
| **CC BY-SA 4.0** (Z-Anatomy) | Yes | **Required** | If you share a modified version of the *model file*, it must carry the same licence. |
| **CC BY-NC** (some Sketchfab / Objaverse / glTF samples) | **No** for a channel that earns money | - | Filter these out. |
| **GPL / MIT / BSD addons and generators** (Infinigen, Blosm, tree generators, Blender MCP) | Yes | Not required for renders | The licence covers the tool's code. What you render with it is yours. |
| **GPL on model files** (fr24 aircraft) | Unclear how GPL applies to art | - | Prefer another source if the video matters. |
| **No licence file** (pmndrs-market, gn-stylized-scene) | Not granted by default | - | Use only after confirming on the creator's page. |
| **BlenderKit Royalty-Free** | Yes | Not required | You may not resell or redistribute the raw asset. |
| **NASA media** | Yes | Customary: "NASA" | Do not imply NASA endorses the channel; logo use is restricted. |

Also outside the licence: real people, brand logos, and religious imagery carry their own
sensitivities regardless of what the model's licence allows.

`python3 scripts/atlas.py credits` prints the credit lines for everything in `assets/`.
For hand-downloaded CC-BY models, add an entry to `assets/manifest.json` yourself.
