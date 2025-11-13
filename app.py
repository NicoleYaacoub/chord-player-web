"""
Flask backend for Chord Player Web.
Exposes REST endpoints for chord and progression synthesis.
"""

import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from backend.synth.chord_engine import synthesize_chord, synthesize_progression
import numpy as np
from scipy.io.wavfile import write
import tempfile

# -----------------------------------
# Flask setup
# -----------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,      # absolute path to frontend
    static_url_path=""               # leave empty to serve files correctly
)
CORS(app)



# ==============================
# Helper: save NumPy array as WAV
# ==============================

def save_temp_wav(signal, sample_rate=44100):
    """Save a NumPy signal to a temporary .wav file and return its path."""
    temp_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=temp_dir)
    write(temp_file.name, sample_rate, signal)
    return temp_file.name


# ==============================
# Routes
# ==============================

@app.route("/api/chord", methods=["POST"])
def api_chord():
    """
    Generate a single chord.
    Expected JSON:
      {
        "chord": "Cmaj7",
        "preset": "piano",
        "duration": 2.0
      }
    """
    data = request.get_json()
    chord = data.get("chord", "Cmaj7")
    preset = data.get("preset", "piano")
    duration = float(data.get("duration", 2.0))

    signal, notes = synthesize_chord(chord, preset, duration)
    file_path = save_temp_wav(signal)

    return jsonify({
        "status": "ok",
        "chord": chord,
        "notes": notes,
        "audio_url": f"/api/audio?path={os.path.basename(file_path)}"
    })


@app.route("/api/progression", methods=["POST"])
def api_progression():
    """
    Generate a progression of chords.
    Expected JSON:
      {
        "chords": ["Cmaj7", "Am7", "Dm7", "G7"],
        "preset": "piano",
        "duration": 2.0
      }
    """
    data = request.get_json()
    chords = data.get("chords", [])
    preset = data.get("preset", "piano")
    duration = float(data.get("duration", 2.0))

    signal, all_notes = synthesize_progression(chords, preset, duration)
    file_path = save_temp_wav(signal)

    return jsonify({
        "status": "ok",
        "chords": all_notes,
        "audio_url": f"/api/audio?path={os.path.basename(file_path)}"
    })


@app.route("/api/audio")
def get_audio():
    """Serve generated WAV files from /static."""
    path = request.args.get("path")
    full_path = os.path.join(os.path.dirname(__file__), "static", path)

    # 🔒 Segurança opcional: verificar se o ficheiro existe
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(full_path, mimetype="audio/wav")


# ==============================
# Frontend route
# ==============================

@app.route("/")
def serve_index():
    """Serve the frontend (index.html)."""
    return send_from_directory(app.static_folder, "index.html")


# ==============================
# Run
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

