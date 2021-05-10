'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from unittest.mock import MagicMock, AsyncMock
import pytest

from src.requester import Requester


BINANCE_GET_KLINES = [[0, 0, 0, 0, 0]] * 100


# pylint: disable=W0212,W0621
@pytest.fixture
def strategies():
    '''Manage strategies as a test resource.'''
    macd_mock = MagicMock()
    macd_mock.name.return_value = 'MACD_000000'
    macd_mock.get_requisites.return_value = {'pair': 'XRPUSDT', 'interval': 1}
    return [macd_mock]


@pytest.fixture
def requester(mocker, strategies):
    '''Manage requester as a test resource and isolate module.'''
    binance_mock = AsyncMock()
    binance_mock.get_klines.return_value = BINANCE_GET_KLINES

    binance_mocker = mocker.patch('src.requester.Binance')
    binance_mocker.return_value = binance_mock

    session = MagicMock()
    return Requester(session, strategies)


def test_init(requester, strategies):
    '''Test if init values are correctly settled.'''
    assert isinstance(requester._strategies, list)
    assert len(requester._strategies) == len(strategies)


@pytest.mark.asyncio
async def test_request_data(requester, strategies, mocker):
    '''Test if requester is collecting required data.'''
    mocked_sleep = mocker.patch('asyncio.sleep')
    assert await requester._request_data(strategies[0])
    requester._session.query.assert_called_once()
    requester._session.add.assert_called()
    requester._session.commit.assert_called_once()
    requester._binance.get_klines.assert_called_once()
    mocked_sleep.assert_called_once()
