"""Shot timing for the Puru miniature reel.
python3 build_timing.py                      -> estimate from text length (no narration yet)
python3 build_timing.py narr/sentences.json  -> exact: per-sentence start/end from the Swaram narration (anti-drift)
Writes mg/src/timing.json: lines, starts, durs (seconds), nf (frames per shot), end (frames), sentences."""
import json, sys, os
FPS = 30; HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(os.path.join(HERE, 'brief/plan.json')))
L = plan['lines']; n = len(L)
sents = []
if len(sys.argv) > 1:
    sents = json.load(open(sys.argv[1]))                        # [{para, start, end, text}]
    starts = [min(s['start'] for s in sents if s['para'] == i) for i in range(n)]
    total = max(s['end'] for s in sents) + 0.8
    ends = starts[1:] + [total]
    starts[0] = 0.0
    durs = [b - a for a, b in zip(starts, ends)]
else:
    rate = 13.5                                                  # Telugu characters per second in Datta's narration pace
    durs = [max(5.0, len(l['text'].replace(' ', '')) / rate + 0.9) for l in L]
    starts = [sum(durs[:i]) for i in range(n)]
sc_ = float(os.environ.get('NFSCALE', 1.0))                     # test runs only: shrink every shot
if sc_ != 1.0: durs = [d * sc_ for d in durs]; starts = [sum(durs[:i]) for i in range(n)]
nf = [round((starts[i] + durs[i]) * FPS) - round(starts[i] * FPS) for i in range(n)]
out = {'lines': [{'shot': l['shot'], 'text': l['text'], 'keywords': l['keywords']} for l in L],
       'starts': [round(x, 3) for x in starts], 'durs': [round(x, 3) for x in durs], 'nf': nf, 'end': sum(nf), 'sentences': sents,
       'estimated': not sents}
json.dump(out, open(os.path.join(HERE, 'mg/src/timing.json'), 'w'), ensure_ascii=False, indent=1)
print('shots', n, 'total', round(sum(durs), 1), 's', 'frames', sum(nf), 'estimated' if not sents else 'exact')
