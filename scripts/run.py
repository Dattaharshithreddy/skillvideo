#!/usr/bin/env python3
"""CGI shorts pipeline: tts -> refs -> images -> animate -> assemble.

Usage:
  python run.py PROJECT [--stage tts|refs|images|animate|assemble] [--only s01,s02] [--force] [--free]
Every stage skips outputs that already exist unless --force is given.
"""
import argparse, asyncio, base64, json, math, os, shutil, subprocess, sys, textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
STAGES = ["tts", "refs", "images", "animate", "assemble"]


# ---------------------------------------------------------------- helpers
def log(*a):
    print("[cgi-shorts]", *a, flush=True)


def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_project(p: Path):
    spec = json.loads((p / "shots.json").read_text())
    cfg = json.loads((HERE / "default_config.json").read_text())
    if (p / "config.json").exists():
        cfg = deep_merge(cfg, json.loads((p / "config.json").read_text()))
    for d in ["audio", "images", "clips", "refs", "out"]:
        (p / d).mkdir(exist_ok=True)
    ids = [s["id"] for s in spec["shots"]]
    if len(ids) != len(set(ids)):
        sys.exit("shots.json: shot ids must be unique")
    return spec, cfg


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"command failed: {' '.join(map(str, cmd[:6]))} ...")
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)]).strip())


def selected(spec, only):
    return [s for s in spec["shots"] if not only or s["id"] in only]


def bump_cost(p, key, amount):
    f = p / "out" / "usage.json"
    u = json.loads(f.read_text()) if f.exists() else {}
    u[key] = u.get(key, 0) + amount
    f.write_text(json.dumps(u, indent=2))


def fal():
    try:
        import fal_client
    except ImportError:
        sys.exit("pip install fal-client  (or use --free)")
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set (or use --free)")
    return fal_client


def download(url, dest):
    import requests
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    Path(dest).write_bytes(r.content)


def first_url(result, kind):
    if kind == "image":
        imgs = result.get("images") or ([result["image"]] if "image" in result else [])
        return imgs[0]["url"]
    v = result.get("video")
    return v["url"] if isinstance(v, dict) else v


# ---------------------------------------------------------------- 1. TTS
# The whole script is narrated in ONE take (natural flow), then shots are cut on word timings,
# because these videos cut every 1.2-2 s, often mid-sentence.
def full_text(spec):
    return " ".join(s["line"].strip() for s in spec["shots"])


def words_from_alignment(al):
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, s0, c0, last = [], "", None, 0, 0
    for i, (c, a, b) in enumerate(zip(chars, st, en)):
        if c.isspace():
            if cur:
                words.append({"w": cur, "s": s0, "e": last, "c": c0})
            cur, s0 = "", None
        else:
            if s0 is None:
                s0, c0 = a, i
            cur += c
            last = b
    if cur:
        words.append({"w": cur, "s": s0, "e": last, "c": c0})
    return words


def attach_offsets(text, words):
    """Give each timed word its character offset in text (for TTS engines that don't)."""
    low, cur = text.lower(), 0
    for w in words:
        k = low.find(w["w"].lower().strip(".,!?;:\"'"), cur)
        if k >= 0:
            w["c"], cur = k, k + 1
        else:
            w["c"] = cur
    return words


def tts_elevenlabs(spec, cfg, text, mp3):
    import requests
    v = spec.get("voice", {})
    vid = v.get("voice_id", "pNInz6obpgDQGcFmaJgB")
    body = {"text": text, "model_id": cfg["elevenlabs_model"],
            "voice_settings": {"stability": v.get("stability", 0.45), "similarity_boost": v.get("similarity", 0.8),
                               "style": v.get("style", 0.15), "use_speaker_boost": True, "speed": v.get("speed", 1.08)}}
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps",
                      headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}, json=body, timeout=300)
    r.raise_for_status()
    d = r.json()
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    return words_from_alignment(d["alignment"])


