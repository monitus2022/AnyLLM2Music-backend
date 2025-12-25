import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app
from src.schemas.music import MusicPlan, MusicRhythm, MusicNotes, TempoFeel, Instrument, StructureSection, LengthScale, RhythmSection

client = TestClient(app)


@patch('src.routes.llm.music_plan_service')
@patch('src.routes.llm.notes_gen_service')
@patch('src.routes.llm.json_to_midi_bytes')
def test_full_pipeline_generate_midi_from_description(mock_midi, mock_notes_service, mock_plan_service):
    # Mock the services
    mock_plan = MusicPlan(
        genre_style="Jazz",
        mood_emotion="Relaxed",
        tempo_feel=TempoFeel(bpm=120, meter="4/4", feel="Swing"),
        key_tonality="C Major",
        instruments=[Instrument(name="Piano", role="melody")],
        structure=[StructureSection(section="Intro", bars=4, transition="Fade in")],
        motivic_ideas={"Intro": "Simple motif"},
        dynamic_contour="Crescendo",
        length_scale=LengthScale(total_bars=16, duration_seconds="1:00"),
        looping_behavior="Repeat"
    )
    mock_rhythm = MusicRhythm(sections=[
        RhythmSection(section="Intro", bars=4, bass=["pattern"], perc=["kick"], melody=["mel"], harmony=["harm"], voiceLeading=["vl"], dynamics=["dyn"], polyphony="mono", loop="repeat")
    ])
    mock_notes = MusicNotes(channels=[])

    mock_plan_service.generate_music_rhythm_given_description.return_value = (mock_plan, mock_rhythm)
    mock_notes_service.generate_all_channel_notes.return_value = mock_notes
    mock_midi.return_value = b'midi_bytes'

    response = client.get("/generate_midi_from_description?description=A jazz piece")

    assert response.status_code == 200
    data = response.json()
    assert "midi_data" in data
    assert data["description"] == "A jazz piece"


@patch('src.routes.llm.music_plan_service')
def test_pipeline_failure_at_plan(mock_plan_service):
    mock_plan_service.generate_music_rhythm_given_description.return_value = (None, None)

    response = client.get("/generate_midi_from_description?description=A jazz piece")

    assert response.status_code == 200
    data = response.json()
    assert "error" in data


@patch('src.routes.llm.music_plan_service')
@patch('src.routes.llm.notes_gen_service')
def test_pipeline_failure_at_notes(mock_notes_service, mock_plan_service):
    mock_plan = MusicPlan(
        genre_style="Jazz",
        mood_emotion="Relaxed",
        tempo_feel=TempoFeel(bpm=120, meter="4/4", feel="Swing"),
        key_tonality="C Major",
        instruments=[Instrument(name="Piano", role="melody")],
        structure=[StructureSection(section="Intro", bars=4, transition="Fade in")],
        motivic_ideas={"Intro": "Simple motif"},
        dynamic_contour="Crescendo",
        length_scale=LengthScale(total_bars=16, duration_seconds="1:00"),
        looping_behavior="Repeat"
    )
    mock_rhythm = MusicRhythm(sections=[])

    mock_plan_service.generate_music_rhythm_given_description.return_value = (mock_plan, mock_rhythm)
    mock_notes_service.generate_all_channel_notes.return_value = None

    response = client.get("/generate_midi_from_description?description=A jazz piece")

    assert response.status_code == 200
    data = response.json()
    assert "error" in data