'''Test dbmanager module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import shutil
from pathlib import Path
import pytest

from src.dbmanager import DBManager


TEST_PATH = Path('test')
SESSION_ID = '123'

@pytest.fixture
def manager():
    '''Manage dbmanager as a test resource.'''
    return DBManager(TEST_PATH, SESSION_ID)


# pylint: disable=W0212,W0621
def test_init(manager):
    '''Test if all object values are correct.'''
    assert manager._databases_dir == TEST_PATH / 'databases'
    assert manager._last_session_file == TEST_PATH / 'last_session.pickle'
    assert manager._session_id == SESSION_ID


def test_files():
    '''Test if all files has been created.'''
    assert (TEST_PATH / 'databases').exists()
    assert (TEST_PATH / 'databases' / (SESSION_ID + '.sqlite3')).exists()
    assert (TEST_PATH / 'last_session.pickle').exists()


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    '''Delete test dir after all tests has been executed.'''
    def delete_test_dir():
        shutil.rmtree(TEST_PATH)
    request.addfinalizer(delete_test_dir)
