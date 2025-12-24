import pytest
from unittest.mock import Mock, patch, mock_open
from src.services.music_plan import MusicPlanService
from src.schemas.music import MusicPlan, MusicChords, MusicRhythm, TempoFeel, Instrument, StructureSection, LengthScale


@pytest.fixture
def sample_music_plan():
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
def sample_music_chords():
    return MusicChords(
        key="C",
        sections=[]
    )


@pytest.fixture
def sample_music_rhythm():
    return MusicRhythm(sections=[])


@pytest.fixture
def mock_llm_service():
    service = Mock()
    return service


def test_generate_music_plan_given_description(mock_llm_service, sample_music_plan):
    service = MusicPlanService(mock_llm_service)
    mock_llm_service.prompt_llm.return_value = sample_music_plan

    result = service.generate_music_plan_given_description("A jazz piece")

    assert result == sample_music_plan
    mock_llm_service.prompt_llm.assert_called_once()
    call_args = mock_llm_service.prompt_llm.call_args[0][0]
    assert "A jazz piece" in call_args.user_messages


def test_generate_music_plan_given_description_llm_failure(mock_llm_service):
    service = MusicPlanService(mock_llm_service)
    mock_llm_service.prompt_llm.return_value = None

    result = service.generate_music_plan_given_description("A jazz piece")

    assert result is None


def test_generate_music_rhythm_given_description(mock_llm_service, sample_music_plan, sample_music_chords, sample_music_rhythm):
    service = MusicPlanService(mock_llm_service)
    mock_llm_service.prompt_llm.side_effect = [sample_music_plan, sample_music_chords, sample_music_rhythm]

    with patch("builtins.open", mock_open()) as mock_file:
        result = service.generate_music_rhythm_given_description("A jazz piece")

    assert result == (sample_music_plan, sample_music_rhythm)
    assert mock_llm_service.prompt_llm.call_count == 3


def test_generate_music_rhythm_given_description_plan_failure(mock_llm_service):
    service = MusicPlanService(mock_llm_service)
    mock_llm_service.prompt_llm.return_value = None

    result = service.generate_music_rhythm_given_description("A jazz piece")

    assert result is None