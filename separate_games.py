import os
import sys
import csv
from functools import partial

from conf import RAWGAMES as GAMEDIR


def append_game(games, row):
    games.setdefault(row[0], []).append(row)


def main():
    fname = get_file_name()
    with open(fname) as f:
        reader = csv.reader(f)
        header = next(reader)
        games = {}

        append = partial(append_game, games)
        map(append, reader)
        for game_name, rows in games.iteritems():
            with open(os.path.join(GAMEDIR, game_name) + '.csv', 'w') as f:
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
