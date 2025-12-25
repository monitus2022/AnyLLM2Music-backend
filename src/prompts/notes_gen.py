# Step 4: Note Events Generation

NOTE_EVENTS_OUTPUT_FORMAT = {
    "channels": [
        {
            "channel": "melody",
            "sections": [
                {
                    "section": "Intro",
                    "bars": [
                        {
                            "bar": 1,
                            "events": [
                                [1, "D4", "quarter", 80],
                                [2, "F4", "eighth", 85],
                                [2.5, "A4", "eighth", 85]
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "channel": "bass",
            "sections": [
                {
                    "section": "Intro",
                    "bars": [
                        {
                            "bar": 1,
                            "events": [
                                [1, "D2", "quarter", 90]
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

NOTE_EVENTS_ARRAY_EXPLANATION = {
    "beat": 1, "pitch": "D4", "duration": "quarter", "velocity": 80
}

ALLOWED_DURATIONS = ["whole", "dotted_whole", "half", "dotted_half", "quarter", "dotted_quarter", "eighth", "dotted_eighth", "sixteenth", "dotted_sixteenth", "thirty-second"]

ALL_CHANNELS = ["melody", "bass", "perc", "harmony"]


def generate_note_events_prompt(section_name: str, rhythm_input: str, music_plan_input: str):
    return f"""
You are a symbolic music generator.
Given the music plan and rhythmic plan, output structured note events in JSON for all channels in the {section_name} section only.
Include melody, bass, perc, and harmony channels.

Allowed durations: {', '.join(ALLOWED_DURATIONS)}

Output format:
----------------
{str(NOTE_EVENTS_OUTPUT_FORMAT)}
----------------

In the example, the first element in "events" represent the following:
{str(NOTE_EVENTS_ARRAY_EXPLANATION)}

Music Plan:
{music_plan_input}

Rhythm Plan:
{rhythm_input}
"""
