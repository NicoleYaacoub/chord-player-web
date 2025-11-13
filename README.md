# 🎹 Chord Player Web

A lightweight web application that generates and plays chords and chord
progressions using a Python/Flask backend and a clean HTML/JS frontend.\
Supports multiple presets, piano-note highlighting, MIDI-to-frequency
conversion, ADSR envelopes, and real-time waveform synthesis.

## 🚀 Features

### 🎼 Chord Engine

-   Supports all standard chord types: maj, min, 7, maj7, dim, aug,
    sus4, add9, etc.
-   Supports slash chords (e.g., Cmaj7/E)
-   Uses musicpy for chord parsing
-   Converts notes → MIDI → frequency
-   Real-time synthesis using ADSR and waveforms

### 🎹 Interactive Web Interface

-   Input any chord or progression
-   Choose preset (Piano, Strings, Pluck, Accordion, Pad)
-   Piano keyboard that lights up active notes

### 🔊 Audio Generation

-   Pure Python synthesis (NumPy)
-   WAV generation on the fly
-   REST API endpoints

## 🧩 Project Structure

CHORD_PLAYER_WEB/
├── backend/
│   ├── app.py                   # Flask backend (API + serving frontend)
│   ├── static/                  # Generated WAV files (audio cache)
│   └── synth/
│       ├── __init__.py
│       └── chord_engine.py      # Core synthesis engine
│
├── frontend/
│   ├── index.html               # Main UI
│   ├── css/
│   │   └── style.css            # UI styles
│   └── js/
│       └── main.js              # Fetch + piano + audio control
│
├── tests/                       # Test scripts
│   └── ...
├── run_test.py                  # Helper to run tests
├── requirements.txt
└── README.md


## 📦 Installation

### 1. Clone

git clone https://github.com/SEU-REPO/chord-player-web.git

### 2. Environment

python -m venv venv\
pip install -r requirements.txt

## ▶️ Run

python app.py

## 🔌 API

### POST /api/chord

{ "chord": "Cmaj7", "preset": "piano", "duration": 2.0 }

### POST /api/progression

{ "chords": \["Cmaj7","Am7"\], "preset": "piano" }

## 🛠️ Technologies

Python, Flask, NumPy, SciPy, JS, HTML/CSS, musicpy

## 👩‍💻 Author

Nicole Yaacoub

