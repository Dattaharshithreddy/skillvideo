#!/usr/bin/env python3
"""qc_frames.py - automatic checks for frame sequences and finished videos.

    python3 qc_frames.py check  <frames_dir> [--ext png]
    python3 qc_frames.py video  <file.mp4> [--width 1080 --height 1920 --fps 24] [--report out.md]
    python3 qc_frames.py assemble <frames_dir> <out.mp4> [--fps 24] [--audio a.wav] [--ext png]

`check` finds missing or duplicated frame numbers, mixed image sizes and unreadable files.
`video` checks size, frame rate, audio/video length, and measures holds (still frames), fast bursts and
sudden jumps so a person knows where to look. It cannot judge drawing or acting.
Needs ffmpeg/ffprobe on the path, plus Pillow and numpy. Exit code 1 means a hard failure.
"""
import argparse, hashlib, json, os, re, subprocess, sys


def _frames(d, ext):
    out = []
    for n in sorted(os.listdir(d)):
        m = re.search(r'(\d+)\.%s$' % re.escape(ext), n)
        if m:
            out.append((int(m.group(1)), os.path.join(d, n)))
    return sorted(out)


def check(d, ext='png'):
    from PIL import Image
    fr = _frames(d, ext)
    problems, notes = [], []
    if not fr:
        print('FAIL: no .%s frames with a number in the name in %s' % (ext, d)); return 1
    nums = [n for n, _ in fr]
    dup = sorted({n for n in nums if nums.count(n) > 1})
    if dup:
        problems.append('frame numbers used more than once: %s' % dup[:20])
    missing = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
    if missing:
        problems.append('%d missing frame numbers, first ones: %s' % (len(missing), missing[:20]))
    sizes, last, same, longest, run = {}, None, 0, 0, 0
    for n, p in fr:
        try:
            with Image.open(p) as im:
                sizes.setdefault(im.size, []).append(n)
        except Exception as e:
            problems.append('frame %d cannot be opened: %s' % (n, e)); continue
        h = hashlib.md5(open(p, 'rb').read()).hexdigest()
        if h == last:
            same += 1; run += 1; longest = max(longest, run)
        else:
            run = 0
        last = h
    if len(sizes) > 1:
        problems.append('mixed image sizes: %s' % {k: len(v) for k, v in sizes.items()})
    notes.append('%d frames, numbers %d to %d, size %s' % (len(fr), nums[0], nums[-1], list(sizes)[0] if sizes else '?'))
    notes.append('%d frames identical to the one before (holds); longest hold %d frames' % (same, longest + 1 if longest else 0))
    for x in notes:
        print('  ', x)
    for x in problems:
        print('FAIL:', x)
    print('PASS' if not problems else '%d problem(s)' % len(problems))
    return 1 if problems else 0


def _probe(path):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video')
    a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    num, den = v['r_frame_rate'].split('/')
    return dict(width=int(v['width']), height=int(v['height']), fps=float(num) / float(den),
                vdur=float(v.get('duration') or j['format']['duration']), adur=float(a['duration']) if a and a.get('duration') else None,
                nframes=int(v['nb_frames']) if v.get('nb_frames') else None, vcodec=v['codec_name'], acodec=a['codec_name'] if a else None)


