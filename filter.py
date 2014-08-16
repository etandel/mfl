import sys
import csv


def dallas_attacks(row):
    return row[4] == 'DAL'


def project(*columns):
    if columns:
        return lambda r: tuple(r[c] for c in columns)
    else:
        return lambda r: r[:]


TRANSFORM = project()
PREDICATE = dallas_attacks

def main():
    fname = get_file_name()
    with open(fname) as f:
        reader = csv.reader(f)
        header = next(reader)
        newrows = map(TRANSFORM, filter(PREDICATE, reader))

    with open('out.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(TRANSFORM(header))
        writer.writerows(newrows)


def get_file_name():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        raise ValueError('Filename not given')


if __name__ == '__main__':
    main()
