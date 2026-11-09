# Models, costs, swapping

All AI generation goes through **fal.ai** (one key, pay-per-use, hundreds of models). Endpoints change often — before the first paid call each session, fetch `https://fal.ai/models/<endpoint-id>/llms.txt` and confirm the parameter names, then update `config.json`.

## Defaults (scripts/default_config.json, checked Nov 2026)
| Stage | Endpoint | Notes |
|---|---|---|
| Character refs + stills (no character) | `fal-ai/nano-banana-2` | text-to-image, `aspect_ratio: "9:16"` |
| Stills with characters | `fal-ai/nano-banana-2/edit` | `image_urls` = reference sheets (up to 14) |
| Image → video | `bytedance/seedance-2.0/image-to-video` | `image_url`; top-rated image-to-video model mid-2026 |

Alternatives for `video.endpoint` (set `image_field` accordingly):
- Kling 3.0 Pro — uses `start_image_url`; strong motion, ~$0.56 per 5 s without audio.
- Kling 2.5 Turbo Pro (`fal-ai/kling-video/v2.5-turbo/pro/image-to-video`) — cheaper, ~$0.07/s.
- Veo 3.1 — highest fidelity, ~$0.20/s without audio.
Always set audio off — narration and SFX are added in assembly.

## Budget for a 30 s short (~20 shots)
- Stills: ~20–30 images incl. retries → ~$1–2
- Video: 20 × 5 s → ~$7–12 depending on model (fewer with `still: true` shots)
- Narration: ElevenLabs ~1,000 characters → covered by a starter plan
Use `still: true` on low-motion shots and `--free` drafts to cut cost.

## config.json keys
Any key in `scripts/default_config.json` can be overridden per project:
```json
{
  "image": {"endpoint": "fal-ai/nano-banana-2", "args": {"aspect_ratio": "9:16"}},
  "edit":  {"endpoint": "fal-ai/nano-banana-2/edit", "args": {"aspect_ratio": "9:16"}},
  "video": {"endpoint": "bytedance/seedance-2.0/image-to-video", "image_field": "image_url",
            "durations": [5, 10], "duration_format": "str", "args": {}},
  "captions": {"font": "DejaVu Sans", "size": 68, "words_per_group": 3, "max_chars": 16,
               "y_ratio": 0.78, "outline": 2, "shadow": 4, "uppercase": false},
  "music_volume": 0.12, "tail": 0.25
}
```
`duration_format`: `"str"` → `"5"`, `"int"` → `5`, `"str_s"` → `"5s"`, `"none"` → omit.

Shots last ~1.5 s but most models generate at least 5 s, so you pay for 5 s per shot. To save money, mark simple shots `still: true`, or generate one clip and reuse it for two consecutive shots by copying it to both ids with different `clip_start` values.

## Narration
The whole script is voiced in ONE take so it flows naturally; shots are cut on the word timings. ElevenLabs `/v1/text-to-speech/{voice_id}/with-timestamps` gives character-level timing → exact word captions. Good calm, friendly male premade voices: "Adam" (`pNInz6obpgDQGcFmaJgB`), or pick one in the Voice Library and paste its id. Default `speed` is 1.08 to hit ~2.9 words/s.
Fallback `edge-tts` (free) with `en-US-GuyNeural` / `en-US-ChristopherNeural`; word timings come from its WordBoundary events.

## Fully local alternative: Blender
For total control (and zero per-clip cost) Claude Code can drive Blender headless (`blender -b -P scene.py`): import CC0 models (Poly Haven, Sketchfab CC), Mixamo-rigged characters, animate the camera with keyframes, render 1080x1920 PNG sequences in ~3 s chunks with Cycles/EEVEE, then feed the clips into `clips/<id>.mp4` and run only `--stage assemble`. Slower to set up, but every shot is repeatable and editable.
