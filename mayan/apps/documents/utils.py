from __future__ import unicode_literals


def parse_range(astr):
    # http://stackoverflow.com/questions/4248399/
    # page-range-for-printing-algorithm
    result = set()
    for part in astr.split(','):
        x = part.split('-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)
