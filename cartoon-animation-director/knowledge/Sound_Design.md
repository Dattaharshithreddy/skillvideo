# Sound Design

**Knowledge base document 7 of the master mission (Phase 1).**
Version 1.1, 2026-11-11. Follows documents 1 to 6 in this folder.

A silent cartoon is not silent. With no dialogue from the leads, sound carries weight, texture, mood, timing and half of every joke. This document covers every layer of the soundtrack, how our engine makes it, how to synchronise and mix it, where outside sounds may come from, and a complete workflow from picture to finished audio.

## 0. How to read this document

### 0.1 Labels

| Label | Meaning | Status |
|---|---|---|
| **[M]** | Read from our code, or a command run this session | Established project capability or fact |
| **[T-earlier]** | Recorded in `references/06-pipeline-and-tools.md` as tested before this document | Not re-checked now |
| **[C]** | Craft convention; no primary source opened | Established practice |
| **[V]** | Read this session as an excerpt returned by a search | Verified at excerpt level |
| **[R]** | My recommendation or proposed workflow | Untested |
| **[U]** | Unverified assumption | Check first |

### 0.2 The limit that governs everything here

**I cannot hear.** I can place a sound on a frame, measure its level and length, and confirm that a file has an audio stream. I cannot tell whether a bonk is funny, whether the music is pleasant, or whether a voice sounds like a grandmother. Every judgement of how something sounds belongs to Harshith's ears. No audio in this project has been confirmed by ear in anything I have on record.

### 0.3 What is not repeated

The comedy rules for sound (hit on the contact frame, silence before the big hit, one sound per hit frame) and a full cue sheet for one gag are in `Slapstick_Comedy.md` section 12. This document builds on them.

---

## 1. What sound does

| Job | Example |
|---|---|
| **Sells the physics** | How heavy, how hard, how fast: a low thud for Bheemu sitting, a light tap for Bujji |
| **Tells the audience it is safe** | A hollow, pitched bonk says "unhurt" before the picture can (`Slapstick_Comedy.md` section 13) |
| **Directs the eye** | A sound from an event makes the viewer look at it |
| **Sets place and time** | Crows and a far-off auto say morning in a lane |
| **Carries feeling** | Music and its absence |
| **Marks time** | Rhythm tells the viewer when to expect the next thing, so that it can be broken |

A useful test for every sound: which of these jobs is it doing? A sound doing none is clutter.

---

## 2. The layers of a soundtrack

| Layer | What it is | In our series |
|---|---|---|
| Dialogue | Spoken words | Humans only (Ammamma, Chintu), sparingly |
| Vocalisations | Non-word character sounds: laughs, grunts, yelps | Animals never talk; their sounds are instruments or, later, real animal recordings |
| Foley | Everyday sounds made by movement: steps, cloth, handling | Synthesised today |
| Hard and cartoon effects | Impacts, whooshes, boings, pops | `sound.py` |
| Ambience | The sound of the place | Not built yet |
| Music | Score | `sound.py` |
| Silence | The deliberate absence of the above | A tool, section 10 |

Build and judge them in this order of importance for a silent comedy [R]: effects on the key actions, then silence, then music, then Foley, then ambience, then any dialogue.

---

## 3. What the engine provides [M]

Read from `toon-slapstick/engine/sound.py`, `voice.py` and `show.py`.

### 3.1 Instruments and effects

- **Pitched instruments:** `xylo`, `pizz`, `reed`, `brass`, `timp`, `bansuri` (with an optional slide into the note), `veena`, `tanpura` (drone).
- **Percussion:** `tabla` (named strokes, for example `na`, `ge`), `ghatam`, `manjira`, `cymbal`, `tihai` (a three-part cadence).
- **Effects by name for `Score.hit`:** `bonk`, `boing`, `crash`, `whoosh`, `zip`, `pop`, `skid`, `flap`, `sniff`, `munch`, `gulp`, `wah` (a failure phrase), `tada`, plus `timp`, `cymbal`, `tihai`, `manjira`, `ghatam`.
- **Pitch slides:** `slide(n0, n1, d)`.