def tts_edge(cfg, spec, text, mp3):
    try:
        import edge_tts
    except ImportError:
        sys.exit("pip install edge-tts  (free narration) or set ELEVENLABS_API_KEY")
    voice = spec.get("voice", {}).get("edge_voice", cfg["voice_fallback"])
    rate = spec.get("voice", {}).get("edge_rate", "+10%")

    async def go():
        try:
            com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
        except TypeError:
            com = edge_tts.Communicate(text, voice, rate=rate)
        audio, words = bytearray(), []
        async for ch in com.stream():
            if ch["type"] == "audio":
                audio += ch["data"]
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append({"w": ch["text"], "s": s, "e": s + ch["duration"] / 1e7})
        return bytes(audio), words

    audio, words = asyncio.run(go())
    mp3.write_bytes(audio)
    return attach_offsets(text, words)


def tts_kokoro(spec, cfg, text, mp3):
    """Free, offline, good-quality voice (Kokoro). Phrase-level synthesis split at punctuation gives exact
    phrase boundaries; words inside a phrase are timed by syllable weight."""
    import re
    try:
        import numpy as np, soundfile as sf
        from kokoro_onnx import Kokoro
    except ImportError:
        sys.exit("pip install kokoro-onnx soundfile  (then download the model files, see references/models.md)")
    mdir = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "kokoro"))
    k = Kokoro(str(mdir / "kokoro-v1.0.int8.onnx"), str(mdir / "voices-v1.0.bin"))
    v = spec.get("voice", {})
    voice, speed = v.get("kokoro_voice", "am_michael"), float(v.get("speed", 1.08))
    phrases = [x.strip() for x in re.findall(r"[^,.;!?]+[,.;!?]?", text) if x.strip()]
    gap = {",": 0.10, ";": 0.15, ".": 0.26, "?": 0.26, "!": 0.26}
    wt = lambda w: max(1, len(re.findall(r"[aeiouy]+", w.lower()))) + 0.15 * len(w)
    out, words, t, cur, sr = [], [], 0.0, 0, 24000
    for ph in phrases:
        a, sr = k.create(ph, voice=voice, speed=speed, lang="en-us")
        a = np.asarray(a, dtype=np.float32)
        idx = np.where(np.abs(a) > 0.012)[0]
        if len(idx):
            a = a[max(idx[0] - int(0.02 * sr), 0): idx[-1] + int(0.04 * sr)]
        d, toks = len(a) / sr, ph.split()
        W, acc = sum(wt(x) for x in toks), 0
        for tk in toks:
            c = text.find(tk, cur); cur = c + len(tk)
            st = t + d * acc / W; acc += wt(tk)
            words.append({"w": tk, "s": round(st, 3), "e": round(t + d * acc / W, 3), "c": c})
        g = gap.get(ph[-1], 0.05)
        out += [a, np.zeros(int(g * sr), np.float32)]; t += d + g
    wav = mp3.with_suffix(".wav")
    sf.write(str(wav), np.concatenate(out), sr)
    run(["ffmpeg", "-y", "-i", str(wav), "-b:a", "192k", str(mp3)])
    return words


def stage_tts(p, spec, cfg, a):
    text = full_text(spec)
    mp3, js = p / "audio" / "narration.mp3", p / "audio" / "narration.json"
    if mp3.exists() and js.exists() and not a.force and json.loads(js.read_text()).get("text") == text:
        return
    prov = spec.get("voice", {}).get("provider", "elevenlabs")
    use_eleven = bool(os.environ.get("ELEVENLABS_API_KEY")) and not a.free and prov == "elevenlabs"
    if prov == "kokoro":
        log("narration via Kokoro (offline)")
        words = tts_kokoro(spec, cfg, text, mp3)
    else:
        log("narration via", "ElevenLabs" if use_eleven else "edge-tts")
        words = tts_elevenlabs(spec, cfg, text, mp3) if use_eleven else tts_edge(cfg, spec, text, mp3)
    if use_eleven:
        bump_cost(p, "tts_chars", len(text))
    if not words:  # last resort: spread evenly
        d, toks, c = duration(mp3), text.split(), 0
        for i, t in enumerate(toks):
            c = text.find(t, c)
            words.append({"w": t, "s": d * i / len(toks), "e": d * (i + 1) / len(toks), "c": c})
    js.write_text(json.dumps({"text": text, "words": words}))
    log(f"narration: {duration(mp3):.1f}s, {len(words)} words, {len(text.split())/duration(mp3):.2f} words/s")


