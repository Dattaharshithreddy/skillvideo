#!/usr/bin/env python3
"""3d-asset-atlas CLI. Standard library only (needs `git` on PATH for GitHub packs).

  atlas.py list [--kind asset-pack|api|web|generator|addon|tool|index]
  atlas.py find <subject...>            e.g. find train | find king | find hill rock
  atlas.py info <id>
  atlas.py fetch <id> [--set NAME]      download a pack into assets/<id>/
  atlas.py fetch nasa --path "3D Models/Astronaut"     only part of a big repo
  atlas.py polyhaven search <words> [--type models|hdris|textures]
  atlas.py polyhaven get <asset_id> [--res 2k] [--type models|hdris|textures]
  atlas.py 3dassets search <words>
  atlas.py 3dassets get <slug>
  atlas.py used                         what is downloaded + licence of each
  atlas.py credits                      credit lines to paste in the reel caption

Everything lands in assets/ (git-ignored). assets/manifest.json records source and licence.
"""
import argparse, datetime, json, os, pathlib, re, shutil, subprocess, sys, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = pathlib.Path(os.environ.get("ATLAS_ASSETS", ROOT / "assets"))
MANIFEST = ASSETS / "manifest.json"
UA = "3d-asset-atlas/1.0 (personal reel pipeline)"   # Poly Haven's API terms ask for an identifying user-agent

# words people say -> category tags used in the catalog
SYNONYMS = {
    "train": "trains", "locomotive": "trains", "railway": "trains", "rail": "trains", "metro": "trains",
    "human": "humans", "person": "humans", "people": "humans", "man": "humans", "woman": "humans", "villager": "humans",
    "king": "kings", "queen": "queens", "emperor": "kings", "raja": "kings", "rani": "queens", "royal": "kings",
    "soldier": "kingdom", "knight": "kingdom", "castle": "kingdom", "fort": "kingdom", "palace": "kingdom", "medieval": "kingdom",
    "building": "buildings", "house": "buildings", "tower": "buildings", "temple": "temples", "statue": "statues", "idol": "statues",
    "rock": "rocks", "stone": "rocks", "boulder": "rocks", "hill": "hills", "mountain": "mountains", "ghat": "hills",
    "tree": "trees", "forest": "trees", "plant": "plants", "grass": "nature", "river": "rivers", "landscape": "terrain",
    "location": "locations", "place": "locations", "map": "locations", "town": "city", "street": "roads", "road": "roads",
    "car": "vehicles", "bus": "vehicles", "bike": "vehicles", "plane": "aircraft", "aeroplane": "aircraft", "flight": "aircraft",
    "body": "anatomy", "organ": "anatomy", "heart": "anatomy", "brain": "anatomy", "bone": "anatomy", "muscle": "anatomy",
    "drug": "molecules", "medicine": "molecules", "molecule": "molecules", "protein": "molecules", "tablet": "molecules",
    "sky": "hdri", "lighting": "hdri", "planet": "space", "rocket": "space", "satellite": "space", "animal": "animals",
    "room": "interiors", "kitchen": "interiors", "history": "history",
}


def catalog():
    return json.loads((ROOT / "catalog" / "sources.json").read_text())["sources"]


def by_id(i):
    for s in catalog():
        if s["id"] == i:
            return s
    sys.exit(f"no source '{i}'. Run: atlas.py list")


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest):
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_name(dest.name + ".part")
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.rename(dest)
    return dest


def safe_name(s):
    """Names from remote JSON become file names: keep them inside the target folder."""
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", str(s)).strip("._")
    return s or "unnamed"


def record(key, src, **extra):
    ASSETS.mkdir(parents=True, exist_ok=True)
    m = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    entry = dict(source=src["id"], name=src["name"], url=src["url"], license=src["license"],
                 credit=src.get("credit", ""), fetched=datetime.date.today().isoformat())
    entry.update(extra)                     # per-asset values (e.g. a 3dassets.dev credit) override the source defaults
    m[key] = entry
    MANIFEST.write_text(json.dumps(m, indent=1) + "\n")


# ---------------------------------------------------------------- commands
def cmd_list(a):
    for s in catalog():
        if a.kind and s["kind"] != a.kind:
            continue
        print(f"{s['id']:24} {s['kind']:11} {s['license'][:34]:34} {', '.join(s['categories'][:6])}")


