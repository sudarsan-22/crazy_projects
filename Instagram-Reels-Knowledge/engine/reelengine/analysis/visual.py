"""Per-sample visual features from the proxy (PyAV decode → OpenCV maths) + YuNet faces + motion centroid."""
import av
import cv2
import numpy as np

from .. import config

_DET = None


def _detector(w, h):
    global _DET
    if not config.YUNET.exists():
        return None
    if _DET is None:
        _DET = cv2.FaceDetectorYN.create(str(config.YUNET), "", (w, h), score_threshold=0.75)
    _DET.setInputSize((w, h))
    return _DET


def features(proxy_path, hz=config.ANALYSIS_HZ, faces=True):
    """Return {'w','h','hz','samples':[{t, motion, sharp, luma, shift, faces, mc}]} on the source timeline."""
    samples, prev_small, prev_gray = [], None, None
    next_t, step = 0.0, 1.0 / hz
    with av.open(str(proxy_path)) as c:
        st = c.streams.video[0]
        st.thread_type = "AUTO"
        W = H = None
        for fr in c.decode(st):
            t = float(fr.pts * fr.time_base) if fr.pts is not None else next_t
            if t + 1e-6 < next_t:
                continue
            next_t = t + step
            img = fr.to_ndarray(format="bgr24")
            H, W = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sw = 160
            small = cv2.resize(gray, (sw, max(1, int(H * sw / W))), interpolation=cv2.INTER_AREA).astype(np.float32)
            rec = {"t": round(t, 3), "luma": round(float(gray.mean()) / 255, 4),
                   "sharp": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 1)}
            if prev_small is not None:
                diff = np.abs(small - prev_small)
                rec["motion"] = round(float(diff.mean()) / 255, 5)
                mask = diff > 25
                mass = float(mask.mean())
                if mass > 0.002:
                    ys, xs = np.nonzero(mask)
                    rec["mc"] = [round(float(xs.mean()) / small.shape[1], 4), round(float(ys.mean()) / small.shape[0], 4),
                                 round(mass, 4)]
                (dx, dy), resp = cv2.phaseCorrelate(prev_small, small)
                rec["shift"] = round(float(np.hypot(dx, dy)) / sw, 5)   # global camera movement (fraction of width)
            else:
                rec["motion"], rec["shift"] = 0.0, 0.0
            prev_small = small
            if faces:
                fw = 320
                fh = int(H * fw / W)
                det = _detector(fw, fh)
                if det is not None:
                    _, fs = det.detect(cv2.resize(img, (fw, fh)))
                    rec["faces"] = [] if fs is None else [
                        [round((f[0] + f[2] / 2) / fw, 4), round((f[1] + f[3] / 2) / fh, 4),
                         round(f[2] / fw, 4), round(f[3] / fh, 4), round(float(f[-1]), 3)] for f in fs]
            samples.append(rec)
    return {"w": W, "h": H, "hz": hz, "samples": samples}