def timing(p, spec, cfg):
    """Return {shot_id: (start, end)} cut on word timings, plus the word list."""
    data = json.loads((p / "audio" / "narration.json").read_text())
    words, total = data["words"], duration(p / "audio" / "narration.mp3") + cfg["tail"]
    starts, off = [], 0
    for s in spec["shots"]:
        frag_start = off
        off += len(s["line"].strip()) + 1
        w = next((w for w in words if w["c"] >= frag_start), None)
        starts.append(w["s"] if w else total)
    starts[0] = 0.0
    out = {}
    for i, s in enumerate(spec["shots"]):
        end = starts[i + 1] if i + 1 < len(starts) else total
        out[s["id"]] = (starts[i], max(end, starts[i] + 0.3))
    return out, words


# ---------------------------------------------------------------- 2. character refs
def stage_refs(p, spec, cfg, a):
    chars = spec.get("characters", {})
    if not chars or a.free or spec.get("engine") == "blender":
        return
    fc = fal()
    for cid, c in chars.items():
        out = p / "refs" / f"{cid}.png"
        if out.exists() and not a.force:
            continue
        prompt = (f"character reference sheet of {c['description']}, full body front view and close-up "
                  f"portrait side by side, neutral pose, neutral expression, plain light grey background, "
                  f"{spec.get('style', '')}")
        res = fc.subscribe(cfg["image"]["endpoint"], arguments={"prompt": prompt, **cfg["image"]["args"],
                                                                "aspect_ratio": "16:9"})
        download(first_url(res, "image"), out)
        bump_cost(p, "images", 1)
        log("ref", cid)


# ---------------------------------------------------------------- 3. stills
def placeholder(path, text):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), (28, 32, 40))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
    except OSError:
        f = ImageFont.load_default()
    y = 500
    for ln in textwrap.wrap(text, 28):
        d.text((80, y), ln, fill=(220, 220, 220), font=f)
        y += 70
    img.save(path)


def stage_images(p, spec, cfg, a):
    if spec.get("engine") == "blender":
        return
    fc = None if a.free else fal()
    style = spec.get("style", "")
    for s in selected(spec, a.only):
        out = p / "images" / f"{s['id']}.png"
        if out.exists() and not a.force:
            continue
        if a.free:
            placeholder(out, s.get("image", s.get("line", "")))
            log("placeholder still", s["id"], "(drop a real image at", out, ")")
            continue
        chars = [c for c in s.get("characters", []) if (p / "refs" / f"{c}.png").exists()]
        detail = spec.get("detail", cfg.get("detail_suffix", ""))
        prompt = f"{s['image']}. {detail}. {style}"
        if chars:
            descs = "; ".join(f"image {i+1} shows the {c}" for i, c in enumerate(chars))
            prompt = f"{descs}. Keep their face, hair and clothing identical. Scene: {prompt}"
            urls = [fc.upload_file(str(p / "refs" / f"{c}.png")) for c in chars]
            res = fc.subscribe(cfg["edit"]["endpoint"],
                               arguments={"prompt": prompt, "image_urls": urls, **cfg["edit"]["args"]})
        else:
            res = fc.subscribe(cfg["image"]["endpoint"], arguments={"prompt": prompt, **cfg["image"]["args"]})
        download(first_url(res, "image"), out)
        bump_cost(p, "images", 1)
        log("still", s["id"])


