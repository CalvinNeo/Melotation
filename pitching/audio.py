#coding:utf8

import numpy as np
import wave, scipy
from scipy.io import wavfile
# include entire numpy/scipy/matplotlib suite to avoid namespace pollute
import pylab as pl
import matplotlib.pyplot as plt
import math

from ada_config import *
from note import *

def test_pitching(config, sr, data):
    def nextpow2(n):
        m_f = np.log2(n)
        m_i = np.ceil(m_f)
        return int(2**m_i)

    def findtop(k_top, f, p):
        '''
            In: (f,p) are ndarray which share same dimension
                f(as cood-Y) is frequency to each frame(as cood-X)
                p(as cood-Y) is strength to each frame(as cood-X)
            Out: note_index(MIDI), strength, note_freq
        '''
        freq_index = [0] * len(config.note_freq)
        sf, maxsf = 0, np.nonzero(np.abs(f-config.note_freq[-1])<config.freq_radius)[0][0]+1
        # find index(freq_index) of all config.note_freq in f
        for nf in xrange(len(config.note_freq)):
            # # method 1
            # freq_index[nf] = np.nonzero(np.abs(f-config.note_freq[nf])<config.freq_radius)[0][0]
            # method 2
            # while sf < len(f):
            #     if abs(f[sf]-config.note_freq[nf]) < config.freq_radius:
            #         freq_index[nf] = sf
            #         break
            #     else:
            #         sf += 1
            # method 3: assert config.note_freq is ascending
            freq_index[nf] = np.nonzero(np.abs(f[sf:maxsf]-config.note_freq[nf])<config.freq_radius)[0][0] + sf
            sf = freq_index[nf]
        sorted_freq, sorted_note = zip(*sorted(zip(freq_index, config.note_index), cmp = lambda x,y: cmp(p[x[0]],p[y[0]]), reverse = True))
        return sorted_note[0:k_top], [p[i] for i in sorted_freq[0:k_top]], [f[i] for i in sorted_freq[0:k_top]]

    def note_filter(f, p):
        '''
            Adaptive k_top
            ref: find_top
        '''
        freq_index = [0] * len(config.note_freq)
        try:
            sf, maxsf = 0, np.nonzero(np.abs(f-config.note_freq[-1])<config.freq_radius)[0][0]+1
        except IndexError:
            return [],[],[]
        miu, sigma = np.mean(p[:maxsf]), np.std(p[:maxsf])
        for nf in xrange(len(config.note_freq)):
            try:
                freq_index[nf] = np.nonzero(np.abs(f[sf:maxsf]-config.note_freq[nf])<config.freq_radius)[0][0] + sf
            except IndexError:
                pass
            sf = freq_index[nf]
        sorted_freq, sorted_note = zip(*sorted(zip(freq_index, config.note_index), cmp = lambda x,y: cmp(p[x[0]],p[y[0]]), reverse = True))
        try:
            k_top = next(x for x in xrange(len(sorted_freq)) if p[sorted_freq[x]] < config.strength_thres*sigma+miu)
        except StopIteration:
            k_top = 1
        return sorted_note[0:k_top], [p[i] for i in sorted_freq[0:k_top]], [f[i] for i in sorted_freq[0:k_top]]


    # sr, data = scipy.io.wavfile.read('TRIMED_CHORD_C.wav')
    # sr, data = scipy.io.wavfile.read('echdc.wav')
    size = data.shape[0]
    Fs = sr #Sampling frequency
    T = 1.0/Fs #Sampling period
    L = size #Length of signal
    if L <= 0:
        return [],[],[] 
    t = np.arange(L) * T #Time vector
    n = nextpow2(L)
    Y = pl.fft(data[:,0], n)
    P = np.abs(Y/n)
    f = np.arange(n/2)*1.0*Fs/n
    # f = np.array([Fs*i/n for i in range(n/2)])
    # np.savetxt("foo.csv", f, delimiter=",")
    # plt.plot(np.array(t), data[:, 0])
    # plt.show()
    # plt.plot(f, P[0:n/2])
    # plt.show()
    notes, strength, freq = note_filter(f, P[:n/2])
    return notes, strength, freq, [index_to_name(x) for x in notes]

def test_segmentation(config, sr, data):
    size = data.shape[0]
    prevfreq = set()
    for si in xrange(size/config.music_sampling_frame):
        notes, strength, freq, name = test_pitching(config, sr, data[si*config.music_sampling_frame:(si+3)*config.music_sampling_frame])
        if set(notes) != prevfreq:
            print name
            prevfreq = set(notes)
if __name__ == '__main__':
    import time
    starttime = time.clock()
    sr, data = scipy.io.wavfile.read('iscale_c.wav')
    # print test_pitching(AdaptiveConfig(), sr, data)
    print test_segmentation(AdaptiveConfig(), sr, data)
    print time.clock() - starttime

