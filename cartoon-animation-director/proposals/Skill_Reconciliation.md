# Skill Reconciliation Proposal

**PROPOSAL ONLY. Neither file has been changed, replaced or installed.** Version 1.0, 2026-11-11.

Compares the existing `cartoon-animation-director/SKILL.md` (written before the knowledge base, about 520 words) with `cartoon-animation-director/knowledge/Animation_Skill.md` (written as document 10, about 1,900 words), and recommends one final structure.

## 1. What each file contains

| Topic | Existing `SKILL.md` | `Animation_Skill.md` |
|---|---|---|
| Front matter (`name`, `description`) | Yes | Yes; same name, longer description |
| Says the engine is the separate `toon-slapstick` skill | Yes | Yes |
| Setup commands (clone, install) | No | Yes |
| Read-first list | `references/09`, `04`, `07`, then `01 03 05 06 08` | `references/09`, the decision register, then a job-to-document table for `knowledge/` |
| The A to H action workflow | Yes | Yes, with "contacts on an even engine frame" and "per-frame table" added |
| Staging rules from real mistakes (five) | Yes, as their own section | Folded into "Method" in shorter words |
| Workflow selector (which process for which request) | No | Yes |
| Content rules (silent, no bubbles, animals never talk, friends, imitation test, episode 1) | No (they live in lessons learned) | Yes |
| Protected paths and what needs approval | No | Yes |
| Review branch rules | No | Yes |
| Stop conditions | No | Yes |
| Drift check command | No | Yes |
| The four gates | No | Yes |
| Validation commands | Tools section only | Yes |
| Honesty rules | Yes (four) | Yes (eight) |
| Reporting format | No | Yes |
| What to do when Harshith corrects something | Yes | Yes, plus the decision register |
| `qc_frames.py assemble` | Yes | **Missing** |
| `new_episode.py` | Yes | Yes |

## 2. Missing from both

| Missing | Why it matters |
|---|---|
| The read-only checkers built on 2026-11-11 (`check_keys.py`, `check_safe_area.py`, `check_docs.py`, `check_protected.py`, `check_audio.py`) | They are now the fastest validation |
| Decision: generative video tools are optional; the engine is the primary workflow | Approved 2026-11-11 |
| Decision: no audio or voice is approved until heard in actual episode output; audio review is part of pilot acceptance | Approved 2026-11-11 |
| Decision: the pilot uses approved production assets and existing controls; restage instead of waiting for review assets | Approved 2026-11-11 |
| The pilot's location (`pilot/Pilot_Plan.md`, `toon-slapstick/episodes/11-one-more-page/`) | Current work |
| The `proposals/` folder and its rule (proposals are separate from approved material) | New |
| The master mission text is not in the repository | A dependency a fresh session cannot see |
| How `references/01` to `06` relate to `knowledge/` 01 to 09 | Two sets of documents cover overlapping ground |

## 3. Conflicts

| # | Conflict | Recommended resolution |
|---|---|---|
| 1 | Two read-first lists that point at different folders | `knowledge/` is the primary source for method. `references/07` (rubric), `08` (pilot spec) and `09` (lessons learned) stay live. `references/01` to `06` stay as short handbooks, each with one line at the top pointing to the fuller knowledge document; none is deleted |
| 2 | `Animation_Skill.md` says `api.md` has the wrong stage size | No longer true: `api.md` was corrected on 2026-11-11. Remove that sentence |
| 3 | `Animation_Skill.md` section 2 tells every session to read the Bible's register; the existing file does not | Keep it. The register is where approvals live |
| 4 | Two files with the same `name` in one repository | Only one may be the Skill. See section 4 |
| 5 | The existing file's five staging rules are in Harshith's corrections' own words; the new file paraphrases them | Keep the original five, verbatim, as their own section |
| 6 | `knowledge/` is described as documentation, but `Animation_Skill.md` is an instruction file, not a knowledge document | Move the final Skill text out of `knowledge/` (section 4) |

Not a conflict but worth knowing: the `toon-slapstick` skill installed in Harshith's Claude account is older than the copy in the repository. The installed text still uses the earlier character names (Pandu, Gajju) and an earlier episode path. This proposal does not touch it.

## 4. Recommended final structure

**One Skill file: `cartoon-animation-director/SKILL.md`.** The project's actual format is a folder with a `SKILL.md` that has `name` and `description` front matter (`toon-slapstick/SKILL.md` and the root `SKILL.md` follow it).

Proposed contents, in order, about 2,000 words:

1. Front matter. Description kept under 200 characters.
2. What this skill is, and that the engine is `toon-slapstick`.
3. Setup.
4. Read first: lessons learned; decision register; then the job-to-document table.
5. Choose the workflow (the selector table).
6. The A to H action workflow (the fuller version).
7. **Staging rules from real mistakes: the five original rules, unchanged.**
8. Standing content and method rules.
9. Protected paths, approvals, review branch, proposals folder, stop conditions.
10. Character consistency and the drift check.
11. The four gates. Add: the animatic is reviewed before detailed animation; audio is reviewed by ear at the candidate gate.
12. Validation: the existing commands **plus the five checkers and `qc_frames.py assemble`**.
13. Decisions of 2026-11-11: engine primary and generative tools optional; no audio approved until heard; pilot on approved assets.
14. Honesty rules; reporting format; corrections; repository practice.
15. Known dependency: the master mission text is not in the repository.

**Then:**

- `knowledge/Animation_Skill.md` becomes a three-line pointer to `SKILL.md`, so that two copies cannot drift apart. Document 10 stays in the knowledge base as an entry, not as a second Skill.
- The previous `SKILL.md` is kept in Git history; nothing is lost.
- Installing the Skill into Harshith's Claude account is a separate step, done only when he asks.

## 5. Alternatives

| Option | For | Against |
|---|---|---|
| **A. Merge into `SKILL.md`, pointer in `knowledge/` (recommended)** | One source; correct folder for a Skill | One more edit to a document-10 file |
| B. Keep both; `SKILL.md` short, pointing to `Animation_Skill.md` for detail | Smallest change to `SKILL.md` | A session that loads only `SKILL.md` gets the thin version; two files to keep in step |
| C. Replace `SKILL.md` with `Animation_Skill.md` as it is | Fastest | Loses `assemble` and the verbatim staging rules; keeps the stale `api.md` sentence; omits today's decisions and the checkers |

## 6. What I need from Harshith

1. Choose A, B or C.
2. Confirm that `references/01` to `06` should stay, with a pointer line added to each.
3. Say whether the Skill should also be installed in your Claude account, and when.

Until then both files stay exactly as they are.
