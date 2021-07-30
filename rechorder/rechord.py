#!/usr/bin/env python
# coding: utf-8

# # Rechorder
# 
# ## Automatic sheet music composition

# In[4]:


from sys import platform
import struct
import numpy as np
from scipy.fftpack import fft
import pyaudio
import music21 # install musescore

import warnings
warnings.filterwarnings('ignore')


# In[5]:


class Rechorder():
    def __init__(self, title='title', date='1970/01/01', composer='composer'):
        self.title    = title
        self.date     = date
        self.composer = composer
        
        # stream constants
        self.FORMAT   = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE     = 22050
        self.CHUNK    = 1024 * 2

        self.scale = ['A', "A#", 'B', 'C', "C#", 'D', "D#", 'E', 'F', "F#", 'G', "G#"]
        self.types = {'1': "whole", '2': "half", '4': "quarter", '8': "eighth", '16': "sixteenth"}
        
        us = music21.environment.UserSettings()
        if not us['musescoreDirectPNGPath']:
            if platform == 'linux':
                us['musescoreDirectPNGPath'] = '/usr/bin/musescore'
            elif platform == 'darwin':
                us['musescoreDirectPNGPath'] = '/Applications/MuseScore.app/Contents/MacOS/mscore'
            elif platform == 'win32':
                us['musescoreDirectPNGPath'] = 'C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe'

    def key_to_note(self, key):
        note = self.scale[(key - 1) % 12] + str((key + 8) // 12)
        print(note)
        return note

    def freqs_to_key(self, fs):
        fs_max = -np.sort(-fs)
        key    = None
        i      = 0
        
        while not key:
            i += 1
            hz   = round((np.where(fs == fs_max[i])[0][0]) * self.RATE / self.CHUNK) # convert FFT to hz
            note = int(round(12 * np.log2(hz/440) + 49)) # hz to note
            if note > 0 and note < 109:
                key = note
        
        return key, hz

    def transcribe(self):
        self.music = []
        nps        = 12 # in 1 second, the program records 12 notes
        i          = 0
        j          = 1
        
        while i < len(self.notes): # optimize loop
            try:
                if self.notes[i] == self.notes[j]:
                    j += 1
                else:
                    dur = str(min([1,2,4,8,16,32], key=lambda x:abs(x-(round(1 / (j - i) * nps)))))
                    self.music.append(self.notes[i] + '-' + dur)
                    i = j
                    j += 1 # slightly faster
            except IndexError:
                dur = str(min([1,2,4,8,16,32,64], key=lambda x:abs(x-(round(1 / (j - i) * nps))))) # can this cause div 0 error?
                self.music.append(self.notes[i] + '-' + dur)
                i = j + 1
        
        self.display()

    def display(self):
        s = music21.stream.Score()
        s.insert(0, music21.metadata.Metadata())
        s.metadata.title    = self.title
        s.metadata.date     = self.date
        s.metadata.composer = self.composer
        
        for n in self.music:
            if n[0] == 'R':
                s.append(music21.stream.note.Rest(n[n.index('-')+1:]))
            else:
                s.append(music21.note.Note(n[:n.index('-')], type=self.types[n[n.index('-')+1:]]))
        
        s.show()

    def record(self, rests = True):
        # stream object
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        
        print("\nstarted recording...\n")
        notes = ['R']
        try:
            while True:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
                data_np = np.array(data_int, dtype='b')[::2] + 128
                if np.percentile(np.abs(data_np), 90) >= 200: # check volume if a note is being played
                    # compute FFT and update line
                    fs = np.abs(fft(data_int)[0:self.CHUNK])
                    key, hz = self.freqs_to_key(fs) # convert most common frequencies
                    notes.append(self.key_to_note(key))
                elif rests and len(notes) > 1:
                    notes.append('R')
        except KeyboardInterrupt:
            p.close(stream)
            print("\n\nended recording\n")
        
        self.notes = notes[1:]
        self.transcribe()
