# Phone Safe Area: Investigation

**Status: evidence insufficient to change any staging. Nothing has been changed.** Version 1.0, 2026-11-11.

## Question

Does the phone player's interface cover our characters?

## What was done

- The camera helper was read: `Show.shot` keeps the floor 360 px above the bottom edge of the 1080 x 1920 picture at any zoom.
- `tools/check_safe_area.py episode` computed where each character stands in episode 2 ("Mango Season"), from poses and camera. This is arithmetic.
- `tools/check_safe_area.py overlay` took four frames from the **actual rendered file** of episode 2 in the repository and drew two sets of margins over them. The two pictures are beside this file.

## What the published margin figures say

They are unofficial and disagree: bottom 300 to 672 px, top 120 to 380, right 96 to 192, left 40 to 60 (`Storyboard_and_Cinematography.md` 2.4).

## Results for episode 2 (measured)

| Margins assumed | Bheemu: worst share of body under the bottom band | Gaju | Bujji | Ammamma |
|---|---|---|---|---|
| Largest quoted (top 288, bottom 672, right 192) | 85% | 100% | 100% | 59% |
| Middle (top 180, bottom 390, right 100) | 8% | 13% | 11% | 6% |
| Smallest quoted (top 120, bottom 300, right 96) | 0% | 0% | 0% | 0% |

- `safe_area_ep02_largest_quoted_margins.png`: under the largest figures, the small characters stand entirely in the covered band and the faces of the tall ones are just clear.
- `safe_area_ep02_smallest_quoted_margins.png`: under the smallest figures, everything is clear.

The pilot animatic gives the same pattern, because it uses the same camera helper.

## Conclusion

The answer depends completely on which margin is real, and no source I found is official. **A device check is still required.** One look at any existing episode in the real Shorts player, with a screenshot, settles it.

## If the device check shows a problem (proposals only)

| Option | What changes | Touches |
|---|---|---|
| A. Raise the floor line in new episodes' shots (use the `up` argument of `Show.shot`) | Staging of new work only | Episode files only; no engine change |
| B. Frame closer, so the cast sits higher in the picture | Shot plan | Episode files only |
| C. Change `Show.cy` so the floor is higher by default | Every episode that uses it | Engine file: needs approval and regression |

Existing episodes would not be changed in any option without a separate decision. Episode 1 is not to be changed.
