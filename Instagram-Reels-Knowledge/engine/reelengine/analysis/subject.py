"""Subject path for 9:16 reframing: faces → motion centroid → hold; then a smoothed 'virtual camera'."""
import numpy as np


def raw_path(visual):
    """Per-sample subject centre (cx, cy in 0..1 of the source frame) or None, with its source."""
    out = []
    for s in visual["samples"]:
        faces = s.get("faces") or []
        if faces:
            f = max(faces, key=lambda f: f[2] * f[3] * f[4])
            out.append((s["t"], f[0], f[1], "face"))
        elif s.get("mc") and s["mc"][2] > 0.004:
            out.append((s["t"], s["mc"][0], s["mc"][1], "motion"))
        else:
            out.append((s["t"], None, None, "none"))
    return out


def smooth(raw, deadzone=0.06, max_speed=0.35, median=5):
    """Virtual camera: fill gaps, median-filter, then move only when the subject leaves a dead-zone,
    never faster than max_speed (fraction of frame width per second)."""
    ts = np.array([r[0] for r in raw], float)
    xs = np.array([np.nan if r[1] is None else r[1] for r in raw], float)
    ys = np.array([np.nan if r[2] is None else r[2] for r in raw], float)
    if np.all(np.isnan(xs)):
        xs[:] = 0.5
        ys[:] = 0.5
    for arr in (xs, ys):
        good = ~np.isnan(arr)
        arr[~good] = np.interp(ts[~good], ts[good], arr[good])
    k = max(1, median | 1)
    pad = k // 2
    xm = np.array([np.median(xs[max(0, i - pad):i + pad + 1]) for i in range(len(xs))])
    ym = np.array([np.median(ys[max(0, i - pad):i + pad + 1]) for i in range(len(ys))])
    cam = np.empty_like(xm)
    cam[0] = xm[0]
    for i in range(1, len(xm)):
        dt = ts[i] - ts[i - 1]
        err = xm[i] - cam[i - 1]
        move = 0.0 if abs(err) <= deadzone else err - np.sign(err) * deadzone
        lim = max_speed * dt
        cam[i] = cam[i - 1] + float(np.clip(move, -lim, lim))
    found = sum(1 for r in raw if r[1] is not None)
    return {"t": [round(float(t), 3) for t in ts], "cx": [round(float(x), 4) for x in cam],
            "cy": [round(float(y), 4) for y in ym], "raw_cx": [round(float(x), 4) for x in xm],
            "coverage": round(found / max(1, len(raw)), 3),
            "sources": {k: sum(1 for r in raw if r[3] == k) for k in ("face", "motion", "none")}}


def crop_x_expr(path, t0, t1, crop_frac, max_keys=40):
    """FFmpeg crop x expression over segment-local time t (source time minus t0) for a crop whose
    width is crop_frac of the input width. Piecewise-linear between keyframes."""
    ts, cx = np.array(path["t"]), np.array(path["cx"])
    sel = (ts >= t0 - 0.5) & (ts <= t1 + 0.5)
    ts, cx = ts[sel], cx[sel]
    if len(ts) == 0:
        return f"(iw-iw*{crop_frac:.5f})/2"
    if len(ts) > max_keys:
        idx = np.linspace(0, len(ts) - 1, max_keys).round().astype(int)
        ts, cx = ts[idx], cx[idx]
    left = np.clip(cx - crop_frac / 2, 0, 1 - crop_frac)   # crop left edge as a fraction of width
    lt = ts - t0
    if len(lt) == 1:
        return f"iw*{left[0]:.5f}"
    expr = f"{left[-1]:.5f}"
    for i in range(len(lt) - 2, -1, -1):
        a, b, la, lb = lt[i], lt[i + 1], left[i], left[i + 1]
        seg = f"({la:.5f}+({lb - la:.5f})*(t-({a:.4f}))/{max(b - a, 1e-3):.4f})"
        expr = f"if(lt(t,{b:.4f}),{seg},{expr})"
    expr = f"if(lt(t,{lt[0]:.4f}),{left[0]:.5f},{expr})"
    return f"iw*({expr})"
