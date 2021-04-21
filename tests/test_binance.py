'''Test binance wrapper module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import os
import pytest

from src.wrappers.binance import Binance


API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# pylint: disable=W0212,W0621
@pytest.fixture
def binance():
    '''Manage dbmanager as a test resource.'''
    return Binance([API_KEY, API_SECRET])


def test_init(binance):
    '''Test __init__ method.'''
    assert isinstance(binance._tokens, list)


@pytest.mark.asyncio
async def test_klines(binance):
    '''Test get_klines method.'''
    klines = await binance.get_klines()
    assert isinstance(klines, list)


@pytest.mark.asyncio
async def test_account(binance):
    '''Test get_account method.'''
    account = await binance.get_account()
    assert isinstance(account, dict)


@pytest.mark.asyncio
async def test_asset_balance(binance):
    '''Test get_asset_balance'''
    balance = await binance.get_asset_balance('BTC')
    assert isinstance(balance, dict)
    assert balance['asset'] == 'BTC'
