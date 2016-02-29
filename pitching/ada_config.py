#coding:utf8

import note
class AdaptiveConfig:
    def __init__(self):
        self.note_freq = note.get_freq()[12:]
        self.note_index = range(12,120)
        self.freq_radius = 1.2
        # self.music_sampling_time = 0.1 # second
        self.window_unit_length = 3000 # frame number in one sampling window unit
        self.strength_thres = 15 # consider major if stregth level is above miu+sigma*strength_thres
        self.strength_filterate = 99.95
        self.abs_strength_thres = 0.0
        self.ntop_outstanding = 15
        self.window_unit_lbound = 1
        self.window_unit_ubound = 3
        self.window_step = 2
        self.pitchlevel = (True, False)

