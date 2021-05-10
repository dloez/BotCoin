'''Create database tables based on classes and create engine session.'''
import pickle
import random
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime
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
        self._create_orm(config.strategies)

    def _create_orm(self, strategies):
        '''Append ORM classes into strategies.'''
        counter = 0
        strats = []
        for strat in strategies:
            prices_table_name = f"prices_{strat['pair'].lower()}_{strat['interval']}"
            orders_table_name = f"orders_{strat['name']}"

            price_attributes = {
                '__tablename__': prices_table_name,
                '__table_args__': {'extend_existing': True},
                'id': Column(Integer, primary_key=True),
                'price': Column(Float)
            }

            order_attributes = {
                '__tablename__': orders_table_name,
                'id': Column(Integer, primary_key=True),
                'side': Column(String),
                'price': Column(Float),
                'timestamp': Column(DateTime)
            }

            price_orm = type(f'ClosePrice{counter}', (self.Base,), price_attributes)
            order_orm = type(f'Order{counter}', (self.Base,), order_attributes)
            orm = (price_orm, order_orm)
            strat['orm'] = orm
            counter += 1

            strat = Strategy(
                name=strat['name'],
                pair=strat['pair'],
                price_table=price_attributes['__tablename__'],
                order_table=order_attributes['__tablename__']
            )
            strats.append(strat)
        self.Base.metadata.create_all(self._engine)
        self._session.query(Strategy).delete()

        for strat in strats:
            self._session.add(strat)
        self._session.commit()

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
    '''Strategy orm'''
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    pair = Column(String)
    price_table = Column(String)
    order_table = Column(String)
