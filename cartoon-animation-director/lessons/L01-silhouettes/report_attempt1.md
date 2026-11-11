# Lesson 1, attempt 1: silhouettes (2026-11-11)

**Exercise:** six Bheemu key poses, colour and silhouette. File: `L01_silhouettes_attempt1.png`.
**Inspected:** the still sheet, by Claude. Not yet reviewed by Harshith.
**Pass mark:** 10 of 12. **Score: 7 of 12. Not passed.**

| Pose | Score | What the silhouette says | Problem |
|---|---|---|---|
| 1 neutral | 2 | A bear standing | Fine as a rest pose, but perfectly mirrored |
| 2 reach up | 2 | Reaching or waving | Torso stays upright; the body does not join the reach |
| 3 wind-up to pull | 1 | Leaning and pointing | One arm is lost inside the body; nothing says "pull" |
| 4 shock | 1 | Arms out, could be a hug | Mirrored left and right (twins); no line of action |
| 5 sitting dazed | 0 | A short standing bear | Legs merge into the body; "sitting" cannot be read |
| 6 run | 1 | Leaning with arms out | Legs are a blur blob; no stride |

## Causes

1. **The torso is one rigid shape.** It can tilt but not bend, so no pose has a curved line of action. This is the engine, not the posing.
2. **Sitting was made by hiding the legs**, not by drawing a sitting pose.
3. **Poses were keyed symmetrically.**
4. **The run uses a spinning-legs blur** even in a still key pose.

## Corrections (scope: global, the Bheemu and Gaju models)

1. Add a spine bend to the body so the chest and hips can curve (C and S lines of action).
2. Draw a real sitting pose: legs forward or to one side, visible outside the body outline.
3. Rule: left and right limbs never share the same offsets in a key pose.
4. Run key poses use real leg positions (contact, passing, push-off); the blur is only for 1-3 frame zips.

**Next:** make these four changes, repeat the exercise as attempt 2, and show Harshith both sheets side by side.
