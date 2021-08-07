'''Parent of strategies.'''
import sys
import threading
from datetime import datetime
import random
from colorama import Fore

from wrappers.binance import Binance
from listener import Listener


def sync(interval):
    '''Return ammount of seconds until next min.'''
    secs = int(datetime.now().strftime('%S'))
    return interval - secs


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
    def __init__(self, session, orm, arguments):
        threading.Thread.__init__(self)

        tokens = arguments['tokens']
        self._session = session()
        self._binance = Binance(key=tokens['binance_api_key'], secret=tokens['binance_api_secret'])
        self._name = arguments['name']
        self.arguments = arguments

        self.price = orm[0]
        self.order = orm[1]

        self._listener = Listener(tokens, self._session, self.order)

        self._pair_assets = {}
        self._set_base_quote_assets()
        print(f'{Fore.GREEN}Loading strategy: {self.name}')

    def _set_base_quote_assets(self):
        symbols = self._binance.get_exchange_info()['symbols']

        symbol_info = {}
        for symbol in symbols:
            if symbol['symbol'] == self.arguments['pair']:
                symbol_info = symbol

        if not symbol_info:
            print(f'{Fore.RED}The symbol {self.arguments["pair"]} does not exists!')
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

        self._pair_assets['tick_size'] = tick_size
        self._pair_assets['step_size'] = step_size

        self._pair_assets['base'] = {
            'asset': symbol_info['baseAsset'],
            'precision': symbol_info['baseAssetPrecision'],
        }
        self._pair_assets['quote'] = {
            'asset': symbol_info['quoteAsset'],
            'precision': symbol_info['quoteAssetPrecision']
        }

    def _get_prices(self):
        prices = self._session.query(self.price).all()
        clean_prices = []
        for price in prices:
            clean_prices.append(price.price)
        return clean_prices

    def _purchase(self):
        price = float(self._binance.get_ticker_24hr(self.arguments['pair'])['lastPrice']) + self.arguments['offset']
        price = adjust_size(price, tick_size=self._pair_assets['tick_size'])
        amount = float(self._binance.get_asset_balance(self._pair_assets['quote']['asset'])['free']) / price
        amount = adjust_size(amount, step_size=self._pair_assets['step_size'])

        # order_data = self._binance.new_order(
        #     symbol=self.arguments['pair'],
        #     side='BUY',
        #     order_type='LIMIT',
        #     price=price,
        #     quantity=amount,
        #     time_in_force='GTC'
        # )

        order = self.order(
            order_id=random.randint(1000, 9999),
            side='buy',
            symbol=self.arguments['pair'],
            price=price,
            amount=amount,
            status='NEW',
            timestamp=datetime.utcnow()
        )
        self._session.add(order)
        self._session.commit()

        #self._listener.attach(order, 30)
        print(f"{Fore.MAGENTA}{self.arguments['name']}: Buying at {price}")

    def _sell(self):
        price = float(self._binance.get_ticker_24hr(self.arguments['pair'])['lastPrice']) + self.arguments['offset']
        amount = self._binance.get_asset_balance(self._pair_assets['base']['asset'])['free']
        amount = adjust_size(amount, step_size=self._pair_assets['step_size'])

        # order_data = self._binance.new_order(
        #     symbol=self.arguments['pair'],
        #     side='BUY',
        #     order_type='LIMIT',
        #     price=price,
        #     quantity=amount,
        #     time_in_force='GTC'
        # )

        order = self.order(
            order_id=random.randint(1000, 9999),
            side='sell',
            symbol=self.arguments['pair'],
            price=price,
            amount=amount,
            status='NEW',
            timestamp=datetime.utcnow()
        )
        self._session.add(order)
        self._session.commit()

        #self._listener.attach(order, 30)
        print(f"{Fore.LIGHTBLUE_EX}{self.arguments['name']}: Selling at {price}")
