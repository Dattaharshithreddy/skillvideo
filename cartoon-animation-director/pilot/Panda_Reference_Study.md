# Panda Reference Study

Version 1.0, 2026-11-11. Asked for by Harshith: study real pandas and an animated film panda frame by frame before changing Bheemu's acting again.

## How it was done

In the built-in browser, each video's own player was paused and stepped by setting its time directly, usually every 0.25 to 0.5 seconds, and in places every 0.4 seconds through a single movement. Frames were laid out as contact sheets in the browser and inspected there. **No frame was saved into this repository**: the footage belongs to its owners. Below are observations in my own words.

| Video | What was stepped through |
|---|---|
| Real panda eating bamboo, sitting (YouTube `1lmHyX4BnEg`, 1:14) | 2 to 46 s at 4 s, then 34 to 38 s at 0.5 s and 36.2 to 37.8 s at 0.2 s |
| Close-ups of a giant panda (YouTube `k-7_sWrR1rk`, 7:14) | Whole video at 30 s; 125 to 130.6 s at 0.4 s (one feed-to-mouth movement); 186 to 224 s at 1 s (moving on a log) |
| Nat Geo Wild, "Giant Pandas 101" (YouTube `dqT-UlYlg1s`, 4:31) | Whole video at 8.8 s; 80 to 85.5 s at 0.5 s (walking); 115 to 120 s (head-down foraging) |
| Kung Fu Panda, official trailer 1 (YouTube `PXi3Mv6KMzY`, 2:09) | Whole trailer at 4 s; 66 to 73 s at 0.75 s and 70.2 to 71.4 s at 0.4 s (holding a staff); 118 to 126 s (walking, carrying) |

Searching YouTube for more videos stopped working partway through: result pages loaded empty. So the film was studied from one trailer only, not from several clips.

## What real pandas do

**Holding.** The paw is a big rounded mitt with short toes buried in fur. To hold bamboo it closes like a fist: the stalk lies across the palm, the toes curl over the front of it, and the stalk sticks out on both sides of the paw. A wrist pad (the "false thumb") stops it sliding out; the paw does not pinch with separate fingers.

**Eating.** The paw lifts the food close to the chin and mostly stays there. The **head turns and tilts to the food**, and the panda chews from the side of the mouth. The arm moves less than you would expect.

**Sitting.** The typical pose is on the rump, back leaning on something, hind legs splayed forward, belly showing, food held in front of the chest with both paws. It looks relaxed and heavy.

**Walking.** Slow and rolling, head low, front feet turned in, weight shifting side to side. Real pandas walk on all fours.

**Overall.** Everything is unhurried and heavy, with long still moments and small adjustments.

## What the animated film does

**Holding.** The same principle as the real animal, made clearer. A stylised panda holding a staff closes a fist around it; the staff is visible on both sides of the paw, the short fingers curl over its front, and the forearm comes into the fist from the side, so you always see the arm reaching the object.

**Weight.** Big round body, short legs, wide stance, elbows out. Movements start with the belly.

I noted principles only. Nothing of that character's design, poses or gestures is to be copied (lessons learned 18 and 32).

## What this changes for Bheemu

| Finding | Applied in animatic v006 | Not applied |
|---|---|---|
| The object passes through a closed fist; fingers in front, palm behind | Yes. The arm and palm are drawn behind the book; only the finger end of Bheemu's own approved paw is drawn again in front, clipped to a small disc, so the fingers curl over the cover's edge. Same for the ball when he holds it | |
| The forearm should be seen reaching the object | Yes. The paws now sit on the book's outer edges, so the forearm shows beside the book and the fist straddles the edge | |
| The head goes to the food; the arm moves little | | No eating in this pilot |
| Pandas read and eat sitting back on the rump | | **Proposal only.** Bheemu reading sitting back against the wall, book on his belly, would be far more panda-like. It changes the staging of five shots, and lessons learned (lesson 1) says his sitting pose does not yet read well, so it needs your decision |
| Slow, heavy, rolling movement; long still moments | | Applies at detailed animation, after the animatic gate |

## Engine note

The engine draws a prop wholly in front of or wholly behind a character. The layered grip in v006 is done inside the pilot's own file by clipping the approved paw drawing; `chars.py` is not changed. If you accept it, the proper home is the engine: "a held object sits between the palm and the fingers". That would be a proposal for your approval, not something to build silently.
