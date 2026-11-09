# cgi-shorts

A Claude Code skill for making Zack D Films-style vertical 3D shorts. It has two engines:
- **Blender** (`"engine": "blender"`): real 3D scenes rendered on your own NVIDIA GPU.
- **AI video** via fal.ai (default).

## Install on a GPU server (Amazon Linux 2023 or Ubuntu)
```bash
git clone https://github.com/Dattaharshithreddy/skillvideo ~/.claude/skills/cgi-shorts
bash ~/.claude/skills/cgi-shorts/blender/setup_server.sh
source ~/.bashrc
```
Then run `claude` and ask for a short. Start with `SKILL.md` and `references/blender-mode.md`.
