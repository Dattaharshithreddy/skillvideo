# Backup CPU render on GitHub runners

Emergency backup only — Kaggle (free GPU) is the main renderer. Needs the repo secret `HF_TOKEN` (write access to the
`HarshithReddy05/tirumala-reel` bucket).

- Render: create or change `gha.json` here, e.g. `{ "slices": 40, "spp": 24, "respct": 72 }`. Frames go to the bucket's `seq2/`.
  Pushing it again cancels a run in progress. `"only": [3, 7]` re-renders just those slices; `"test": true` times 3 frames.
- Finish: create or change `post.json` (any content). Adds voice, music and the Telugu overlay; the final MP4 lands in the
  bucket's `final/` and, encrypted with `hf/handoff_pub.pem`, on the `tirumala-final` branch.
