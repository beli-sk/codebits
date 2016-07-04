#!/usr/bin/env python
from __future__ import print_function
import sys
import time

try:
    g = int(sys.argv[1])
except IndexError, ValueError:
    print('Mem eat - Allocate specified amount of memory (in whole GB units).')
    print('use: {} <size_GB>'.format(sys.argv[0]))
else:
    print('Allocating {} GB of memory... '.format(sys.argv[1]), end='')
    sys.stdout.flush()
    try:
        s = bytearray(g*1024*1024*1024)
        print('done.')
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print('Aborted.')
