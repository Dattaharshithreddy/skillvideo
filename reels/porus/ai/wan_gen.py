"""Step 2: generate each miniature clip with Wan 2.2 TI2V-5B from the saved prompt embeddings (no text encoder in memory).
Usage: python ai/wan_gen.py [clip ids...]   (default: all clips not yet rendered)"""
import json, os, sys, time, torch
from diffusers import WanPipeline, AutoencoderKLWan
from diffusers.utils import export_to_video
M = 'Wan-AI/Wan2.2-TI2V-5B-Diffusers'
W, H, NF, STEPS = int(os.environ.get('W', 576)), int(os.environ.get('H', 1024)), int(os.environ.get('NF', 97)), int(os.environ.get('STEPS', 30))
P = json.load(open('ai/prompts.json')); E = torch.load('ai/embeds.pt')
vae = AutoencoderKLWan.from_pretrained(M, subfolder='vae', torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(M, vae=vae, text_encoder=None, tokenizer=None, torch_dtype=torch.bfloat16).to('cuda')
os.makedirs('ai/clips', exist_ok=True)
ids = sys.argv[1:] or [c['id'] for c in P['clips']]
for i, cid in enumerate(ids):
    out = f'ai/clips/{cid}.mp4'
    if os.path.exists(out): continue
    t0 = time.time(); g = torch.Generator('cuda').manual_seed(1000 + i)
    fr = pipe(prompt_embeds=E[cid].to('cuda', torch.bfloat16), negative_prompt_embeds=E['neg'].to('cuda', torch.bfloat16),
              height=H, width=W, num_frames=NF, guidance_scale=5.0, num_inference_steps=STEPS, generator=g).frames[0]
    export_to_video(fr, out, fps=24)
    print('CLIP', cid, round(time.time() - t0), 's', flush=True)
print('GEN_DONE')
