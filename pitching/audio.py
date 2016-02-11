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

def test_pitching(config):
    def nextpow2(n):
        m_f = np.log2(n)
        m_i = np.ceil(m_f)
        return int(2**m_i)

    def findtop(k_top, f, p, return_freq = False):
        index = [0] * len(config.note_freq)
        sf = 0
        maxsf = np.nonzero(np.abs(f-config.note_freq[-1])<config.freq_radius)[0][0]+1
        # find index of all config.note_freq in f
        for nf in xrange(len(config.note_freq)):
            # # method 1
            # index[nf] = np.nonzero(np.abs(f-config.note_freq[nf])<config.freq_radius)[0][0]
            # method 2
            # while sf < len(f):
            #     if abs(f[sf]-config.note_freq[nf]) < config.freq_radius:
            #         index[nf] = sf
            #         break
            #     else:
            #         sf += 1
            # method 3: assert config.note_freq is ascending
            index[nf] = np.nonzero(np.abs(f[sf:maxsf]-config.note_freq[nf])<config.freq_radius)[0][0] + sf
            sf = index[nf]
        sorted_freq, sorted_index = zip(*sorted(zip(index, config.note_index), cmp = lambda x,y: cmp(p[x[0]],p[y[0]]), reverse = True))
        if return_freq:
            return [f[i] for i in sorted_freq][0:k_top]
        else:
            return sorted_index[0:k_top]
    # sr, data = scipy.io.wavfile.read('TRIMED_CHORD_C.wav')
    sr, data = scipy.io.wavfile.read('echdc.wav')
    size = data.shape[0]
    Fs = sr #Sampling frequency
    T = 1.0/Fs #Sampling period
    L = size #Length of signal
    t = [i*T for i in range(L)] #Time vector
    n = nextpow2(L)
    Y = pl.fft(data[:,0], n)
    P = np.abs(Y/n)
    f = np.array([Fs*i/n for i in range(n/2)])
    # np.savetxt("foo.csv", f, delimiter=",")
    # plt.plot(np.array(t), data[:, 0])
    # plt.show()
    # plt.plot(f, P[0:n/2])
    # plt.show()
    print findtop(5, f, P, True)
    print findtop(5, f, P)
    print [index_to_name(x) for x in findtop(5, f, P)]


def test_segmentation(config):
    sr, data = scipy.io.wavfile.read('escale_c.wav')
    size = data.shape[0]

if __name__ == '__main__':
    import time
    starttime = time.clock()
    test_pitching(AdaptiveConfig())
    print time.clock() - starttime