Everything is synthesised with numpy. No recorded sample is used by the engine.

### 3.2 Placing sound on the picture

| Call | Does |
|---|---|
| `Score(frames)` | A score for that many frames at 24 fps |
| `hit(f, name, v, **kw)` | An effect starting on frame `f` |
| `note(f, inst, note, d, v)` | One note of an instrument |
| `slide(f, n0, n1, frames)` | A pitch slide over a number of frames |
| `steps(f0, f1, every, notes)` | A note on every step between two frames |
| `run(f0, f1, start, every, up)` | A scale run, up or down |
| `music(f0, f1, mood)` | A bed: `calm`, `sneak`, `chase`, `sweet` |
| `raga(f0, f1, mood, sa)` | The Indian-scale equivalent |
| `duck(f0, f1, amount)` | Pulls the music down between two frames, with a 40 ms ramp |
| `write(path)` | Mixes and writes the WAV file |
| `Show.tap(f, stroke)` | One tabla stroke on a frame |
| `Show.close(END, x, y)` | Places a `tihai` to land on the last frame, then the iris |
| `show.laugh(...)` | A bouncing laugh with bansuri giggles |

The sample position of a sound is `int(44100 × f / 24)`. One frame is 1837.5 samples, or 41.7 ms. One musical beat is 12 frames (`Score.BEAT`), which is 120 beats a minute.

### 3.3 The mix that `write` applies

1. Music at gain 0.5 plus effects at gain 0.85.
2. One echo: the signal delayed 85 ms at 0.18.
3. Soft clipping with `tanh`.
4. Peak-normalised to 0.92 of full scale.
5. Written as 16-bit, 44.1 kHz, the same signal in both channels.

So today's soundtrack is **two buses (music, effects), one fixed echo, no stereo placement, no per-sound equalisation, and no loudness measurement.** Voices go into the effects bus.

### 3.4 Voices

- `voice.speak(ep, actor, f, name)` plays a recorded line from frame `f`, ducks the music to 0.45 for its length, and opens and closes the speaker's mouth every two frames according to the loudness of the line.
- The lines are WAV files made with the AI4Bharat Indic-TTS Telugu model (a FastPitch voice with a HiFi-GAN vocoder, female speaker), listed in `toon-slapstick/voice/lines.json`; `tools/tts_telugu.py` shows how they were made.
- One voice serves both humans: lowered 1.5 semitones for Ammamma and raised 5 for Chintu, by resampling. Resampling changes speed along with pitch, so Chintu's lines also play faster and Ammamma's slower.
- Leading silence is trimmed so that the mouth and the sound start together.
- `references/06-pipeline-and-tools.md` records the voices as tested, with quality not confirmed by Harshith.

---

## 4. Dialogue

**Standing rules.** Animals never talk. Only humans may speak, with generated Telugu voice. No captions, bubbles or boards (lessons learned 7 to 9).

**Principles [C].**

- In a visual comedy a line of dialogue should do something the picture cannot: name a thing, give an order, land a punchline word. If the picture already says it, cut the line.
- Short lines. The existing ones are two to five words, which is right.
- Write for the ear: common words, one idea, the important word last.
- Leave air. At least 6 frames of quiet before a line and 12 after, so that it is heard and the reaction has room [R].
- Never put a line over the main hit or the main reaction.
- A line starts on a frame where the speaker is on screen and already facing the listener, unless an off-screen call is the point.

**Lip movement.** Ours is a loudness flap on twos [M]. That is acceptable for short lines at a distance. In a close-up it will read as flapping; stage speaking humans in medium or wider shots until there is something better [R]. Mouth charts are a deferred design decision (`Character_Design_Bible.md` section 13).

**Checks.** The line is intelligible on a phone speaker (ears). A Telugu speaker confirms the wording and pronunciation (a person). The line's file name, text and speaker are in `lines.json` (automatic).

**Options for better voices.** Other TTS models; Harshith's own dubbing tool, which he has named as an option; a human voice actor. Each is a listening decision.

---

## 5. Character vocalisations

