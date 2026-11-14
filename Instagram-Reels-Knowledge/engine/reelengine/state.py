"""Production folders (KB doc 26 layout) + production.json state machine (KB doc 32 §10)."""
import datetime
import json
import re
from pathlib import Path

from . import config

SUBDIRS = ["source", "analysis", "audio", "plan", "build", "renders", "publish", "licenses"]
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".mts", ".3gp"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus"}


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def slugify(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:40] or "reel"


class Production:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state_path = self.root / "production.json"

    @property
    def id(self):
        return self.root.name.split("_")[0]

    def d(self, sub):
        p = self.root / sub
        p.mkdir(parents=True, exist_ok=True)
        return p

    def load(self):
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {"id": self.id, "folder": self.root.name, "created": now(), "stages": {}, "versions": {}, "log": []}

    def save(self, st):
        self.state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False))

    def mark(self, stage, **info):
        st = self.load()
        st["stages"][stage] = {"at": now(), **info}
        st["log"].append(f"{now()} {stage}")
        self.save(st)
        return st

    def videos(self):
        return sorted(p for p in self.d("source").iterdir() if p.suffix.lower() in VIDEO_EXT)

    def next_version(self):
        nums = [int(m.group(1)) for p in self.d("renders").iterdir()
                if (m := re.match(r"v(\d+)_", p.name))]
        return (max(nums) + 1) if nums else 1

    def latest_version(self):
        nums = [int(m.group(1)) for p in self.d("renders").iterdir()
                if (m := re.match(r"v(\d+)_", p.name))]
        return max(nums) if nums else None


def all_productions():
    return sorted(p for p in config.PRODUCTIONS.iterdir() if p.is_dir() and re.match(r"P\d{3}_", p.name))


def find(ref):
    p = Path(ref)
    if p.is_dir():
        return Production(p)
    hits = [q for q in all_productions() if q.name.startswith(ref)]
    if len(hits) != 1:
        raise SystemExit(f"Production '{ref}' not found (or ambiguous): {[h.name for h in hits]}")
    return Production(hits[0])


def create(slug, date=None):
    nums = [int(p.name[1:4]) for p in all_productions()]
    pid = f"P{(max(nums) + 1) if nums else 1:03d}"
    date = date or datetime.date.today().isoformat()
    root = config.PRODUCTIONS / f"{pid}_{date}_{slugify(slug)}"
    for s in SUBDIRS:
        (root / s).mkdir(parents=True, exist_ok=True)
    prod = Production(root)
    prod.save(prod.load())
    return prod
