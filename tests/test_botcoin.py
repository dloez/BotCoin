'''Test Botcoin module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from src.botcoin import parse_args


def test_parser():
    '''Check if arguments are correctly parsed'''
    parser = parse_args([
        '--id',     '123',
        '--pair',   'BTCUSDT',
        '--strat',  'TEST',
        '--tokens', '123#123'
    ])

    assert parser.id == '123'
    assert parser.pair == 'BTCUSDT'
    assert parser.strat == 'TEST'
    assert parser.tokens == '123#123'

    parser = parse_args([
        '--tokens', '123#123'
    ])

    assert not parser.id
    assert parser.pair == 'XRPUSDT'
    assert parser.strat == 'MACD'
    assert parser.tokens == '123#123'
