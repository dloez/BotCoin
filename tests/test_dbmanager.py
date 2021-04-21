'''Test dbmanager module.'''
import sys
sys.path.append('./src')

# pylint: disable=C0413
import shutil
from pathlib import Path
import pytest

from src.dbmanager import DBManager, Table, Record, RecordGroup


TABLE_NAME = 'TABLE_000000'
TEST_PATH = Path('test')
SESSION_ID = '123'

# pylint: disable=W0212,W0621
# Table
@pytest.fixture
def table():
    '''Manage table as a test resource.'''
    return Table(TABLE_NAME)


def test_table_init(table):
    '''Test if init values are correctly settled.'''
    assert table.name == TABLE_NAME
    assert isinstance(table._fields, list)


def test_add_field(table):
    '''Test add_field method.'''
    field_1 = table.add_field(
        name='test_field_1',
        data_type='text',
        primary_key='True'
    )

    field_2 = table.add_field(
        name='test_field_1',
        data_type='real'
    )

    field_3 = table.add_field(
        name='test_field_2',
        data_type='real',
    )

    field_4 = table.add_field(
        name='test_field_3',
        data_type='real',
        not_null=True
    )

    # check that all fields are added or not
    assert isinstance(field_1, dict)
    assert not field_2
    assert isinstance(field_3, dict)
    assert isinstance(field_4, dict)

    # check that all fields has correct arguments
    assert field_1['primary_key']
    assert not field_1['not_null']

    assert not field_3['primary_key']
    assert not field_3['not_null']

    assert not field_4['primary_key']
    assert field_4['not_null']


def test_table_generate_sql(table):
    '''Test if sql code is correctly generated.'''
    table.add_field(name='test_field_1', data_type='text', primary_key='True')
    table.add_field(name='test_field_2', data_type='real')
    table.add_field(name='test_field_3', data_type='real', not_null=True)

    sql = (
        f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ('
            'test_field_1 TEXT PRIMARY KEY,'
            'test_field_2 REAL,'
            'test_field_3 REAL NOT NULL'
        ');'
    )
    assert sql == table.generate_sql()


# Record
@pytest.fixture
def record():
    '''Manage record as a test resource.'''
    return Record(
        table=TABLE_NAME,
        test_field_1='test',
        test_field_2='test'
    )


def test_record_init(record):
    '''Test if all record init values are correctly settled.'''
    assert record._fields == {'table': TABLE_NAME, 'test_field_1': 'test', 'test_field_2': 'test'}


def test_record_generate_sql(record):
    '''Test if sql code is correctly generated.'''
    sql = (
        f'INSERT INTO {TABLE_NAME} VALUES '
            '("test","test");'
    )
    assert sql == record.generate_sql()


# RecordsGroup
@pytest.fixture
def group():
    '''Manage RecordGroup as a test resource.'''
    return RecordGroup(TABLE_NAME)


def test_group_init(group):
    '''Test if init values are settled correctly.'''
    assert group._table == TABLE_NAME
    assert isinstance(group._records, list)


def test_add_record(group):
    '''Test that records are properly added.'''
    group.add_record(value_1='test', value_2='test')
    group.add_record(value_1='test', value_2='test')
    assert len(group._records) == 2


def test_group_generate_sql(group):
    '''Test if sql code is correctly generated.'''
    group.add_record(value_1='test', value_2='test')
    group.add_record(value_1='test', value_2='test')

    sql = (
        f'INSERT INTO {TABLE_NAME} VALUES '
        '("test","test"),'
        '("test","test");'
    )
    assert sql == group.generate_sql()


# DBManager || Should we mock Table, Record and RecordGroup?
@pytest.fixture
def manager():
    '''Manage dbmanager as a test resource.'''
    return DBManager(TEST_PATH, SESSION_ID)


def test_dbmanager_init(manager):
    '''Test if all object values are correct.'''
    assert manager._databases_dir == TEST_PATH / 'databases'
    assert manager._last_session_file == TEST_PATH / 'last_session.pickle'
    assert manager._session_id == SESSION_ID


def test_files():
    '''Test if all files has been created.'''
    assert (TEST_PATH / 'databases').exists()
    assert (TEST_PATH / 'last_session.pickle').exists()


def test_get_database(manager):
    '''Test if manager is targeting the correct database.'''
    assert manager._get_database() == str(TEST_PATH / 'databases' /SESSION_ID) + '.sqlite3'


def test_create_table(manager, table):
    '''Test if table has been created.'''
    table.add_field(name='test_field_1', data_type='TEXT')
    table.add_field(name='test_field_2', data_type='TEXT')
    assert manager.create_table(table)


def test_insert(manager, record, group):
    '''Test if record has been added to the table.'''
    group.add_record(test_field_1='test', test_field_2='test')
    print(group.generate_sql())
    assert manager.insert(record)
    assert manager.insert(group)


def test_truncate_table(manager, table):
    '''Test if table has been truncated.'''
    table.add_field(name='test_field_1', data_type='TEXT')
    table.add_field(name='test_field_2', data_type='TEXT')
    assert manager.truncate_table(table)


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    '''Delete test dir after all tests has been executed.'''
    def delete_test_dir():
        shutil.rmtree(TEST_PATH)
    request.addfinalizer(delete_test_dir)
