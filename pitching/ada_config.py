#coding:utf8

import note
class AdaptiveConfig:
	def __init__(self):
		self.note_freq = note.get_freq()[12:]
		self.note_index = range(12,120)
		self.freq_radius = 0.9
		self.music_sampling = 0.1 # second

