"""Step 1: encode every prompt with Wan's UMT5 text encoder once, save the embeddings, then exit (keeps RAM low)."""
import json, torch, ftfy, html, re
from transformers import AutoTokenizer, UMT5EncoderModel
M = '/opt/wan/model'
P = json.load(open('ai/prompts.json'))
tok = AutoTokenizer.from_pretrained(M, subfolder='tokenizer')
te = UMT5EncoderModel.from_pretrained(M, subfolder='text_encoder', torch_dtype=torch.bfloat16, device_map='cuda').eval()
def clean(t): return re.sub(r'\s+', ' ', html.unescape(html.unescape(ftfy.fix_text(t)))).strip()
@torch.no_grad()
def enc(t):
    x = tok([clean(t)], padding='max_length', max_length=512, truncation=True, add_special_tokens=True, return_attention_mask=True, return_tensors='pt')
    n = int(x.attention_mask.gt(0).sum()); e = te(x.input_ids.cuda(), x.attention_mask.cuda()).last_hidden_state[0, :n]
    return torch.cat([e, e.new_zeros(512 - n, e.size(1))])[None].cpu()
out = {'neg': enc(P['neg'])}
for c in P['clips']: out[c['id']] = enc(c['prompt'])
torch.save(out, 'ai/embeds.pt'); print('ENCODED', len(out))
