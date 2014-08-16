import os
import sys
import csv
import codecs
from functools import partial

from conf import PROCD_GAMES as GAMEDIR, ENCODING


KEYWORDS  = {
    'p': ['pass', 'sacked'],
    's': ['No Play', 'Touchback'],
    'f': ['field goal'],
    'u': ['punts'],
}


def get_play_type(row):
    desc = row[11]
    for playtype, words in KEYWORDS.iteritems():
        for w in words:
            if w in desc:
                return playtype
    else:
        playtype = None
        while playtype not in {'r', 'p', 'k', 'u', 'f', 's'}:
            msg = '\n' + desc + "\n(R)un, (P)ass, (K)ick-off, p(U)nt, (F)G or (S)kip: "
            playtype = raw_input(msg).lower()
        return playtype


def add_playtype(row):
    return row + [get_play_type(row)]
    

def main():
    fname = get_file_name()
    with codecs.open(fname, 'r', ENCODING) as f:
        reader = csv.reader(f)
        header = next(reader) + ['playtype']
        rows = filter(None, map(add_playtype, reader))

    outfname = os.path.join(GAMEDIR, os.path.basename(fname))
    with codecs.open(outfname, 'w', ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def get_file_name():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise ValueError('Filename not given')


if __name__ == '__main__':
    main()
