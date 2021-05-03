'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
from pathlib import Path
import yaml
import pytest

from src.reader import read


INIT_TEST_FILE = Path('test_init.yaml')


def test_read():
    '''Test that read function is loading yaml file correctly.'''
    config = read(INIT_TEST_FILE)
    assert config.error == 'wrong init path'

    test_data = {
        'id': '123',
        'tokens': {
            'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
            'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
        },
        'strategies': [
            {
                'strat': 'macd',
                'name': 'MACD_000000',
                'pair': 'XRPUSDT',
                'interval': 1
            },
            {
                'strat': 'macd',
                'name': 'MACD_000001',
                'pair': 'BTCUSDT',
                'interval': 1
            }
        ]
    }

    with open(INIT_TEST_FILE, 'w') as file:
        yaml.dump(test_data, file)

    config = read(INIT_TEST_FILE)
    assert not config.error


    test_data = {
        'id': '123',
        'strategies': [
            {
                'strat': 'macd',
                'name': 'MACD_000000',
                'pair': 'XRPUSDT',
                'interval': 1
            },
            {
                'strat': 'macd',
                'name': 'MACD_000001',
                'pair': 'BTCUSDT',
                'interval': 1
            }
        ]
    }

    with open(INIT_TEST_FILE, 'w') as file:
        yaml.dump(test_data, file)

    config = read(INIT_TEST_FILE)
    assert config.error == 'missing tokens'

    test_data = {
        'id': '123',
        'tokens': {
            'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
            'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
        }
    }

    with open(INIT_TEST_FILE, 'w') as file:
        yaml.dump(test_data, file)

    config = read(INIT_TEST_FILE)
    assert config.error == 'missing strategies'


    test_data = {
        'id': '123',
        'tokens': {
            'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
            'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
        },
        'strategies': [
            {
                'strat': 'macd',
                'name': 'MACD_000000',
                'pair': 'XRPUSDT',
                'interval': 1
            },
            {
                'strat': 'macd',
                'name': 'MACD_000001',
                'pair': 'BTCUSDT',
                'interval': 1
            }
        ]
    }

    with open(INIT_TEST_FILE, 'w') as file:
        yaml.dump(test_data, file)

    config = read(INIT_TEST_FILE)
    assert config.id == test_data['id']
    assert config.strategies
    assert 'tokens' in config.strategies[0]


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    '''Delete test file after all tests has been executed.'''
    def delete_test_file():
        INIT_TEST_FILE.unlink()
    request.addfinalizer(delete_test_file)
