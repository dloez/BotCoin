#!/usr/bin/env python
'''Interface between user and the trader bot.'''
import argparse
import sys
from pathlib import Path

from manager import Manager


def parse_args(args):
    '''This is required to test arguments.'''
    parser = argparse.ArgumentParser(description='Automate crypto trades.')
    parser.add_argument(
        '--id',
        default=None,
        help='session id, specify last if you want to use the lattest id used.'
    )

    return parser.parse_args(args)


def main():
    '''Initialize bot based on user arguments.'''
    # pylint: disable=W0612
    manager = Manager(STORAGE_DIR, parse_args(sys.argv[1:]))


STORAGE_DIR = Path('../storage')

if __name__ == '__main__':
    main()
