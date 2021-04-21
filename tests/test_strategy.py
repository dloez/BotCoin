'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import pytest

from src.strategies.strategy import Strategy


@pytest.fixture
def strategy():
    '''Manager strategy as a test resource.'''
    return Strategy('test', 'XRPUSDT')


# pylint: disable=W0212,W0621
def test_init(strategy):
    '''Test if init values are correctly settled.'''
    assert strategy._pair == 'XRPUSDT'
    assert '_' in strategy._name
    assert strategy._requisites == {'pair': 'XRPUSDT'}


def test_requisites(strategy):
    '''Test that strategies are returnning correct requisites.'''
    assert isinstance(strategy.get_requisites(), dict)
    assert 'pair' in strategy.get_requisites().keys()
