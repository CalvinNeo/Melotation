#coding:utf8

# include entire numpy/scipy/matplotlib suite to avoid namespace pollute
import math

def get_freq(index = None):
    '''
        In MIDI
        define A4 440Hz
        define C4 60, so A1 is 69, C0 is 12
        index = 69 + 12 * math.log(freq / 440, 2)
        freq = 440 * (2 ** ((p-69) / 12))
        the list from c-1 to b5
    '''
    if index == None:
        return [440 * (2 ** ((i - 69) / 12.0)) for i in range(120)]
    else:
        return 440 * (2 ** ((index - 69) / 12.0))

def name_to_index(name):
    '''
        ref get_freq()
    '''
    note_name, gs = (name[0:2], 2) if len(name) > 1 and name[1] == '#' else (name[0], 1)
    note_group = 0 if len(name) == 1 else -1 if name[gs] == '-' else int(name[gs])
    return 12 + 12 * note_group + ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'].index(note_name.lower())

def index_to_name(index):
    '''
        ref get_freq()
    '''
    return ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'][index % 12] + str(index / 12 - 1)

def assemble(crtnotes, prevnotes):
    pass

if __name__ == '__main__':
    # print name_to_index('c4')
    # print get_freq(60)
    # print index_to_name(60)
    print get_freq()[12:]
    # print get_freq(name_to_index('c4'))
    # print get_freq(name_to_index('e4'))
    # print get_freq(name_to_index('g4'))