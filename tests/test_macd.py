'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from unittest.mock import MagicMock
import pytest

from src.strategies.macd import MACD


STRATEGY_NAME = 'TEST_000000'
PAIR = 'XRPUSDT'
DBMANAGER_SELECT = [(0,)] * 1000


@pytest.fixture
def macd():
    '''Manage macd as a test resource.'''
    binance_mock = MagicMock()

    dbmanager_mock = MagicMock()
    dbmanager_mock.create_table.return_value = True
    dbmanager_mock.select.return_value = DBMANAGER_SELECT

    return MACD(STRATEGY_NAME, PAIR, dbmanager_mock, binance_mock)


# pylint: disable=W0212,W0621
def test_wait_prices(macd):
    '''Test if method returns prices.'''
    prices = macd._wait_prices()
    assert isinstance(prices, list)
