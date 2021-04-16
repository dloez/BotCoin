'''Make operations between bot and databases.'''
import pickle
import random
import sqlite3
import os
import sys


# pylint: disable=R0903
class DBManager:
    '''Manage database operations.'''
    def __init__(self, storage_dir, session_id):
        self._databases_dir = storage_dir / 'databases'
        self._last_session_file = storage_dir / 'last_session.pickle'
        self._session_id = None
        self._connection = None
        self._cursor = None

        # select desired id
        self._check_paths()
        if not session_id:
            self._session_id = str(random.randint(100000, 999999))
        elif session_id == 'last':
            self._load_id()
        else:
            self._session_id = session_id

        print('Session id: {}'.format(self._session_id))

        # create database connection
        database = str(self._databases_dir / self._session_id) + '.sqlite3'
        self._connection = sqlite3.connect(database)
        self._cursor = self._connection.cursor()
        self._dump_id()

    def _check_paths(self):
        if not self._databases_dir.exists():
            self._databases_dir.mkdir(parents=True, exist_ok=True)

        if not self._last_session_file.exists():
            file = self._last_session_file.open('w')
            file.close()

    def _load_id(self):
        if os.path.getsize(self._last_session_file) > 0:
            with self._last_session_file.open('rb') as file:
                self._session_id = pickle.load(file)
        else:
            print('There is no last id, exiting...')
            sys.exit()

    def _dump_id(self):
        with self._last_session_file.open('wb') as file:
            pickle.dump(self._session_id, file)
