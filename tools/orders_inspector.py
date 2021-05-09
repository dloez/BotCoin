'''Check results for actuals orders.'''
import sys
sys.path.append('.')

# pylint: disable=C0413
import argparse
import random
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime
from colorama import init, Fore

from src.wrappers.binance import Binance
from src.dbmanager import DBManager, Strategy


def parse_args(args):
    '''Script arguments.'''
    parser = argparse.ArgumentParser(description='Return orders results.')
    parser.add_argument(
        '--start',
        required=True,
        type=int,
        help='Start ammount of money.'
    )

    return parser.parse_args(args)


def get_session(database):
    '''Return database session.'''
    engine = create_engine(f'sqlite:///{database}')
    session = sessionmaker()
    session.configure(bind=engine)
    return session()


def get_order_orm(base, strat):
    '''Create order orm.'''
    new_attrs = {
        '__tablename__': strat.order_table,
        '__table_args__': {'extend_existing': True},
        'id': Column(Integer, primary_key=True),
        'side': Column(String),
        'price': Column(Float),
        'timestamp': Column(DateTime)
    }
    return type(f'Order{random.randint(100, 999)}', (base,), new_attrs)


def main():
    '''Load database and return orders result.'''
    init(autoreset=True)
    args = parse_args(sys.argv[1:])
    base = DBManager.Base
    binance = Binance()

    databases = STORAGE_PATH.glob('**/*.sqlite3')
    for database in databases:
        print(f'Reading {database}...')
        session = get_session(database)

        strats = session.query(Strategy).all()
        for strat in strats:
            order = get_order_orm(base, strat)
            orders = session.query(order).all()

            total = args.start
            total_fees = 0
            for order in orders:
                if order.side == 'buy':
                    fees = FEES * total / 100
                    total_fees += fees
                    total = (total - fees) / order.price
                else:
                    total = total * order.price
                    fees = FEES * total / 100
                    total -= fees
                    total_fees += fees

            if orders and orders[-1].side == 'buy':
                price = float(binance.get_avg_price(strat.pair)['price'])
                total = total * price

            color = Fore.RESET
            if total >= args.start:
                color = Fore.GREEN
            else:
                color = Fore.RED

            print('\t-Results for {} -> {}Total: {:.2f} // Fees: {:.2f} // Fees free: {:.2f}'.format(
                strat.name,
                color,
                total,
                total_fees,
                total + total_fees
            ))


STORAGE_PATH = Path('./storage/databases')
FEES = 0.075

if __name__ == '__main__':
    main()
