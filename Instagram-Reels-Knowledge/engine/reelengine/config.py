"""Paths and house settings. Every value cites the KB doc it comes from, so docs and code stay in sync."""
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]          # .../Instagram-Reels-Knowledge/engine
KB = ENGINE.parent                                    # .../Instagram-Reels-Knowledge
TOOLS = KB / "tools"
ASSETS = KB / "assets"
SFX_DIR = ASSETS / "sfx"
FONTS_DIR = ASSETS / "fonts"
MODELS_DIR = ASSETS / "models"
PRODUCTIONS = KB / "productions"
INBOX = PRODUCTIONS / "inbox"
TEMPLATES = PRODUCTIONS / "_templates"
YUNET = MODELS_DIR / "face_detection_yunet_2023mar.onnx"

# Canvas / export (KB 07 §1, 28 §1)
WIDTH, HEIGHT, FPS = 1080, 1920, 30
MAX_DURATION_S = 180.0            # recommendation eligibility (KB 01)

# Loudness (KB 24 §6): -16 clean export for in-app library music, -14 when music is baked in
LUFS_CLEAN, LUFS_BAKED, TRUE_PEAK = -16.0, -14.0, -1.0
LUFS_TOLERANCE = 1.0

# Safe zone in 1080x1920 pixels (KB 07 §2; identical to tools/analyze_reel.py overlay + 60 px left margin)
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 250, 380, 60, 140

# Proxies used for analysis (KB 32 §1 principle: cheap iteration)
PROXY_LONG_SIDE = 960
PROXY_FPS = 30
ANALYSIS_HZ = 5                   # visual feature sampling rate

# Reading pace for on-screen text (KB 21 §6 practitioner rule, configurable)
MIN_TEXT_S = 0.8
WORDS_PER_S = 3.0

# Moment-scoring weights per pillar (KB 32 §5.1). Proposals only; Claude decides.
MOMENT_WEIGHTS = {
    "default": {"sound_peak": 1.0, "speech": 0.6, "motion": 0.8, "face": 0.6, "scene_start": 0.3,
                "blur": 0.8, "exposure": 0.5},
    "pets": {"sound_peak": 0.8, "speech": 0.3, "motion": 1.2, "face": 0.2, "scene_start": 0.3,
             "blur": 0.8, "exposure": 0.5},
    "comedy": {"sound_peak": 1.2, "speech": 1.0, "motion": 0.6, "face": 0.9, "scene_start": 0.3,
               "blur": 0.6, "exposure": 0.4},
}

# Brand text styles (KB 16 brand kit, 21 §6; matches the styles used in P001 build/text.ass)
ASS_STYLES = {
    #        font                         size  primary      outline bold  outline shadow
    "hook":    ("Noto Sans Black",            80, "&H00FFFFFF", 7, 3),
    "caption": ("Noto Sans Black",            62, "&H00FFFFFF", 6, 2),
    "caption_ta": ("Noto Sans Tamil Black",   64, "&H00FFFFFF", 6, 2),
    "card":    ("Noto Sans Condensed Black", 132, "&H0000C4FF", 8, 4),   # #FFC400 mass yellow (BGR)
    "sub":     ("Noto Sans Black",            50, "&H00FFFFFF", 5, 2),
    "tag":     ("Noto Sans Condensed Black",  40, "&H00FFFFFF", 3, 1),
    "bruh":    ("Noto Sans Condensed Black", 150, "&H00303BFF", 9, 4),   # fail-red #FF3B30 (BGR)
}
PUNCH_COLOUR = "&H0000C4FF&"      # yellow highlight for the punch word (KB 16 S6)