def video(path, width=1080, height=1920, fps=24.0, report=None):
    import numpy as np
    info = _probe(path)
    problems, lines = [], []
    if (info['width'], info['height']) != (width, height):
        problems.append('size is %dx%d, expected %dx%d' % (info['width'], info['height'], width, height))
    if abs(info['fps'] - fps) > 0.01:
        problems.append('frame rate is %.3f, expected %.3f' % (info['fps'], fps))
    if info['adur'] is None:
        problems.append('no audio stream')
    elif abs(info['adur'] - info['vdur']) > 0.1:
        problems.append('audio (%.2f s) and video (%.2f s) differ by more than 0.1 s' % (info['adur'], info['vdur']))
    w, h = 54, 96
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'scale=%d:%d' % (w, h), '-pix_fmt', 'gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)
    n = len(fr)
    if info['nframes'] and info['nframes'] != n:
        problems.append('container says %d frames, decoded %d' % (info['nframes'], n))
    d = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2))               # mean change per frame, 0-255
    still = d < 0.15
    runs, run = [], 0
    for i, s in enumerate(still):
        if s:
            run += 1
        else:
            if run:
                runs.append((i - run, run)); run = 0
    if run:
        runs.append((len(still) - run, run))
    longest = max(runs, key=lambda r: r[1]) if runs else (0, 0)
    jumps = [int(i) + 1 for i in np.where(d > 28)[0]]              # cuts, flashes, or flicker: a person should look at each
    dark = [int(i) for i in np.where(fr.mean(axis=(1, 2)) < 6)[0]]
    lines += ['file: %s' % os.path.basename(path),
              'size %dx%d, %.2f fps, %d frames, %.2f s, video %s, audio %s' % (info['width'], info['height'], info['fps'], n, info['vdur'], info['vcodec'], info['acodec']),
              'still frames: %.0f%% of the film; longest hold %d frames starting at frame %d' % (100.0 * still.mean(), longest[1], longest[0]),
              'holds of 24 frames or more (check they have some life): %s' % ([r for r in runs if r[1] >= 24][:12] or 'none'),
              'big frame-to-frame jumps at frames (each should be a planned cut or hit): %s' % (jumps[:40] or 'none'),
              'near-black frames: %d (first %s, last %s)' % (len(dark), dark[0] if dark else '-', dark[-1] if dark else '-')]
    for x in lines:
        print('  ', x)
    for x in problems:
        print('FAIL:', x)
    print('PASS (automatic checks only; drawing, motion and sound still need a person)' if not problems else '%d problem(s)' % len(problems))
    if report:
        with open(report, 'w') as f:
            f.write('# Automatic QC\n\n' + '\n'.join('- ' + x for x in lines) + '\n\n' +
                    ('**Automatic result: PASS**\n' if not problems else '**Automatic result: FAIL**\n' + '\n'.join('- ' + x for x in problems) + '\n') +
                    '\nThese checks cover frame integrity, format and audio length only (rubric lines 10-12 in part).\n')
    return 1 if problems else 0


def assemble(d, out, fps=24, audio=None, ext='png'):
    fr = _frames(d, ext)
    if check(d, ext):
        print('not assembling: fix the frame sequence first'); return 1
    lst = os.path.join(d, '_frames.txt')
    with open(lst, 'w') as f:
        for _, p in fr:
            f.write("file '%s'\nduration %f\n" % (os.path.abspath(p), 1.0 / fps))
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst]
    if audio:
        cmd += ['-i', audio]
    cmd += ['-r', str(fps), '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-tune', 'animation', '-pix_fmt', 'yuv420p']
    if audio:
        cmd += ['-c:a', 'aac', '-b:a', '160k', '-shortest']
    cmd += ['-movflags', '+faststart', out]
    subprocess.run(cmd, check=True); os.remove(lst)
    print('wrote', out)
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check'); c.add_argument('dir'); c.add_argument('--ext', default='png')
    v = sub.add_parser('video'); v.add_argument('file'); v.add_argument('--width', type=int, default=1080); v.add_argument('--height', type=int, default=1920)
    v.add_argument('--fps', type=float, default=24.0); v.add_argument('--report')
    a = sub.add_parser('assemble'); a.add_argument('dir'); a.add_argument('out'); a.add_argument('--fps', type=int, default=24); a.add_argument('--audio'); a.add_argument('--ext', default='png')
    args = ap.parse_args()
    if args.cmd == 'check':
        sys.exit(check(args.dir, args.ext))
    if args.cmd == 'video':
        sys.exit(video(args.file, args.width, args.height, args.fps, args.report))
    sys.exit(assemble(args.dir, args.out, args.fps, args.audio, args.ext))
