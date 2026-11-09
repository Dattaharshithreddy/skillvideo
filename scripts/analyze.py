#!/usr/bin/env python3
"""Frame-by-frame analysis of a short: cuts, shot lengths, camera motion, brightness/saturation/contrast,
plus first/last-frame contact sheets per shot. Compares against targets measured from the reference channel.

Usage:
  python analyze.py VIDEO.mp4 [--look A|B|C] [--out DIR]
Writes DIR/report.md and DIR/shots_XX.png (default DIR = <video folder>/analysis).
Use it on your own render (QC) or on any reference video you have locally (to study it).
"""
import argparse, json, statistics, subprocess, sys
from pathlib import Path

# Measured Nov 2026 from 6 reference Shorts (see references/shot-breakdowns.md)
TARGETS = {
    "pacing": {"avg_shot": (1.2, 2.2), "max_shot": (0, 4.5), "still_frac": (0, 0.25), "motion_median": (12, 32),
               "duration": (25, 48)},
    "A": {"luma": (0.45, 0.72), "sat": (0.40, 0.65), "contrast": (0.12, 0.22)},   # bright explainer
    "B": {"luma": (0.33, 0.55), "sat": (0.25, 0.48), "contrast": (0.17, 0.32)},   # realistic story
    "C": {"luma": (0.55, 0.75), "sat": (0.25, 0.45), "contrast": (0.10, 0.18)},   # science / abstract
}
SW, SH = 24, 42          # motion/cut probe size (same scale the targets were measured at)
FPS_PROBE = 12


def ff(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode()[-2000:])
    return r.stdout


def probe(path):
    out = json.loads(ff(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height:format=duration", "-of", "json", str(path)]))
    return float(out["format"]["duration"]), out["streams"][0]["width"], out["streams"][0]["height"]


def raw_frames(path, fps, w, h):
    data = ff(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}:flags=area",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    n = w * h * 3
    return [data[i:i + n] for i in range(0, len(data) - n + 1, n)]


def detect_cuts(diffs, step, hi=40, ratio=1.7, gap=0.5):
    """A cut (or fast whip transition) = a frame-difference spike well above the last few frames."""
    cuts = [0.0]
    for i in range(2, len(diffs)):
        base = min(diffs[max(0, i - 3):i])
        t = (i + 1) * step
        if diffs[i] >= hi and diffs[i] >= ratio * max(base, 8) and t - cuts[-1] >= gap:
            cuts.append(round(t, 2))
    return cuts


def look_stats(path):
    fr = raw_frames(path, 1, 54, 96)
    rows = []
    for f in fr:
        L, S = [], 0.0
        for i in range(0, len(f), 3):
            r, g, b = f[i] / 255, f[i + 1] / 255, f[i + 2] / 255
            mx, mn = max(r, g, b), min(r, g, b)
            L.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
            S += (mx - mn) / mx if mx else 0
        m = sum(L) / len(L)
        rows.append((m, S / len(L), statistics.pstdev(L)))
    avg = lambda k: round(sum(r[k] for r in rows) / len(rows), 3)
    return {"luma": avg(0), "sat": avg(1), "contrast": avg(2), "luma_min": round(min(r[0] for r in rows), 2)}


def contact_sheets(path, cuts, D, outdir, per_page=8, w=270):
    from PIL import Image, ImageDraw
    h = int(w * 16 / 9)
    pages = []
    tmp = outdir / "_f.png"
    for p0 in range(0, len(cuts), per_page):
        idx = list(range(p0, min(p0 + per_page, len(cuts))))
        sheet = Image.new("RGB", (4 * w, ((len(idx) * 2 + 3) // 4) * (h + 24)), "black")
        d = ImageDraw.Draw(sheet)
        k = 0
        for i in idx:
            a, b = cuts[i], (cuts[i + 1] if i + 1 < len(cuts) else D)
            for tag, t in (("a", a + 0.08), ("b", max(a + 0.1, b - 0.12))):
                ff(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1",
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", str(tmp)])
                x, y = (k % 4) * w, (k // 4) * (h + 24)
                sheet.paste(Image.open(tmp), (x, y + 24))
                d.text((x + 4, y + 5), f"shot {i+1}{tag}  {t:.1f}s  ({b-a:.1f}s)", fill=(255, 230, 0))
                k += 1
        name = outdir / f"shots_{p0 // per_page + 1:02d}.png"
        sheet.save(name)
        pages.append(name.name)
    tmp.unlink(missing_ok=True)
    return pages


def check(val, rng):
    return "PASS" if rng[0] <= val <= rng[1] else "WARN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--look", choices=["A", "B", "C"], default="A")
    ap.add_argument("--out")
    ap.add_argument("--no-sheets", action="store_true")
    a = ap.parse_args()
    v = Path(a.video).resolve()
    out = Path(a.out) if a.out else v.parent / "analysis"
    out.mkdir(parents=True, exist_ok=True)

    D, W, H = probe(v)
    fr = raw_frames(v, FPS_PROBE, SW, SH)
    diffs = [sum(abs(x - y) for x, y in zip(fr[i], fr[i - 1])) / (SW * SH * 3) for i in range(1, len(fr))]
    cuts = detect_cuts(diffs, 1 / FPS_PROBE)
    lens = [round((cuts[i + 1] if i + 1 < len(cuts) else D) - t, 2) for i, t in enumerate(cuts)]
    pace = {"duration": round(D, 2), "shots": len(cuts), "avg_shot": round(D / len(cuts), 2),
            "max_shot": max(lens), "min_shot": min(lens),
            "motion_median": round(statistics.median(diffs), 1),
            "still_frac": round(sum(x < 10 for x in diffs) / len(diffs), 2)}
    look = look_stats(v)
    pages = [] if a.no_sheets else contact_sheets(v, cuts, D, out)

    T = TARGETS
    lines = [f"# Analysis: {v.name}", f"{W}x{H}, look target {a.look}", "", "## Pacing",
             "| metric | value | target | |", "|---|---|---|---|"]
    for k in ["duration", "avg_shot", "max_shot", "motion_median", "still_frac"]:
        lines.append(f"| {k} | {pace[k]} | {T['pacing'][k][0]}–{T['pacing'][k][1]} | {check(pace[k], T['pacing'][k])} |")
    lines += [f"| shots | {pace['shots']} | | |", "", "## Look", "| metric | value | target | |", "|---|---|---|---|"]
    for k in ["luma", "sat", "contrast"]:
        lines.append(f"| {k} | {look[k]} | {T[a.look][k][0]}–{T[a.look][k][1]} | {check(look[k], T[a.look][k])} |")
    if W * 16 != H * 9:
        lines.append(f"\nWARN: not 9:16 ({W}x{H})")
    lines += ["", "## Shots (start s → length s)", ", ".join(f"{i+1}: {c}→{l}" for i, (c, l) in enumerate(zip(cuts, lens))),
              "", "## Contact sheets (a = first frame, b = last frame of each shot)"] + [f"- {p}" for p in pages]
    lines += ["", "## How to read",
              "- a vs b nearly identical → the shot is static: add a camera move (push-in/orbit/follow) or shorten it.",
              "- max_shot WARN → split that shot or add a whip move in the middle.",
              "- still_frac WARN → too many frozen moments; use `still: false` clips or stronger motion prompts.",
              "- luma/sat WARN → adjust the `style` lighting/colour words, or regenerate the outlier stills.",
              "- Cut detection also counts fast whip moves inside one scene; that matches how the reference cuts."]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n→ {out/'report.md'}")


if __name__ == "__main__":
    main()
