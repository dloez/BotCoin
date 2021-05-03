'''Test Botcoin module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from src.botcoin import parse_args


def test_parser():
    '''Check if arguments are correctly parsed'''
    parser = parse_args([
        '--init',       'test_path',
        '--id',         '123',
        '--strat',      'TEST',
        '--name',       'MACD_000000',
        '--interval',   '2',
        '--pair',       'BTCUSDT',
        '--tokens',     '123#123'
    ])

    assert parser.init == 'test_path'
    assert parser.id == '123'
    assert parser.strat == 'TEST'
    assert parser.name == 'MACD_000000'
    assert parser.interval == 2
    assert parser.pair == 'BTCUSDT'
    assert parser.tokens == '123#123'

    parser = parse_args([
        '--tokens', '123#123'
    ])

    assert not parser.init
    assert not parser.id
    assert parser.strat == 'MACD'
    assert not parser.name
    assert parser.pair == 'XRPUSDT'
    assert parser.interval == 1
    assert parser.tokens == '123#123'