def cmd_find(a):
    want = set()
    for w in a.words:
        w = w.lower()
        w1 = w[:-1] if w.endswith("s") else w
        want |= {w, w1, SYNONYMS.get(w, w), SYNONYMS.get(w1, w1)}
    hits = []
    for s in catalog():
        if s["kind"] == "index":
            continue
        cats = set(s["categories"])
        text = (s["what"] + " " + s["name"]).lower()
        score = 3 * len(want & cats) + sum(1 for w in want if re.search(r"\b" + re.escape(w), text))
        if "everything" in cats:
            score += 1
        if score:
            hits.append((score, s))
    if not hits:
        print("nothing in the catalog. Try BlenderKit / Sketchfab, or generate it (see SUBJECTS.md).")
        return
    order = {"asset-pack": 0, "api": 1, "web": 2, "addon": 3, "generator": 4, "tool": 5}
    for score, s in sorted(hits, key=lambda h: (-h[0], order.get(h[1]["kind"], 9))):
        how = s["fetch"]["method"]
        how = {"git": f"atlas.py fetch {s['id']}", "toxsam": f"atlas.py fetch {s['id']} --set <name>",
               "polyhaven": "atlas.py polyhaven search <words>", "3dassets": "atlas.py 3dassets search <words>"}.get(how, "manual: " + s["url"])
        print(f"[{s['kind']}] {s['id']}  -  {s['license']}\n    {s['what']}\n    get: {how}\n")


def cmd_info(a):
    print(json.dumps(by_id(a.id), indent=1, ensure_ascii=False))


def git(*args, cwd=None):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def fetch_git(s, dest, only=None):
    f = dict(s["fetch"])
    if only:
        f["paths"] = only
    if dest.exists():
        print(f"already there: {dest} (delete it to re-download)")
        return
    url = f"https://github.com/{f['repo']}.git"
    if f.get("paths"):
        git("clone", "--depth", "1", "--filter=blob:none", "--sparse", "-q", url, str(dest))
        git("sparse-checkout", "set", "--no-cone", *["/" + p.strip("/") + ("" if "." in p.split("/")[-1] else "/") for p in f["paths"]], cwd=dest)
    else:
        git("clone", "--depth", "1", "-q", url, str(dest))


def fetch_toxsam(s, dest, which):
    base = f"https://raw.githubusercontent.com/{s['fetch']['registry']}/main/data/"
    projects = http_json(base + "projects.json")
    names = {p["id"].removeprefix("pm-"): p for p in projects}
    if not which:
        print("pick a set with --set NAME:")
        for n, p in names.items():
            print(f"  {n:28} {p['description']}")
        return False
    if which not in names:
        sys.exit(f"no set '{which}'. Run without --set to list them.")
    p = names[which]
    items = http_json(base + p["asset_data_file"])
    out = dest / safe_name(which)
    n = 0
    for it in items:
        u = it.get("model_file_url", "")
        if urllib.parse.urlparse(u).netloc != "raw.githubusercontent.com":
            continue
        ext = pathlib.PurePosixPath(urllib.parse.urlparse(u).path).suffix.lower()
        if ext not in (".glb", ".gltf", ".fbx"):
            continue
        download(u, out / (safe_name(it["name"]) + ext))
        n += 1
    print(f"{n} models -> {out}  ({p.get('license', '?')})")
    return True


def cmd_fetch(a):
    s = by_id(a.id)
    m = s["fetch"]["method"]
    dest = ASSETS / s["id"]
    if m == "git":
        fetch_git(s, dest, a.path)
        record(s["id"], s, path=str(dest.relative_to(ASSETS)))
        print(f"-> {dest}\nlicence: {s['license']}")
    elif m == "toxsam":
        if fetch_toxsam(s, dest, a.set):
            record(f"{s['id']}/{a.set}", s, path=f"{s['id']}/{a.set}")
    elif m == "polyhaven":
        print("use: atlas.py polyhaven search <words>   then   atlas.py polyhaven get <asset_id>")
    elif m == "3dassets":
        print("use: atlas.py 3dassets search <words>   then   atlas.py 3dassets get <slug>")
    else:
        print(f"manual source: {s['url']}\n{s['fetch'].get('hint', '')}\nlicence: {s['license']}")


