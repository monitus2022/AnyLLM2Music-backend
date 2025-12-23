# Step 4: Note Events Generation

NOTE_EVENTS_OUTPUT_FORMAT = {
    "sections": [
        {
            "section": "Intro",
            "bars": [
                {
                    "bar": 1,
                    "events": [
                        [1, "D4", "quarter", 80],
                        [2, "F4", "eighth", 85],
                        [2.5, "A4", "eighth", 85],
                        [1, "D2", "quarter", 90],
                        [1, "PercKick", "quarter", 100]
                    ]
                }
            ]
        }
    ]
}

NOTE_EVENTS_ARRAY_EXPLANATION = {
    "beat": 1, "pitch": "D4", "duration": "quarter", "velocity": 80}

ALL_CHANNELS = ["melody", "bass", "perc", "harmony"]


def generate_note_events_prompt(channel: str, rhythm_input: str, music_plan_input: str):
    return f"""
You are a symbolic music generator.
Given the music plan and rhythmic plan, output structured note events in JSON for the {channel} channel only.
Do not include other channels.

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
