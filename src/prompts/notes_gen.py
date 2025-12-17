# Step 4: Note Events Generation

NOTE_EVENTS_OUTPUT_FORMAT = {
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

RHYTHM_INPUT = """<No rtythm input is provided from previous steps>"""

ALL_CHANNELS = ["melody", "bass", "perc", "harmony"]

channel = ALL_CHANNELS[0] # By default

NOTE_EVENTS_PROMPT = f"""
You are a symbolic music generator.
Given the harmonic + rhythmic plan, output structured note events in JSON.
Only include the {channel} channel. Do not include other channels.

Output format:
----------------
{NOTE_EVENTS_OUTPUT_FORMAT}
----------------

In the example, the first element in "events" represent the following:
{"beat":1, "pitch":"D4", "duration":"quarter", "velocity":80}

Input:
{RHYTHM_INPUT}
"""




