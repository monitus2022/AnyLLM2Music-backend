from pydantic import BaseModel
from typing import Optional
from .music import MusicPlan, MusicRhythm


class GenerateMidiRequest(BaseModel):
    music_plan: MusicPlan
    music_rhythm: MusicRhythm
    model: Optional[str] = None
    kwargs: Optional[dict] = None


class ConvertMidiToAudioRequest(BaseModel):
    midi_data: str
    soundfont: Optional[str] = None