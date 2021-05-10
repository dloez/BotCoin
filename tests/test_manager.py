'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from src.manager import Manager


STORAGE_PATH = Path('./test')
CONFIG = SimpleNamespace(
    error=None,
    id='123',
    strategies=[
        {
            'strat': 'macd',
            'tokens': {
                'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
                'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
            },
            'name': 'macd001',
            'interval': 1,
            'pair': 'XRPUSDT',
            'orm': (None, None)
        },
        {
            'strat': 'macd',
            'tokens': {
                'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
                'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
            },
            'name': 'macd002',
            'pair': 'BTCUSDT',
            'interval': 1,
            'offset': 0,
            'orm': (None, None)
        }
    ]
)


# pylint: disable=W0212,W0621
@pytest.fixture
def manager(mocker):
    '''Test manager as a test resource.'''
    dbmanager_mocker = mocker.patch('src.manager.DBManager')
    dbmanager_mocker.return_value = MagicMock()

    requester_mocker = mocker.patch('src.manager.Requester')
    requester_mocker.return_value = MagicMock()

    macd_mocker = mocker.patch('src.manager.MACD')
    macd_mocker.return_value = MagicMock()

    return Manager(STORAGE_PATH, CONFIG)


def test_init(manager):
    '''Test if all init values have been correctly settled.'''
    assert len(manager._strategies) == len(CONFIG.strategies)


def test_execute_strategies(manager):
    '''Test if requester and strategies have been started.'''
    manager.start()
    manager._requester.start.assert_called_once()
    manager._strategies[0].start.assert_called()
