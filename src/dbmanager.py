'''Create database tables based on classes and create engine session.'''
import pickle
import random
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Table, Column, Integer, Float, String, DateTime
from colorama import Fore


# pylint: disable=R0903
class DBManager():
    '''Create ORM and manage database engine.'''
    Base = declarative_base()

    def __init__(self, storage_dir, config):
        self._session_id = config.id
        self._databases_dir = storage_dir / 'databases'
        self._last_session_file = storage_dir / 'last_session.pickle'

        self._check_paths()
        self._check_id()

        self._engine = None
        self._engine = create_engine(f"sqlite:///{str(self._databases_dir / self._session_id) + '.sqlite3'}")

        # session = configured sessionmaker // _session = initiliazed session
        self.session = sessionmaker()
        self.session.configure(bind=self._engine)
        self._session = self.session()
        self._init_database(config.strategies)

    def _init_database(self, strategies):
        '''Append ORM classes into strategies.'''
        for strat in strategies:
            table_name = f"prices_{strat['symbol'].lower()}_{strat['interval']}"
            Table(table_name, self.Base.metadata,
                Column('id', Integer, primary_key=True),
                Column('value', Float),
                extend_existing=True
            )
        self.Base.metadata.create_all(self._engine)

    def _check_paths(self):
        '''Check that all necesary fields and dirs are created.'''
        if not self._databases_dir.exists():
            self._databases_dir.mkdir(parents=True, exist_ok=True)

        if not self._last_session_file.exists():
            file = self._last_session_file.open('w')
            file.close()

    def _check_id(self):
        if not self._session_id:
            self._session_id = str(random.randint(100000, 999999))
        elif self._session_id == 'last':
            self._load_id()
        else:
            self._session_id = self._session_id
        self._dump_id()

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


class Strategy(DBManager.Base):
    '''Strategy orm.'''
    __tablename__ = 'strategies'
    name = Column(String, primary_key=True)
    symbol = Column(String)
    interval = Column(Integer)
    offset = Column(Float)
    orders = relationship('Order')


class Order(DBManager.Base):
    '''Order orm.'''
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=True)
    side = Column(String)
    price = Column(Float)
    quantity = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime)
    strategy_id = Column(Integer, ForeignKey('strategies.name'))
