#!/usr/bin/env python
import codecs
import csv
import sys
from collections import Counter
from itertools import repeat
from math import floor

import numpy as np

from conf import ENCODING
from utils import project_dict as project, save_matrix


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
            transition[i, j] /= matrix[i].sum()

    return transition

def get_playtype(desc):
    desc = desc.lower()
    if 'safety' in desc:
        return 'safety'
    elif 'punt' in desc:
        return 'punt'
    elif 'field goal' in desc:
        return 'fg'
    elif 'fumble' in desc or 'intercepted' in desc or 'turnover' in desc:
        return 'to'
    elif 'touchdown' in desc:
        return 'td' 
    else:
        return 'regular'


def _normalize_togo(togo):
    togo = int(togo)
    if togo > 10:
        return '10'
    elif 7 <= togo <= 10:
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


get_info = project('off', 'down', 'togo', 'ydline', 'description')

def get_play(row):
    """
    This doesn't set TO on downs, because it would need a lookahead
    into the next play.
    """
    atkr, down, togo, yrdline, desc = get_info(row)
    play = {'playtype': get_playtype(desc)}
    try:
        play.update({
            'down': down,
            'togo': _normalize_togo(togo),
            'yrd': _normalize_yrd(yrdline),
            'atkr': atkr,
        })

    except:
        if play['playtype'] == 'regular':
            input(row)
    play['_raw'] = row
    return play


def is_tod(play):
    return play.get('down') == '4' and play['playtype'] == 'regular'


def set_to_on_downs(drive):
    """
    Solve get_playtype() deficiency by returning a new play list where
    plays which are TO on downs are fixed as a *new* play dict.
    For all other plays, the *same* dict is returned.
    """
    last_play = drive[-1]
    if is_tod(last_play):
        last_play['playtype'] = 'to'


def PREDICATE(row):
    desc = row['description'].lower()
    return not ('kicks' in desc or
                'extra point' in desc or
                'two-point' in desc or
                desc.replace('\xa0', '') == ''  or
                '(kick formation) penalty' in desc or
                not row['togo'])


def update_finals(graph):
    for final in ('safety', 'to', 'td', 'fg', 'punt'):
        state = {'playtype': final}
        graph.create_edge(state, state)


def drives(reader):
    drives = []
    current_drive = [next(reader)]
    current_atkr = get_info(current_drive[0])[0]
    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        else:
            atkr = get_info(row)[0]
            if atkr != current_atkr:
                drives.append(current_drive)
                current_drive = []
                current_atkr = atkr
            current_drive.append(row)
    return drives


def process_file(graph, initial_states, fname):
    with codecs.open(fname, 'r', ENCODING) as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for drive in drives(reader):
            drive = list(map(get_play, filter(PREDICATE, drive)))
            if drive:
                set_to_on_downs(drive)
                graph.add_drive(drive)


def get_file_names():
    if len(sys.argv) > 1:
        return sys.argv[1:]
    else:
        raise ValueError('Filename not given')


def main():
    graph = MFLGraph()
    initial_states = []

    for fname in get_file_names():
        process_file(graph, initial_states, fname)
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


if __name__ == '__main__':
    main()
