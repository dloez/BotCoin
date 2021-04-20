'''Make operations between bot and databases.'''
import pickle
import random
import sqlite3
import os
import sys
from colorama import init, Fore


class DBManager:
    '''Manage database operations.'''
    def __init__(self, storage_dir, session_id):
        # init colorama
        init(autoreset=True)

        self._databases_dir = storage_dir / 'databases'
        self._last_session_file = storage_dir / 'last_session.pickle'
        self._session_id = None
        self._connection = None

        # select desired id
        self._check_paths()
        if not session_id:
            self._session_id = str(random.randint(100000, 999999))
        elif session_id == 'last':
            self._load_id()
        else:
            self._session_id = session_id

        print(f'{Fore.GREEN}Session id: {self._session_id}')
        self._dump_id()

    def _check_paths(self):
        '''Check that all necesary fields and dirs are created.'''
        if not self._databases_dir.exists():
            self._databases_dir.mkdir(parents=True, exist_ok=True)

        if not self._last_session_file.exists():
            file = self._last_session_file.open('w')
            file.close()

    def _load_id(self):
        '''Load previous session id if exists.'''
        if os.path.getsize(self._last_session_file) > 0:
            with self._last_session_file.open('rb') as file:
                self._session_id = pickle.load(file)
        else:
            print(f'{Fore.RED}There is no last id, exiting...')
            sys.exit()

    def _dump_id(self):
        '''Save current id for future uses.'''
        with self._last_session_file.open('wb') as file:
            pickle.dump(self._session_id, file)

    def _get_database(self):
        '''Return name of the selected database based on session id.'''
        return str(self._databases_dir / self._session_id) + '.sqlite3'

    def create_table(self, table):
        '''Create table.'''
        with sqlite3.connect(self._get_database()) as conn:
            cursor = conn.cursor()
            cursor.execute(table.generate_sql())
            cursor.close()

    def insert(self, record):
        '''Insert record into table.'''
        with sqlite3.connect(self._get_database()) as conn:
            cursor = conn.cursor()
            cursor.execute(record.generate_sql())
            cursor.close()

    def truncate_table(self, table):
        '''Delete and recreate table.'''
        with sqlite3.connect(self._get_database()) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE {table.name};")
            cursor = conn.cursor()
            self.create_table(table)

class Table:
    '''Helper class to handle creation of sql tables.'''
    def __init__(self, name):
        self.name = name
        self._fields = []

    def add_field(self, name, data_type, primary_key=False, not_null=False):
        '''Add field to table.'''
        field = {
            'name': name,
            'type': data_type,
            'primary_key': primary_key,
            'not_null': not_null
        }

        self._fields.append(field)

    def generate_sql(self):
        '''Generate sql code.'''
        sql = f'CREATE TABLE IF NOT EXISTS {self.name} (\n'
        for field in self._fields:
            sql += f"\t{field['name']} {field['type']} "

            if field['primary_key']:
                sql += 'PRIMARY KEY '

            if field['not_null']:
                sql += 'NOT NULL '

            sql = sql[:-1] + ',\n'
        sql = sql[:-2] + '\n);'
        return sql

# pylint: disable=R0903
class Record:
    '''Helper class to handle creation of sql records.'''
    def __init__(self, **kwargs):
        init(autoreset=True)
        self._fields = {}

        if 'table' not in kwargs:
            print(f'{Fore.RED}Unspecified table.')
        else:
            self._fields = kwargs

    def generate_sql(self):
        '''Generate sql code.'''
        sql = f"INSERT INTO {self._fields['table']}\nVALUES("
        for field_name, field_value in self._fields.items():
            if field_name == 'table':
                continue
            sql += field_value + ','
        sql = sql[:-1] + ');'
        return sql


class RecordsGroup:
    '''Helper class the creation of multiple sql records with a single call.'''
    def __init__(self, table):
        self._table = table
        self._records = []

    def add_record(self, **kwargs):
        '''Add record to group.'''
        fields = []
        for field in kwargs.values():
            fields.append(field)
        self._records.append(fields)

    def generate_sql(self):
        '''Generate sql code.'''
        sql = f"INSERT INTO {self._table}\nVALUES"
        for record in self._records:
            sql += '\n\t('
            for field in record:
                sql += f'{field},'
            sql = sql[:-1] + '),'
        sql = sql[:-1] + ';'
        return sql
