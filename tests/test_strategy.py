'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import os
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

from src.strategies.strategy import Strategy
from src.strategies.strategy import sync


ARGUMENTS = {
    'tokens': {
        'binance_api_key': os.environ['BINANCE_API_KEY'],
        'binance_api_secret': os.environ['BINANCE_API_SECRET']
    },
    'name': 'test',
    'pair': 'XRPUSDT',
    'interval': 1,
    'offset': 0
}
QUERY = [SimpleNamespace(price=0)] * 10


# pylint: disable=W0212,W0621
@pytest.fixture
def strategy(mocker):
    '''Manager strategy as a test resource.'''
    binance_mock = MagicMock()
    binance_mock.get_avg_price.return_value = '0'

    binance_mocker = mocker.patch('src.strategies.strategy.Binance')
    binance_mocker.return_value = binance_mock()

    session = MagicMock()
    session.all.return_value = QUERY

    strategy_fix = Strategy(session, (MagicMock(), MagicMock()), ARGUMENTS)
    return strategy_fix


def test_init(strategy):
    '''Test if init values are correctly settled.'''
    assert strategy._name == ARGUMENTS['name']
    assert strategy.arguments == ARGUMENTS


def test_get_prices(strategy):
    '''Test that all records from the database has been collected.'''
    prices = strategy._get_prices()
    strategy._session.query.assert_called_once()
    assert isinstance(prices, list)


def test_purchase(strategy):
    '''Test purchase.'''
    strategy._purchase()
    strategy._binance.get_avg_price.assert_called_once()
    strategy.order.asser_called_once()
    strategy._session.add.assert_called_once()
    strategy._session.commit.assert_called_once()


def test_sell(strategy):
    '''Test purchase.'''
    strategy._sell()
    strategy._binance.get_avg_price.assert_called_once()
    strategy.order.asser_called_once()
    strategy._session.add.assert_called_once()
    strategy._session.commit.assert_called_once()


def test_sync():
    '''Test if sync method returns int value.'''
    assert isinstance(sync(60), int)
