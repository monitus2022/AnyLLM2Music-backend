from midi2audio import FluidSynth
from src.schemas.music import MusicNotes, ChannelNotes, SectionNotes, BarNotes
import os
from .midi import json_to_midi

# Constants
TICKS_PER_BEAT = 480  # Standard MIDI ticks per beat
DEFAULT_BPM = 120


def midi_to_audio(midi_path: str, audio_path: str = 'output.wav', soundfont_path: str = None) -> str:
    """Convert MIDI to audio using FluidSynth."""
    if soundfont_path is None:
        # Use default soundfont, assuming it's installed
        soundfont_path = 'soundfonts/8bit.sf2'  # Common location

    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(
            f"Soundfont not found at {soundfont_path}. Please install FluidSynth soundfonts.")

    fs = FluidSynth(soundfont_path)
    fs.midi_to_audio(midi_path, audio_path)
    return audio_path


def synthesize_audio(music_notes: MusicNotes, bpm: int = DEFAULT_BPM, midi_path: str = 'output.mid', audio_path: str = 'output.wav', soundfont_path: str = 'soundfonts/8bit.sf2') -> str:
    """Full pipeline: JSON to MIDI to Audio."""
    # Convert JSON to MIDI
    midi_file = json_to_midi(music_notes, bpm, midi_path)

    # Convert MIDI to Audio
    audio_file = midi_to_audio(midi_file, audio_path, soundfont_path)

    return audio_file
