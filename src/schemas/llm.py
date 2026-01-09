from pydantic import BaseModel
from typing import Optional
from .music import MusicPlan, MusicChords, MusicRhythm


class GeneratePlanRequest(BaseModel):
    description: str
    model: Optional[str] = None
    kwargs: Optional[dict] = None


class GenerateChordsRequest(BaseModel):
    music_plan: MusicPlan
    description: Optional[str] = None
    model: Optional[str] = None
    kwargs: Optional[dict] = None


class GenerateRhythmRequest(BaseModel):
    music_chords: MusicChords
    description: Optional[str] = None
    model: Optional[str] = None
    kwargs: Optional[dict] = None


class GenerateNotesRequest(BaseModel):
    music_plan: MusicPlan
    music_rhythm: MusicRhythm
    model: Optional[str] = None
    kwargs: Optional[dict] = None