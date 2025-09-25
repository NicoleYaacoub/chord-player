from musicpy import get_chord
import numpy as np
import sounddevice as sd

presets_input = input("Choose the preset (piano/strings/pluck/accordion/pad): ").strip().lower()

#dicionário de presets
PRESETS = {
    "piano": {
        "adsr": [0.005, 0.12, 0.20, 0.15],
        "waveform": "sine"       
    },
    "strings": {
        "adsr": [0.4, 0.3, 0.7, 0.6],
        "waveform": "sawtooth"    
    },
    "pluck": {
        "adsr": [0.002, 0.08, 0.00, 0.10],
        "waveform": "triangle"    
    },
    "accordion": {
        "adsr": [0.20, 0.20, 0.80, 0.20],
        "waveform": "sawtooth"    
    },

    "pad": {
        "adsr": [0.60, 0.50, 0.70, 0.80],
        "waveform": "square"    
    },

} 

#validaçao do preset input 
if presets_input in PRESETS:
    adsr = PRESETS[presets_input]["adsr"]
    waveform_input = PRESETS[presets_input]["waveform"]
else:
    print("Invalid preset. Using piano as default.")
    adsr = PRESETS["piano"]["adsr"]
    waveform_input = PRESETS["piano"]["waveform"]


while True:

    ch_input = input("Enter chord: ").upper()

    chord_part = "" 
    bass_note = ""

    if len(ch_input) > 1 and "/" in ch_input: #se houver acordes com baixo diferente
        chord_part , bass_note = ch_input.split("/")
    else:
        chord_part = ch_input
        bass_note = None

    if bass_note:
        letter_bass = bass_note.upper()
        number_bass = "3"

    if len(chord_part) > 1 and chord_part[1] in [ "#" , "b" ]: 
        base = chord_part[:2]
        ch_type = chord_part[2:]
    else:
        base = chord_part[:1]
        ch_type = chord_part[1:]

    if ch_type == "" or ch_type == "M" or ch_type == "Maj":
        ch_type = "maj"

    if ch_type == "m":
        ch_type = "min"

    try:
        ch = get_chord(base , ch_type)
        break
    except:
        print("Invalid chord. Try Again.")

note_number = {'C':0 , 'C#':1 , 'D':2 , 'D#':3 , 'E':4 , 'F':5 , 'F#':6 , 'G':7 , 'G#':8 , 'A':9 , 'A#':10, 'B':11}
equival = {
    'DB':'C#', 'EB':'D#', 'GB':'F#', 'AB':'G#', 'BB':'A#',
    'E#':'F', 'B#':'C', 'CB':'B', 'FB':'E'
}


#Criar os pares (nota, oitava)
notes_separated = []
for n in ch: #percorre cada nota do acorde
    note = str(n) #transforma a nota em str
    letter = ""
    number = ""
    for x in note: #percorre cada caracter da str
        if x.isdigit():
            number += x
        else:
            letter += x
    notes_separated.append((letter, number))



def note_to_midi(letter, number): #função que calcula o numero midi
    note_name = equival.get(letter.upper(), letter.upper())
    note_num = note_number[note_name] 
    midi_number = note_num + (int(number) + 1) * 12
    return midi_number


#lista com os numeros midi de cada nota do acorde
midi_list = []
for l, n in notes_separated:
    midi = note_to_midi(l, n)
    midi_list.append(midi)


def midi_to_freq(midi_list):
    freq_list = []
    for m in midi_list:
        freq = 440 * pow(2, (m-69)/12)
        freq_list.append(freq)
    return freq_list

freqs = midi_to_freq(midi_list)
if bass_note:
    bass_midi = note_to_midi(letter_bass , number_bass)
    bass_freq = midi_to_freq([bass_midi])[0]
    freqs_final = [bass_freq] + freqs
else:
    freqs_final = freqs

duration = 2
sample_rate = 44100
t = np.linspace(0 , duration , num = sample_rate * duration , endpoint=False)


def adsr_envelope(duration, adsr:list, sample_rate = 44100): 

    attack_samples = int(adsr[0] * sample_rate)
    decay_samples = int(adsr[1] * sample_rate)
    release_samples = int(adsr[3] * sample_rate)
    sustain_samples = max(0, int((duration * sample_rate) - (attack_samples + decay_samples + release_samples)))

    attack = np.linspace(0, 1, attack_samples, endpoint=False)
    decay = np.linspace(1, adsr[2], decay_samples, endpoint=False)
    sustain = np.ones(sustain_samples) * adsr[2]
    release = np.linspace(adsr[2] , 0 , release_samples)

    envelope = np.concatenate([attack, decay, sustain, release])
    expected = duration * sample_rate

    if len(envelope) != expected:
        if len(envelope) > expected:
            envelope = envelope[:expected]
        else:
            envelope = np.pad(envelope, (0, expected - len(envelope)))

    return envelope



def generate_waveform(freq, t, waveform):
    sine = np.sin(2* np.pi * freq * t)
    square = np.sign(sine + 1e-12)
    sawtooth = 2 * ((freq * t) % 1) -1
    triangle = 2 * np.abs(2*((freq * t) %1) -1) -1
    if waveform == "square": 
        return square
    elif waveform == "sawtooth": 
        return sawtooth
    elif waveform == "triangle": 
        return triangle
    else: 
        return sine


waves = []
for f in freqs_final:
    wave = generate_waveform(f, t, waveform_input)
    waves.append(wave)


signal = sum(waves) 
peak = np.max(np.abs(signal))
if peak > 0:
    signal = signal / peak


#chamar a função adsr
envelope = adsr_envelope(duration, adsr, sample_rate)
#aplicar a função ao sinal
signal = signal[:len(envelope)] * envelope

signal = signal.astype(np.float32) #converte o sinal para float32
sd.play(signal, samplerate=sample_rate)
sd.wait()
