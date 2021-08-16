'''Parent of strategies.'''
import sys
import threading
from colorama import Fore

import dbmanager
from wrappers.binance import Binance
from listener import Listener


def adjust_size(amount, tick_size=0, step_size=0):
    '''Removes excess of decimals.'''
    if tick_size:
        return round(amount, tick_size)

    first_part, second_part = str(amount).split('.')
    second_part = second_part[:step_size]
    return float(f'{first_part}.{second_part}')


# pylint: disable=R0902
class Strategy(threading.Thread):
    '''Define structure of all strategies.'''
    def __init__(self, db_manager, indicator_manager, arguments, test_mode):
        threading.Thread.__init__(self)
        self.name = arguments['name']

        self._tokens = arguments['tokens']
        self._db_manager = db_manager
        self._binance = Binance(key=self._tokens['binance_api_key'], secret=self._tokens['binance_api_secret'])
        self._indicator_manager = indicator_manager
        self._test_mode = test_mode
        self.prices_table = f"prices_{arguments['symbol'].lower()}_{arguments['interval']}"
        self.data = {}
        self._init_strategy(arguments)

        self._listener = Listener(self._tokens, self._db_manager)

        self._symbol_assets = {}
        self._set_base_quote_assets(arguments['symbols'])
        print(f'{Fore.GREEN}Loading strategy: {self.data["name"]}')

    def _init_strategy(self, arguments):
        with self._db_manager.create_session() as session:
            strategy = session.query(dbmanager.Strategy).get(arguments['name'])
            if not strategy:
                strategy = dbmanager.Strategy(
                    name=arguments['name'],
                    symbol=arguments['symbol'],
                    interval=arguments['interval'],
                    offset=arguments['offset'],
                    benefit=arguments['benefit'],
                    loss=arguments['loss']
                )
                session.add(strategy)
                session.commit()

            self.data['name'] = strategy.name
            self.data['symbol'] = strategy.symbol
            self.data['interval'] = strategy.interval
            self.data['offset'] = strategy.offset
            self.data['benefit'] = strategy.benefit
            self.data['loss'] = strategy.loss

    def _set_base_quote_assets(self, symbols):
        symbol_info = {}
        for symbol in symbols:
            if symbol['symbol'] == self.data['symbol']:
                symbol_info = symbol

        if not symbol_info:
            print(f'{Fore.RED}The symbol {self.data["symbol"]} does not exists!')
            sys.exit()

        tick_size = 0
        step_size = 0
        for fil in symbol_info['filters']:
            if fil['filterType'] == 'PRICE_FILTER':
                tick_size = fil['tickSize']
            if fil['filterType'] == 'LOT_SIZE':
                step_size = fil['stepSize']

        for i, char in enumerate(step_size.split('.')[1]):
            if char == '1':
                step_size = i + 1
                break

        for i, char in enumerate(tick_size.split('.')[1]):
            if char == '1':
                tick_size = i + 1
                break

        self._symbol_assets['tick_size'] = tick_size
        self._symbol_assets['step_size'] = step_size

        self._symbol_assets['base'] = {
            'asset': symbol_info['baseAsset'],
            'precision': symbol_info['baseAssetPrecision'],
        }
        self._symbol_assets['quote'] = {
            'asset': symbol_info['quoteAsset'],
            'precision': symbol_info['quoteAssetPrecision']
        }

    def _get_price(self):
        return float(self._binance.get_ticker_24hr(self.data['symbol'])['lastPrice'])
