# Lessons learned and change log

Rules marked **confirmed** came from Harshith's own corrections or approvals and are binding.
Rules marked **experimental** are ideas being tested; do not treat them as standards yet.

## Confirmed rules

| # | Date | Rule | Where it came from |
|---|---|---|---|
| 1 | 2026-11-09 | Push every successful render to GitHub immediately. | Renders were lost when a server was replaced. |
| 2 | 2026-11-10 | Limbs are drawn as anatomy, never as attached geometric shapes. Paws have toes, hands have four fingers and a thumb, arms have elbows, legs have knees. | "hands and legs are shapes", "why you attach geometrical shapes like hexagon" |
| 3 | 2026-11-10 | Change only what was asked. Keep an approved face, body or design untouched when fixing something else. | "Dont change face. Only change is hands and legs and fingers" |
| 4 | 2026-11-10 | Show a drawing sheet and get it looked at before animating a new or changed character. | Several rounds of redrawing the panda. |
| 5 | 2026-11-10 | When a reference image is given, match its shapes and proportions, not a personal idea of the subject. | "Match the image. In ur image is like toy." |
| 6 | 2026-11-10 | Series is Bheemu (panda) and Gaju (baby elephant). Friends, not enemies. Telugu small-town home. Vertical 9:16. | Naming and format decisions. |
| 7 | 2026-11-10 | Silent comedy. No speech bubbles, no boards held by characters, no captions. | "No dont use bubbles", "Create normal video only like 1st one" |
| 8 | 2026-11-10 | Telugu text appears only as scenery: walls, posters, notices, shop boards, banners, the auto. Lines are original and funny. | "Dialogues come in walls or posters ... not like characters talking" |
| 9 | 2026-11-10 | Animals never talk. Only humans (Ammamma, Chintu) may speak, with generated Telugu voice. | "If anyone speaks it should be humans" |
| 10 | 2026-11-10 | Do not change episode 1. | "Dont change first video" |
| 11 | 2026-11-11 | Ten quick episodes with two or three poses per action are not acceptable quality. Hands, expressions and movement must carry the action. | "Its basic, not looking real at all" |
| 12 | 2026-11-11 | Study how the action is staged in classic theatrical cartoons before animating it (for example how a cat drinks milk). | "Check how cat drink milk in tom and jerry" |

## Experimental (being tested)

| # | Date | Idea | Status |
|---|---|---|---|
| E1 | 2026-11-11 | Line boil: ink lines wobble every 3 frames (`Stage.boil = True`) for a hand-drawn feel. | In the milk acting test; not yet judged by Harshith. |
| E2 | 2026-11-11 | AI in-betweening (ToonCrafter, Wan 2.2 first-last-frame) between engine key poses. | Key frames prepared; not yet run. |
| E3 | 2026-11-11 | Close shots and step-by-step entrances (paw, paw, ears, eyes). | In the milk acting test. |
| E4 | 2026-11-10 | Free Telugu voice (AI4Bharat Indic-TTS); Chintu is the female voice pitched up. | Used in episodes 2-10; Harshith has not confirmed how it sounds. |

## Known failures to avoid repeating

- A character's head sliding away from the body when leaning (stretched neck). Move the body with the head.
- Characters cut off at the frame edge or hidden behind each other. Check on the contact sheet.
- Background elements that should move (a tree being shaken) painted into the static background.
- Passing the same keyword twice into a pose call (crashes the render).
- Reporting work as done from a contact sheet alone. Sheets show poses, not motion.

## Findings from our own exercises

| Date | Finding | Action |
|---|---|---|
| 2026-11-11 | Lesson 1: Bheemu's torso cannot bend, so poses have no line of action; sitting and running do not read as silhouettes (7/12). | Add spine bend, a drawn sitting pose, real run poses; forbid mirrored key poses. |
| 2026-11-11 | Automatic check of episode 7: about 58% of frames are still (our measurement of a classic chase cartoon was about 14%). | Our episodes hold too long with too little life; add moving holds and more acting. |

## Change log
- 2026-11-11: added findings from Lesson 1 and the first automatic video check.

- 2026-11-11: file created from the corrections in the first production run (episodes 1-10, acting test).
