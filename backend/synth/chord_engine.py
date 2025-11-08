"""
Chord synthesis engine for Chord Player Web.

This module provides:
 - note/chord parsing and frequency generation
 - ADSR envelope synthesis
 - waveform generation
 - chord progression playback (offline signal generation)

Author: Nicole Yaacoub
"""

import numpy as np
from musicpy import get_chord


# ==============================
# Global constants
# ==============================

NOTE_NUMBER = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

EQUIVAL = {
    # Flats → sharps
    'DB': 'C#', 'EB': 'D#', 'GB': 'F#', 'AB': 'G#', 'BB': 'A#',
    # Enharmonic equivalents
    'E#': 'F', 'B#': 'C', 'CB': 'B', 'FB': 'E',
    # Double sharps (rare cases)
    'FX': 'G', 'CX': 'D', 'GX': 'A', 'AX': 'B', 'DX': 'E'
}

PRESETS = {
    "piano": {"adsr": [0.005, 0.12, 0.20, 0.15], "waveform": "sine"},
    "strings": {"adsr": [0.4, 0.3, 0.7, 0.6], "waveform": "sawtooth"},
    "pluck": {"adsr": [0.002, 0.08, 0.00, 0.10], "waveform": "triangle"},
    "accordion": {"adsr": [0.20, 0.20, 0.80, 0.20], "waveform": "sawtooth"},
    "pad": {"adsr": [0.60, 0.50, 0.70, 0.80], "waveform": "square"}
}


# ==============================
# Utility functions
# ==============================

def note_to_midi(letter, number):
    """Convert note (ex: 'C', '4') to MIDI number."""
    note_name = EQUIVAL.get(letter.upper(), letter.upper())
    note_num = NOTE_NUMBER[note_name]
    return note_num + (int(number) + 1) * 12


def midi_to_freq(midi):
    """Convert MIDI number to frequency (Hz)."""
    return 440 * pow(2, (midi - 69) / 12)


def adsr_envelope(duration, adsr, sample_rate=44100):
    """Generate an ADSR envelope given time constants and sustain level."""
    attack, decay, sustain, release = adsr
    a = int(attack * sample_rate)
    d = int(decay * sample_rate)
    r = int(release * sample_rate)
    s = max(0, int(duration * sample_rate) - (a + d + r))

    attack_curve = np.linspace(0, 1, a, endpoint=False)
    decay_curve = np.linspace(1, sustain, d, endpoint=False)
    sustain_curve = np.ones(s) * sustain
    release_curve = np.linspace(sustain, 0, r)

    env = np.concatenate([attack_curve, decay_curve, sustain_curve, release_curve])
    expected = int(duration * sample_rate)

    if len(env) > expected:
        env = env[:expected]
    else:
        env = np.pad(env, (0, expected - len(env)))

    return env


def generate_waveform(freq, t, waveform):
    """Generate waveform samples for a given frequency and type."""
    sine = np.sin(2 * np.pi * freq * t)
    if waveform == "square":
        return np.sign(sine + 1e-12)
    elif waveform == "sawtooth":
        return 2 * ((freq * t) % 1) - 1
    elif waveform == "triangle":
        return 2 * np.abs(2 * ((freq * t) % 1) - 1) - 1
    return sine


# ==============================
# Chord parsing and normalization
# ==============================

def normalize_chord_type(ch_type):
    """
    Normalize chord type strings into musicpy-compatible forms.
    Examples:
        'm7(5-)' → 'm7b5'
        'ø' → 'm7b5'
        '°' → 'dim'
        '+' → 'aug'
    """
    clean = ch_type.strip().lower()
    clean = clean.replace("(5-)", "b5").replace("(b5)", "b5").replace("(♭5)", "b5")
    clean = clean.replace("(#5)", "#5").replace("(5#)", "#5")
    clean = clean.replace("(", "").replace(")", "").replace("-", "b")

    aliases = {
        "": "maj",
        "maj": "maj",
        "maj7": "maj7",
        "m": "min",
        "min": "min",
        "m7b5": "m7b5",
        "min7b5": "m7b5",
        "ø": "m7b5",
        "dim": "dim",
        "°": "dim",
        "+": "aug",
        "aug": "aug",
        "sus2": "sus2",
        "sus4": "sus4",
        "m9": "min9",
        "m11": "min11",
        "m13": "min13",
    }

    return aliases.get(clean, clean)


def chord_to_freqs(ch_input):
    """Convert a chord string into a list of frequencies and note names."""
    ch_input = ch_input.upper()

    # Split chord and bass note
    if "/" in ch_input:
        chord_part, bass_note = ch_input.split("/")
    else:
        chord_part, bass_note = ch_input, None

    # Identify root and chord type
    if len(chord_part) > 1 and chord_part[1] in ["#", "B"]:
        base, ch_type = chord_part[:2], chord_part[2:]
    else:
        base, ch_type = chord_part[:1], chord_part[1:]

    base = EQUIVAL.get(base, base)
    ch_type = normalize_chord_type(ch_type)

    # Generate chord notes using musicpy
    ch = get_chord(base, ch_type)

    # Split letter and octave for each note
    notes_separated = []
    for n in ch:
        note = str(n)
        letter = "".join([c for c in note if not c.isdigit()])
        number = "".join([c for c in note if c.isdigit()])
        notes_separated.append((letter, number))

    # Build main chord lists
    freqs = [midi_to_freq(note_to_midi(l, n)) for l, n in notes_separated]
    notes_list = [f"{l}{n}" for l, n in notes_separated]

    # Add bass (slash chord), if present — force octave 3
    if bass_note:
        bass_oct = '3'
        bass_freq = midi_to_freq(note_to_midi(bass_note, bass_oct))
        freqs = [bass_freq] + freqs
        notes_list = [f"{bass_note}{bass_oct}"] + notes_list

    return freqs, notes_list


# ==============================
# Synthesis core
# ==============================

def synthesize_chord(ch_input, preset="piano", duration=2.0, sample_rate=44100):
    """Generate a single chord waveform and corresponding note list."""
    freqs, notes = chord_to_freqs(ch_input)
    adsr = PRESETS[preset]["adsr"]
    waveform = PRESETS[preset]["waveform"]

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waves = [generate_waveform(f, t, waveform) for f in freqs]
    signal = sum(waves)

    # Normalize and apply ADSR envelope
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal /= peak

    envelope = adsr_envelope(duration, adsr, sample_rate)
    signal = signal[:len(envelope)] * envelope

    return signal.astype(np.float32), notes


def synthesize_progression(chords, preset="piano", duration=2.0, sample_rate=44100):
    """Generate a waveform for a full chord progression."""
    full_signal = np.array([], dtype=np.float32)
    all_notes = []

    for ch in chords:
        signal, notes = synthesize_chord(ch, preset, duration, sample_rate)
        full_signal = np.concatenate((full_signal, signal))
        all_notes.append((ch, notes))

    peak = np.max(np.abs(full_signal))
    if peak > 0:
        full_signal /= peak

    return full_signal, all_notes
