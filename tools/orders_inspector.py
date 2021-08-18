'''Calculate benefits/losses on bot runs.'''
import sys
sys.path.append('.')

# pylint: disable=C0413
import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from colorama import init, Fore

from src.wrappers.binance import Binance, SIDE_BUY
from src.dbmanager import Strategy, Order


def parse_args(args):
    '''Script arguments.'''
    parser = argparse.ArgumentParser(description='Return orders results.')
    parser.add_argument(
        '--start',
        type=int,
        help='Start ammount of money in case of test mode.'
    )

    return parser.parse_args(args)


def get_session(database):
    '''Return database session.'''
    engine = create_engine(f'sqlite:///{database}')
    return Session(engine)


def main():
    '''Load database and return orders result.'''
    init(autoreset=True)
    args = parse_args(sys.argv[1:])
    binance = Binance()

    databases = STORAGE_PATH.glob('**/*.sqlite3')
    for database in databases:
        print(f'Reading {database}...')
        session = get_session(database)

        strats = session.query(Strategy).all()
        for strat in strats:
            orders = list(session.query(Order).filter(Order.strategy_id==strat.name).all())
            total = args.start
            total_fees = 0

            for order in orders:
                if order.side == SIDE_BUY:
                    fees = FEES * total / 100
                    total_fees += fees
                    total = (total - fees) / order.price
                else:
                    total = total * order.price
                    fees = FEES * total / 100
                    total -= fees
                    total_fees += fees

            if orders and orders[-1].side == 'buy':
                price = float(binance.get_ticker_24hr(strat.pair)['lastPrice'])
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
