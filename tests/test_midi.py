import pytest
from mido import MidiFile
from io import BytesIO
from src.services.midi import json_to_midi_bytes, beat_to_ticks, json_to_midi, pitch_to_midi, duration_to_ticks
from src.schemas.music import MusicNotes, ChannelNotes, SectionNotes, BarNotes


@pytest.fixture
def sample_music_notes():
    return MusicNotes(channels=[
        ChannelNotes(channel="melody", sections=[
            SectionNotes(section="Intro", bars=[
                BarNotes(bar=1, events=[
                    [1.0, "C4", "quarter", 80],
                    [2.0, "D4", "eighth", 70]
                ]),
                BarNotes(bar=2, events=[
                    [1.0, "E4", "half", 75]
                ])
            ])
        ]),
        ChannelNotes(channel="perc", sections=[
            SectionNotes(section="Intro", bars=[
                BarNotes(bar=1, events=[
                    [1.0, "kick", "quarter", 90]
                ])
            ])
        ])
    ])


def test_json_to_midi_bytes(sample_music_notes):
    midi_bytes = json_to_midi_bytes(sample_music_notes)

    assert isinstance(midi_bytes, bytes)
    assert len(midi_bytes) > 0

    # Parse with mido to verify
    buffer = BytesIO(midi_bytes)
    mid = MidiFile(file=buffer)
    assert mid.ticks_per_beat == 480
    assert len(mid.tracks) >= 2  # At least tempo track and channels


def test_json_to_midi(sample_music_notes, tmp_path):
    output_path = tmp_path / "test.mid"
    result_path = json_to_midi(sample_music_notes, output_path=str(output_path))

    assert result_path == str(output_path)
    assert output_path.exists()

    # Verify file
    mid = MidiFile(str(output_path))
    assert mid.ticks_per_beat == 480


def test_beat_to_ticks():
    assert beat_to_ticks(1.0) == 0
    assert beat_to_ticks(2.0) == 480
    assert beat_to_ticks(1.5) == 240


def test_pitch_to_midi():
    assert pitch_to_midi("C4") == 60
    assert pitch_to_midi(60) == 60
    assert pitch_to_midi("rest") == -1
    assert pitch_to_midi("kick", is_percussion=True) == 36


def test_duration_to_ticks():
    assert duration_to_ticks("quarter") == 480
    assert duration_to_ticks("eighth") == 240
    with pytest.raises(ValueError):
        duration_to_ticks("invalid")


def test_json_to_midi_bytes_empty():
    empty_notes = MusicNotes(channels=[])
    midi_bytes = json_to_midi_bytes(empty_notes)

    assert isinstance(midi_bytes, bytes)
    buffer = BytesIO(midi_bytes)
    mid = MidiFile(file=buffer)
    # Empty notes result in no tracks
    assert len(mid.tracks) == 0