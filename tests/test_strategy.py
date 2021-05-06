'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import os
from unittest.mock import MagicMock
import pytest

from src.strategies.strategy import Strategy
from src.strategies.strategy import sync


ARGUMENTS = {
    'tokens': {
        'binance_api_key': os.environ['BINANCE_API_KEY'],
        'binance_api_secret': os.environ['BINANCE_API_SECRET']
    },
    'name': 'TEST',
    'pair': 'XRPUSDT',
    'interval': 1,
    'offset': 0
}
DBMANAGER_SELECT = [(0,)] * 1000


# pylint: disable=W0212,W0621
@pytest.fixture
def strategy(mocker):
    '''Manager strategy as a test resource.'''
    dbmanager_mock = MagicMock()
    dbmanager_mock.create_table.return_value = True
    dbmanager_mock.select.return_value = DBMANAGER_SELECT

    binance_mocker = mocker.patch('src.strategies.strategy.Binance')
    binance_mocker.return_value = MagicMock()

    strategy_fix = Strategy(dbmanager_mock, ARGUMENTS)
    return strategy_fix


def test_init(strategy):
    '''Test if init values are correctly settled.'''
    assert strategy._name == ARGUMENTS['name']
    assert strategy.arguments == ARGUMENTS
    assert strategy.prices_table == 'PRICES_XRPUSDT_1'
    assert strategy.orders_table == 'ORDERS_TEST'


def test_create_tables(strategy):
    '''Test that tables has been created.'''
    strategy._dbmanager.create_table.assert_called()


def test_get_prices(strategy):
    '''Test that all records from the database has been collected.'''
    prices = strategy._get_prices()
    strategy._dbmanager.select.assert_called_once()
    assert isinstance(prices, list)
    assert len(prices) == len(DBMANAGER_SELECT)


def test_sync():
    '''Test if sync method returns int value.'''
    assert isinstance(sync(60), int)
