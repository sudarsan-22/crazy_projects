"""Autonomous loop (KB 32 §9): render → QC → AUTO fixes (≤3 rounds) → package. Creative failures are reported
for Claude to fix in the EDL; nothing is ever published."""
import json
import subprocess
import tempfile
from pathlib import Path

from . import config, qc
from .edl.text import LAYOUT
from .package import package
from .render import render
from .state import Production, now


def renormalise(path, target):
    """Two-pass loudnorm on the audio only (video stream copied)."""
    path = Path(path)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af",
                        f"loudnorm=I={target}:TP={config.TRUE_PEAK}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
    ln = (f"loudnorm=I={target}:TP={config.TRUE_PEAK}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / path.name
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-map", "0:v", "-map",
                        "0:a", "-c:v", "copy", "-af", ln, "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                        "-movflags", "+faststart", str(tmp)], check=True)
        tmp.replace(path)


def move_text(edl, report, res):
    """Shift EDL text items whose rendered box leaves the safe zone. Returns the list of changes."""
    W, H = edl.get("width", 1080), edl.get("height", 1920)
    n_raw = len(edl.get("text", []))
    changes = []
    for b in report["text_boxes"]:
        if b.get("inside_safe_zone", True) or b["box"] is None or b["line"] >= n_raw:
            continue
        x0, y0, x1, y1 = b["box"]
        dx = (config.SAFE_LEFT - x0 + 6) if x0 < config.SAFE_LEFT else \
            ((W - config.SAFE_RIGHT) - x1 - 6) if x1 > W - config.SAFE_RIGHT else 0
        dy = (config.SAFE_TOP - y0 + 6) if y0 < config.SAFE_TOP else \
            ((H - config.SAFE_BOTTOM) - y1 - 6) if y1 > H - config.SAFE_BOTTOM else 0
        it = edl["text"][b["line"]]
        style = res["text"][b["line"]]["style"]
        x, y = it.get("pos") or LAYOUT[style][0]
        it["pos"] = [int(x + dx), int(y + dy)]
        changes.append(f"text '{it['text'][:30]}' moved by ({dx:+d},{dy:+d}) px into the safe zone")
    return changes


def deliver(prod: Production, edl_path=None, max_rounds=3, draft=False, log=print):
    edl_path = Path(edl_path or prod.root / "build" / "edl.json").resolve()
    decisions = prod.d("plan") / "decisions.md"
    history = []
    for rnd in range(1, max_rounds + 1):
        version, results = render(prod, edl_path, draft=draft, log=log)
        verdicts = {}
        for variant in results:
            rep = qc.run(prod, version, variant, evidence=(variant != "syncguide"), log=log)
            verdicts[variant] = rep
        main = "clean" if "clean" in verdicts else "final"
        rep = verdicts[main]
        res = json.loads((prod.root / "build" / f"edl.v{version}.resolved.json").read_text())
        fixes, manual = [], []
        for c in rep["checks"]:
            if c["status"] != "fail":
                continue
            if c.get("autofix") == "renormalise":
                for v in results:
                    renormalise(results[v]["output"], res["loudness_lufs"])
                fixes.append("renormalised loudness")
            elif c.get("autofix") == "move_text":
                edl = json.loads(edl_path.read_text())
                ch = move_text(edl, rep, res)
                if ch:
                    edl_path.write_text(json.dumps(edl, indent=1, ensure_ascii=False))
                    fixes += ch
                else:
                    manual.append(c)
            else:
                manual.append(c)
        fixes = list(dict.fromkeys(fixes))
        history.append({"round": rnd, "version": version, "verdict": rep["verdict"], "auto_fixes": fixes,
                        "needs_claude": [f"{c['area']}: {c['detail']}" for c in manual]})
        with decisions.open("a") as f:
            f.write(f"\n## {now()} · deliver round {rnd} → v{version}: QC {rep['verdict']}\n")
            for x in fixes:
                f.write(f"- AUTO: {x}\n")
            for c in manual:
                f.write(f"- NEEDS CLAUDE: {c['area']}: {c['detail']}\n")
        if manual:
            log(f"  stopped: {len(manual)} failure(s) need an EDL change (see build/qc_v{version}_{main}.md)")
            return {"delivered": False, "version": version, "history": history}
        if fixes and any(f.startswith("text") for f in fixes):
            continue                           # EDL changed → re-render
        if fixes:                               # loudness fixed in place → re-measure, then package
            rep = qc.run(prod, version, main, evidence=False, log=log)
            if rep["verdict"] == "fail":
                continue
        final = package(prod, version, log=log)
        return {"delivered": True, "version": version, "final": str(final), "history": history}
    return {"delivered": False, "version": version, "history": history}
