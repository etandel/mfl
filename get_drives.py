import codecs
import csv
import sys
from collections import Counter
from itertools import repeat
from math import floor

import numpy as np

from filter import *


class MFLGraph:
    def __init__(self, plays=None):
        self.hashes = set()
        self.edges = {}

        if plays is not None:
            self.add_drive(plays)


    def add_drive(self, plays):
        for from_, to in zip(plays[:-1], plays[1:]):
            self.create_edge(from_, to)

    def create_edge(self, v1, v2):
        h1 = self._hash(v1)
        h2 = self._hash(v2)

        self.hashes.add(h1)
        self.hashes.add(h2)

        self._add_edge(h1, h2)

    def _hash(self, play):
        if play['playtype'] != 'regular':
            h = play['playtype']
        else:
            h = ''.join(('z', play['yrd'], play['togo'], play['down']))
        return h

    def _add_edge(self, e1_h, e2_h):
        e1_edges = self.edges.setdefault(e1_h, [])
        e1_edges.append(e2_h)

    def to_matrix(self):
        hashes = sorted(list(self.hashes))
        n = len(hashes)
        matrix = np.zeros((n, n))

        for from_i, from_ in enumerate(hashes):
            for to in self.edges.get(from_, ''):
                to_i = hashes.index(to)
                matrix[from_i, to_i] += 1
        return matrix


def transition_matrix(matrix):
    transition = matrix.copy()
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            transition[i, j] /=  matrix[i].sum()

    return transition

def get_playtype(desc):
    desc = desc.lower()
    if 'punt' in desc:
        return 'punt'
    elif 'touchdown' in desc:
        return 'td' 
    elif 'field goal' in desc:
        return 'fg'
    elif 'fumble' in desc or 'intercepted' in desc:
        return 'to'
    elif 'safety' in desc:
        return 'safety'
    else:
        return 'regular'


def _normalize_togo(togo):
    togo = int(togo)
    if togo > 10:
        return '10'
    elif 7 <= togo < 10:
        return '7'
    elif 5 <= togo < 7:
        return '5'
    elif 3 <= togo < 5:
        return '3'
    elif 1 <= togo < 3:
        return '1'
    else:
        return '0'


def _normalize_yrd(yrdline):
    return str(floor((100 - float(yrdline)) / 10))


def get_play(row):
    down, togo, yrdline, desc = project(6, 7, 8, 11)(row)
    play = {'playtype': get_playtype(desc)}
    if play['playtype'] == 'regular':
        try:
            play.update({
                'down': down,
                'togo': _normalize_togo(togo),
                'yrd': _normalize_yrd(yrdline),
            })

        except:
            input(row)
    return play


def drives(plays):
    i = 0
    while i < len(plays) - 1:
        drive = []
        while i < len(plays) - 1 and plays[i]['playtype'] == 'regular':
            drive.append(plays[i])
            i += 1
        drive.append(plays[i])
        i += 1
        yield drive


TRANSFORM = get_play
def PREDICATE(row):
    desc = row[11].lower()
    return not ('kicks' in desc or
                'extra point' in desc or
                'two-point' in desc or
                desc.replace('\xa0', '') == ''  or
                '(kick formation) penalty' in desc or
                not row[7])


def save_matrix(header, m, name='out.csv'):
    with codecs.open(name, 'w', 'iso-8859-1') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(m)


def update_finals(graph):
    for final in ('safety', 'to', 'td', 'fg', 'punt'):
        state = {'playtype': final}
        graph.create_edge(state, state)


def main():
    fname = get_file_name()
    with codecs.open(fname, 'r', 'iso-8859-1') as f:
        reader = csv.reader(f)
        header = next(reader)
        plays = list(map(TRANSFORM, filter(PREDICATE, reader)))

    graph = MFLGraph()
    initial_states = []
    for drive in drives(plays):
        initial_states.append(graph._hash(drive[0]))
        graph.add_drive(drive)
    update_finals(graph)

    initial_states = Counter(initial_states)
    initial_states_head = sorted(list(initial_states.keys()))
    initial_states_prob = [initial_states[h]/sum(initial_states.values()) for h in initial_states_head]

    m = graph.to_matrix()
    tm = transition_matrix(m)

    header = sorted(list(graph.hashes))
    save_matrix(header, m, 'cis.csv')
    save_matrix(header, tm, 'trans.csv')
    save_matrix(initial_states_head, [initial_states_prob], 'initial_states.csv')


def get_file_name():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise ValueError('Filename not given')


if __name__ == '__main__':
    main()
