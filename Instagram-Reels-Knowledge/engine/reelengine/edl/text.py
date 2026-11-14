"""Text items → ASS (libass) with brand styles (KB 16, 21 §6) and safe-zone default positions (KB 07 §2)."""
import re

from .. import config
from .resolve import event_time

TAMIL = re.compile(r"[஀-௿]")
SAFE_CX = (config.SAFE_LEFT + config.WIDTH - config.SAFE_RIGHT) // 2      # 500: centre of the safe area

# style → (default pos, alignment)
LAYOUT = {
    "hook": ((SAFE_CX, 470), 5), "caption": ((SAFE_CX, 1330), 5), "caption_ta": ((SAFE_CX, 1330), 5),
    "card": ((SAFE_CX, 1290), 5), "sub": ((SAFE_CX, 1395), 5), "bruh": ((SAFE_CX, 900), 5),
    "tag": ((config.SAFE_LEFT + 12, config.SAFE_TOP + 14), 7),
}
ANIMS = {
    "pop": r"\fscx40\fscy40\t(0,140,\fscx108\fscy108)\t(140,240,\fscx100\fscy100)\fad(0,120)",
    "fade": r"\fad(150,150)",
    "stamp": r"\fscx180\fscy180\t(0,90,\fscx100\fscy100)\fad(0,100)",
    "none": "",
}


def ts(t):
    t = max(0.0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def header(extra_styles=()):
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {config.WIDTH}", f"PlayResY: {config.HEIGHT}",
             "WrapStyle: 0", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
             "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
             "MarginL, MarginR, MarginV, Encoding"]
    for name, (font, size, prim, outl, shad) in config.ASS_STYLES.items():
        align = LAYOUT.get(name, ((0, 0), 5))[1]
        # letter spacing MUST be 0 for anything that may carry Tamil: libass disables complex-script
        # shaping when Spacing != 0 (found in QC evidence 2026-11-07). Only Latin display styles get +2.
        spacing = 2 if name in ("card", "tag") else 0
        lines.append(f"Style: {name},{font},{size},{prim},&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,"
                     f"{spacing},0,1,{outl},{shad},{align},{config.SAFE_LEFT},{config.SAFE_RIGHT},0,1")
    lines += list(extra_styles)
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return lines


def build(edl, tl, total, hand_ass=None):
    """Return (ass_text, resolved_items). resolved_items carry final times/positions for QC."""
    extra_styles, extra_events = [], []
    if hand_ass:
        sec = None
        for line in hand_ass.splitlines():
            if line.startswith("["):
                sec = line.strip()
            elif sec == "[V4+ Styles]" and line.startswith("Style:"):
                extra_styles.append(line)
            elif sec == "[Events]" and line.startswith(("Dialogue:", "Comment:")):
                extra_events.append(line)
    lines = header(extra_styles)
    items = []
    for i, it in enumerate(edl.get("text", [])):
        start = event_time(edl, it["start"], tl)
        if it.get("end") is not None:
            end = event_time(edl, it["end"], tl)
        else:
            end = start + float(it.get("dur") or max(config.MIN_TEXT_S, len(it["text"].split()) / config.WORDS_PER_S + 0.5))
        end = min(end, total)
        style = it.get("style", "caption")
        tamil = bool(TAMIL.search(it["text"]))
        if tamil and style in ("caption", "hook", "sub"):
            style = "caption_ta"                 # Tamil glyphs need the Tamil font (no letter spacing)
        elif tamil and style in ("card", "tag", "bruh"):
            raise ValueError(f"text item {i}: Tamil text in Latin display style '{style}'; use caption_ta")
        if style not in config.ASS_STYLES:
            raise ValueError(f"text item {i}: unknown style '{style}' (have {list(config.ASS_STYLES)})")
        (dx, dy), _ = LAYOUT[style]
        x, y = it.get("pos") or (dx, dy)
        anim = it.get("anim") or {"card": "slide_in", "bruh": "stamp", "tag": "fade"}.get(style, "pop")
        if anim == "slide_in":
            tag = rf"\move(-320,{y},{x},{y},0,220)\fad(0,150)"
        else:
            tag = rf"\pos({x},{y})" + ANIMS.get(anim, "")
        body = it["text"].replace("\n", r"\N")
        if it.get("punch") and it["punch"] in body:
            prim = config.ASS_STYLES[style][2]
            body = body.replace(it["punch"], "{\\c" + config.PUNCH_COLOUR + "}" + it["punch"] + "{\\c" + prim + "&}", 1)
        lines.append(f"Dialogue: 2,{ts(start)},{ts(end)},{style},,0,0,0,,{{{tag}}}{body}")
        items.append({"i": i, "style": style, "text": it["text"], "start": round(start, 3), "end": round(end, 3),
                      "pos": [x, y], "needs_check": bool(it.get("needs_check") or tamil)})
    lines += extra_events
    return "\n".join(lines) + "\n", items
