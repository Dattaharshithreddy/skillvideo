# Engine reference

Stage is 1920x1080, y grows downward, floor line `GROUND = 900`, 24 fps. Positions are world pixels;
an actor's `(x, y)` is the point between its feet.

## Skeleton of an episode

```python
from toon import Stage, GROUND
from chars import Momo, Gullu
from scene import Painted, kitchen, Prop, table, puffs, stars, iris, title_card
from acting import take, zip_off, walk, arc, squash, blink, look, bob
from sound import Score, xylo, pizz

st = Stage(480, bg=Painted(5800, kitchen))   # 480 frames = 20 s
sc = Score(480)
momo = Momo(x=700, z=3); gullu = Gullu(x=1400, z=2)
st.add(momo, gullu)

momo.move(24, 28, 'snap', yaw=0.8, pupil=(0.8, 0))     # frames 24-28: snap the head right
f = take(st, momo, 40)                                 # helpers return their end frame
sc.music(0, 240, 'calm'); sc.hit(43, 'timp')

st.sheet([24, 28, 40, 45, 52], 'check.png')            # look before rendering
st.render('out.mp4', audio=sc.write('audio.wav'), scale=0.5)
```

## Timeline (every actor, prop and the camera)

- `a.move(f0, f1, ease, **params)` hold until `f0`, arrive at the new values on `f1`.
- `a.set(f, **params)` instant change on frame `f`.
- `a.value(name, f)` read a parameter at a frame.
- `a.attach(f0, f1, other, anchor, dx, dy)` ride on another actor's anchor (a prop in a hand).
- `st.probe(f, actor, anchor)` world position of an anchor at a frame, for aiming things.

Eases: `lin`, `in` (falls), `out` (rises, arrivals), `io` (calm acting), `snap` (cartoon snap),
`over` (overshoot and settle), `elastic` (jelly settle), `antic` (pull back first), `bounce`, `step`.

Common parameters: `x y rot sx sy alpha z show`. `z` sets draw order (higher is in front).

## Character pose parameters (`chars.py`)

| Parameter | Meaning |
|---|---|
| `face` | body turn, -1 left, 0 front, 1 right |
| `yaw`, `pitch` | head turn and nod, -1..1 (face features slide round the head) |
| `head_dx head_dy head_rot head_sx head_sy` | head offset, tilt, squash |
| `eye_open` | 0 closed, 1 normal, 1.3 wide. `happy=1` makes closed eyes smile |
| `eye_pop`, `pupil_s` | eye size and pupil size (pop 1.5 + small pupils = shock) |
| `pupil` | `(x, y)` gaze, -1..1 |
| `lid` | upper lid drop 0..1 (sleepy, suspicious) |
| `brow`, `brow_ang`, `brow_asym` | lift in px, tilt in degrees (+ angry, - sad), one-brow raise |
| `mouth_w`, `mouth_open`, `smile` | width factor, open 0..1, smile -1..1 |
| `cheeks` | full cheeks 0..1 (chewing) |
| `armL`, `armR` | hand offset `(dx, dy)` from the rest position; `bendL/R` elbow bow |
| `handL`, `handR` | `'mitt'`, `'fist'`, `'open'`, `'point'` (Momo) |
| `step`, `stride`, `wheel` | walk phase in cycles, stride px, `wheel=1` for the run blur |
| `footL`, `footR` | extra foot offset `(dx, lift)` |
| `sweat` | 1 shows sweat drops |
| Momo only | `glasses_dy`, `glasses_rot`, `scarf_fly` |
| Gullu only | `ear` (-1 folded .. 1 up; alternate for flapping), `trunk` (tip offset from its root), `trunk_bend`, `trunk_curl`, `cap_dy` |

Anchors published each frame: `handL handR head top mouth belly`, and `trunk` for Gullu.

## Acting helpers (`acting.py`)

`blink`, `look`, `bob` (bounce to the beat), `walk` (returns footfall frames), `arc` (thrown object),
`squash`, `take`, `shake` (vibrate), `scramble`, `zip_off`, `chew`, `flap` (returns flap frames).

## Scene (`scene.py`)

- `Painted(width, paint_fn)` background painted once, then panned by the camera. `kitchen` is the example.
- `Prop(draw_fn, **params)` any object; `draw_fn(g, pose, f)` draws around (0,0) and may return anchors.
  Included: `table`, `plate`, `dosa`, `pan`, `book`, `fridge`.
- Effects: `puffs` (dust), `stars` (impact), `zip_lines`, `marks` (surprise ticks).
- Screen overlays: `iris(st, f0, f1, cx, cy)`, `title_card(st, f0, f1, title, sub)`.
- Camera: `st.cam.move(f0, f1, ease, x=, y=, zoom=)`, `st.shake(f, amount, frames)`,
  `st.cut(f, x=, y=, zoom=)` for a hard cut (prevents smears across the cut).

## Sound (`sound.py`)

- `sc.music(f0, f1, mood)` with moods `calm`, `sneak`, `chase`, `sweet`.
- `sc.hit(f, name, v)` effects: `bonk crash whoosh zip munch gulp pop flap sniff skid boing wah tada timp cymbal`.
- `sc.note(f, instrument, midi_note, seconds, v)` instruments: `xylo pizz reed brass`.
- `sc.slide(f, note0, note1, frames)` slide whistle. `sc.steps(...)`, `sc.run(...)` for footsteps and scale runs.
- `sc.duck(f0, f1, amount)` pull the music down. `sc.write(path)`.

## Adding things

- **New character**: subclass `Character` in `chars.py`. Set `HEIGHT`, `INK`, `STREAK`, extra `POSE`
  keys, and write `draw()` using `self.begin(g, p)` ... `self.end(g)`, `self._eye`, `self._mouth`,
  `self._legs`, and `tube`/`smooth`/`oval` for shapes. Keep shapes round: round shapes squash,
  stretch and turn well. Render a pose sheet and look at it before animating.
- **New prop**: a function `fn(g, p, f)` that draws with `g.shape(path, fill)`.
- **New set**: a paint function like `kitchen(g, width)` using flat shapes with `ink=False`.
  Keep furniture tops near y=650 so they sit at the characters' waist height.
- **Vertical shorts**: `Stage(frames, size=(1080, 1920))` is not wired yet; the stage constants
  `W, H` in `toon.py` set the frame. Chases read best in 16:9.
