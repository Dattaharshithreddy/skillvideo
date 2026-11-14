#!/usr/bin/env python3
"""Build word-by-word 9:16 reel captions (ASS) and the narration track from per-line TTS clips.

Input plan.json:
{"gap": 0.15, "font": "Poppins", "lines": [
  {"audio": "audio/l01.wav", "roman": "Train track ela maaruthundi?", "keywords": ["maaruthundi"]}, ...]}
Each line is its own TTS clip, so line timing is exact; words inside a line are timed by
character length. Output: captions.ass + narration.wav (clips joined with `gap` seconds of silence).
"""
import json, subprocess, sys, pathlib

def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())

def ts(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def main(plan_path, out_dir):
    plan = json.loads(pathlib.Path(plan_path).read_text(encoding="utf-8"))
    base = pathlib.Path.cwd()  # audio paths are relative to the project root
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    gap, font = plan.get("gap", 0.15), plan.get("font", "Poppins")
    hi = plan.get("highlight", "&H0033A0FF")  # ASS BGR: orange
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,{font},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,3,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events, t, concat = [], 0.0, []
    for i, line in enumerate(plan["lines"]):
        clip = (base / line["audio"]).resolve(); d = dur(clip)
        words = line["roman"].split(); keys = {k.lower().strip("?.!,") for k in line.get("keywords", [])}
        weights = [max(len(w.strip("?.!,")), 2) for w in words]; total = sum(weights)
        # group into chunks of 1-2 short words, like the reference reels
        chunks, cur = [], []
        for w, wt in zip(words, weights):
            cur.append((w, wt))
            if len(cur) == 2 or sum(len(x[0]) for x in cur) >= 9 or w[-1] in "?.!,":
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        s = t
        for ch in chunks:
            e = s + d * sum(x[1] for x in ch) / total
            txt = " ".join((f"{{\\c{hi}}}{w}{{\\c&H00FFFFFF&}}" if w.lower().strip("?.!,") in keys else w) for w, _ in ch)
            events.append(f"Dialogue: 0,{ts(s)},{ts(e)},Word,,0,0,0,,{{\\pos(540,1180)\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{txt}")
            s = e
        concat.append(clip); t += d + gap
    (out / "captions.ass").write_text(head + "\n".join(events) + "\n", encoding="utf-8")
    # narration: clips + silence, 48 kHz mono, no tempo change
    lst = out / "concat.txt"; sil = out / "gap.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                    "-t", str(gap), sil], check=True)
    parts = []
    for c in concat:
        r = out / f"_{c.stem}_48k.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(c), "-ar", "48000", "-ac", "1", str(r)], check=True)
        parts += [f"file '{r.resolve()}'", f"file '{sil.resolve()}'"]
    lst.write_text("\n".join(parts) + "\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", out / "narration.wav"], check=True)
    print(f"captions.ass + narration.wav written; total {t:.2f}s, {len(events)} caption chunks")

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit("usage: reel_captions.py plan.json OUT_DIR")
    main(sys.argv[1], sys.argv[2])
