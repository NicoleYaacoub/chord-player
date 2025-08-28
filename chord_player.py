#re1: receber o acorde do utilizador
#re2: calcular a frequência das notas
#re3: gerar som com ondas sinusoidais
    #re3.1: criar variável t
    #re3.2: criar ondas sinusoidais para cada freq 
    #re3.3: somar as ondas e normalizar
#re4: ouvir o acorde diretamente no Python com sounddevice

#re5: pedir a waveform ao utilizador
#re6: criar a waveform para as varias frequencias
#re7: ouvir 


#fillipe

from musicpy import get_chord
import numpy as np
import sounddevice as sd


waveform_input = input("Enter wave form:[sine/square/sawtooth/triangle]: ").strip().lower()

while True:

    ch_input = input("Enter chord: ")

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

print("Chord Notes:", notes_separated)

if bass_note:
    print("Bass note is:" , bass_note,number_bass)

print("Freqs:", freqs_final)

duration = 2
sample_rate = 44100
t = np.linspace(0 , duration , num = sample_rate * duration , endpoint=False)

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

sd.play(signal, samplerate= sample_rate)
sd.wait()