Bheemu and Gaju never speak, and Harshith has said he wants real panda and baby elephant sounds for them. `references/06-pipeline-and-tools.md` lists those as recorded files to be supplied, not yet available [T-earlier]. Until they exist, vocal sounds are instruments.

**A vocal palette per character (proposal [R]; every row needs ears).**

| Character | Register and instrument today | Typical sounds | With real recordings later |
|---|---|---|---|
| Bheemu | Low, round: low `reed` or `brass` with a slow attack | A contented hum; a short grunt of effort; a sigh | Panda bleats and huffs, pitched low |
| Gaju | High, bright: `bansuri`, short `brass` toots | A giggle; a small trumpet of surprise; a sniff | Baby elephant squeaks and small trumpets |
| Laddu | Mid, nasal: `reed` with a slide | A rising "mrr?"; a flat annoyed note; a purr as a slow tremolo | Cat recordings |
| Bujji | Very high, tiny: `xylo`, `pizz` | A squeak of alarm; rapid thumping foot on `ghatam` | Rabbit thump recorded; rabbits are mostly silent |
| Ammamma, Chintu | Voice | Words, plus a laugh or a "hmm" | |

**Rules [R].**

- One register per character, kept for the whole series, so that a sound off screen identifies who made it.
- Vocal sounds follow the breath of the action: effort on the push, release on the landing.
- No vocal sound on a hold that is meant to be silent.
- Real animal recordings need a licence that permits the use (section 14) and must not be distressing: no pain or fear calls.
- An instrument standing in for a voice must not form a recognisable tune or catchphrase from an existing cartoon (lessons learned 32).

---

## 6. Foley

Foley is the small, physical layer: feet, cloth, hands on things. It is what makes a drawing seem to touch the world.

| Source | Sound character | Our stand-in today [M] |
|---|---|---|
| Bheemu's steps | Soft, heavy, slow | Low tabla stroke (`ge`) per step, via `show.enter` or `Score.steps` |
| Gaju's steps | Light, quick, slightly rubbery | Higher stroke, softer |
| Laddu | Almost silent pads | Nothing, or the faintest tick; silence is the characterisation |
| Bujji | Rapid light taps | `ghatam` or `xylo` |
| Humans | Bare feet on a stone floor; saree rustle; bangles | `manjira` for bangles is a natural fit |
| Handling props | Steel vessels, a bowl set down, a book closed | `pop`, `ghatam`, a short `xylo` |
| Eating and drinking | Munch, lap, gulp | `munch`, `gulp` |

**Rules [C] unless marked.**

- A footstep sounds on the frame the foot takes weight, not when it lifts. `acting.walk` returns the footfall frames for exactly this [M].
- Weight is pitch and length: heavier is lower and longer.
- Do not score every step in a long walk. Establish the rhythm, thin it out, bring it back when it matters [R].
- Surfaces change the sound: stone floor, earth, a wooden cot. The engine has no surface control; choose the stroke by hand.

**Recording your own [R, for a person].** A phone in a quiet room, close to the source, records usable Foley: a steel tumbler on a table, cloth, bare feet. Record 5 seconds of the room's own silence with each session. Keep the files with a note of what, where and when, so that the rights are unambiguous: a sound you recorded yourself is yours.

---

## 7. Cartoon sound effects

Cartoon effects are not realistic. They are musical exaggerations that describe the *idea* of an action.

| Family | Describes | In the engine [M] | Design rule [C] |
|---|---|---|---|
| Impacts | A hit, a landing | `bonk`, `crash`, `timp`, `pop` | Sharp start on the contact frame; pitch by size |
| Movement | Fast travel | `whoosh`, `zip` | Starts with the move; ends before the arrival sound |
| Elastic | Stretch, spring, wobble | `boing` | Pitch bends with the stretch |
| Friction | A slide to a stop | `skid` | Falls in pitch as speed drops |
| Rise and fall | Height | `slide`, `run` | Up for up, down for down |
| Small actions | A blink, an eye slide, an idea | `ghatam`, `manjira`, a high `xylo` | Tiny and dry |
| Body | Eating, sniffing, flapping | `munch`, `gulp`, `sniff`, `flap` | In rhythm with the drawing |
| Comment | The score reacts | `wah`, `tada`, `tihai` | Once per event; after the reaction, not on it |

