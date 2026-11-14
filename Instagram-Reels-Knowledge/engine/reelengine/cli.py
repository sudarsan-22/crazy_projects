"""reel — autonomous Reel editor CLI (KB docs 26 + 32).

  uv run --project engine reel <command> ...      (run from the KB folder)

  doctor                         environment smoke tests (KB 33 §8)
  ingest FILES.. [--slug S]      new production from files (or --inbox: everything in productions/inbox/)
  ingest --prod P001             (re)index an existing production's source/
  analyze P001 [--no-speech] [--lang ta|en] [--model large-v3-turbo]
  moments P001 [--pillar default|pets|comedy]
  audio P001 --ref FILE [--start S --dur D --rights in_app_library --name "Track" --role villain]
  validate P001 [EDL]            resolve markers/sync/macros; print timeline + problems (no render)
  render P001 [EDL] [--draft] [--variants clean,syncguide]
  qc P001 [--version N] [--variant clean]
  deliver P001 [EDL]             render → QC → auto-fix (≤3 rounds) → publish/ package
  status P001
  run FILES.. [--slug S]         ingest + analyze + moments in one go (then Claude writes build/edl.json)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import config
from .state import Production, find


def _p(ref):
    return find(ref)


def cmd_ingest(a):
    from .ingest import ingest
    files = list(a.files)
    if a.inbox:
        files += [p for p in sorted(config.INBOX.iterdir()) if p.is_file() and p.name != "README.txt"]
    prod = _p(a.prod) if a.prod else None
    if not files and prod is None:
        sys.exit("nothing to ingest")
    prod, sources = ingest(files, prod=prod, slug=a.slug)
    print(f"{prod.root.name}: {len([s for s in sources if s['kind'] == 'video'])} video(s)")
    for s in sources:
        if s["kind"] == "video":
            i = s["info"]
            print(f"  {s['file']}: {i['width']}x{i['height']} {i['fps']}fps {i['duration']:.1f}s "
                  f"{i.get('codec')} flags={s.get('flags')}")
    return prod


def cmd_analyze(a):
    from .analyze import analyze
    analyze(_p(a.prod), speech=not a.no_speech, model=a.model, language=a.lang)


def cmd_moments(a):
    from .moments import propose
    out = propose(_p(a.prod), pillar=a.pillar)
    for m in out["moments"]:
        print(f"  #{m['rank']:2d} {m['stem'][:20]:20s} {m['t']:6.1f}s score {m['score']:.2f}  {m['why']}")


def cmd_audio(a):
    from .audio import analyse_reference
    analyse_reference(_p(a.prod), a.ref, start=a.start, dur=a.dur, rights=a.rights, name=a.name, role=a.role,
                      use_ml=not a.no_ml)


def cmd_validate(a):
    from .edl.compile import compile_edl
    prod = _p(a.prod)
    edl = Path(a.edl or prod.root / "build" / "edl.json")
    c = compile_edl(edl, "clean", 0, prod.d("build") / "validate", prod.d("analysis"))
    r = c["report"]
    print(f"total {r['total']:.3f}s ({r['frames']} frames @ {r['fps']}), rights {r['audio_rights']}, "
          f"loudness {r['loudness_lufs']} LUFS")
    for x in r["timeline"]:
        print(f"  {x['id']:8s} {x['start']:7.3f} → {x['end']:7.3f}  core {x['core']:.3f} freeze {x['freeze']}")
    for s in r["sync"]:
        print(f"  sync {s['event']} → {s['marker']}: {s['flex']} {s['value_before']} → {s['value_after']} "
              f"(error {s['error_frames']} frames{'' if s['solved'] else ', NOT SOLVED'})")
    for m in r["macros"]:
        print(f"  macro {m}")
    for t in r["text"]:
        print(f"  text [{t['style']}] {t['start']:.2f}–{t['end']:.2f} {t['text'][:40]!r}"
              f"{'  ← needs check' if t['needs_check'] else ''}")
    for p in r["problems"]:
        print(f"  PROBLEM: {p}")
    return 1 if r["problems"] or any(not s["solved"] for s in r["sync"]) else 0


def cmd_render(a):
    from .render import render
    variants = a.variants.split(",") if a.variants else None
    v, res = render(_p(a.prod), a.edl, variants=variants, draft=a.draft)
    for k, r in res.items():
        print(f"v{v} {k}: {r['output']}")


def cmd_qc(a):
    from . import qc
    prod = _p(a.prod)
    v = a.version or prod.latest_version()
    rep = qc.run(prod, v, a.variant)
    for c in rep["checks"]:
        print(f"  {c['status']:5s} {c['area']}: {c['detail']}")
    return 1 if rep["verdict"] == "fail" else 0


def cmd_deliver(a):
    from .deliver import deliver
    r = deliver(_p(a.prod), a.edl, draft=a.draft)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0 if r["delivered"] else 1


def cmd_status(a):
    prod = _p(a.prod)
    st = prod.load()
    print(prod.root.name)
    for k, v in st["stages"].items():
        print(f"  {k:10s} {v}")
    for k, v in st.get("versions", {}).items():
        print(f"  v{k}: {v}")


def cmd_doctor(a):
    smoke = config.ENGINE / "tests" / "smoke.py"
    return subprocess.run([sys.executable, str(smoke), "--t2"]).returncode


def cmd_run(a):
    prod = cmd_ingest(a)
    a.prod = str(prod.root)
    cmd_analyze(a)
    cmd_moments(a)
    print(f"\nNext: Claude writes {prod.root / 'build' / 'edl.json'} then `reel deliver {prod.id}`")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="reel", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("doctor")
    s.set_defaults(fn=cmd_doctor)
    for name, fn in (("ingest", cmd_ingest), ("run", cmd_run)):
        s = sub.add_parser(name)
        s.add_argument("files", nargs="*")
        s.add_argument("--slug")
        s.add_argument("--prod")
        s.add_argument("--inbox", action="store_true")
        if name == "run":
            s.add_argument("--no-speech", action="store_true")
            s.add_argument("--lang")
            s.add_argument("--model", default="large-v3-turbo")
            s.add_argument("--pillar", default="default")
        s.set_defaults(fn=fn)
    s = sub.add_parser("analyze")
    s.add_argument("prod")
    s.add_argument("--no-speech", action="store_true")
    s.add_argument("--lang")
    s.add_argument("--model", default="large-v3-turbo")
    s.set_defaults(fn=cmd_analyze)
    s = sub.add_parser("moments")
    s.add_argument("prod")
    s.add_argument("--pillar", default="default")
    s.set_defaults(fn=cmd_moments)
    s = sub.add_parser("audio")
    s.add_argument("prod")
    s.add_argument("--ref", required=True)
    s.add_argument("--start", type=float, default=0.0)
    s.add_argument("--dur", type=float)
    s.add_argument("--rights", default="in_app_library")
    s.add_argument("--name")
    s.add_argument("--role")
    s.add_argument("--no-ml", action="store_true")
    s.set_defaults(fn=cmd_audio)
    for name, fn in (("validate", cmd_validate), ("render", cmd_render), ("deliver", cmd_deliver)):
        s = sub.add_parser(name)
        s.add_argument("prod")
        s.add_argument("edl", nargs="?")
        if name != "validate":
            s.add_argument("--draft", action="store_true")
        if name == "render":
            s.add_argument("--variants")
        s.set_defaults(fn=fn)
    s = sub.add_parser("qc")
    s.add_argument("prod")
    s.add_argument("--version", type=int)
    s.add_argument("--variant", default="clean")
    s.set_defaults(fn=cmd_qc)
    s = sub.add_parser("status")
    s.add_argument("prod")
    s.set_defaults(fn=cmd_status)
    a = ap.parse_args(argv)
    rc = a.fn(a)
    sys.exit(rc if isinstance(rc, int) else 0)


if __name__ == "__main__":
    main()
