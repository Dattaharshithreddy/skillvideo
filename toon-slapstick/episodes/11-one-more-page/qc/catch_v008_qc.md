# QC report: Chintu's catch, animatic v008 (S9, film frames ~576-620)

Made with the cartoon-animation-director workflow (A-H) and QC rubric. Animatic, not animation.

## A-E plan
- **A. Analysis.** Chintu wants his ball back. Bheemu lobs it underhand. A cricketer takes a ball below the chest
  with a "reverse cup": squared up, knees soft, both hands low in front of the body, elbows out, fingers down,
  little fingers together, eyes on the ball into the hands, then the hands ride down with it.
- **B. Timing.** Square up 4 f (b0+36); eyes up with the arc (b0+48) and down into the hands (b0+55); ball on ONES;
  contact b0+61 on a drawn (even) frame; give 4 f 'out'; bring to chest 5 f; happy bounce 3 f over + 4 f settle.
- **C. Keys.** Ready cup / contact (fingers closed over the front) / give (lowest, knees bent) / ball at chest / happy.
- **D. Path.** The ball's arc ends beside him at hand height, then travels the last 3 frames sideways into the palms,
  so it never passes in front of his face.

## Problems found and fixed (v007 -> v008)
| Observed issue | Where | Cause | Fix | Scope |
|---|---|---|---|---|
| Hands crossed over each other | v007 catch | profile view (face -1): the near arm reaches across the body | squared up to face -0.2, elbows-out bend (+0.6), hands in front of his own belly | local; rule 42 |
| Hands blended into Gaju's ear | v007 catch | hands reached left over Gaju's ear (staging, rule 3: nothing important behind something) | Chintu stands at x 1185 (was 1140); hands stay in front of his body; Gaju's ear flare removed in the last lean | local; rule 42 |
| Ball crossed his face on the frame before contact | first v008 try | arc dropped through the face; ball held on twos | ball always on ones; last 3 frames come in sideways at hand height | local |

## What was inspected
- Contact sheets of engine frames for the catch (t = b0+36 to b0+88) and stills of S9 start to end: done.
- Frames 580-595 pulled from the rendered v008 MP4: done; ball comes in from the side, lands in the palms, fingers close.
- Full-speed viewing and sound: NOT done (Claude cannot watch at speed or hear). Harshith.
- Automatic: qc_frames PASS, check_keys no findings, protected files unchanged.
