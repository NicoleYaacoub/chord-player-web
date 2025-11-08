/* ---------------------------------------
   Main logic: send chord to Flask backend
--------------------------------------- */

document.getElementById("playBtn").addEventListener("click", async () => {
  const chordInput = document.getElementById("chordInput").value.trim();
  const preset = document.getElementById("presetSelect").value;
  const output = document.getElementById("output");
  const audioPlayer = document.getElementById("audioPlayer");

  if (!chordInput) {
    output.innerHTML = "<p style='color:red'>Please enter a chord!</p>";
    return;
  }

  // Detect progression (multiple chords)
  const chords = chordInput.split(",").map(c => c.trim());
  const endpoint = chords.length > 1 ? "/api/progression" : "/api/chord";
  const body = chords.length > 1
    ? { chords, preset, duration: 2 }
    : { chord: chords[0], preset, duration: 2 };

  try {
    output.innerHTML = "<p>Generating sound...</p>";

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    if (data.status === "ok") {
      output.innerHTML = `
        <h3>${data.chord || "Chord progression"}</h3>
        <p><strong>Notes:</strong> ${
          data.notes ? data.notes.join(", ") : data.chords.map(c => c[1].join(", ")).join(" | ")
        }</p>
      `;

      // 🔥 highlight the notes on the piano
      highlightNotes(data.notes || []);

      // 🎧 play audio
      audioPlayer.src = data.audio_url;
      audioPlayer.play();

      // 🕓 clear highlights automatically after sound finishes
      setTimeout(clearHighlights, 2000); // matches 2s duration
    } else {
      output.innerHTML = "<p style='color:red'>Error generating audio.</p>";
    }
  } catch (err) {
    output.innerHTML = `<p style='color:red'>Error: ${err.message}</p>`;
    console.error(err);
  }
});

/* ---------------------------------------
   Piano visual setup and highlighting
--------------------------------------- */

// notes across two octaves (C4–B5)
const NOTES = [
  "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
  "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5"
];

const piano = document.getElementById("piano");

// build the piano layout (aligned keys)
function createPiano() {
  const WHITE_NOTES = ["C", "D", "E", "F", "G", "A", "B"];
  const BLACK_NOTES = ["C#", "D#", "F#", "G#", "A#"];
  const NOTE_ORDER = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

  const numOctaves = 2;
  const whiteKeyWidth = 40;

  for (let octave = 4; octave < 4 + numOctaves; octave++) {
    let whiteIndex = 0;

    NOTE_ORDER.forEach(note => {
      const key = document.createElement("div");
      const fullNote = `${note}${octave}`;
      key.dataset.note = fullNote;

      if (BLACK_NOTES.includes(note)) {
        key.classList.add("key", "black");
        // posicionar entre as brancas
        key.style.left = `${(whiteIndex - 0.5) * whiteKeyWidth}px`;
      } else {
        key.classList.add("key", "white");
        key.style.left = `${whiteIndex * whiteKeyWidth}px`;
        whiteIndex++;
      }

      piano.appendChild(key);
    });
  }
}


// highlight active keys
function highlightNotes(notes) {
  clearHighlights();
  notes.forEach(n => {
    const pure = n.replace(/[0-9]/g, "");
    const key = document.querySelector(`.key[data-note^='${pure}']`);
    if (key) key.classList.add("active");
  });
}

// clear all highlights
function clearHighlights() {
  document.querySelectorAll(".key").forEach(k => k.classList.remove("active"));
}

// create piano when page loads
createPiano();
