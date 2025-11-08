"""
Quick test script for the Chord Player Web synthesis engine.
Runs directly in terminal to check chord and progression synthesis.
"""

import sounddevice as sd
from backend.synth.chord_engine import synthesize_chord, synthesize_progression

# ==============================
# CONFIGURATION
# ==============================

SAMPLE_RATE = 44100
DURATION = 2.0
PRESET = "piano"

# ==============================
# SINGLE CHORD TEST
# ==============================

print("🎹 Testing single chord synthesis...")
chord = "Bm7(5-)"
signal, notes = synthesize_chord(chord, PRESET, DURATION, SAMPLE_RATE)
print(f"Chord: {chord}")
print(f"Notes: {notes}")

sd.play(signal, samplerate=SAMPLE_RATE)
sd.wait()

# ==============================
# CHORD PROGRESSION TEST
# ==============================

print("\n🎶 Testing chord progression synthesis...")
progression = ["Cmaj7", "Am7", "Dm7", "G7"]
signal_prog, all_notes = synthesize_progression(progression, PRESET, DURATION, SAMPLE_RATE)

for chord_name, notes in all_notes:
    print(f"{chord_name}: {notes}")

sd.play(signal_prog, samplerate=SAMPLE_RATE)
sd.wait()

print("\n✅ Test completed successfully!")
