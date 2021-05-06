'''Parent of strategies.'''
import threading
from datetime import datetime
from colorama import Fore

from dbmanager import Table
from wrappers.binance import Binance


def sync(interval):
    '''Return ammount of seconds until next min.'''
    secs = int(datetime.now().strftime('%S'))
    return interval - secs


class Strategy(threading.Thread):
    '''Define structure of all strategies.'''
    def __init__(self, dbmanager, arguments):
        threading.Thread.__init__(self)

        tokens = arguments['tokens']
        self._binance = Binance(key=tokens['binance_api_key'], secret=tokens['binance_api_secret'])
        self._dbmanager = dbmanager
        self._name = arguments['name']
        self.arguments = arguments

        self.prices_table = f"PRICES_{self.arguments['pair']}_{self.arguments['interval']}"
        self.orders_table = f"ORDERS_{self.arguments['name']}"
        print(f'{Fore.GREEN}Strat name: {self.name}')

        self._create_tables()

    def _get_prices(self):
        values = self._dbmanager.select('value', self.prices_table)
        clean_values = []
        for value in values:
            clean_values.append(*value)
        return clean_values

    def _create_tables(self):
        table = Table(self.prices_table)
        table.add_field(name='value', data_type='real', atributes=['not null'])
        self._dbmanager.create_table(table)

        table = Table(self.orders_table)
        table.add_field(name='side', data_type='text', atributes=['not null'])
        table.add_field(name='price', data_type='real', atributes=['not null'])
        table.add_field(name='timestamp', data_type='datetime', atributes=['timestamp', 'not null'])
        self._dbmanager.create_table(table)
