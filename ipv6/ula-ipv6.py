#!/usr/bin/env python3
import sys
import random
import argparse
from crypt import crypt

chars = '0123456789abcdef'

parser = argparse.ArgumentParser(description='Generate random unique local IPv6 prefix')
parser.add_argument('-l', '--length', type=int, default=48, choices=(48,52,56,60,64),
        help='Prefix length (default %(default)s)')
args = parser.parse_args()

def randstr(length, chars=chars, choice_function=random.SystemRandom().choice):
    return ''.join((choice_function(chars) for i in range(length)))

print('fd{}:{}:{}{}::/{}'.format(
    randstr(2),
    randstr(4),
    randstr(4),
    ':' + randstr((args.length - 48)//4) + '0'*(4 - (args.length - 48)//4)
        if args.length > 48 else '',
    args.length
    ))
