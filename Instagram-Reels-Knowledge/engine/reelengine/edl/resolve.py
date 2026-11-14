"""Timeline maths for EDL dicts: segment durations (incl. closed-form ramps), event references, sync solving.

Event references: 12.5 | "marker:D" | "end" | "seg2.start" | "seg2.end" | "seg2.freeze_start" | "seg2.start+0.4"
Flex parameters:  "seg1.in" | "seg1.out" | "seg2.freeze_end" | "seg3.speed" (constant speed only)
"""
import math
import re


class EDLError(ValueError):
    pass


def seg_ids(edl):
    for k, s in enumerate(edl["segments"]):
        s.setdefault("id", f"seg{k + 1}")
    return [s["id"] for s in edl["segments"]]


def core_duration(seg):
    L = float(seg["out"]) - float(seg["in"])
    sp = seg.get("speed", 1.0)
    if isinstance(sp, dict):
        s0, s1 = map(float, sp["ramp"])
        return L / s0 if abs(s1 - s0) < 1e-9 else L / (s1 - s0) * math.log(s1 / s0)
    return L / float(sp)


def ramp_setpts(seg):
    """setpts expression (input time T, segment-local) implementing the smooth ramp (KB 29 §4.6)."""
    L = float(seg["out"]) - float(seg["in"])
    s0, s1 = map(float, seg["speed"]["ramp"])
    if abs(s1 - s0) < 1e-9:
        return f"T/{s0}/TB"
    k = s1 - s0
    return f"({L / k:.6f})*log(1+({k:.6f})*T/({L * s0:.6f}))/TB"


def timeline(edl):
    seg_ids(edl)
    out, end = [], 0.0
    for k, s in enumerate(edl["segments"]):
        core = core_duration(s)
        fr = float(s.get("freeze_end", 0) or 0)
        tr = s.get("transition_in") if k > 0 else None
        d_tr = float(tr.get("dur", 0.25)) if tr else 0.0
        start = end - d_tr
        end = start + core + fr
        out.append({"id": s["id"], "index": k, "start": start, "core": core, "freeze": fr,
                    "freeze_start": start + core, "end": end, "transition_in": d_tr})
    return out


def total(edl):
    tl = timeline(edl)
    return tl[-1]["end"] if tl else 0.0


_REF = re.compile(r"^(?P<base>[A-Za-z0-9_:]+?)(?:\.(?P<attr>start|end|freeze_start))?(?P<off>[+-]\d+(?:\.\d+)?)?$")


def event_time(edl, ref, tl=None):
    if isinstance(ref, (int, float)):
        return float(ref)
    ref = str(ref).strip()
    try:
        return float(ref)
    except ValueError:
        pass
    m = _REF.match(ref)
    if not m:
        raise EDLError(f"bad event reference '{ref}'")
    base, attr, off = m.group("base"), m.group("attr"), float(m.group("off") or 0)
    if base.startswith("marker:"):
        key = base.split(":", 1)[1]
        if key not in edl.get("markers", {}):
            raise EDLError(f"unknown marker '{key}' (markers: {list(edl.get('markers', {}))})")
        return float(edl["markers"][key]) + off
    tl = tl or timeline(edl)
    if base == "end":
        return tl[-1]["end"] + off
    hit = next((x for x in tl if x["id"] == base), None)
    if not hit:
        raise EDLError(f"unknown segment '{base}' in '{ref}'")
    return hit[attr or "start"] + off


def _flex(edl, flex):
    sid, _, param = flex.partition(".")
    seg = next((s for s in edl["segments"] if s["id"] == sid), None)
    if seg is None or param not in ("in", "out", "freeze_end", "speed"):
        raise EDLError(f"bad flex '{flex}'")
    if param == "speed" and isinstance(seg.get("speed"), dict):
        raise EDLError(f"flex '{flex}': ramps can't flex speed; flex in/out instead")
    return seg, param


def solve_sync(edl, src_dur, tol=1e-4):
    """Adjust each constraint's flex parameter (bisection) so event == marker - early_frames/fps."""
    seg_ids(edl)
    fps = edl.get("fps", 30)
    report, first = [], {}
    for c in edl.get("sync", []):
        seg, param = _flex(edl, c["flex"])
        first[c["flex"] + c["event"]] = (float(seg.get(param, 0 if param == "freeze_end" else 1.0) or 0),
                                         event_time(edl, c["event"]))
    for _round in range(2):
        report = []
        for c in edl.get("sync", []):
            seg, param = _flex(edl, c["flex"])
            target = float(edl["markers"][c["marker"]]) - c.get("early_frames", 0) / fps
            before_v, before_e = first[c["flex"] + c["event"]]
            lo, hi = {"in": (0.0, float(seg["out"]) - 0.1),
                      "out": (float(seg["in"]) + 0.1, src_dur[seg["id"]]),
                      "freeze_end": (0.0, 10.0),
                      "speed": (0.1, 8.0)}[param]

            def f(v):
                seg[param] = v
                return event_time(edl, c["event"]) - target
            flo, fhi = f(lo), f(hi)
            ok = True
            if flo * fhi > 0:            # no root in range → best effort at nearest bound
                v = lo if abs(flo) < abs(fhi) else hi
                f(v)
                ok = False
            else:
                a, b = lo, hi
                for _ in range(80):
                    mid = (a + b) / 2
                    fm = f(mid)
                    if abs(fm) < tol:
                        break
                    if (fm > 0) == (flo > 0):
                        a, flo = mid, fm
                    else:
                        b = mid
                v = round(mid, 4)
                f(v)
            after = event_time(edl, c["event"])
            report.append({"event": c["event"], "marker": c["marker"], "target": round(target, 4),
                           "before": round(before_e, 4), "after": round(after, 4), "flex": c["flex"],
                           "value_before": round(before_v, 4), "value_after": round(seg[param], 4),
                           "error_frames": round((after - target) * fps, 2), "solved": ok})
    return report
