import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app
from src.schemas.music import MusicPlan, MusicRhythm, MusicNotes

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"app": "AnyLLM2Music"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch('src.routes.llm.music_plan_service')
def test_create_music_plan(mock_service):
    from src.schemas.music import TempoFeel, Instrument, StructureSection, LengthScale
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
    mock_service.generate_music_plan_given_description.return_value = mock_plan

    response = client.get("/create_music_plan?description=A jazz piece")

    assert response.status_code == 200
    mock_service.generate_music_plan_given_description.assert_called_once_with(
        description="A jazz piece", model=None, kwargs=None
    )


@patch('src.routes.llm.music_plan_service')
def test_generate_midi_from_description(mock_service):
    mock_notes = Mock(spec=MusicNotes)
    mock_service.generate_music_rhythm_given_description.return_value = (Mock(), Mock())
    with patch('src.routes.llm.notes_gen_service') as mock_notes_service, \
         patch('src.routes.llm.json_to_midi_bytes', return_value=b'midi_bytes') as mock_midi:
        mock_notes_service.generate_all_channel_notes.return_value = mock_notes

        response = client.get("/generate_midi_from_description?description=A jazz piece")

        assert response.status_code == 200
        data = response.json()
        assert "midi_data" in data


@patch('src.routes.llm.music_plan_service')
def test_generate_midi_from_description_failure(mock_service):
    mock_service.generate_music_rhythm_given_description.return_value = (None, None)

    response = client.get("/generate_midi_from_description?description=A jazz piece")

    assert response.status_code == 200
    data = response.json()
    assert "error" in data


@patch('src.routes.llm.llm_service')
def test_llm_health(mock_service):
    mock_service.health_check.return_value = {"status": "ok"}

    response = client.get("/llm_health?model=test")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}