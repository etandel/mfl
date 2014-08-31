#!/usr/bin/env python
import sys

import pytest



args = ['-rsxX', '-q', '--tb=native'] + sys.argv[1:]
if any('tests' in arg for arg in args):
    sys.exit(pytest.main(args))
else:
    sys.exit(pytest.main(args + ['tests/']))

