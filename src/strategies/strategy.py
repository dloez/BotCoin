'''Parent of strategies.'''
import sys
import threading
from datetime import datetime
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
        count = 0
        for digit in tick_size.split('.')[1]:
            count += 1
            if digit != 1:
                continue
            break
        return round(amount, count)

    first_part, second_part = str(amount).split('.')
    count = 0
    for digit in step_size.split('.')[1]:
        count += 1
        if digit != 1:
            continue
        break
    second_part = second_part[:count]
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
        self._listener = Listener(tokens, self._session)

        self.price = orm[0]
        self.order = orm[1]

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
                tick_size = float(fil['tickSize'])
            if fil['filterType'] == 'LOT_SIZE':
                step_size = float(fil['stepSize'])

        self._pair_assets['base'] = {
            'asset': symbol_info['baseAsset'],
            'precision': symbol_info['baseAssetPrecision'],
        }
        self._pair_assets['quote'] = {
            'asset': symbol_info['quoteAsset'],
            'precision': symbol_info['quoteAssetPrecision']
        }
        self._pair_assets['tick_size'] = str(tick_size)
        self._pair_assets['step_size'] = str(step_size)

    def _get_prices(self):
        prices = self._session.query(self.price).all()
        clean_prices = []
        for price in prices:
            clean_prices.append(price.price)
        return clean_prices

    def _purchase(self):
        price = float(self._binance.get_avg_price(self.arguments['pair'])['price']) + self.arguments['offset']
        price = adjust_size(price, tick_size=self._pair_assets['tick_size'])
        amount = float(self._binance.get_asset_balance(self._pair_assets['quote']['asset'])['free']) / price
        amount = adjust_size(amount, step_size=self._pair_assets['step_size'])

        order_data = self._binance.new_order(
            symbol=self.arguments['pair'],
            side='BUY',
            order_type='LIMIT',
            price=price,
            quantity=amount,
            time_in_force='GTC'
        )

        order = self.order(
            order_id=order_data['orderId'],
            side='buy',
            symbol=order_data['symbol'],
            price=price,
            amount=amount,
            status='NEW',
            timestamp=datetime.utcnow()
        )
        self._session.add(order)
        self._session.commit()

        self._listener.attach(order, 30)
        with threading.Lock():
            print(f"{Fore.MAGENTA}{self.arguments['name']}: Buying at {price}")

    def _sell(self):
        price = float(self._binance.get_avg_price(self.arguments['pair'])['price']) - self.arguments['offset']
        price = adjust_size(price, tick_size=self._pair_assets['tick_size'])
        amount = self._binance.get_asset_balance(self._pair_assets['base']['asset'])['free']
        amount = adjust_size(amount, step_size=self._pair_assets['step_size'])

        order_data = self._binance.new_order(
            symbol=self.arguments['pair'],
            side='BUY',
            order_type='LIMIT',
            price=price,
            quantity=amount,
            time_in_force='GTC'
        )

        order = self.order(
            order_id=order_data['orderId'],
            side='sell',
            symbol=order_data['symbol'],
            price=price,
            amount=amount,
            status='NEW',
            timestamp=datetime.utcnow()
        )
        self._session.add(order)
        self._session.commit()

        self._listener.attach(order, 30)
        with threading.Lock():
            print(f"{Fore.LIGHTBLUE_EX}{self.arguments['name']}: Selling at {price}")