**Rules.**

1. **Sharp attack on the contact frame; never earlier** (`Slapstick_Comedy.md` 12.2).
2. **Bigger is lower; smaller is higher.** The same event on Bheemu and on Bujji differs by an octave or more [R].
3. **One effect per hit frame.**
4. **Vary repeats.** The second and third of anything change pitch, level or instrument, or the ear hears a machine [C].
5. **The effect ends before the next one starts,** unless a pile-up is the joke.
6. **Make our own.** The classic studio effects are recognisable property. Our effects are synthesised in our own code with Indian instruments; that is both the legal position I would want and the identity of the series. Never lift an effect from a cartoon's soundtrack.
7. **No pain sounds.** No cracks, no realistic thuds on bodies, no screams.

---

## 8. Ambience

Ambience is the continuous sound of a place. It tells the viewer where they are in the first second and makes silence feel like a real room and not a muted video.

**Today [M].** The engine has no ambience generator. `tanpura` gives a drone, which is music, not place. The existing episodes have music and effects only.

**A proposal [R].** One loop per location, 20 to 30 seconds, used very quietly:

| Location | Bed | Occasional details |
|---|---|---|
| Kitchen | A faint room tone; a pressure-cooker hiss far off | A steel vessel, a tap dripping |
| Courtyard and garden | Morning birds, leaves | A crow; a far temple bell |
| Lane | Distant traffic, a cycle bell | An auto passing; a vendor's call without words |
| Terrace, evening | Wind, far music | A kite's flutter |
| Night | Crickets | A dog far away |

Rules: ambience sits well below everything else; it does not stop for the pre-hit silence unless the silence is meant to be total; it must not contain recognisable music, speech or brand sounds; it changes when the location changes, on the cut. Sources are section 14. Adding ambience means a way to mix in recorded files, which the engine does not have: that is an engine capability to propose, not to slip in.

---

## 9. Music

**What music does in slapstick [C].** It sets tempo and mood, follows the action closely enough to underline it, and gets out of the way before the biggest moments.

**Two ways of scoring.**

- **Following the action** ("mickey-mousing"): a note for every step, rise, fall and hit. `sound.py` is built for this [M]. It suits a wordless cartoon and tires the ear if every tiny move is scored.
- **Underscore:** a bed that holds a mood while effects carry the action.

Use both: underscore in set-ups and endings, close following through the action, nothing in the wait.

**Our system [M].**

- Tempo: 12 frames a beat, 120 beats a minute. Planning main beats on multiples of 12 makes the music fit without forcing.
- Moods: `calm`, `sneak`, `chase`, `sweet`, each a chord pattern and melody shape; `raga` gives Indian-scale versions from a tonic `sa`.
- Ending: a `tihai` that lands on the final frame, then the iris.

**Rules [R].**

- One tonic for an episode. Effects that are pitched (`bonk`, `xylo`, `timp`) should be notes of the current scale, or they sound like mistakes.
- Change mood on a story turn, and on a beat.
- Stop the music; do not fade it, before a big hit. Bring it back after the reaction, not on it.
- A small theme per character is worth having: three or four notes for Gaju's mischief, a slow phrase for Bheemu. This is a proposal; the tunes must be composed, original, and heard.
- Original music only. A synthesised imitation of an existing tune is still that tune.

---

## 10. Silence

| Kind | What stops | Use |
|---|---|---|
| Musical silence | Music only | The wait; a slow burn. Ambience and tiny effects continue |
| Dramatic silence | Music and effects | The 4 to 12 frames before the biggest hit |
| Total silence | Everything | Very rare; reads as the film breaking. Once a season |
| The gap | Nothing new starts | After a hit, before the reaction sound |

Silence only works by contrast, so the section before it needs steady sound. A whole episode of sparse sound has no silence in it, only emptiness. See `Slapstick_Comedy.md` section 6.1 for the matching pauses in the picture.

---

## 11. Comedic timing in sound

