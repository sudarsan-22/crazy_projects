"""Stage 1: copy originals into source/ (never modify them), hash, probe, build analysis proxies + WAVs."""
import hashlib
import json
import shutil
from pathlib import Path

from . import config, ff
from .state import AUDIO_EXT, IMAGE_EXT, VIDEO_EXT, Production, create


def sha256(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def proxy_paths(prod: Production, src: Path):
    return {"proxy": prod.d("analysis/proxy") / f"{src.stem}.mp4",
            "wav48": prod.d("analysis/wav") / f"{src.stem}_48k.wav",
            "wav16": prod.d("analysis/wav") / f"{src.stem}_16k.wav"}


def make_proxy(src: Path, dst: Path, info: dict):
    """Display-oriented, SDR, CFR 30 fps proxy with the long side = 960 px. Timeline = source timeline."""
    w, h = info["width"], info["height"]
    scale = (f"scale={config.PROXY_LONG_SIDE}:-2" if w >= h else f"scale=-2:{config.PROXY_LONG_SIDE}")
    vf = []
    if info.get("hdr"):
        vf.append(ff.tonemap_chain("mobius"))
    vf += [scale, f"fps={config.PROXY_FPS}", "format=yuv420p"]
    ff.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-map", "0:v:0", "-an",
            "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-g", str(config.PROXY_FPS), dst])


def ingest(files=(), prod: Production | None = None, slug=None, proxies=True):
    files = [Path(f).resolve() for f in files]
    if prod is None:
        prod = create(slug or (files[0].stem if files else "reel"))
    src_dir = prod.d("source")
    copied = []
    for f in files:
        if f.parent == src_dir:
            continue
        dst = src_dir / f.name
        if dst.exists():
            if dst.stat().st_size == f.stat().st_size:
                continue
            dst = src_dir / f"{f.stem}_{len(list(src_dir.iterdir()))}{f.suffix}"
        shutil.copy2(f, dst)                          # copy, never move: the original stays untouched
        copied.append(dst.name)

    sources = []
    for f in sorted(src_dir.iterdir()):
        if f.name == "sources.json" or f.name.startswith(".") or not f.is_file():
            continue
        ext = f.suffix.lower()
        kind = "video" if ext in VIDEO_EXT else "image" if ext in IMAGE_EXT else "audio" if ext in AUDIO_EXT else "other"
        entry = {"file": f.name, "kind": kind, "bytes": f.stat().st_size, "sha256": sha256(f)}
        if kind == "video":
            info = ff.media_info(f)
            entry["info"] = info
            if proxies and info.get("has_video"):
                pp = proxy_paths(prod, f)
                if not pp["proxy"].exists():
                    make_proxy(f, pp["proxy"], info)
                if info.get("has_audio"):
                    if not pp["wav48"].exists():
                        ff.extract_wav(f, pp["wav48"], 48000, mono=False)
                    if not pp["wav16"].exists():
                        ff.extract_wav(f, pp["wav16"], 16000, mono=True)
                entry["proxy"] = str(pp["proxy"].relative_to(prod.root))
                entry["wav48"] = str(pp["wav48"].relative_to(prod.root)) if info.get("has_audio") else None
                entry["wav16"] = str(pp["wav16"].relative_to(prod.root)) if info.get("has_audio") else None
            flags = [k for k in ("vfr", "hdr") if info.get(k)] + ([f"rot{info['rotation']}"] if info.get("rotation") else [])
            entry["flags"] = flags
        sources.append(entry)
    (src_dir / "sources.json").write_text(json.dumps(sources, indent=2))
    vids = [s for s in sources if s["kind"] == "video"]
    prod.mark("ingested", videos=len(vids), copied=copied,
              total_video_s=round(sum(s["info"]["duration"] for s in vids), 2))
    return prod, sources
