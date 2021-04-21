'''Test module.'''
import sys

sys.path.append('./src')

# pylint: disable=C0413
import os
from unittest.mock import MagicMock
import pytest

from src.requester import Requester


BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']
BINANCE_GET_KLINES = [[0, 0, 0, 0, 0]] * 33

# pylint: disable=W0212,W0621
@pytest.fixture
def strategies():
    '''Manage strategies as a test resource.'''
    macd_mock = MagicMock()
    macd_mock.name.return_value = 'MACD_000000'
    macd_mock.get_requisites.return_value = {'pair': 'XRPUSDT'}
    return [macd_mock]


@pytest.fixture
def requester(mocker, strategies):
    '''Manage requester as a test resource and isolate module.'''
    dbmanager_mock = MagicMock()
    dbmanager_mock.create_table.return_value = True
    dbmanager_mock.truncate_table.return_value = True
    dbmanager_mock.insert.return_value = True

    requester_fix = Requester(dbmanager_mock, strategies, [BINANCE_API_KEY, BINANCE_API_SECRET])
    mocked_get_klines = mocker.patch.object(requester_fix._binance, 'get_klines')
    mocked_get_klines.return_value = BINANCE_GET_KLINES
    return requester_fix


def test_init(requester, strategies):
    '''Test if init values are correctly settled.'''
    assert isinstance(requester._strategies, list)
    assert len(requester._strategies) == len(strategies)


def test_init_database(requester, strategies):
    '''Test that tables has been created in the database.'''
    for strat in strategies:
        assert strat.name in requester._tables.keys()

    requester._dbmanager.create_table.assert_called()


@pytest.mark.asyncio
async def test_request_data(requester, strategies, mocker):
    '''Test if requester is collecting required data.'''
    mocked_sleep = mocker.patch('asyncio.sleep')
    assert await requester._request_data(strategies[0])
    requester._binance.get_klines.assert_called_once()
    requester._dbmanager.truncate_table.assert_called_once()
    requester._dbmanager.insert.assert_called_once()
    mocked_sleep.assert_called_once()
