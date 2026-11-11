# Kid hands and catching: reference study (v1.0, 2026-11-11)

Asked for by Harshith: "watch how kids hands fingers and movements are showed in other toons and design the
character that way, he is not catching ball properly here, u can check chota bheem also".
Study only. Nothing below is copied: no character design, outfit, colour scheme or sequence is taken from any show.

## Footage watched (frame by frame, contact sheets in the built-in browser)
- Green Gold Telugu, "Chhota Bheem - Gully Cricket" (youtube.com/watch?v=nI0ceVhcv30): 0:30-9:30 at 36 s steps, then 3:32-4:03 at 2 s steps and single frames at 3:53.5, 3:55.5, 3:57.5, 4:03.5.
- Green Gold TV, "Chhota Bheem vs Keechak - Dholakpur's Cricket Final" (youtube.com/watch?v=PJFKt0mtPDI): 3:20-18:20 at 60 s steps, 4:30-6:46 at 3-4 s steps, a catch at 5:55-6:03 at 0.75 s steps.
- Real children (coaching / motor-development sources): two hands, eyes on the ball, the hands and arms "give" with the ball to soak up its force; beginners trap the ball against the chest with stiff arms.

## What the frames show
1. **Hands are big and simple.** Kid hands are drawn large for the body: a round palm, short thick fingers with round tips, a clear thumb. They read at wide-shot size.
2. **Holding = fingers in front.** A stick or ball passes through the curled hand: the fingers wrap over the FRONT of the object, the palm is behind it, part of the object shows between thumb and fingers (cricket final, 5:57). Same rule as Bheemu (lessons rule 40).
3. **Before a catch the hand opens wide.** Fingers spread and slightly curled, palm toward the ball, arm reaching out to meet it (cricket final, 6:00).
4. **Hands meet the ball in front of the body**, not at the face. After contact the arms sink a little (the give) and then the ball is brought in to the chest.
5. **Gestures are whole-hand**: a hand to the cheek, both hands on the object, never a limp single hand.

## Applied in animatic v007 (approved Chintu model, cast.py unchanged)
- Hands come up early, both open, chest high, out in front; eyes track the ball.
- The ball lands between the palms; the fingers close over the front (same layered redraw as Bheemu's grip: `KidFingersOver` in animatic.py redraws only the finger end of Chintu's own hands, clipped to a disc).
- The arms give with the ball for 4 frames, then the happy bounce.
- Known limit: on twos the hands close one frame before the ball arrives.

## Proposed (REVIEW ONLY, not applied)
- Hands drawn 17% bigger (hand scale 11.5 -> 13.5) on the redesign options: `storyboard/chintu_redesign_options.png`.
