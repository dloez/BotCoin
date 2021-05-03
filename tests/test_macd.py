'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from unittest.mock import MagicMock
import pytest

from src.strategies.macd import MACD
from .test_strategy import TOKENS, STRATEGY_NAME, STRATEGY_ARGUMENTS, DBMANAGER_SELECT


# pylint: disable=W0212,W0621
@pytest.fixture
def macd():
    '''Manage macd as a test resource.'''
    dbmanager_mock = MagicMock()
    dbmanager_mock.create_table.return_value = True
    dbmanager_mock.select.return_value = DBMANAGER_SELECT

    binance_mock = MagicMock()

    macd_fix = MACD(dbmanager_mock, TOKENS, STRATEGY_NAME, STRATEGY_ARGUMENTS)
    macd_fix._binance = binance_mock

    return  macd_fix


def test_wait_prices(macd):
    '''Test if method returns prices.'''
    prices = macd._wait_prices()
    assert isinstance(prices, list)
