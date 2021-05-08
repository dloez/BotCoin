'''Check results for actuals orders.'''
import sys
sys.path.append('.')

# pylint: disable=C0413
import sqlite3
import argparse
from pathlib import Path
import yaml
from colorama import init, Fore

from src.wrappers.binance import Binance


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

# pylint: disable=R0914
def main():
    '''Load database and return orders result.'''
    init(autoreset=True)
    args = parse_args(sys.argv[1:])
    binance = Binance()

    databases = (STORAGE_DIR / 'databases').glob('**/*.sqlite3')
    for database in databases:
        with sqlite3.connect(database) as conn:
            print(f'Reading {database}...')
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type = "table";')
            tables = cursor.fetchall()
            clean_tables = []
            for table in tables:
                if 'PRICES' in table[0]:
                    continue
                clean_tables.append(*table)
            tables = clean_tables

            for table in tables:
                strat_name = table.split('_')[1] + '_' + table.split('_')[2]
                with open(INIT_FILE, 'r') as file:
                    init_content = yaml.load(file, Loader=yaml.FullLoader)

                pair = ''
                for strat in init_content['strategies']:
                    if strat['name'] == strat_name:
                        pair = strat['pair']

                cursor.execute(f'SELECT * FROM {table};')
                orders = cursor.fetchall()

                total = args.start
                total_fees = 0
                jump = 0
                for order in orders:
                    if jump == 0:
                        fees = FEES * total / 100
                        total_fees += fees
                        total = (total - fees) / order[1]
                        jump += 1
                    else:
                        total = total * order[1]
                        fees = FEES * total / 100
                        total -= fees
                        total_fees += fees
                        jump = 0

                if jump == 1:
                    price = binance.get_avg_price(pair)['price']
                    total = total * float(price)

                color = Fore.RESET
                if total >= args.start:
                    color = Fore.GREEN
                else:
                    color = Fore.RED
                print('\tResults for {}:{} Total -> {:.2f} // Fees free -> {:.2f} // Fees -> {:.2f}'.format(
                    table,
                    color,
                    total,
                    total + total_fees,
                    total_fees
                ))


STORAGE_DIR = Path('./storage')
INIT_FILE = Path('./init.yaml')
FEES = 0.075

if __name__ == '__main__':
    main()
