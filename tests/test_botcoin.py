'''Test Botcoin module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from src.botcoin import parse_args


def test_parser():
    '''Check if arguments are correctly parsed'''
    parser = parse_args(['--id', '123'])
    assert parser.id == '123'
