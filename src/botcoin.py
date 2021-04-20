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

    parser.add_argument(
        '--pair',
        default='XRPUSDT',
        help='pair of cryptos used for trading. Example: XRPUSDT, BTCUSDT'
    )

    parser.add_argument(
        '--strat',
        default='CSMACD',
        help='strategy used for trading (Default = CSMACD). Available: CSMACD'
    )

    parser.add_argument(
        '--strat-name',
        help='define strat name so it can use previous data.'
    )

    parser.add_argument(
        '--tokens',
        required=True,
        help='binance REST API key and secret. Format: api_key#api_secret'
    )

    return parser.parse_args(args)


def main():
    '''Initialize bot based on user arguments.'''
    # pylint: disable=W0612
    manager = Manager(STORAGE_DIR, parse_args(sys.argv[1:]))


STORAGE_DIR = Path('../storage')

if __name__ == '__main__':
    main()
