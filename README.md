# 🎹 Chord Player
This is a simple Python project that generates and plays musical chords using sine waves.  
It allows the user to input a chord name and hear its sound using real-time audio playback.

## Features
- Parse user-input chord names (e.g. `Cmaj7`, `G#m`, `F7/A`)
- Generate sine waves for each note in the chord
- Play the resulting chord through the speakers using Python
- Supports chord extensions and slash chords (chord inversions)

## Dependencies

pip install numpy sounddevice musicpy

- musicpy: for chord parsing
- numpy: for generating sine wave signals
- sounddevice: for playing audio in real time

Made with 💛 by Nicole Yaacoub
