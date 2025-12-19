# Step 1: Music Plan ---------------------------------------------

MUSIC_PLAN_OUTPUT_FORMAT = {
    "1_genre_style": "Retro 8-bit chiptune with NES/SNES influences (square waves, limited polyphony)",
    "2_mood_emotion": "Tense and energetic battle atmosphere, building urgency and triumph",
    "3_tempo_feel": {"bpm": 160, "meter": "4/4", "feel": "Straight 8ths with swing on percussion"},
    "4_key_tonality": "C minor (Aeolian mode, with occasional Phrygian inflections)",
    "5_instruments": [
        {"name": "Square Wave Lead", "role": "melody"},
        {"name": "Triangle Wave", "role": "bass"},
        {"name": "Noise Channel", "role": "percussion"},
        {"name": "DPCM Saw Pad", "role": "harmony/pad"},
    ],
    "6_structure": [
        {"section": "Intro", "bars": 4, "transition": "fade in to A"},
        {"section": "A", "bars": 8, "transition": "build to B"},
        {"section": "B", "bars": 8, "transition": "tension release to A or bridge"},
        {"section": "Bridge", "bars": 4, "transition": "half-time feel to outro"},
        {"section": "Outro", "bars": 4, "transition": "fade out"},
    ],
    "7_motivic_ideas": {
        "Intro": "Motif1: Rising chromatic tension (C-Db-D-Eb)",
        "A": "Motif2: Staccato arpeggio ascent (C-Eb-G-Bb), Motif1 echoes",
        "B": "Motif3: Descending scale run (G-F-Eb-D-C), counterpoint with Motif2",
        "Bridge": "Motif4: Dissonant cluster (Ab-Bb-C-Db)",
        "Outro": "Motif1 inverted + resolve to C",
    },
    "8_dynamic_contour": "pp intro (build tension) → mf A (steady energy) → f B (climax) → mp bridge (release) → p outro (fade)",
    "9_length_scale": {"total_bars": 28, "duration_seconds": "approx 42s at 160 BPM"},
    "10_looping_behavior": "Seamless loop from end of A back to A; outro optional for full playthrough",
}

MUSIC_PLAN_USER_DESCRIPTION = """<User didn't input any description>"""

MUSIC_PLAN_USER_PARAMETERS = """{
    "genre_style": "8-bit chiptune",
    "tempo": "120 BPM",
    "key": "C minor",
    "time_signature": "4/4",
    "duration_seconds": 30,
    "mood_emotion": "energetic",
}"""

DEFINE_MUSIC_PLAN_PROMPT = f"""
You are a music composer planning a piece before writing notes. 
Given a text description (e.g., "retro 8-bit battle theme"), create a structured outline of the music. 
Format the answer as a json with concise but specific details. 
If user provide any specified parameters (e.g., tempo, key, duration, genre, mood, instruments, time signature), 
override defaults with these values.
However, always ensure tempo is 60-200 BPM, duration fits the structure, and instruments match the genre.

Output format:
----------------------
{str(MUSIC_PLAN_OUTPUT_FORMAT)}
----------------------
Do not generate notes or MIDI tokens yet—only the high-level outline.

User input for music generic description:

{MUSIC_PLAN_USER_DESCRIPTION}

User input for specific parameters:

{MUSIC_PLAN_USER_PARAMETERS}
"""

# Step 2: Chord generation ---------------------------------------------

CHORD_OUTPUT_FORMAT = {
    "key": "D minor (Dorian inflections)",
    "sections": [
        {
            "name": "Intro",
            "bars": 4,
            "chords": ["Dm", "Dm(add9)/F", "Bb", "F/C"],
            "motifs": {"Intro": [1, 2, 3, 4]},
            "loop": "cut to A",
        },
        {
            "name": "A",
            "bars": 8,
            "chords": ["Dm", "Bb", "F", "C", "Dm", "Gm", "Am", "Dm"],
            "motifs": {"A": [5, 6, 7, 8, 9, 10, 11, 12]},
            "loop": "repeat or to B",
        },
    ],
}

MUSIC_PLAN_INPUT = """<No music input is provided from previous steps>"""

DEFINE_CHORD_PROMPT = f"""
You are a music arranger. 
Given the outline below, output only the harmonic backbone in compact JSON.

Output format:
---------------
{str(CHORD_OUTPUT_FORMAT)}
---------------
Do not include rhythm grids, dynamics, or other details yet.

Outline:
{MUSIC_PLAN_INPUT}

User specified parameters:
{str(MUSIC_PLAN_USER_PARAMETERS)}
"""

# Step 3: Rtythm generation ---------------------------------------------

RHYTHM_OUTPUT_FORMAT = {
    "sections": [
        {
            "section": "Intro",
            "bars": 2,
            "bass": ["8ths C-G (Cm root-5th) bars 1-2"],
            "perc": ["Kick on 1, Hi-hat 8ths bars 1-2"],
            "melody": ["Motif Intro: C-Eb-G-C (arpeggio, 8ths) bars 1-2"],
            "harmony": ["Sustain Cm triad (C-Eb-G) bars 1-2"],
            "voiceLeading": ["stepwise C-Eb-G"],
            "dynamics": ["pp (vel 40-60) bars 1-2"],
            "polyphony": "≤2 voices/channel",
            "loop": "fade to A"
        },
        {
            "section": "A",
            "bars": 8,
            "bass": ["8ths D-G (Dm root-5th) bars 1-6", "sync 16ths D-G-A-G bars 7-8"],
            "perc": ["Kick on 1, Snare on 2+4, Hi-hat 8ths bars 1-7; snare fill (snare 16ths) bar 8"],
            "melody": ["Motif A: C-Db-D-Eb (rising chromatic, 8ths) bars 1-2,5-6", "Motif B: Eb-D-C-Bb (descending, quarters) bars 3-4,7-8"],
            "harmony": ["Sustain Dm triad (D-F-A) bars 1-6", "Bb triad (Bb-D-F) bar 7", "crescendo bar 7"],
            "voiceLeading": ["stepwise D-E-F in bass", "leaps Eb-C in melody"],
            "dynamics": ["mf (vel 60-80) bars 1-4", "crescendo (vel 80-100) bar 7", "f (vel 90-110) bar 8"],
            "polyphony": "≤2 voices/channel, no overlaps in harmony",
            "loop": "resolves to Em, repeat or transition to B"
        }
    ]
}

MUSIC_CHORDS_INPUT = """<No chord input is provided from previous steps.>"""

DEFINE_RHYTHM_PROMPT = f"""
You are a music arranger.
Given the harmonic backbone below, expand into rhythmic and expressive detail for ALL sections in compact JSON.
Reference specific pitches from chords and motifs. Include basic patterns for percussion (e.g., kick on beat 1, snare on 2+4).
Ensure details are sufficient for direct note event creation without further inference—include pitches, durations, and velocities where possible.

Output format:
---------------
{str(RHYTHM_OUTPUT_FORMAT)}
Do not regenerate chords—only add rhythmic/expression detail for each section.

Backbone:
{MUSIC_CHORDS_INPUT}

User specified parameters:
{str(MUSIC_PLAN_USER_PARAMETERS)}
"""
