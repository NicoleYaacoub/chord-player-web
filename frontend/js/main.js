/* ---------------------------------------
   MAIN FUNCTIONALITY: CHORD + AUDIO
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
      // ---- notes coming from backend ----
      let notes = data.notes || [];

      // If user typed a slash chord, force the FIRST note (bass) to octave 3 for display,
      // leaving the upper voices as delivered (typically around 4–5).
      if (chordInput.includes("/")) {
        notes = notes.map((n, i) => i === 0 ? n.replace(/\d+/, "3") : n);
      }

      // Keep notes within C3–C6 visually (only if something escaped)
      notes = clampToRange(notes, 3, 6);

      output.innerHTML = `
        <h3>${data.chord || "Chord progression"}</h3>
        <p><strong>Notes:</strong> ${notes.join(", ")}</p>
      `;

      // 🔥 highlight on the keyboard
      highlightNotes(notes);

      // 🎧 audio
      audioPlayer.src = data.audio_url;
      audioPlayer.play();

      // ⏳ clear after ~duration
      setTimeout(clearHighlights, 2000);
    } else {
      output.innerHTML = "<p style='color:red'>Error generating audio.</p>";
    }
  } catch (err) {
    output.innerHTML = `<p style='color:red'>Error: ${err.message}</p>`;
    console.error(err);
  }
});

// clamp visual notes to a given octave span (minOct .. maxOct inclusive of the top C)
function clampToRange(notes, minOct, maxOct) {
  return notes.map(n => {
    const m = n.match(/^([A-G]#?b?)(\d)$/);
    if (!m) return n;
    let [, name, octStr] = m;
    let oct = parseInt(octStr, 10);
    if (oct < minOct) oct = minOct;
    if (oct > maxOct) oct = maxOct;
    return `${name}${oct}`;
  });
}

/* ---------------------------------------
   PIANO VISUALIZATION (C3 → C6)
--------------------------------------- */

const piano = document.getElementById("piano");

function createPiano() {
  const whiteKeyWidth = 40;
  const blackKeyOffset = { "C#": 0.65, "D#": 1.55, "F#": 3.4, "G#": 4.3, "A#": 5.2 };
  const NOTE_ORDER = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

  const START_OCTAVE = 3;
  const END_OCTAVE = 6; // exclusive → ends at B5; we will add C6 manually at the end

  // Calculate white keys count & set piano width dynamically (centered by CSS margin:auto)
  const whiteKeysCount = (END_OCTAVE - START_OCTAVE) * 7 + 1; // +C6
  piano.style.width = `${whiteKeysCount * whiteKeyWidth}px`;

  for (let octave = START_OCTAVE; octave < END_OCTAVE; octave++) {
    NOTE_ORDER.forEach((note, i) => {
      const fullNote = `${note}${octave}`;
      const key = document.createElement("div");
      key.dataset.note = fullNote;

      if (note.includes("#")) {
        key.classList.add("key", "black");
        key.style.left = `${(blackKeyOffset[note] + (octave - START_OCTAVE) * 7) * whiteKeyWidth}px`;
      } else {
        key.classList.add("key", "white");
        key.style.left = `${((i - Math.floor(i / 2)) + (octave - START_OCTAVE) * 7) * whiteKeyWidth}px`;
      }

      piano.appendChild(key);
    });
  }

  // Final C6
  const lastKey = document.createElement("div");
  lastKey.classList.add("key", "white");
  lastKey.dataset.note = "C6";
  lastKey.style.left = `${((END_OCTAVE - START_OCTAVE) * 7) * whiteKeyWidth}px`;
  piano.appendChild(lastKey);
}

/* ---------------------------------------
   NOTE HIGHLIGHTING (enharmonics)
--------------------------------------- */

function highlightNotes(notes) {
  clearHighlights();

  const normalize = n =>
    n.replace("Db", "C#")
     .replace("Eb", "D#")
     .replace("Gb", "F#")
     .replace("Ab", "G#")
     .replace("Bb", "A#");

  notes.forEach(n => {
    const fixed = normalize(n);
    const el = document.querySelector(`.key[data-note='${fixed}']`);
    if (el) el.classList.add("active");
  });
}

function clearHighlights() {
  document.querySelectorAll(".key").forEach(k => k.classList.remove("active"));
}

// Build keyboard
createPiano();
