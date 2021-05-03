'''Parent of strategies.'''
import threading
import random
from datetime import datetime
from colorama import init, Fore

from dbmanager import Table
from wrappers.binance import Binance


def sync(interval):
    '''Return ammount of seconds until next min.'''
    secs = int(datetime.now().strftime('%S'))
    return interval - secs


class Strategy(threading.Thread):
    '''Define structure of all strategies.'''
    def __init__(self, dbmanager, tokens, name, arguments):
        threading.Thread.__init__(self)
        init(autoreset=True)

        self._binance = Binance(key=tokens['binance_api_key'], secret=tokens['binance_api_secret'])
        self._dbmanager = dbmanager
        self._requisites = arguments

        if '_' not in name:
            self._name = f'{name}_{str(random.randint(100000, 999999))}'
        else:
            self._name = name

        self.prices_table = self._name + '_PRICES'
        self.orders_table = self._name + '_ORDERS'
        print(f'{Fore.GREEN}Strat name: {self.name}')

        self._create_tables()

    def get_requisites(self):
        '''Return requisites.'''
        return self._requisites

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
