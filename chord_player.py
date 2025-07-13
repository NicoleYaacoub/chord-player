#re1: receber o acorde do utilizador
#re2: calcular a frequência das notas
#re3: gerar som com ondas sinusoidais
    #re3.1: criar variável t
    #re3.2: criar ondas inusoidais para cada freq 
    #re3.3: somar as ondas e normalizar
#re4: ouvir o acorde diretamente no Python com sounddevice

from musicpy import get_chord, chord
import numpy as np
import sounddevice as sd

#re1

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

#re2
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

#re3.1
duration = 2
sample_rate = 44100
t = np.linspace(0 , duration , num = sample_rate * duration , endpoint=False)

#re3.2
waves = []
for f in freqs_final:
    wave = np.sin( 2 * np.pi * f * t)
    waves.append(wave)

signal = sum(waves) 
signal = signal / np.max(np.abs(signal))

sd.play(signal, samplerate= sample_rate)
sd.wait()