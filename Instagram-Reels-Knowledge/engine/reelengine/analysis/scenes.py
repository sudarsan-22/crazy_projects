"""Shot boundaries with PySceneDetect 0.7 (AdaptiveDetector suits handheld phone footage)."""
from scenedetect import AdaptiveDetector, detect


def shots(proxy):
    scenes = detect(str(proxy), AdaptiveDetector(), backend="pyav")
    return [[round(a.seconds, 3), round(b.seconds, 3)] for a, b in scenes]
