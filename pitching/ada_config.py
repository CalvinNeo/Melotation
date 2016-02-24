#coding:utf8

import note
class AdaptiveConfig:
    def __init__(self):
        self.note_freq = note.get_freq()[12:]
        self.note_index = range(12,120)
        self.freq_radius = 1.2
        # self.music_sampling_time = 0.1 # second
        self.music_sampling_frame = 3000 # frame
        self.strength_thres = 10 # consider major if stregth level is above miu+sigma*strength_thres

