#!/usr/bin/env python
#
# Copyright 2015 Michal Belica <devel@beli.sk>
#
# Licensed under MIT license.
#
import re
import os
import sys
import argparse
import subprocess

APTGET="/usr/bin/apt-get"

re_stats = r'^(?P<upgraded>\d+) upgraded, (?P<installed>\d+) newly installed, (?P<to_remove>\d+) to remove and (?P<not_upgraded>\d+) not upgraded.$'

class DebianUpdate(object):

    def __init__(self, args):
        self.args = args

    def do_update(self):
        cmd = [APTGET, 'update']
        cmd.append('--trivial-only') if not self.args.interactive else None
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(cmd, shell=False,
                    stdout=subprocess.PIPE if not self.args.interactive else None,
                    stderr=subprocess.STDOUT,
                    stdin=devnull if not self.args.interactive else None,
                    )
            out = proc.communicate()[0]
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(returncode=proc.returncode, cmd=cmd, output=out)
        if self.args.verbose >= 2 and not self.args.interactive:
            sys.stdout.write(out)

    def get_stats(self):
        cmd = [APTGET, 'upgrade']
        cmd.append('--assume-no')
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(cmd, shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=devnull,
                    )
            out = proc.communicate()[0]
        if proc.returncode not in (0, 1):
            raise subprocess.CalledProcessError(returncode=proc.returncode, cmd=cmd, output=out)

        if self.args.verbose >= 2:
            sys.stdout.write(out)

        if not out:
            raise Exception('No output from upgrade command.')
        m = re.search(re_stats, out, re.M)
        if m:
            return {
                    'upgraded': m.group('upgraded'),
                    'installed': m.group('installed'),
                    'to_remove': m.group('to_remove'),
                    'not_upgraded': m.group('not_upgraded'),
                    }
        else:
            raise Exception('Unknown output from called process')

    def do_upgrade(self):
        cmd = [APTGET]
        cmd.append('upgrade')
        cmd.append('--assume-yes') if not self.args.interactive else None
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(cmd, shell=False,
                    stdout=subprocess.PIPE if not self.args.interactive else None,
                    stderr=subprocess.STDOUT,
                    stdin=devnull if not self.args.interactive else None,
                    )
            out = proc.communicate()[0]
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(returncode=proc.returncode, cmd=cmd, output=out)
        if self.args.verbose >= 2 and not self.args.interactive:
            sys.stdout.write(out)

    def print_stats(self, stats):
        if self.args.verbose:
            sys.stdout.write('Packages to be upgraded: %s\n' % stats['upgraded'])
            sys.stdout.write('Packages to be installed: %s\n' % stats['installed'])
            sys.stdout.write('Packages to remove: %s\n' % stats['to_remove'])
            sys.stdout.write('Packages not upgraded: %s\n' % stats['not_upgraded'])
        else:
            for k, v in stats.iteritems():
                sys.stdout.write('%s=%s\n' % (k, v))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', '-u', action='store_true',
            help='run update first')
    parser.add_argument('--upgrade', '-U', action='store_true',
            help='run update first')
    parser.add_argument('--stats', '-s', action='store_true',
            help='print stats')
    parser.add_argument('--verbose', '-v', action='count',
            help='verbose output (repeat for more)')
    parser.add_argument('--interactive', '-i', action='store_true',
            help='run apt-get interactively')
    args = parser.parse_args()

    debian_update = DebianUpdate(args)

    try:
        if args.update:
            if args.verbose:
                sys.stdout.write('Running update...\n')
            debian_update.do_update()
        if args.stats:
            if args.verbose:
                sys.stdout.write('Running upgrade to gather stats...\n')
            debian_update.print_stats(debian_update.get_stats())
        if args.upgrade:
            if args.verbose:
                sys.stdout.write('Running upgrade...\n')
            debian_update.do_upgrade()
        if not args.update and not args.stats and not args.upgrade:
            sys.stdout.write('Nothing to do.\n')
    except subprocess.CalledProcessError as e:
        sys.stderr.write('FAIL subprocess: code=%d command=%s\n' % (e.returncode, e.cmd))
        if e.output:
            sys.stderr.write('--- output ---\n')
            sys.stderr.write(e.output)
            sys.stderr.write('--- end of output ---\n')

