'''Test module.'''
import sys

sys.path.append('./src')

# pylint: disable=C0413
from unittest.mock import MagicMock
import pytest

from src.strategies.strategy import Strategy


STRATEGY_NAME = 'TEST_000000'
PAIR = 'XRPUSDT'
DBMANAGER_SELECT = [(0,)] * 1000

@pytest.fixture
def strategy():
    '''Manager strategy as a test resource.'''
    binance_mock = MagicMock()

    dbmanager_mock = MagicMock()
    dbmanager_mock.create_table.return_value = True
    dbmanager_mock.select.return_value = DBMANAGER_SELECT

    return Strategy(STRATEGY_NAME, PAIR, dbmanager_mock, binance_mock)


# pylint: disable=W0212,W0621
def test_init(strategy):
    '''Test if init values are correctly settled.'''
    assert strategy._pair == PAIR
    assert strategy._name == STRATEGY_NAME
    assert strategy._requisites == {'pair': 'XRPUSDT'}
    assert strategy.prices_table == STRATEGY_NAME + '_PRICES'
    assert strategy.orders_table == STRATEGY_NAME + '_ORDERS'


def test_requisites(strategy):
    '''Test that strategies are returnning correct requisites.'''
    assert isinstance(strategy.get_requisites(), dict)
    assert 'pair' in strategy.get_requisites().keys()


def test_create_tables(strategy):
    '''Test that tables has been created.'''
    strategy._dbmanager.create_table.assert_called()


def test_get_prices(strategy):
    '''Test that all records from the database has been collected.'''
    prices = strategy._get_prices()
    strategy._dbmanager.select.assert_called_once()
    assert isinstance(prices, list)
    assert len(prices) == len(DBMANAGER_SELECT)
