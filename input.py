import numpy as np
import pyaudio
import struct
from scipy.fftpack import fft

notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

music = []

class rechord(object):
    def __init__(self):
        # stream constants
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 22050
        self.pause = False

        self.notes = []
        self.hz = None

        # stream object
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

        self.mic_input()
    
    def conv(self):
        fs_max = -np.sort(-self.fs)

        self.keys = []
        i = 0
        while not self.hz:
            i += 1
            hz = (np.where(self.fs == fs_max[i])[0][0]) * self.RATE / self.CHUNK # convert FFT to hz
            key = int(round(12 * np.log2(hz/440) + 49)) # hz to note on piano

            if key > 0 and key < 109:
                self.key = key
                self.hz = round(hz)

    def display(self):
        note = notes[(self.key - 1) % 12] + str((self.key+8) // 12) # note as string
        music.append(note)

        print(note, '\t', self.hz)
        self.hz = None

    def mic_input(self):
        print("stream started\n")

        try:
            while True:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
                data_np = np.array(data_int, dtype='b')[::2] + 128

                if np.percentile(np.abs(data_np), 90) >= 200: # check volume if a note is being played
                    # compute FFT and update line
                    yf = fft(data_int)
                    self.fs = np.abs(yf[0:self.CHUNK])

                    self.conv()
                    self.display()

        except KeyboardInterrupt:
            self.p.close(self.stream)
            print(f"\n\nstream ended\n\n{music}")

if __name__ == "__main__":
    rechord()
