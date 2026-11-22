"""Depth map for a photo with Depth Anything V2 (CPU). Writes <out>/<name>_depth.png (16-bit, near = bright)."""
import sys, numpy as np, torch
from PIL import Image
from transformers import pipeline
src, out = sys.argv[1], sys.argv[2]
pipe = pipeline('depth-estimation', model=sys.argv[3] if len(sys.argv) > 3 else 'depth-anything/Depth-Anything-V2-Large-hf', device='cpu')
im = Image.open(src).convert('RGB')
d = pipe(im)['predicted_depth'].squeeze().numpy().astype(np.float32)
d = np.array(Image.fromarray(d).resize(im.size, Image.BICUBIC))
d = (d - d.min()) / (d.max() - d.min() + 1e-6)
Image.fromarray((d * 65535).astype(np.uint16)).save(out); print('depth', out, d.shape)
