#!/usr/bin/env python
import codecs
import csv
import sys


def project_dict(*keys):
    if keys:
        return lambda d: tuple(d[k] for k in keys)
    else:
        raise ValueError('Empty key list.')


def project_tuple(*columns):
    if columns:
        return lambda r: tuple(r[c] for c in columns)
    else:
        return lambda r: r[:]


def save_matrix(header, m, name='out.csv'):
    with codecs.open(name, 'w', 'iso-8859-1') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(m)