Adding to `Slapstick_Comedy.md` 12.2:

- **Sound can set up a gag the picture has not shown.** An off-screen rising slide tells the audience something is coming.
- **The rule of three is audible.** Two matching sounds, then a different third.
- **The "button".** A small, dry sound after a reaction closes a gag the way a full stop closes a sentence: one `ghatam` tick, one soft stroke.
- **Late is funnier than early.** A reaction sound a few frames after the visual reaction reads as dawning; a sound before it reads as an error.
- **The same sound, smaller,** for the topper.
- **Let the laugh happen.** After the main reaction leave at least 12 frames with no new sound event [R].

---

## 12. Synchronisation

### 12.1 The numbers

- One frame is 41.7 ms. The engine places sound to the frame exactly [M].
- Broadcast tests summarised in ITU-R BT.1359-1 put the threshold of noticing at about 45 ms when sound is early and about 125 ms when it is late [V, cited in `Slapstick_Comedy.md`]. So: never early; up to one frame late is safe; the QC rubric's bar is within one frame.

### 12.2 What to sync to

| Event | Sync point |
|---|---|
| Impact | The frame where the squash is **drawn**. On twos that can differ from the frame the prop arrives (`Slapstick_Comedy.md` 11.2) |
| Footstep | The frame the foot takes weight |
| Whoosh | The first frame of the fast move |
| Blink, eye move | The first frame of the change |
| Speech | The first frame of the line; the mouth flap follows the audio [M] |
| Music change | A beat boundary, on or just after the picture change |

### 12.3 Where sync is lost

- A key lost on a held frame, so the picture event is a frame later than planned (`Engine_Change_Proposals.md`, P1).
- Re-timing the picture without moving the cues. Cues should be written relative to named frames in the episode file, not as bare numbers [R].
- Audio and video of different lengths. `qc_frames.py video` fails a file where they differ by more than 0.1 s [M].
- Players and phones add their own delay. That is outside our control.

### 12.4 Checking

Automatic: audio stream present; lengths match. By comparison: the cue sheet's frame for each hit against the per-frame table of the picture (`Slapstick_Comedy.md` shows such a table). By ear and eye: watch the hits. I can do the first two.

---

## 13. Mixing

### 13.1 The order of importance

When two sounds compete, the one higher in this list wins and the other is lowered or moved [C]:

1. The main hit of the gag
2. Dialogue
3. Reaction sounds
4. Other effects and Foley
5. Music
6. Ambience

### 13.2 Tools we have [M]

Per-sound volume (`v`), two bus gains in `write`, and `duck`. That is all. There is no equaliser, compressor, pan or reverb control.

### 13.3 Loudness

- A widely quoted target for online video is about −14 LUFS integrated with true peaks no higher than −1 dBTP [V]. One source points out that YouTube's own upload guide does not publish a loudness figure [V], so treat −14 as a convention, not a rule.
- **The engine does not measure loudness.** It normalises the peak to 0.92, which is about −0.7 dBFS [M, arithmetic]. That is above the conventional −1 dBTP ceiling, and lossy encoding can push peaks higher still [V].
- **Measured on 2026-11-11 with `tools/check_audio.py` on the ten final encodes in the repository [M]:** integrated loudness from −12.2 to −14.3 LUFS; true peak from −0.7 to **+2.7 dBTP** (episode 6), above 0 dBTP in four episodes (1, 6, 8, 9). A true peak above 0 can clip on playback. These are numbers; nobody has listened for distortion, and no file was changed.
- Loudness can be measured, and corrected at encode time, with ffmpeg and no engine change. Both commands were run on a synthetic test clip this session and work with this build (ffmpeg 6.1.1) [M]:

```bash
# measure
ffmpeg -hide_banner -i episode.mp4 -af ebur128=peak=true -vn -f null -
# measure against a target and report what normalising would do
ffmpeg -hide_banner -i episode.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=summary -vn -f null -
```

Whether to normalise is a listening decision. A cartoon with long quiet stretches and a few loud hits will measure low on integrated loudness; forcing it to −14 may raise the quiet parts more than is wanted [R].

