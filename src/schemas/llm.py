from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from .music import MusicPlan, MusicChords, MusicRhythm


class GeneratePlanRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    model: Optional[str] = None
    kwargs: Optional[dict] = None

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        # Allow only alphanumeric, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s.,!?-]+$', v):
            raise ValueError('Description contains invalid characters')
        # Check for forbidden patterns
        forbidden_patterns = ['ignore', 'override', 'system prompt', 'admin', 'hack']
        if any(pattern in v.lower() for pattern in forbidden_patterns):
            raise ValueError('Description contains prohibited content')
        # Strip leading/trailing whitespace
        return v.strip()


class GenerateChordsRequest(BaseModel):
    music_plan: MusicPlan
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    model: Optional[str] = None
    kwargs: Optional[dict] = None

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is None:
            return v
        # Allow only alphanumeric, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s.,!?-]+$', v):
            raise ValueError('Description contains invalid characters')
        # Check for forbidden patterns
        forbidden_patterns = ['ignore', 'override', 'system prompt', 'admin', 'hack']
        if any(pattern in v.lower() for pattern in forbidden_patterns):
            raise ValueError('Description contains prohibited content')
        # Strip leading/trailing whitespace
        return v.strip()


class GenerateRhythmRequest(BaseModel):
    music_chords: MusicChords
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    model: Optional[str] = None
    kwargs: Optional[dict] = None

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is None:
            return v
        # Allow only alphanumeric, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s.,!?-]+$', v):
            raise ValueError('Description contains invalid characters')
        # Check for forbidden patterns
        forbidden_patterns = ['ignore', 'override', 'system prompt', 'admin', 'hack']
        if any(pattern in v.lower() for pattern in forbidden_patterns):
            raise ValueError('Description contains prohibited content')
        # Strip leading/trailing whitespace
        return v.strip()


class GenerateNotesRequest(BaseModel):
    music_plan: MusicPlan
    music_rhythm: MusicRhythm
    model: Optional[str] = None
    kwargs: Optional[dict] = None