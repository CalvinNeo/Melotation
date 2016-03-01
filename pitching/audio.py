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

def test_pitching(config, sr, data, show_outstanding_level=False):
    '''
        using ISTFT to annotate
    '''
    def nextpow2(n):
        return int(2**np.ceil(np.log2(n)))

    def findtop(k_top, f, p):
        '''
            In: (f,p) are ndarray which share same dimension
                f(as cood-Y) is frequency to each frame(as cood-X)
                p(as cood-Y) is strength to each frame(as cood-X)
            Out: note_index(MIDI from 12(C-1) to 120(C9)), strength, note_freq
            return k most outstanding frequencies in all frequencies which belong to one note(128 cases in MIDI)
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
        sorted_freq_index, sorted_note_index = zip(*sorted(zip(freq_index, config.note_index), cmp = lambda x,y: cmp(p[x[0]],p[y[0]]), reverse = True))
        return sorted_note_index[0:k_top], [p[i] for i in sorted_freq_index[0:k_top]], [f[i] for i in sorted_freq_index[0:k_top]]

    def note_filter(f, p):
        '''
            Adaptive k_top
            ref: find_top
            return most possible answer
        '''
        freq_index = [0] * len(config.note_freq)
        try:
            sf, maxsf = 0, np.nonzero(np.abs(f-config.note_freq[-1])<config.freq_radius)[0][0]+1
        except IndexError:
            # no suitable note
            return [],[],[]
        for nf in xrange(len(config.note_freq)):
            try:
                freq_index[nf] = np.nonzero(np.abs(f[sf:maxsf]-config.note_freq[nf])<config.freq_radius)[0][0] + sf
            except IndexError:
                pass
            sf = freq_index[nf]
        sorted_freq_index, sorted_note_index = zip(*sorted(zip(freq_index, config.note_index), cmp = lambda x,y: cmp(p[x[0]],p[y[0]]), reverse = True))
        # # method 1: choose from all frame(time unit)
        # miu, sigma = np.mean(p[:maxsf]), np.std(p[:maxsf])
        # method 2: choose from n-top outstanding freq
        miu, sigma  = np.mean(np.vectorize(lambda i:p[i])(sorted_freq_index[0:config.ntop_outstanding])), np.std(p[:maxsf])
        if config.pitchlevel[1]:
            med = np.percentile(p[:maxsf], config.strength_filterate)
        judging = [lambda x:p[sorted_freq_index[x]] < config.strength_thres*sigma+miu, lambda x: p[sorted_freq_index[x]] < config.strength_filterate]
        def dojudge(x):
            return reduce(lambda a,b: a or b, [config.pitchlevel[i] and judging[i](x) for i in xrange(len(config.pitchlevel))])
        try:
            k_top = next(x for x in xrange(len(sorted_freq_index)) if dojudge(x))
        except StopIteration:
            # reach the end of array
            k_top = 1
        return sorted_note_index[0:k_top], [p[i] for i in sorted_freq_index[0:k_top]], [f[i] for i in sorted_freq_index[0:k_top]]

        def overtone_filter():
            '''
                An overtone is any frequency greater than the fundamental frequency of a sound
                e.g. a4 = 440Hz as fundamental tone, then 2*440=880Hz iscalled 1st overtone/2nd harmonic/2nd partial
                When pitching, we are to identify the fundamental, not overtones
            '''
            pass

    size = data.shape[0]
    Fs = sr # Sampling frequency
    T = 1.0/Fs # Sampling period
    L = size # Length of signal
    if L <= 0:
        return [],[],[] 
    t = np.arange(L) * T #Time vector
    n = nextpow2(L)
    '''
        Clarification:
        Assume we play piano at the tempo of Prestissimo(200 BPM and over, 200 Quater notes in a minus),
        we play almost 107 Hundred twenty-eighth note in a second, so duration for every note is 9ms.
        Consider our sampling rate is usually 44100Hz, whose duration is 0.02ms

    '''
    window = scipy.hanning(L) # using hanning windows function to calculate STFT
    Y = pl.fft(window*data[:,0], n)
    P = np.abs(Y/n)
    f = np.arange(n/2)*1.0*Fs/n
    # f = np.array([Fs*i/n for i in range(n/2)])
    # np.savetxt("foo.csv", f, delimiter=",")
    # plt.plot(np.array(t), data[:, 0])
    # plt.show()
    if show_outstanding_level:
        plt.plot(f, P[0:n/2])
        plt.show()
    notes, strength, freq = note_filter(f, P[:n/2])
    return notes, strength, freq, [index_to_name(x) for x in notes]

def test_segmentation(config, sr, data):
    size = data.shape[0]
    prevfreq = (set(), set(), 0)
    duration = 1 # the length of current note/pause
    for si in range(size/config.window_unit_length)[config.window_unit_lbound:-1-config.window_unit_ubound:config.window_step]:
        notes, strength, freq, name = test_pitching(config, sr, data[(si-config.window_unit_lbound)*config.window_unit_length:(si+config.window_unit_ubound)*config.window_unit_length])
        if set(notes) != prevfreq[0]:
            print prevfreq[1], duration, prevfreq[2]
            if set(notes): 
                prevfreq = (set(notes), set(name), strength)
            else: # pause
                prevfreq = (set([]), 'pause', 0)
            duration = 1
        else:
            duration += 1
    print prevfreq[1], duration, prevfreq[2]
            
if __name__ == '__main__':
    import time
    starttime = time.clock()
    # echdc escale_c escale_c_b
    sr, data = scipy.io.wavfile.read('escale_c.wav')
    # print test_pitching(AdaptiveConfig(), sr, data, False)
    print test_segmentation(AdaptiveConfig(), sr, data)

    # print np.fromfunction(lambda i,j: j, (1,10)).ravel()
    # print np.array([1,2,3,4,5,6,7,8])
    print time.clock() - starttime

