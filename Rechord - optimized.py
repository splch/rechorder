from datetime import date
import struct
import numpy as np
from scipy.fftpack import fft
import pyaudio
import music21 # install musescore

def input_stream(key, hz, notes):
    note = scale[(key - 1) % 12] + str((key+8) // 12) # note as string
    print(note, '\t', int(hz))
    return note

def transcribe(notes):
    music = []
    nps = 12 # in 1 second, the program records 12 notes
    i = 0
    j = 1
    while i < len(notes):
        try:
            if notes[i] == notes[j]:
                j += 1
            else:
                dur = str(min([1,2,4,8,16,32], key=lambda x:abs(x-(round(1 / (j - i) * nps)))))
                music.append(notes[i] + '-' + dur)
                i = j
        except IndexError:
            dur = str(min([1,2,4,8,16,32,64], key=lambda x:abs(x-(round(1 / (j - i) * nps)))))
            music.append(notes[i] + '-' + dur)
            i = j
            i += 1
        
    s = music21.stream.Score()
    s.insert(0, music21.metadata.Metadata())
    s.metadata.title = "title"
    day = date.today()
    s.metadata.date = f"{day.year}/{day.month}/{day.day}"
    s.metadata.composer = "composer"
    for n in music:
        if n[0] == 'R':
            s.append(music21.stream.note.Rest(n[n.index('-')+1:]))
        else:
            s.append(music21.note.Note(n[:n.index('-')], type=types[n[n.index('-')+1:]]))
    try:
        s.show()
    except:
        s.show("text")
    return 0

def conv(fs):
    fs_max = -np.sort(-fs)
    key = None
    i = 0
    while not key:
        i += 1
        hz = round((np.where(fs == fs_max[i])[0][0]) * RATE / CHUNK) # convert FFT to hz
        note = int(round(12 * np.log2(hz/440) + 49)) # hz to note on piano
        if note > 0 and note < 109:
            key = note
    return key, hz

def record(rests = True):
    # stream object
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK,
    )
    print("recording...\n")
    notes = ['R']
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
            data_np = np.array(data_int, dtype='b')[::2] + 128
            if np.percentile(np.abs(data_np), 90) >= 200: # check volume if a note is being played
                # compute FFT and update line
                fs = np.abs(fft(data_int)[0:CHUNK])
                key, hz = conv(fs) # convert most common frequencies
                notes.append(input_stream(key, hz, notes))
            elif rests and len(notes) > 1:
                notes.append('R')
    except KeyboardInterrupt:
        p.close(stream)
        print("\n\nterminated recording\n\n")
    return notes

# stream constants
CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
scale = ['A', "A#", 'B', 'C', "C#", 'D', "D#", 'E', 'F', "F#", 'G', "G#"]
types = {'1': "whole", '2': "half", '4': "quarter", '8': "eighth", '16': "sixteenth"}
notes = record(rests=False) # interrupt to end stream
transcribe(notes)