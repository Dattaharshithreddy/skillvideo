# Root README Update Proposal

**PROPOSAL ONLY. The root `README.md` has not been changed.** Version 1.0, 2026-11-11.

## The problem

The root `README.md` describes one thing: the **cgi-shorts** skill (Zack D Films-style 3D shorts, Blender or AI video through fal.ai), with install commands that clone the repository into `~/.claude/skills/cgi-shorts`. The repository now also holds the 2D engine, ten cartoon episodes, the cartoon method and a ten-document knowledge base. A newcomer reading the README would not know the cartoons exist, and could conclude that they are made with AI video.

## Does a change conflict with the cgi-shorts workflow?

Checked in the repository:

| Fact | Consequence |
|---|---|
| The cgi-shorts install clones the whole repository into a skills folder and uses the root `SKILL.md` | Adding text to `README.md` does not affect it. `SKILL.md` is what a skill loader reads |
| `scripts/run.py`, `blender/` and root `references/` are used only by cgi-shorts | Not touched by this proposal |
| The cartoon folders (`toon-slapstick/`, `cartoon-animation-director/`) are not referenced by any cgi-shorts script (searched `scripts/` and `blender/`) | No coupling |

So adding a section is safe. **Rewriting or removing the existing cgi-shorts text would not be**, because it is that skill's install guide. I propose adding only.

## Proposed change: insert this block at the top, above the existing text, and change nothing else

```markdown
# skillvideo

This repository holds three separate things. They do not depend on each other.

| Folder | What it is | How pictures are made |
|---|---|---|
| `toon-slapstick/` | The 2D cartoon engine and the **Bheemu & Gaju** episodes | Drawn and animated by our own code on CPU. No AI video generation |
| `cartoon-animation-director/` | The production method for the cartoons: knowledge base, QC tools, checkers, pilot | Not a renderer |
| Repository root (`SKILL.md`, `scripts/`, `blender/`, `references/`) | **cgi-shorts**: Zack D Films-style 3D explainer shorts | Blender, or AI video through fal.ai |

Start here for the cartoons: `cartoon-animation-director/SKILL.md`, then `cartoon-animation-director/knowledge/`.
The rest of this file is the cgi-shorts guide, unchanged.

---
```

The existing heading `# cgi-shorts` and everything under it stay as they are.

## Not proposed

- No change to the root `SKILL.md`.
- No change to `references/models.md`, although its prices and endpoints were not re-checked.
- No move or rename of any folder.

## What I need from Harshith

Approve the block as written, edit it, or decline. One open point: the name in the first heading. I used the repository's name; say if you want another.
