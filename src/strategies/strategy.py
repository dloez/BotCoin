'''Parent of strategies.'''
import sys
import threading
from datetime import datetime
from colorama import Fore

import dbmanager
from wrappers.binance import Binance
from wrappers.binance import SIDE_BUY, SIDE_SELL, STATUS_NEW
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
    def __init__(self, session, indicator_manager, arguments, test_mode):
        threading.Thread.__init__(self)
        self.name = arguments['name']

        tokens = arguments['tokens']
        self._session_maker = session
        self.__session = self._session_maker()
        self._binance = Binance(key=tokens['binance_api_key'], secret=tokens['binance_api_secret'])
        self._indicator_manager = indicator_manager
        self._test_mode = test_mode
        self.prices_table = f"prices_{arguments['symbol'].lower()}_{arguments['interval']}"
        self.data = None
        self._init_strategy(arguments)

        self._listener = Listener(tokens, self._session_maker)

        self._symbol_assets = {}
        self._set_base_quote_assets(arguments['symbols'])
        print(f'{Fore.GREEN}Loading strategy: {self.data.name}')

    def _init_strategy(self, arguments):
        self.data = self.__session.query(dbmanager.Strategy).get(arguments['name'])
        if not self.data:
            self.data = dbmanager.Strategy(
                name=arguments['name'],
                symbol=arguments['symbol'],
                interval=arguments['interval'],
                offset=arguments['offset'],
                benefit=arguments['benefit'],
                loss=arguments['loss']
            )
            self.__session.add(self.data)
            self.__session.commit()

    def _set_base_quote_assets(self, symbols):
        symbol_info = {}
        for symbol in symbols:
            if symbol['symbol'] == self.data.symbol:
                symbol_info = symbol

        if not symbol_info:
            print(f'{Fore.RED}The symbol {self.data.symbol} does not exists!')
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

    def _new_order(self, side):
        price = float(self._binance.get_ticker_24hr(self.data.symbol)['lastPrice']) + self.data.offset
        price = adjust_size(price, tick_size=self._symbol_assets['tick_size'])

        if side == SIDE_BUY:
            quantity = float(self._binance.get_asset_balance(self._symbol_assets['quote']['asset'])['free']) / price
            quantity = adjust_size(quantity, step_size=self._symbol_assets['step_size'])
        elif side == SIDE_SELL:
            quantity = self._binance.get_asset_balance(self._symbol_assets['base']['asset'])['free']
            quantity = adjust_size(quantity, step_size=self._symbol_assets['step_size'])

        binance_order_id = None
        if self._test_mode != 0:
            order_data = self._binance.new_order(
                symbol=self.data.symbol,
                side=side,
                order_type='LIMIT',
                price=price,
                quantity=quantity,
                time_in_force='GTC'
            )
            binance_order_id = order_data['orderId']

        order = dbmanager.Order(
            order_id=binance_order_id,
            side=side,
            price=price,
            quantity=quantity,
            status=STATUS_NEW,
            timestamp=datetime.utcnow(),
            strategy_id=self.data.name
        )

        session = self._session_maker()
        session.add(order)
        session.commit()

        #self._listener.attach(order, 30)
        print(f"{Fore.MAGENTA}{self.data.name}: New {side.lower()} order at {price}")
