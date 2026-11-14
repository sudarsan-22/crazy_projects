"""Thin, safe wrappers around ffmpeg/ffprobe (argument lists only, never shell strings)."""
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path

HDR_TRC = {"arib-std-b67", "smpte2084"}


class FFError(RuntimeError):
    pass


def run(cmd, timeout=3600, check=True):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=timeout)
    if check and p.returncode:
        tail = "\n".join(p.stderr.strip().splitlines()[-30:])
        raise FFError(f"{Path(str(cmd[0])).name} failed ({p.returncode}):\n{tail}")
    return p


def probe(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    return json.loads(p.stdout)


def _rate(r):
    try:
        f = Fraction(r)
        return float(f) if f else None
    except (ValueError, ZeroDivisionError):
        return None


def rotation(vs):
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            return int(float(sd["rotation"]))
    rot = (vs.get("tags") or {}).get("rotate")
    return int(rot) if rot else 0


def media_info(path):
    """Summary of a media file: display size (rotation applied), fps, VFR/HDR flags, audio."""
    info = probe(path)
    vs = next((s for s in info["streams"] if s["codec_type"] == "video"
               and not (s.get("disposition") or {}).get("attached_pic")), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"].get("duration") or (vs or {}).get("duration") or 0)
    out = {"path": str(path), "duration": round(dur, 4), "has_video": vs is not None,
           "has_audio": au is not None, "format": info["format"].get("format_name")}
    if vs:
        w, h, rot = int(vs["width"]), int(vs["height"]), rotation(vs)
        if abs(rot) in (90, 270):
            w, h = h, w
        r, avg = _rate(vs.get("r_frame_rate", "0/0")), _rate(vs.get("avg_frame_rate", "0/0"))
        out.update({
            "codec": vs.get("codec_name"), "width": w, "height": h, "rotation": rot,
            "fps": round(avg or r or 0, 3), "r_frame_rate": r, "avg_frame_rate": avg,
            "vfr": bool(r and avg and abs(r - avg) / r > 0.01),
            "color_transfer": vs.get("color_transfer"),
            "hdr": vs.get("color_transfer") in HDR_TRC, "pix_fmt": vs.get("pix_fmt"),
            "nb_frames": int(vs["nb_frames"]) if str(vs.get("nb_frames", "")).isdigit() else None,
        })
    if au:
        out.update({"audio_codec": au.get("codec_name"), "sample_rate": int(au.get("sample_rate") or 0),
                    "channels": au.get("channels")})
    return out


def tonemap_chain(kind="mobius"):
    tm = {"mobius": "tonemap=tonemap=mobius:param=0.3:desat=0",
          "hable": "tonemap=tonemap=hable:desat=0"}[kind]
    return ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
            f"{tm},zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def extract_wav(src, dst, sr=48000, mono=False, start=None, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.4f}"]
    if dur is not None:
        cmd += ["-t", f"{dur:.4f}"]
    cmd += ["-i", src, "-vn", "-ac", "1" if mono else "2", "-ar", str(sr), "-c:a", "pcm_s16le", dst]
    run(cmd)
    return Path(dst)


def ebur128(path):
    """Integrated loudness (LUFS), loudness range (LU), true peak (dBTP) of the first audio stream."""
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true",
             "-f", "null", "-"], check=False)
    s = p.stderr[p.stderr.rfind("Summary:"):]

    def g(pat):
        m = re.search(pat, s)
        return float(m.group(1)) if m else None
    return {"integrated_lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra_lu": g(r"LRA:\s+(-?[\d.]+) LU"),
            "true_peak_dbtp": g(r"Peak:\s+(-?[\d.]+) dBFS")}


def _intervals(stderr, start_key, end_key):
    starts = [float(x) for x in re.findall(rf"{start_key}:\s*(-?[\d.]+)", stderr)]
    ends = [float(x) for x in re.findall(rf"{end_key}:\s*(-?[\d.]+)", stderr)]
    return [(s, ends[i] if i < len(ends) else None) for i, s in enumerate(starts)]


def blackdetect(path, min_d=0.1):
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf",
             f"scale=270:-2,blackdetect=d={min_d}:pix_th=0.10", "-f", "null", "-"], check=False)
    return _intervals(p.stderr, "black_start", "black_end")


def freezedetect(path, min_d=0.5):
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf",
             f"scale=270:-2,freezedetect=n=0.003:d={min_d}", "-f", "null", "-"], check=False)
    return [(float(a), float(b)) for a, b in
            zip(re.findall(r"freeze_start: (-?[\d.]+)", p.stderr), re.findall(r"freeze_end: (-?[\d.]+)", p.stderr))]


def silencedetect(path, noise_db=-45, min_d=0.6):
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af",
             f"silencedetect=noise={noise_db}dB:d={min_d}", "-f", "null", "-"], check=False)
    return _intervals(p.stderr, "silence_start", "silence_end")


def scene_cuts(path, threshold=0.3):
    """Hard-cut times from FFmpeg's scdet (frame-accurate on the rendered file)."""
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf",
             f"scale=270:-2,scdet=threshold={threshold * 100:.1f}", "-f", "null", "-"], check=False)
    return [float(x) for x in re.findall(r"lavfi\.scd\.time:\s*(-?[\d.]+)", p.stderr)]


def frame_at(src, t, out, vf="scale=540:-2"):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(t, 0):.3f}", "-i", src,
         "-frames:v", "1", "-vf", vf, out])
    return Path(out)
