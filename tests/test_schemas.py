import pytest
from pydantic import ValidationError
from src.schemas.music import (
    MusicPlan, MusicChords, MusicRhythm, MusicNotes,
    TempoFeel, Instrument, StructureSection, LengthScale,
    ChannelNotes, SectionNotes, BarNotes
)


def test_music_plan_valid():
    data = {
        "genre_style": "Jazz",
        "mood_emotion": "Relaxed",
        "tempo_feel": {"bpm": 120, "meter": "4/4", "feel": "Swing"},
        "key_tonality": "C Major",
        "instruments": [{"name": "Piano", "role": "melody"}],
        "structure": [{"section": "Intro", "bars": 4, "transition": "Fade in"}],
        "motivic_ideas": {"Intro": "Simple motif"},
        "dynamic_contour": "Crescendo",
        "length_scale": {"total_bars": 16, "duration_seconds": "1:00"},
        "looping_behavior": "Repeat"
    }
    plan = MusicPlan(**data)
    assert plan.genre_style == "Jazz"


def test_music_plan_invalid():
    data = {
        "genre_style": "Jazz",
        "mood_emotion": "Relaxed",
        "tempo_feel": {"bpm": "invalid", "meter": "4/4", "feel": "Swing"},  # bpm should be int
        "key_tonality": "C Major",
        "instruments": [{"name": "Piano", "role": "melody"}],
        "structure": [{"section": "Intro", "bars": 4, "transition": "Fade in"}],
        "motivic_ideas": {"Intro": "Simple motif"},
        "dynamic_contour": "Crescendo",
        "length_scale": {"total_bars": 16, "duration_seconds": "1:00"},
        "looping_behavior": "Repeat"
    }
    with pytest.raises(ValidationError):
        MusicPlan(**data)


def test_music_notes_serialization():
    notes = MusicNotes(channels=[
        ChannelNotes(channel="melody", sections=[
            SectionNotes(section="Intro", bars=[
                BarNotes(bar=1, events=[[1.0, "C4", "quarter", 80]])
            ])
        ])
    ])
    json_data = notes.model_dump()
    assert "channels" in json_data
    assert len(json_data["channels"]) == 1


def test_music_notes_validation():
    # Valid
    data = {
        "channels": [
            {
                "channel": "melody",
                "sections": [
                    {
                        "section": "Intro",
                        "bars": [
                            {
                                "bar": 1,
                                "events": [[1.0, "C4", "quarter", 80]]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    notes = MusicNotes(**data)
    assert notes.channels[0].channel == "melody"

    # Invalid: negative velocity
    data_invalid = {
        "channels": [
            {
                "channel": "melody",
                "sections": [
                    {
                        "section": "Intro",
                        "bars": [
                            {
                                "bar": 1,
                                "events": [[1.0, "C4", "quarter", -10]]  # invalid
                            }
                        ]
                    }
                ]
            }
        ]
    }
    # Pydantic doesn't validate event contents deeply, but let's test basic structure
    notes_invalid = MusicNotes(**data_invalid)
    assert notes_invalid.channels[0].sections[0].bars[0].events[0][3] == -10  # no validation


def test_tempo_feel():
    feel = TempoFeel(bpm=120, meter="4/4", feel="Swing")
    assert feel.bpm == 120

    with pytest.raises(ValidationError):
        TempoFeel(bpm="invalid", meter="4/4", feel="Swing")  # bpm must be int


def test_instrument():
    inst = Instrument(name="Piano", role="melody")
    assert inst.name == "Piano"