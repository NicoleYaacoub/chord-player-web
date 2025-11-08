from backend.synth.chord_engine import chord_to_freqs

def test_chord_to_freqs():
    freqs, notes = chord_to_freqs("Cmaj7")
    assert "C" in notes[0]
