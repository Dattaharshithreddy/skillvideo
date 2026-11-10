---
name: toon-slapstick
description: Make original 2D slapstick cartoons (classic cat-and-mouse chase style, no dialogue) with the Bheemu & Gaju characters or new ones. Use when asked for a 2D cartoon, a chase gag, a Bheemu & Gaju episode, or "Tom and Jerry style" animation. Renders on CPU in about real time; no GPU needed.
---

# toon-slapstick

A 2D cartoon engine plus the craft rules of 1940s theatrical chase cartoons. Characters are redrawn
every frame from pose parameters, so they squash, stretch, smear and act instead of sliding like
cut-out puppets. Backgrounds are soft and painted; characters are inked. Music and sound effects are
synthesised and locked to the picture.

Everything is original: original characters, original music, original gags. Never copy an existing
studio's characters, designs, scores or specific gag sequences. Study the craft, not the property.

## Workflow

1. **Read `references/craft.md`** before writing a single key. It holds the gag structure and the
   frame-count timing table. Timing is the whole style.
2. **Write the gag as beats** (one line each): setup, complication, slow burn, take, chase, big hit,
   topper, ending. One location, two characters, one object they both want. No dialogue.
3. **Put it on a beat grid.** 24 fps, 12 frames = one musical beat. Start actions on beats and land
   hits on beats.
4. **Write `episodes/<name>/episode.py`** by copying `episodes/01-dosa-snatch/episode.py`. API in
   `references/api.md`.
5. **Check contact sheets before rendering**: `python3 episode.py sheet 40,52,63,110 check.png`
   and LOOK at the image. Fix staging (who overlaps what, what is off-screen, what reads at
   thumbnail size) while it costs seconds.
6. **Render**: `python3 episode.py preview` (half size) then `python3 episode.py final`.
   A 30 second short renders in about 1 minute at half size and about 4 minutes at 1080p on 2 CPU cores.
7. **Watch the stills from the final file** at the hits and the takes. Deliver the MP4.

Setup: `pip install skia-python numpy scipy uharfbuzz` and `ffmpeg` on the path.
Format: vertical 1080x1920. Music: use `sc.raga(f0, f1, mood)` (tabla, flute, veena) and end on `sc.hit(END - 25, 'tihai')`.

## Rules that make it look right

- **Pose to pose, with holds.** Hit a strong pose in 2-5 frames, then hold it 6-16 frames with a
  little life (blink, bob, settle). Even spacing ("floaty") is the number one way to ruin the style.
- **Anticipation before every action, reaction after every hit.** `'antic'`, `take()`, `squash()`.
- **Fast moves are 1-5 frames and smeared.** The engine smears automatically above ~46 px/frame.
- **Squash on arrival, stretch on departure, keep the volume.** Shorter means wider.
- **Characters on twos, pans and fast action on ones.** Automatic.
- **The pause is the joke.** Hold on the realisation (8-12 frames, one blink) before the take.
  Hold the flattened pose after a hit (10-14 frames). Let a character hang in mid-air before falling.
- **Nobody is really hurt.** Flatten, see stars, shake it off, carry on. End on friendship or on a
  final small gag, then iris out.
- **Sound follows action.** Every step, sneak, rise, fall and hit has a note or effect on the
  exact frame. Drop the music to silence just before the biggest hit.

## Files

- `engine/toon.py` core: timeline, easing, camera, stage, render, contact sheets
- `engine/chars.py` Bheemu and Gaju (pose parameters listed at the top of the file)
- `engine/acting.py` reusable moves: `take`, `zip_off`, `scramble`, `walk`, `arc`, `squash`, `blink`...
- `engine/scene.py` painted kitchen, props, dust puffs, impact stars, speed lines, iris, title card
- `engine/sound.py` synth orchestra, sound effects, music beds, `Score`
- `engine/india.py` the Telugu home set, Indian props, and `telugu()` for correctly shaped Telugu lettering
- `engine/cast.py` Ammamma, Chintu, Laddu the cat, Bujji the rabbit
- `series/bheemu-gaju.md` the world, the cast and the ten-episode plan
- `episodes/01-dosa-snatch/` complete 32-second vertical example
- `references/craft.md` what makes the style work, with frame counts
- `references/api.md` engine reference and how to add characters, props and sets

## House rules for Bheemu & Gaju (set by Harshith, November 2026)

- Silent comedy like episode 1. No speech bubbles, no boards held by characters, no captions.
- Telugu lines appear only as part of the scenery: wall paint, posters, shop boards, notices, banners, the auto.
- Bheemu, Gaju, Laddu and Bujji never talk. Only the humans (Ammamma, Chintu) may speak, with `voice.speak()`.
  Voice files live in `voice/`; make new ones with `tools/tts_telugu.py` (free AI4Bharat Indic-TTS Telugu model,
  downloaded from the AI4Bharat/Indic-TTS GitHub release `v1-checkpoints-release/te.zip`; needs `pip install coqui-tts torch torchaudio torchcodec`).
- Draw anatomy, not shapes: fingers and thumbs, elbows, knees, toes, paws, a real trunk.
- Do not change episode 1.

## Shared helpers added for episodes 2-10

- `engine/show.py`: `Show` (title card, camera shortcuts, closing iris, command line and re-encode), expression
  presets (`CALM HAPPY LAUGH ANGRY SHOCK SORRY SLY SLEEP`), `hop`, `laugh`, `enter`, props (ladle, milk pot, ball,
  umbrella, kite, papad, diya, rocket, cot) and effects (`rain`, `zzz`, `splash`, `sparks`, `word`).
- `engine/sets.py`: `garden`, `lane`, `terrace`, `courtyard(night=True)` and the `auto` prop.
- `engine/voice.py`: `speak(ep, actor, frame, name)` plays a line and moves the speaker's mouth.
- Episodes 2-10 in `episodes/` are short (about 150 lines each) and are the best templates to copy.
