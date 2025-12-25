import os
import logging
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from src.schemas.music import MusicNotes, ChannelNotes, SectionNotes, BarNotes

# Constants
TICKS_PER_BEAT = 480  # Standard MIDI ticks per beat
DEFAULT_BPM = 120

# Pitch to MIDI note mapping
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Percussion mapping (MIDI note numbers for GM percussion)
PERCUSSION_MAP = {
    'kick': 36,    # Bass Drum 1
    'snare': 38,   # Acoustic Snare
    'hihat': 42,   # Closed Hi-Hat
    'crash': 49,   # Crash Cymbal 1
    'ride': 51,    # Ride Cymbal 1
    'tom1': 41,    # Low Floor Tom
    'tom2': 43,    # High Floor Tom
    'tom3': 45,    # Low Tom
    'tom4': 47,    # Low-Mid Tom
    'tom5': 48,    # Hi-Mid Tom
    'tom6': 50,    # High Tom
}

def pitch_to_midi(pitch_str, is_percussion: bool = False) -> int:
    """Convert pitch string like 'C4' or 'Eb4' to MIDI note number, or return int if already MIDI."""
    if isinstance(pitch_str, int):
        return pitch_str

    if pitch_str == 'rest':
        return -1  # Special case for rest

    if is_percussion:
        return PERCUSSION_MAP.get(pitch_str.lower(), 36)  # Default to kick

    # Parse note name and octave
    note_name = ''
    octave = 0
    for char in pitch_str:
        if char.isalpha() or char in ['#', 'b']:
            note_name += char
        else:
            octave = int(char)
            break

    # Convert flats to sharps for canonical representation
    flat_to_sharp = {
        'Cb': 'B',  # Cb is B
        'Db': 'C#',
        'Eb': 'D#',
        'Fb': 'E',  # Fb is E
        'Gb': 'F#',
        'Ab': 'G#',
        'Bb': 'A#',
        'C#': 'C#',
        'D#': 'D#',
        'F#': 'F#',
        'G#': 'G#',
        'A#': 'A#',
        'C': 'C',
        'D': 'D',
        'E': 'E',
        'F': 'F',
        'G': 'G',
        'A': 'A',
        'B': 'B'
    }

    canonical_note = flat_to_sharp.get(note_name, note_name)

    # Find note index
    note_index = NOTE_NAMES.index(canonical_note)
    midi_note = (octave + 1) * 12 + note_index
    return midi_note

def duration_to_ticks(duration_str: str, bpm: int = DEFAULT_BPM) -> int:
    """Convert duration string to MIDI ticks."""
    # Assuming 4/4 time, quarter note = 1 beat
    duration_map = {
        'whole': 4,
        'dotted_whole': 6,
        'half': 2,
        'dotted_half': 3,
        'quarter': 1,
        'dotted_quarter': 1.5,
        'eighth': 0.5,
        'dotted_eighth': 0.75,
        '16th': 0.25,
        'sixteenth': 0.25,
        'dotted_sixteenth': 0.375,
        '32nd': 0.125,
        'thirty-second': 0.125
    }

    if duration_str not in duration_map:
        logging.error(f"Unknown duration: {duration_str}")
        raise ValueError(f"Unknown duration: {duration_str}")

    beats = duration_map[duration_str]
    # Ticks = beats * ticks_per_beat
    return int(beats * TICKS_PER_BEAT)

def beat_to_ticks(beat: float, bpm: int = DEFAULT_BPM) -> int:
    """Convert beat position to ticks."""
    # Beat 1 = 0 ticks, beat 2 = ticks_per_beat, etc.
    return int((beat - 1) * TICKS_PER_BEAT)

def json_to_midi(music_notes: MusicNotes, bpm: int = DEFAULT_BPM, output_path: str = 'output.mid') -> str:
    """Convert MusicNotes JSON to MIDI file and return the file path."""
    midi_bytes = json_to_midi_bytes(music_notes, bpm)
    with open(output_path, 'wb') as f:
        f.write(midi_bytes)
    return output_path

def json_to_midi_bytes(music_notes: MusicNotes, bpm: int = DEFAULT_BPM) -> bytes:
    """Convert MusicNotes JSON to MIDI bytes."""
    mid = MidiFile()
    tempo = bpm2tempo(bpm)
    mid.ticks_per_beat = TICKS_PER_BEAT

    # Create tracks for each channel
    channel_tracks = {}
    channel_numbers = {}  # Assign MIDI channels

    # Percussion is channel 9
    percussion_channel = 9
    next_channel = 0

    for channel_data in music_notes.channels:
        channel_name = channel_data.channel
        if channel_name == 'perc':
            channel_num = percussion_channel
        else:
            channel_num = next_channel
            next_channel += 1
            if next_channel == 9:  # Skip percussion channel
                next_channel = 10

        track = MidiTrack()
        mid.tracks.append(track)
        channel_tracks[channel_name] = track
        channel_numbers[channel_name] = channel_num

        # Add track name
        track.append(MetaMessage('track_name', name=channel_name, time=0))

    # Add tempo to first track
    if mid.tracks:
        mid.tracks[0].append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # Process each channel
    for channel_data in music_notes.channels:
        channel_name = channel_data.channel
        track = channel_tracks[channel_name]
        channel_num = channel_numbers[channel_name]

        # Collect all events with absolute timing
        events = []

        for section in channel_data.sections:
            for bar in section.bars:
                bar_num = bar.bar
                for event in bar.events:
                    beat, pitch, duration, velocity = event
                    # Calculate absolute beat position
                    absolute_beat = (bar_num - 1) * 4 + beat
                    start_ticks = int((absolute_beat - 1) * TICKS_PER_BEAT)
                    duration_ticks = duration_to_ticks(duration, bpm)

                    is_perc = (channel_name == 'perc')
                    midi_note = pitch_to_midi(pitch, is_perc)
                    if midi_note >= 0:  # Not a rest
                        # Adjust velocity for percussion to prevent overwhelming
                        adjusted_velocity = min(velocity, 80) if is_perc else velocity
                        events.append((start_ticks, 'note_on', midi_note, adjusted_velocity))
                        events.append((start_ticks + duration_ticks, 'note_off', midi_note, 0))

        # Sort events by time
        events.sort(key=lambda x: x[0])

        # Add events to track
        current_time = 0
        for event_time, event_type, note, velocity in events:
            delta_time = event_time - current_time
            if event_type == 'note_on':
                track.append(Message('note_on', note=note, velocity=velocity, channel=channel_num, time=delta_time))
            else:
                track.append(Message('note_off', note=note, velocity=0, channel=channel_num, time=delta_time))
            current_time = event_time

    # Return MIDI bytes
    from io import BytesIO
    buffer = BytesIO()
    mid.save(file=buffer)
    buffer.seek(0)
    return buffer.read()