def cmd_polyhaven(a):
    s = by_id("polyhaven")
    api = s["fetch"]["api"]
    if a.action == "search":
        allx = http_json(f"{api}/assets?t={a.type}")
        words = [w.lower() for w in a.args]
        rows = []
        for aid, info in allx.items():
            hay = " ".join([aid, info.get("name", ""), " ".join(info.get("categories", [])), " ".join(info.get("tags", []))]).lower()
            if all(w in hay for w in words):
                rows.append((-(info.get("download_count") or 0), aid, info.get("name", ""), ", ".join(info.get("categories", [])[:4])))
        for _, aid, name, cats in sorted(rows)[:40]:
            print(f"{aid:34} {name:34} {cats}")
        print(f"{len(rows)} match(es). get one with: atlas.py polyhaven get <asset_id> --type {a.type}")
        return
    if not a.args:
        sys.exit("give an asset id")
    aid = safe_name(a.args[0])
    files = http_json(f"{api}/files/{aid}")
    dest = ASSETS / "polyhaven" / aid

    def pick(node, *keys):
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return None
            node = node[k]
        return node

    def at_res(node):
        if not isinstance(node, dict):
            return None
        return node.get(a.res) or node.get("2k") or node.get("1k") or next(iter(node.values()), None)

    if a.type == "hdris":
        entry = pick(at_res(files.get("hdri")), "hdr") or pick(at_res(files.get("hdri")), "exr")
        if not entry:
            sys.exit("no HDRI file listed for that id")
        download(entry["url"], dest / pathlib.PurePosixPath(urllib.parse.urlparse(entry["url"]).path).name)
    else:
        key = "gltf" if a.type == "models" else "blend"
        entry = pick(at_res(files.get(key)), key)
        if not entry:
            sys.exit(f"no {key} package listed for that id; formats available: {list(files)}")
        download(entry["url"], dest / pathlib.PurePosixPath(urllib.parse.urlparse(entry["url"]).path).name)
        for rel, inc in (entry.get("include") or {}).items():
            relp = pathlib.PurePosixPath(rel)
            if relp.is_absolute() or ".." in relp.parts:
                continue
            download(inc["url"], dest / relp)
    record(f"polyhaven/{aid}", s, path=f"polyhaven/{aid}")
    print(f"-> {dest}  (CC0)")


def cmd_3dassets(a):
    s = by_id("3dassets-dev")
    api = s["fetch"]["api"]
    if a.action == "search":
        q = urllib.parse.urlencode({"q": " ".join(a.args), "limit": 30})
        for it in http_json(f"{api}/assets?{q}").get("data", []):
            print(f"{it.get('slug', '?'):40} {it.get('name', it.get('title', ''))}")
        return
    if not a.args:
        sys.exit("give a slug")
    slug = safe_name(a.args[0])
    it = http_json(f"{api}/assets/{slug}").get("data", {})
    if not it.get("cdnUrl"):
        sys.exit("that asset has no cdnUrl in the API response")
    lic = it.get("license") or {}
    download(it["cdnUrl"], ASSETS / "3dassets" / f"{slug}.glb")
    record(f"3dassets/{slug}", s, path=f"3dassets/{slug}.glb", credit=(lic.get("attributionText") if isinstance(lic, dict) else "") or "")
    print(f"-> {ASSETS / '3dassets' / (slug + '.glb')}")


def cmd_used(a):
    if not MANIFEST.exists():
        print("nothing downloaded yet")
        return
    for k, v in json.loads(MANIFEST.read_text()).items():
        print(f"{k:40} {v['license'][:60]}")


def cmd_credits(a):
    if not MANIFEST.exists():
        print("nothing downloaded yet")
        return
    need, nice = [], []
    for k, v in json.loads(MANIFEST.read_text()).items():
        lic = v["license"].upper()
        line = f"{v['name']} - {v['credit'] or v['url']} ({v['license'].split(' (')[0][:40]})"
        (nice if lic.startswith("CC0") else need).append(line)
    print("Credit required / check licence:" if need else "Nothing downloaded needs a credit.")
    for l in dict.fromkeys(need):
        print("  3D: " + l)
    if nice:
        print("Optional thanks (CC0):")
        for l in dict.fromkeys(nice):
            print("  " + l)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("list"); x.add_argument("--kind"); x.set_defaults(f=cmd_list)
    x = sub.add_parser("find"); x.add_argument("words", nargs="+"); x.set_defaults(f=cmd_find)
    x = sub.add_parser("info"); x.add_argument("id"); x.set_defaults(f=cmd_info)
    x = sub.add_parser("fetch"); x.add_argument("id"); x.add_argument("--set")
    x.add_argument("--path", action="append", help="only this folder/file of the repo (repeatable), for big repos"); x.set_defaults(f=cmd_fetch)
    x = sub.add_parser("polyhaven"); x.add_argument("action", choices=["search", "get"]); x.add_argument("args", nargs="*")
    x.add_argument("--type", default="models", choices=["models", "hdris", "textures"]); x.add_argument("--res", default="2k"); x.set_defaults(f=cmd_polyhaven)
    x = sub.add_parser("3dassets"); x.add_argument("action", choices=["search", "get"]); x.add_argument("args", nargs="*"); x.set_defaults(f=cmd_3dassets)
    sub.add_parser("used").set_defaults(f=cmd_used)
    sub.add_parser("credits").set_defaults(f=cmd_credits)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