### 13.4 Mixing for a phone

- Small speakers reproduce little bass [C]. A hit that lives only in low frequencies vanishes. Our `bonk` is pitched (default MIDI note 76) [M], which should survive; `timp` at note 41 may not. Ears, on a phone.
- Our output is the same signal in both channels [M], so it cannot collapse badly to mono.
- Many viewers watch with sound off. The story must read without it; that is already the standard of this series.

### 13.5 A mixing pass [R]

1. Effects only, music muted: can every action be followed by ear?
2. Add music: does any hit lose its edge? Duck or thin the music there.
3. Add dialogue: is every word clear? Duck under it (the engine does this by default at 0.45).
4. Measure loudness and peaks.
5. Listen on a phone speaker, then earphones.
6. Note every change as a cue-sheet change, so that it survives a re-render.

---

## 14. Sound libraries and licences

I am not a lawyer. This section says what to check. A monetised channel should be treated as commercial use [R].

| Source | Licence position, as read [V] | Practical rule |
|---|---|---|
| Our own synthesis (`sound.py`) | Ours | Preferred. Nothing to clear |
| Our own recordings | Ours | Keep a note of what, where, when |
| Freesound | The licence is set per sound: CC0, CC BY, or CC BY-NC | Filter to CC0, or CC BY with credit; never NC |
| Pixabay | Its content licence allows free use without attribution; the file may not be redistributed on its own | Usable; keep the download record |
| BBC Sound Effects | The RemArc licence is non-commercial; commercial use is sold separately | Not for the channel |
| YouTube Audio Library | Licensed for use within YouTube | Usable on YouTube only [U beyond the excerpt] |
| Kenney, Sonniss GDC bundles | Described as CC0 and royalty-free | Usable; confirm on the download page |
| AI-generated audio | Depends entirely on the tool's terms | Read them; `AI_Video_Production.md` section 15 |

**Rules.**

- **Keep a licence log** for every outside sound (template in 15.3). No log entry, no use.
- Check the licence on the day of download; pages change.
- "Free" and "royalty-free" do not mean "free for commercial use".
- Never take sound from a film, a cartoon, a song or a video.
- An attribution licence means the credit must actually appear, in the video description.

---

## 15. End-to-end workflow

### 15.1 The stages

| # | Stage | Input | Output | Who | Gate |
|---|---|---|---|---|---|
| 1 | **Spotting** | Locked animatic (`Storyboard_and_Cinematography.md` section 12) | A list of every moment that needs sound | Claude | Every beat of the beat sheet has an entry or a deliberate blank |
| 2 | **Cue sheet** | Spotting list | Table: frame, picture event, layer, sound, level, engine call | Claude | Hits are on drawn contact frames; one sound per hit frame |
| 3 | **Dialogue** | Script lines | WAV files; entries in `lines.json` | Claude with TTS; a Telugu speaker checks | Words and pronunciation approved by a person |
| 4 | **Effects and Foley** | Cue sheet | `hit`, `note`, `slide`, `tap`, `steps` calls | Claude | Matches the cue sheet |
| 5 | **Ambience** | Location list | Loops (not possible in the engine today) | Proposal | |
| 6 | **Music** | Beat sheet, tonic, moods | `music` or `raga` beds, `duck` ranges, ending | Claude | Changes fall on beats; silent where planned |
| 7 | **Mix** | All of the above | `Score.write` output | Claude | Section 13.5 steps 1 to 3 by ear |
| 8 | **Measure** | The WAV or the encoded file | Loudness, peak, length, stream check | Claude | Numbers recorded in the QC report |
| 9 | **Listen** | The rendered preview | Notes | **Harshith** | The only real gate |
| 10 | **Revise** | Notes | Changed cue sheet, new render | Claude | Each note closed; nothing else changed |

Sound starts only when shot lengths are frozen. Sound made against a picture that is still being re-timed is made twice.

### 15.2 Cue sheet template