# ---------------------------------------------------------------- 4. animate
def stage_animate_blender(p, spec, cfg, a):
    """engine: blender -> each shot has "scene": "scenes/sNN.py" (a czlib build(seconds) script) rendered on the GPU."""
    blender = os.environ.get("BLENDER", shutil.which("blender") or "blender")
    drv = HERE.parent / "blender" / "render.py"
    tm, _ = timing(p, spec, cfg)
    q = "preview" if getattr(a, "preview", False) else "final"
    for s in selected(spec, a.only):
        out = p / "clips" / f"{s['id']}.mp4"
        if out.exists() and not a.force:
            continue
        scene = p / s.get("scene", f"scenes/{s['id']}.py")
        if not scene.exists():
            sys.exit(f"missing scene script {scene} for shot {s['id']}")
        secs = tm[s["id"]][1] - tm[s["id"]][0] + 0.35
        log(f"blender {s['id']} ({secs:.2f}s, {q})")
        r = subprocess.run([blender, "-b", "--factory-startup", "-P", str(drv), "--", str(scene), str(out), f"{secs:.3f}",
                            "--quality", q], capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            if ln.startswith("[render]") or "Error" in ln:
                log(ln)
        if r.returncode or not out.exists():
            sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
            sys.exit(f"blender failed on {s['id']}")


def stage_animate(p, spec, cfg, a):
    if spec.get("engine") == "blender":
        return stage_animate_blender(p, spec, cfg, a)
    if a.free:
        log("free mode: stills get Ken Burns motion in assemble")
        return
    fc = fal()
    v = cfg["video"]
    tm, _ = timing(p, spec, cfg)
    for s in selected(spec, a.only):
        out = p / "clips" / f"{s['id']}.mp4"
        if s.get("still") or (out.exists() and not a.force):
            continue
        need = tm[s["id"]][1] - tm[s["id"]][0]
        dur = next((d for d in sorted(v["durations"]) if d >= need), max(v["durations"]))
        args = {"prompt": s.get("motion", "slow cinematic push-in"),
                v["image_field"]: fc.upload_file(str(p / "images" / f"{s['id']}.png")), **v["args"]}
        fmt = v.get("duration_format", "str")
        if fmt != "none":
            args["duration"] = {"str": str(dur), "int": dur, "str_s": f"{dur}s"}[fmt]
        log(f"animating {s['id']} ({dur}s for {need:.1f}s of narration)...")
        res = fc.subscribe(v["endpoint"], arguments=args)
        download(first_url(res, "video"), out)
        bump_cost(p, "video_seconds", dur)


# ---------------------------------------------------------------- 5. assemble
def ass_time(t):
    t = max(t, 0)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def write_captions(path, cfg, words, total):
    """Short 1-3 word chunks exactly as spoken, bold white with a soft shadow, lower-middle of frame."""
    c = cfg["captions"]
    y = int(H * c["y_ratio"])
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{c['font']},{c['size']},&H00FFFFFF,&H00FFFFFF,&H50000000,&H90000000,-1,0,0,0,100,100,0,0,1,{c['outline']},{c['shadow']},5,60,60,0,1
"""
    head += "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    n, maxc = c["words_per_group"], c.get("max_chars", 16)
    groups, cur = [], []
    for w in words:  # break on group size, length, or end of a clause
        if cur and (len(cur) >= n or len(" ".join(x["w"] for x in cur + [w])) > maxc):
            groups.append(cur); cur = []
        cur.append(w)
        if w["w"][-1] in ".,?!;:":
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    lines = []
    for gi, g in enumerate(groups):
        st = g[0]["s"]
        en = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else total
        en = min(en, g[-1]["e"] + 0.6)
        text = " ".join(x["w"] for x in g)
        if c.get("strip_trailing_punct", True):
            text = text.rstrip(".,;:")
        if c.get("uppercase"):
            text = text.upper()
        text = text.replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W//2},{y})}}{text}")
    Path(path).write_text(head + "\n".join(lines) + "\n")


def kenburns_filter(dur, i):
    frames = max(int(round(dur * FPS)), 1)
    zin = i % 2 == 0  # alternate push-in / pull-out so stills never feel static
    # stronger push/pull plus a lateral drift: the reference is almost never still
    z = f"1.0+0.22*on/{frames}" if zin else f"1.22-0.22*on/{frames}"
    dx = f"+(iw-iw/zoom)/2*{0.6 if i % 4 < 2 else -0.6}*(on/{frames}-0.5)"
    return (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2){dx}':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
            f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,format=yuv420p")


def stage_assemble(p, spec, cfg, a):
    tmp = p / "out" / "tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    tm, words = timing(p, spec, cfg)
    vlist, sfx_events = [], []
    for i, s in enumerate(spec["shots"]):
        sid = s["id"]
        t0, t1 = tm[sid]
        # frame-accurate segment lengths so cuts never drift from the narration
        d = (round(t1 * FPS) - round(t0 * FPS)) / FPS
        clip, img = p / "clips" / f"{sid}.mp4", p / "images" / f"{sid}.png"
        seg = tmp / f"v_{i:03d}.mp4"
        if clip.exists() and not s.get("still"):
            ss = float(s.get("clip_start", 0))
            vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                  f"tpad=stop_mode=clone:stop_duration=30,trim=start={ss}:duration={d:.3f},setpts=PTS-STARTPTS,format=yuv420p")
            run(["ffmpeg", "-y", "-i", str(clip), "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast",
                 "-crf", "18", "-r", str(FPS), str(seg)])
        elif img.exists():
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-vf", kenburns_filter(d, i), "-an",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), "-t", f"{d:.3f}", str(seg)])
        else:
            sys.exit(f"no clip or still for {sid}")
        vlist.append(seg)
        if s.get("sfx"):
            hits = list((p / "sfx").glob(f"{s['sfx']}.*")) if (p / "sfx").exists() else []
            if hits:
                sfx_events.append((hits[0], t0))
            else:
                log(f"warning: sfx '{s['sfx']}' not found in sfx/")
    t = max(e for _, e in tm.values())

    lst = tmp / "video.txt"
    lst.write_text("".join(f"file '{x.resolve()}'\n" for x in vlist))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp / "video.mp4")])
    run(["ffmpeg", "-y", "-i", str(p / "audio" / "narration.mp3"), "-af", f"aresample=44100,apad,atrim=0:{t:.3f}",
         "-ac", "2", str(tmp / "voice.wav")])

    # audio mix: voice + sfx (+ looping music, faded out)
    inputs, filt, mix = ["-i", str(tmp / "voice.wav")], [], ["[0:a]"]
    for k, (f, at) in enumerate(sfx_events, start=1):
        inputs += ["-i", str(f)]
        ms = int(at * 1000)
        filt.append(f"[{k}:a]aresample=44100,volume={cfg['sfx_volume']},adelay={ms}|{ms}[s{k}]")
        mix.append(f"[s{k}]")
    music = next(iter(p.glob("music.*")), None)
    if music:
        k = len(sfx_events) + 1
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        filt.append(f"[{k}:a]aresample=44100,volume={cfg['music_volume']},atrim=0:{t:.3f},"
                    f"afade=t=out:st={max(t-1.0,0):.3f}:d=1.0[m]")
        mix.append("[m]")
    filt.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[aout]", "-t", f"{t:.3f}",
         str(tmp / "mix.wav")])

    ass = tmp / "captions.ass"
    write_captions(ass, cfg, words, t)
    final = p / "out" / "final.mp4"
    run(["ffmpeg", "-y", "-i", str(tmp / "video.mp4"), "-i", str(tmp / "mix.wav"),
         "-vf", f"subtitles={ass.as_posix()}" + (f":fontsdir={(p / 'fonts').as_posix()}" if (p / "fonts").exists() else ""), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(final)])
    shutil.copy(ass, p / "out" / "captions.ass")

    u = json.loads((p / "out" / "usage.json").read_text()) if (p / "out" / "usage.json").exists() else {}
    ce = cfg["cost_estimate"]
    est = u.get("images", 0) * ce["image"] + u.get("video_seconds", 0) * ce["video_per_second"]
    (p / "out" / "cost.txt").write_text(f"usage: {u}\nrough fal cost estimate: ${est:.2f} (check your fal dashboard)\n")
    log(f"done: {final}  ({t:.1f}s, {len(spec['shots'])} shots)")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--stage", choices=STAGES)
    ap.add_argument("--only", help="comma-separated shot ids")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--free", action="store_true", help="no paid APIs: edge-tts, placeholder/own stills, Ken Burns")
    ap.add_argument("--preview", action="store_true", help="blender engine: half-res fast render for checking")
    a = ap.parse_args()
    a.only = set(a.only.split(",")) if a.only else None
    p = Path(a.project).resolve()
    spec, cfg = load_project(p)
    fns = {"tts": stage_tts, "refs": stage_refs, "images": stage_images,
           "animate": stage_animate, "assemble": stage_assemble}
    for st in ([a.stage] if a.stage else STAGES):
        log("stage", st)
        fns[st](p, spec, cfg, a)


if __name__ == "__main__":
    main()
