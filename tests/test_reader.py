'''Test module.'''
import sys
from types import SimpleNamespace
sys.path.append('./src')

# pylint: disable=C0413
from pathlib import Path
import yaml
import pytest

from src.reader import read_file, read_arguments


INIT_TEST_FILE = Path('test_init.yaml')


def prepare_file(content):
    '''Write and read init file.'''
    with open(INIT_TEST_FILE, 'w') as file:
        yaml.dump(content, file)

    return read_file(INIT_TEST_FILE)


def test_read_file():
    '''Test that read function is loading yaml file correctly.'''
    config = read_file(INIT_TEST_FILE)
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
            }
        ]
    }

    config = prepare_file(test_data)
    assert not config.error

    test_data = {
        'id': '123',
        'strategies': [
            {
                'strat': 'macd',
            }
        ]
    }

    config = prepare_file(test_data)
    assert config.error == 'missing tokens'

    test_data = {
        'id': '123',
        'tokens': {
            'binance_api_key': 'TU8LjZiscsEGBV1rRrxWvEg0F7BovO4gM1Ukns44mAYRbtNukNaahTwQvJJDnB5J',
            'binance_api_secret': '1M4ruKpeNOJrWjtHBDpGM1rhV7HBHDx5GQOm3NlSJSrN37Rt1LOD7ijxMpeioywm'
        }
    }

    config = prepare_file(test_data)
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
                'interval': 1,
                'offset': 0
            },
            {
                'strat': 'macd',
            }
        ]
    }

    config = prepare_file(test_data)
    assert config.id == test_data['id']
    assert config.strategies
    assert 'tokens' in config.strategies[0].keys()
    assert 'strat' in config.strategies[0].keys()
    assert 'name' in config.strategies[0].keys()
    assert 'pair' in config.strategies[0].keys()
    assert 'interval' in config.strategies[0].keys()
    assert 'offset' in config.strategies[0].keys()

    assert 'tokens' in config.strategies[1].keys()
    assert 'strat' in config.strategies[1].keys()
    assert 'name' in config.strategies[1].keys()
    assert 'pair' in config.strategies[1].keys()
    assert 'interval' in config.strategies[1].keys()
    assert 'offset' in config.strategies[1].keys()


def test_read_arguments():
    '''Test read_arguments.'''
    test_args = SimpleNamespace(
        init='test_path',
        id='123',
        strat='TEST',
        name='MACD_000000',
        pair='BTCUSDT',
        interval=2,
        offset=0.0,
        tokens='123#123'
    )

    config = read_arguments(test_args)
    assert config.id == test_args.id
    assert len(config.strategies) == 1
    assert config.strategies[0]['strat'] == test_args.strat
    assert config.strategies[0]['name'] == test_args.name
    assert config.strategies[0]['pair'] == test_args.pair
    assert config.strategies[0]['interval'] == test_args.interval
    assert config.strategies[0]['offset'] == test_args.offset
    assert config.strategies[0]['tokens']


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    '''Delete test file after all tests has been executed.'''
    def delete_test_file():
        INIT_TEST_FILE.unlink()
    request.addfinalizer(delete_test_file)
