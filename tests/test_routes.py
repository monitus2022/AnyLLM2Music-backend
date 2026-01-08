import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from src.main import app
from src.schemas.music import MusicPlan, MusicRhythm, MusicNotes
import base64

@pytest.fixture
def client():
    return TestClient(app)


def test_read_root(client):
    response = client.get("/v1/music/")
    assert response.status_code == 200
    assert response.json() == {"app": "AnyLLM2Music"}


def test_health_check(client):
    response = client.get("/v1/music/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch('src.routes.llm.music_plan_service')
def test_create_music_plan(mock_service, client):
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
    mock_service.generate_music_plan_given_description = AsyncMock(return_value=mock_plan)

    response = client.get("/v1/music/create_music_plan?description=A jazz piece")

    assert response.status_code == 200
    mock_service.generate_music_plan_given_description.assert_called_once_with(
        description="A jazz piece", model=None, kwargs=None
    )


@patch('src.routes.midi.music_plan_service')
def test_generate_midi_from_description(mock_service, client):
    mock_notes = MusicNotes(channels=[])
    mock_service.generate_music_rhythm_given_description = AsyncMock(return_value=(Mock(), Mock()))
    with patch('src.routes.midi.notes_gen_service') as mock_notes_service, \
           patch('src.routes.midi.json_to_midi_bytes', return_value=b'midi_bytes') as mock_midi:
        mock_notes_service.generate_all_channel_notes = AsyncMock(return_value=mock_notes)

        response = client.get("/v1/music/generate_midi_from_description?description=A jazz piece")

        assert response.status_code == 200
        data = response.json()
        assert "midi_data" in data


@patch('src.routes.midi.music_plan_service')
def test_generate_midi_from_description_failure(mock_service, client):
    mock_service.generate_music_rhythm_given_description = AsyncMock(return_value=(None, None))

    response = client.get("/v1/music/generate_midi_from_description?description=A jazz piece")

    assert response.status_code == 200
    data = response.json()
    assert "error" in data


@patch('src.routes.llm.llm_service')
def test_llm_health(mock_service, client):
    mock_service.health_check = AsyncMock(return_value={"status": "ok"})

    response = client.get("/v1/music/llm_health?model=test")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture
def mock_music_plan():
    from src.schemas.music import TempoFeel, Instrument, StructureSection, LengthScale
    return MusicPlan(
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


@pytest.fixture
def mock_music_chords():
    from src.schemas.music import MusicChords, ChordSection
    return MusicChords(
        key="C",
        sections=[ChordSection(name="Intro", bars=4, chords=["C", "G"], motifs={}, loop="")]
    )


@pytest.fixture
def mock_music_rhythm():
    from src.schemas.music import MusicRhythm, RhythmSection
    return MusicRhythm(
        sections=[RhythmSection(section="Intro", bars=4, bass=[], perc=[], melody=[], harmony=[], voiceLeading=[], dynamics=[], polyphony="", loop="")]
    )


@patch('src.routes.llm.music_plan_service')
def test_generate_plan(mock_service, client, mock_music_plan):
    mock_service.generate_music_plan_given_description = AsyncMock(return_value=mock_music_plan)

    response = client.post("/v1/music/generate_plan", json={"description": "A jazz piece", "model": None, "kwargs": None})

    assert response.status_code == 200
    mock_service.generate_music_plan_given_description.assert_called_once_with(
        description="A jazz piece", model=None, kwargs=None
    )


@patch('src.routes.llm.music_plan_service')
def test_generate_chords(mock_service, client, mock_music_plan, mock_music_chords):
    mock_service.generate_music_chords_given_plan = AsyncMock(return_value=mock_music_chords)

    response = client.post("/v1/music/generate_chords", json={"music_plan": mock_music_plan.model_dump(), "description": "A jazz piece", "model": None, "kwargs": None})

    assert response.status_code == 200
    mock_service.generate_music_chords_given_plan.assert_called_once_with(
        music_plan=mock_music_plan, description="A jazz piece", model=None, kwargs=None
    )


@patch('src.routes.llm.music_plan_service')
def test_generate_rhythm(mock_service, client, mock_music_chords, mock_music_rhythm):
    mock_service.generate_music_rhythm_given_chords = AsyncMock(return_value=mock_music_rhythm)

    response = client.post("/v1/music/generate_rhythm", json={"music_chords": mock_music_chords.model_dump(), "description": "A jazz piece", "model": None, "kwargs": None})

    assert response.status_code == 200
    mock_service.generate_music_rhythm_given_chords.assert_called_once_with(
        music_chords=mock_music_chords, description="A jazz piece", model=None, kwargs=None
    )


@patch('src.routes.llm.notes_gen_service')
def test_generate_notes(mock_notes_service, client, mock_music_plan, mock_music_rhythm):
    mock_notes = MusicNotes(channels=[])
    mock_notes_service.generate_all_channel_notes = AsyncMock(return_value=mock_notes)

    response = client.post("/v1/music/generate_notes", json={"music_plan": mock_music_plan.model_dump(), "music_rhythm": mock_music_rhythm.model_dump(), "model": None, "kwargs": None})

    assert response.status_code == 200
    mock_notes_service.generate_all_channel_notes.assert_called_once_with(
        music_plan=mock_music_plan, music_rhythm=mock_music_rhythm, model=None, kwargs=None
    )


@patch('src.services.midi.FluidSynth')
def test_convert_midi_to_audio(mock_fluidsynth, client):
    # Mock MIDI data (simple base64 encoded bytes)
    midi_bytes = b'MThd'  # base64 for some bytes
    midi_b64 = base64.b64encode(midi_bytes).decode('utf-8')

    # Mock WAV data
    wav_bytes = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x01\x00\x08\x00data\x00\x08\x00\x00'  # minimal WAV
    wav_b64 = base64.b64encode(wav_bytes).decode('utf-8')

    # Mock FluidSynth instance
    mock_fs_instance = Mock()
    mock_fluidsynth.return_value = mock_fs_instance

    # Mock file operations
    mock_file = Mock()
    mock_file.read.return_value = wav_bytes
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)
    with patch('builtins.open', return_value=mock_file) as mock_open, \
         patch('os.unlink') as mock_unlink:

        response = client.post("/v1/music/convert_midi_to_audio", json={"midi_data": midi_b64})

        assert response.status_code == 200
        data = response.json()
        assert "audio_data" in data
        assert data["audio_data"] == wav_b64

        # Verify FluidSynth was called
        mock_fluidsynth.assert_called_once()
        mock_fs_instance.midi_to_audio.assert_called_once()


@patch('src.services.midi.FluidSynth')
def test_convert_midi_to_audio_error(mock_fluidsynth, client):
    mock_fluidsynth.side_effect = Exception("Conversion failed")

    midi_b64 = base64.b64encode(b'invalid').decode('utf-8')

    response = client.post("/v1/music/convert_midi_to_audio", json={"midi_data": midi_b64})

    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Failed to convert MIDI to audio" in data["error"]


@patch('src.routes.midi.notes_gen_service')
def test_generate_midi(mock_notes_service, client, mock_music_plan, mock_music_rhythm):
    mock_notes = MusicNotes(channels=[])
    mock_notes_service.generate_all_channel_notes = AsyncMock(return_value=mock_notes)

    with patch('src.routes.midi.json_to_midi_bytes', return_value=b'midi_bytes'):
        response = client.post("/v1/music/generate_midi", json={"music_plan": mock_music_plan.model_dump(), "music_rhythm": mock_music_rhythm.model_dump(), "model": None, "kwargs": None})

        assert response.status_code == 200
        data = response.json()
        assert "midi_data" in data
        mock_notes_service.generate_all_channel_notes.assert_called_once_with(
            music_plan=mock_music_plan, music_rhythm=mock_music_rhythm, model=None, kwargs=None
        )