from musicpy import get_chord
import numpy as np
import sounddevice as sd

# ==============================
# Constantes globais
# ==============================

NOTE_NUMBER = {'C':0 , 'C#':1 , 'D':2 , 'D#':3 , 'E':4 , 'F':5 , 'F#':6 , 'G':7 , 'G#':8 , 'A':9 , 'A#':10, 'B':11}
EQUIVAL = {
    'DB':'C#', 'EB':'D#', 'GB':'F#', 'AB':'G#', 'BB':'A#',
    'E#':'F', 'B#':'C', 'CB':'B', 'FB':'E'
}

PRESETS = {
    "piano": {"adsr": [0.005, 0.12, 0.20, 0.15], "waveform": "sine"},
    "strings": {"adsr": [0.4, 0.3, 0.7, 0.6], "waveform": "sawtooth"},
    "pluck": {"adsr": [0.002, 0.08, 0.00, 0.10], "waveform": "triangle"},
    "accordion": {"adsr": [0.20, 0.20, 0.80, 0.20], "waveform": "sawtooth"},
    "pad": {"adsr": [0.60, 0.50, 0.70, 0.80], "waveform": "square"}
}

# ==============================
# Funções utilitárias
# ==============================

def note_to_midi(letter, number):
    """Converte nota (ex: C, 4) para número MIDI"""
    note_name = EQUIVAL.get(letter.upper(), letter.upper())
    note_num = NOTE_NUMBER[note_name]
    return note_num + (int(number) + 1) * 12

def midi_to_freq(midi):
    """Converte número MIDI para frequência"""
    return 440 * pow(2, (midi - 69) / 12)

def adsr_envelope(duration, adsr, sample_rate=44100):
    """Cria envelope ADSR"""
    attack, decay, sustain_level, release = adsr
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = max(0, int(duration*sample_rate) - (attack_samples + decay_samples + release_samples))

    attack_curve = np.linspace(0, 1, attack_samples, endpoint=False)
    decay_curve = np.linspace(1, sustain_level, decay_samples, endpoint=False)
    sustain_curve = np.ones(sustain_samples) * sustain_level
    release_curve = np.linspace(sustain_level, 0, release_samples)

    envelope = np.concatenate([attack_curve, decay_curve, sustain_curve, release_curve])
    expected = int(duration * sample_rate)

    # Ajustar tamanho
    if len(envelope) > expected:
        envelope = envelope[:expected]
    else:
        envelope = np.pad(envelope, (0, expected - len(envelope)))

    return envelope

def generate_waveform(freq, t, waveform):
    """Gera onda a partir de frequência"""
    sine = np.sin(2 * np.pi * freq * t)
    if waveform == "square": 
        return np.sign(sine + 1e-12)
    elif waveform == "sawtooth": 
        return 2 * ((freq * t) % 1) - 1
    elif waveform == "triangle": 
        return 2 * np.abs(2 * ((freq * t) % 1) - 1) - 1
    else:  # sine por default
        return sine

# ==============================
# Parsing de acordes
# ==============================

def chord_to_freqs(ch_input):
    """Recebe um acorde em string e devolve lista de frequências"""
    ch_input = ch_input.upper()

    # Separar acorde e baixo
    if "/" in ch_input:
        chord_part, bass_note = ch_input.split("/")
    else:
        chord_part, bass_note = ch_input, None

    # Base + tipo
    if len(chord_part) > 1 and chord_part[1] in ["#", "B"]:
        base, ch_type = chord_part[:2], chord_part[2:]
    else:
        base, ch_type = chord_part[:1], chord_part[1:]

    if ch_type in ["", "M", "MAJ"]:
        ch_type = "maj"
    if ch_type == "M":
        ch_type = "min"

    # Obter notas com musicpy
    ch = get_chord(base, ch_type)

    # Extrair pares (letra, oitava)
    notes_separated = []
    for n in ch:
        note = str(n)
        letter, number = "".join([c for c in note if not c.isdigit()]), "".join([c for c in note if c.isdigit()])
        notes_separated.append((letter, number))

    # Converter para freq
    freqs = [midi_to_freq(note_to_midi(l, n)) for l, n in notes_separated]

    # Adicionar baixo
    if bass_note:
        bass_freq = midi_to_freq(note_to_midi(bass_note, notes_separated[0][1]))  # mesma oitava
        freqs = [bass_freq] + freqs

    return freqs

# ==============================
# Síntese e reprodução
# ==============================

def synthesize_chord(ch_input, preset="piano", duration=2.0, sample_rate=44100):
    """Gera sinal de um acorde dado um preset"""
    freqs = chord_to_freqs(ch_input)
    adsr = PRESETS[preset]["adsr"]
    waveform = PRESETS[preset]["waveform"]

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Somar todas as ondas
    waves = [generate_waveform(f, t, waveform) for f in freqs]
    signal = sum(waves)

    # Normalizar
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal /= peak

    # Aplicar envelope
    envelope = adsr_envelope(duration, adsr, sample_rate)
    signal = signal[:len(envelope)] * envelope

    return signal.astype(np.float32)

def play_signal(signal, sample_rate=44100):
    """Toca o sinal"""
    sd.play(signal, samplerate=sample_rate)
    sd.wait()

# ==============================
# Main
# ==============================

if __name__ == "__main__":
    preset = input("Choose preset (piano/strings/pluck/accordion/pad): ").strip().lower()
    if preset not in PRESETS:
        print("Invalid preset. Using piano as default.")
        preset = "piano"

    chord = input("Enter chord: ")
    duration = float(input("Enter duration in seconds: ") or 2)

    signal = synthesize_chord(chord, preset, duration)
    play_signal(signal)
