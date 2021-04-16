'''Store all necesary strategies and communicate them with database, data collectors, etc.'''
from dbmanager import DBManager


# pylint: disable=R0903
class Manager:
    '''Interface between strategies and db, collectores, etc.'''
    def __init__(self, storage_path, args):
        self._dbmanager = DBManager(storage_path, args.id)
