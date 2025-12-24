import pytest
from unittest.mock import Mock, patch, mock_open
from src.services.notes_gen import NotesGenService
from src.schemas.music import MusicPlan, MusicRhythm, SectionChannelsResponse, ChannelNotes, SectionNotes, BarNotes, RhythmSection, TempoFeel, Instrument, StructureSection, LengthScale


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
def sample_music_rhythm():
    return MusicRhythm(sections=[
        RhythmSection(section="Intro", bars=4, bass=["pattern1"], perc=["kick"], melody=["mel1"], harmony=["harm1"], voiceLeading=["vl1"], dynamics=["dyn1"], polyphony="mono", loop="repeat")
    ])


@pytest.fixture
def sample_section_channels_response():
    return SectionChannelsResponse(channels=[
        ChannelNotes(channel="melody", sections=[
            SectionNotes(section="Intro", bars=[
                BarNotes(bar=1, events=[[1.0, "C4", "quarter", 80]])
            ])
        ])
    ])


@pytest.fixture
def mock_llm_service():
    service = Mock()
    return service


def test_generate_section_notes_given_music_rhythm(mock_llm_service, sample_music_plan, sample_music_rhythm, sample_section_channels_response):
    service = NotesGenService(mock_llm_service)
    mock_llm_service.prompt_llm.return_value = sample_section_channels_response

    result = service.generate_section_notes_given_music_rhythm("Intro", sample_music_plan, sample_music_rhythm)

    assert result == sample_section_channels_response
    mock_llm_service.prompt_llm.assert_called_once()


def test_generate_all_channel_notes(mock_llm_service, sample_music_plan, sample_music_rhythm, sample_section_channels_response):
    service = NotesGenService(mock_llm_service)
    mock_llm_service.prompt_llm.return_value = sample_section_channels_response

    with patch("builtins.open", mock_open()) as mock_file:
        result = service.generate_all_channel_notes(sample_music_plan, sample_music_rhythm)

    assert result is not None
    assert len(result.channels) == 1
    assert result.channels[0].channel == "melody"


def test_generate_all_channel_notes_no_sections(mock_llm_service, sample_music_plan):
    service = NotesGenService(mock_llm_service)
    empty_rhythm = MusicRhythm(sections=[])

    result = service.generate_all_channel_notes(sample_music_plan, empty_rhythm)

    assert result is None