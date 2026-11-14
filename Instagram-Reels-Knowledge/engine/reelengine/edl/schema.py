"""pydantic models. extra='allow' keeps every v0 key (note, reframe, tonemap...) flowing through untouched."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Num = float | int
Ref = float | int | str          # seconds, "marker:D", "seg2.freeze_start", "end"


class Ramp(BaseModel):
    ramp: tuple[float, float]

    @field_validator("ramp")
    @classmethod
    def _pos(cls, v):
        if min(v) <= 0 or max(v) > 8:
            raise ValueError("ramp speeds must be in (0, 8]")
        return v


class Transition(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str = "fade"
    dur: float = 0.25


class Segment(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str | None = None
    src: str
    in_: float = Field(alias="in")
    out: float
    speed: float | Ramp = 1.0
    fit: str = "crop"                     # crop | blur | track
    track: str | None = None
    focus_x: float = 0.5
    focus_y: float = 0.5
    freeze_end: float = 0.0
    audio: Literal["keep", "mute"] = "keep"
    transition_in: Transition | None = None

    @field_validator("speed")
    @classmethod
    def _speed(cls, v):
        if isinstance(v, (int, float)) and not (0.05 <= v <= 8):
            raise ValueError("speed must be within 0.05..8")
        return v


class TextItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    style: str = "caption"
    text: str
    start: Ref
    end: Ref | None = None
    dur: float | None = None
    pos: tuple[int, int] | None = None
    anim: str | None = None               # pop | slide_in | fade | none
    punch: str | None = None              # word to highlight in yellow (KB 16 S6)
    needs_check: bool | None = None


class Sfx(BaseModel):
    model_config = ConfigDict(extra="allow")
    file: str
    at: Ref
    align: Literal["start", "peak", "end"] = "start"
    gain_db: float = -8


class Sync(BaseModel):
    event: str
    marker: str
    flex: str
    early_frames: int = 0


class Component(BaseModel):
    model_config = ConfigDict(extra="allow")
    macro: str


class EDL(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_: str = Field("edl/1", alias="schema")
    output: str | None = None
    fps: int = 30
    width: int = 1080
    height: int = 1920
    crf: int = 17
    loudness_lufs: float | None = None
    audio_rights: Literal["in_app_library", "sound_collection", "original_sound_api", "own_recording",
                          "licensed_file", "none"] = "in_app_library"
    reference_audio: dict | None = None   # {"file", "start", "analysis"}: timing only, never in clean/final
    markers: dict[str, float] = {}
    segments: list[Segment]
    sync: list[Sync] = []
    components: list[Component] = []
    text: list[TextItem] = []
    sfx: list[Sfx] = []
    ass: str | None = None
    music: dict | None = None
    cover_at: Ref | None = None
    caption: dict | None = None           # publish package: caption text, hashtags, keywords, audio name...
