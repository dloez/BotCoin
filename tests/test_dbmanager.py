'''Test module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import shutil
import pytest
import sqlalchemy

from src.dbmanager import DBManager
from .test_manager import CONFIG, STORAGE_PATH


# pylint: disable=W0212,W0621
@pytest.fixture(scope='session')
def dbmanager():
    '''Manage dbmanager as a test resource.'''
    return DBManager(STORAGE_PATH, CONFIG)


def test_init(dbmanager):
    '''Test if all init values have been correctly settled.'''
    databases = STORAGE_PATH / 'databases'
    last_session_file = STORAGE_PATH / 'last_session.pickle'

    assert dbmanager._session_id == CONFIG.id
    assert STORAGE_PATH.exists()
    assert databases.exists()
    assert last_session_file.exists()


def test_tables(dbmanager):
    '''Test if tables are correctly created.'''
    assert sqlalchemy.inspect(dbmanager._engine).has_table('prices_xrpusdt_1')
    assert sqlalchemy.inspect(dbmanager._engine).has_table('prices_btcusdt_1')
    assert sqlalchemy.inspect(dbmanager._engine).has_table('orders_macd001')
    assert sqlalchemy.inspect(dbmanager._engine).has_table('orders_macd002')
    assert sqlalchemy.inspect(dbmanager._engine).has_table('strategies')


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    '''Delete test dir after all tests has been executed.'''
    def delete_test_dir():
        shutil.rmtree(STORAGE_PATH)
    request.addfinalizer(delete_test_dir)