| Film frame | Engine frame | Picture event | Layer | Sound | Level | Call | Note |
|---|---|---|---|---|---|---|---|
| 141 | 140 | Ball lands on Bheemu | Effect | `bonk` | 1.0 | `sc.hit(140, 'bonk')` | Alone on its frame; music ducked from 88 |

Film frame 1 is engine frame 0, as in documents 3 and 4.

### 15.3 Licence log template

| File | What it is | Source URL | Licence | Credit required | Downloaded on | Used in |
|---|---|---|---|---|---|---|

---

## 16. Worked example: cue sheet for "The hand pump" (a plan)

`Slapstick_Comedy.md` example 2 is a written plan; its pump prop and water effect do not exist, so this cannot be rendered or heard. It shows how the layers divide the work. Frames are from that plan.

| Film frames | Picture | Ambience | Foley and effects | Vocal | Music |
|---|---|---|---|---|---|
| 1-36 | Hot garden; Gaju sees the pump | Afternoon bed: cicada-like shimmer, one crow | | A dry little pant (bansuri, breathy) | Slow `calm` bed, sparse |
| 37-60 | Attempt 1: one drop | Continues | Handle: a creak (slow `slide` down), then one high `xylo` drop | | Bed continues |
| 61-80 | Attempt 2: two drops | Continues | Creaks faster and higher; two drops, a third apart | Effort toots | Bed thins |
| 81-104 | He looks up the spout | Continues | A hollow gurgle rising in pitch, quietly, from inside the pump | | **Music out** on 81 |
| 105-112 | Bujji lands on the handle | Continues | One light `ghatam` for the landing; the creak, sharp | Bujji's squeak | Silence |
| 113-114 | Water | **Ambience out for 12 frames** | The gush: a noise burst on 113, alone | | Silence |
| 115-126 | Hold; the cap drips once | Returns | One drop on frame 121 | | Silence |
| 127-150 | Blink; he looks at Bujji | Continues | Two dry ticks | | Silence |
| 151-180 | He fills his trunk and aims | Continues | A long rising slurp | A sly hum | `sneak` bed in on 151 |
| 181-200 | Ammamma appears; he swallows | Continues | `gulp`, big, on the swallow frame | | Music stops dead on 181 |
| 201-216 | A jet from one ear | Continues | A tiny whistle of water | | One `wah`, small |
| 217-264 | All three drink | Continues | Gentle creaks and steady drops in rhythm | Giggles | `sweet` bed; `tihai` to the last frame |

Points to notice: the gurgle (81 to 104) is sound doing the dramatic anticipation; the gush is alone on its frame with even the ambience removed; the reaction ticks come after a gap; the music stops, not fades, twice.

---

## 17. Common mistakes

| Mistake | How to detect | Fix |
|---|---|---|
| Sound made before the picture is locked | Shot lengths changed after cues were written | Freeze lengths first |
| Hit early | Cue frame is before the contact frame | Move it to the drawn contact frame |
| Hit on a lost key | Cue matches the plan but the squash is drawn a frame later | Read the per-frame table; move the cue or the key |
| Two sounds on the hit frame | Cue sheet has two rows for one frame | Remove or shift one |
| Wall-to-wall music | No `duck` and no gap in the bed | Stop it before hits and through waits |
| No silence | Sound events closer than 12 frames apart throughout | Thin them; leave gaps |
| Every step scored | A long walk with a note per step | Establish, thin, return |
| Same sound repeated identically | Three equal rows | Vary pitch, level or instrument |
| Off-key effects | Pitched effects not in the bed's scale | Choose notes from the scale |
| Bass-only impact | A hit that disappears on a phone | Add a pitched or mid-range component |
| Dialogue over the gag | A line overlapping the hit or the reaction | Move the line |
| Borrowed sound | No licence log entry; or it sounds like a known cartoon | Remove; synthesise or record our own |
| Peak too hot | Normalised to 0.92 with no true-peak check | Measure; correct at encode if needed |
| Claiming it sounds good | A report says so and nobody listened | Say "not listened to" |

---

## 18. Checklist

**Plan**
- [ ] Shot lengths frozen
- [ ] Every beat spotted, or deliberately silent
- [ ] Cue sheet written with film and engine frames
- [ ] Each sound has a job from section 1

