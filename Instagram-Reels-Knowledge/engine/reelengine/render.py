"""Stage 7: compile the authored EDL and render it with the (unchanged) v0 renderer tools/reel_render.py."""
import json
import shutil
import subprocess
import time
from pathlib import Path

from . import config
from .edl.compile import compile_edl
from .state import Production


def render_variant(prod: Production, edl_path, variant, version, draft=False, log=print):
    build = prod.d("build")
    c = compile_edl(edl_path, variant=variant, version=version, out_dir=build, analysis_dir=prod.d("analysis"))
    for p in c["report"]["problems"]:
        log(f"  ! {p}")
    t0 = time.time()
    # the v0 renderer is stdlib-only: run it exactly as before, with system Python in isolated mode
    cmd = ["/usr/bin/python3", "-I", str(config.TOOLS / "reel_render.py"), str(c["render_edl"])]
    if draft:
        cmd.append("--draft")
    p = subprocess.run(cmd, capture_output=True, text=True)
    logf = build / f"render_v{version}_{variant}.log"
    logf.write_text(p.stdout + "\n--- stderr ---\n" + p.stderr)
    if p.returncode:
        raise RuntimeError(f"reel_render failed for {variant} (log: {logf}):\n{(p.stdout + p.stderr)[-2500:]}")
    if (build / "render_cmd.txt").exists():
        shutil.copy(build / "render_cmd.txt", build / f"graph_v{version}_{variant}.txt")
    out = Path(json.loads(Path(c["render_edl"]).read_text())["output"])
    wall = round(time.time() - t0, 1)
    log(f"  rendered {out.name} in {wall}s ({c['report']['total']:.2f}s planned)")
    return {"output": out, "resolved": c["resolved"], "report": c["report"], "wall_s": wall,
            "render_edl": c["render_edl"]}


def render(prod: Production, edl_path=None, variants=None, version=None, draft=False, log=print):
    edl_path = Path(edl_path or prod.root / "build" / "edl.json").resolve()
    version = version or prod.next_version()
    snap = prod.d("build") / f"edl.v{version}.json"
    if edl_path != snap:
        shutil.copy(edl_path, snap)                 # history: every rendered version keeps its EDL
    raw = json.loads(edl_path.read_text())
    rights = raw.get("audio_rights", "in_app_library")
    if variants is None:
        variants = ["clean"] if rights == "in_app_library" else ["final"]
        if raw.get("reference_audio") or (rights == "in_app_library" and raw.get("music")):
            variants.append("syncguide")
    results = {}
    for v in variants:
        results[v] = render_variant(prod, snap, v, version, draft=draft, log=log)
    st = prod.load()
    st["versions"][str(version)] = {"edl": snap.name, "variants": {k: r["output"].name for k, r in results.items()},
                                    "draft": draft, "wall_s": {k: r["wall_s"] for k, r in results.items()}}
    prod.save(st)
    prod.mark("rendered", version=version, variants=list(results), draft=draft)
    return version, results
