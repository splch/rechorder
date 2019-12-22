import numpy as np
import pyaudio
import struct
from scipy.fftpack import fft

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

def display(key, hz):
    note = scale[(key - 1) % 12] + str((key+8) // 12) # note as string
    notes.append(note)

    print(note, '\t', hz)

def record():
    print("stream started\n")

    try:
        while True:
            data = stream.read(CHUNK)
            data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
            data_np = np.array(data_int, dtype='b')[::2] + 128

            if np.percentile(np.abs(data_np), 90) >= 200: # check volume if a note is being played
                # compute FFT and update line
                fs = np.abs(fft(data_int)[0:CHUNK])

                key, hz = conv(fs)
                display(key, hz)

    except KeyboardInterrupt:
        p.close(stream)
        print("\n\nstream ended\n\n")

def transcribe(notes): # optimize length algorithm
    music = []
    i = j = 0
    while i < len(notes):
        try:
            if notes[i] == notes[j]:
                j += 1
            else:
                music.append(notes[i] + '-' + str(j-i))
                i = j
        except IndexError:
            music.append(notes[i] + '-' + str(j-i))
            print(notes, '\n\n', music)
            i += 1

# stream constants
CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050

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

scale = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

notes = []

if __name__ == "__main__":
    record()
    transcribe(notes)