**Build**
- [ ] Hits on drawn contact frames, never early, alone on their frame
- [ ] Music stops before the biggest hit and returns after the reaction
- [ ] At least one real silence
- [ ] Repeats varied; pitched effects in key
- [ ] Animals do not speak; human lines short, clear of the gag
- [ ] Every outside sound has a licence log entry
- [ ] Nothing taken from any film, cartoon or song

**Verify (automatic)**
- [ ] Audio stream present; audio and video lengths within 0.1 s
- [ ] Loudness and peak measured and recorded
- [ ] Cue frames compared with the picture's per-frame table

**Verify (people)**
- [ ] Listened to on a phone speaker and on earphones (Harshith)
- [ ] Telugu lines checked by a Telugu speaker
- [ ] The story still reads with the sound off

---

## 19. Limitations and open questions

**Limitations [M].**

- No ambience, no recorded samples, no stereo placement, no equaliser, compressor or reverb control; one fixed echo.
- No loudness measurement in the engine; the peak ceiling is about −0.7 dBFS.
- One synthetic voice for both humans; pitch shifting changes speed.
- Mouth movement is a loudness flap on twos.
- Nothing I produce can be judged by me.

**Open questions for Harshith.**

1. Have you listened to the existing episodes' sound and the two human voices, and what is the verdict? Nothing on record says.
2. Real panda and elephant sounds: will you supply recordings, and under what licence? Until then the instrument palette in section 5 is the proposal.
3. Do you want ambience? It needs a way to mix recorded files, which is an engine change to propose separately.
4. Loudness: measure the ten episodes and report, without changing them? That is a read-only check.
5. Should encodes be normalised to a target with ffmpeg, which changes no engine code but does change the delivered sound? That needs your ears on a before and after.
6. Character themes: wanted? They would be composed as proposals for you to hear.

---

## 20. References

Tags: **[excerpt]** read this session as an excerpt from a search. **[book]** not opened. **[own]** our repository.

- ITU-R BT.1359-1, "Relative timing of sound and vision for broadcasting" **[book]**; thresholds as reported at https://en.wikipedia.org/wiki/Audio-to-video_synchronization **[excerpt, read for document 4]**
- Loudness conventions for online video: https://youlean.co/?p=30813 ; https://josephnilo.com/blog/dialogue-loudness-lufs-true-peak-video/ (notes that YouTube's upload guide gives no LUFS figure) ; https://violetrecording.com/how-to-master-for-youtube/ **[excerpt]**
- Sound library licences: https://swarmify.com/blog/free-sound-effects-websites/ ; https://app.cinevva.com/guides/free-sound-effects-music ; https://www.pro-tools-expert.com/production-expert-1/free-sound-effects-2023 **[excerpt]**. Read each library's own licence page before use.
- Walter Murch, *In the Blink of an Eye*; David Sonnenschein, *Sound Design*; Vanessa Theme Ament, *The Foley Grail*; Daniel Goldmark, *Tunes for 'Toons* **[book]**

**Our own material [own]**
- `toon-slapstick/engine/sound.py`, `voice.py`, `show.py`, `acting.py`; `toon-slapstick/tools/tts_telugu.py`; `toon-slapstick/voice/lines.json`
- `references/05-slapstick-chase-handbook.md` (section 4), `06-pipeline-and-tools.md`, `07-qc-rubric.md`, `09-lessons-learned.md`
- `Slapstick_Comedy.md` (section 12), `Storyboard_and_Cinematography.md`, `Quality_Control.md`, `Engine_Change_Proposals.md`

---

## 21. Change log

| Date | Change |
|---|---|
| 2026-11-11 | Version 1.1. Measured loudness and true peak of the ten episodes added to 13.3. Decision recorded by Harshith: no audio or voice is approved until heard in actual episode output. |
| 2026-11-11 | Version 1.0. Engine audio capabilities read from code. Two ffmpeg loudness commands run on a synthetic clip. No episode audio measured. Nothing heard by anyone for this document. One cue sheet written as a plan. Not reviewed by Harshith. |
