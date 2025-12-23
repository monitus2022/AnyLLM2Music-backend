from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# Models for Music Plan Service
class TempoFeel(BaseModel):
    bpm: int = Field(..., description="Beats per minute")
    meter: str = Field(..., description="Time signature, e.g., '4/4'")
    feel: str = Field(..., description="Rhythmic feel description")


class Instrument(BaseModel):
    name: str = Field(..., description="Instrument name")
    role: str = Field(..., description="Role in the composition, e.g., 'melody', 'bass'")


class StructureSection(BaseModel):
    section: str = Field(..., description="Section name, e.g., 'Intro', 'A'")
    bars: int = Field(..., description="Number of bars in this section")
    transition: str = Field(..., description="Transition description")


class LengthScale(BaseModel):
    total_bars: int = Field(..., description="Total number of bars")
    duration_seconds: str = Field(..., description="Estimated duration")


class MusicPlan(BaseModel):
    genre_style: str = Field(..., alias="genre_style", description="Genre and style description")
    mood_emotion: str = Field(..., alias="mood_emotion", description="Mood and emotional description")
    tempo_feel: TempoFeel = Field(..., alias="tempo_feel", description="Tempo and rhythmic feel")
    key_tonality: str = Field(..., alias="key_tonality", description="Key and tonality")
    instruments: List[Instrument] = Field(..., alias="instruments", description="List of instruments")
    structure: List[StructureSection] = Field(..., alias="structure", description="Song structure sections")
    motivic_ideas: Dict[str, str] = Field(..., alias="motivic_ideas", description="Motivic ideas per section")
    dynamic_contour: str = Field(..., alias="dynamic_contour", description="Dynamic contour description")
    length_scale: LengthScale = Field(..., alias="length_scale", description="Length and scale information")
    looping_behavior: str = Field(..., alias="looping_behavior", description="Looping behavior description")


class ChordSection(BaseModel):
    genre_style: str = Field(..., alias="genre_style", description="Genre and style description")
    mood_emotion: str = Field(..., alias="mood_emotion", description="Mood and emotional description")
    tempo_feel: TempoFeel = Field(..., alias="tempo_feel", description="Tempo and rhythmic feel")
    key_tonality: str = Field(..., alias="key_tonality", description="Key and tonality")
    instruments: List[Instrument] = Field(..., alias="instruments", description="List of instruments")
    structure: List[StructureSection] = Field(..., alias="structure", description="Song structure sections")
    motivic_ideas: Dict[str, str] = Field(..., alias="motivic_ideas", description="Motivic ideas per section")
    dynamic_contour: str = Field(..., alias="dynamic_contour", description="Dynamic contour description")
    length_scale: LengthScale = Field(..., alias="length_scale", description="Length and scale information")
    looping_behavior: str = Field(..., alias="looping_behavior", description="Looping behavior description")


# Models for Chords (used in Music Plan Service)
class ChordSection(BaseModel):
    name: str = Field(..., description="Section name")
    bars: int = Field(..., description="Number of bars")
    chords: List[str] = Field(..., description="List of chords")
    motifs: Dict[str, List[int]] = Field(..., description="Motifs mapping")
    loop: str = Field(..., description="Loop description")


class MusicChords(BaseModel):
    key: str = Field(..., description="Key signature")
    sections: List[ChordSection] = Field(..., description="Chord sections")


# Models for Rhythm (used in Music Plan Service)
class RhythmSection(BaseModel):
    section: str = Field(..., description="Section name")
    bars: int = Field(..., description="Number of bars")
    bass: List[str] = Field(..., description="Bass rhythm patterns")
    perc: List[str] = Field(..., description="Percussion patterns")
    melody: List[str] = Field(..., description="Melody patterns")
    harmony: List[str] = Field(..., description="Harmony patterns")
    voiceLeading: List[str] = Field(..., description="Voice leading descriptions")
    dynamics: List[str] = Field(..., description="Dynamic markings")
    polyphony: str = Field(..., description="Polyphony description")
    loop: str = Field(..., description="Loop description")


class MusicRhythm(BaseModel):
    sections: List[RhythmSection] = Field(..., description="Rhythm sections")


# Models for Notes Generation Service
class NoteEvent(BaseModel):
    beat: float = Field(..., description="Beat position in the bar")
    pitch: str = Field(..., description="Pitch or percussion name")
    duration: str = Field(..., description="Duration type, e.g., 'quarter'")
    velocity: int = Field(..., description="Velocity value")


class BarNotes(BaseModel):
    bar: int = Field(..., description="Bar number")
    events: List[NoteEvent] = Field(..., description="List of note events in this bar")


class SectionNotes(BaseModel):
    section: str = Field(..., description="Section name")
    bars: List[BarNotes] = Field(..., description="List of bars with notes")


class ChannelNotes(BaseModel):
    channel: str = Field(..., description="Channel name, e.g., 'melody'")
    sections: List[SectionNotes] = Field(..., description="List of sections with notes")


class MusicNotes(BaseModel):
    channels: List[ChannelNotes] = Field(..., description="List of channels with notes")


# Combined Response Model
class MusicPlanResponse(BaseModel):
    description: str = Field(..., description="User description or prompt")
    music_plan: MusicPlan = Field(..., description="Detailed music plan")
    music_chords: MusicChords = Field(..., description="Chord progression plan")
    music_rhythm: MusicRhythm = Field(..., description="Rhythm and arrangement plan")
    music_notes: Optional[MusicNotes] = Field(None, description="Generated note events")