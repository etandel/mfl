import codecs
import csv
import sys
from collections import Counter
from itertools import repeat
from math import floor

import numpy as np
from scipy import linalg

from get_drives import save_matrix
from filter import *


def from_file(fname):
    with codecs.open(fname, 'r', 'iso-8859-1') as f:
        reader = csv.reader(f)
        header = next(reader)
        n = len(header)
        rawm = []
        for l in reader:
            rawm.append(list(map(float, l)))
        m = np.matrix(rawm)
        return m, header


def find(prop, iterable):
    for i, e in enumerate(iterable):
        if prop(e):
            return i, e


def abs_identity(matrix):
    m = np.zeros_like(matrix)
    for i in range(5):
        m[i, i] = 1
    return m


def main():
    fname = get_file_name()
    matrix, header = from_file(fname)
    n = len(matrix)
    matrix -= np.identity(n)
    matrix += abs_identity(matrix)

    results = []
    for (idx, abs_state) in enumerate(header[:5]):
        b = np.zeros(n)
        b[idx] = 1
        results.append(linalg.solve(matrix, b))
    save_matrix(header, results, 'abs_prob.csv')


def get_file_name():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise ValueError('Filename not given')


if __name__ == '__main__':
    main()
