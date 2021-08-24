'''Parent of strategies.'''
import sys
import threading
from datetime import datetime
from colorama import Fore

import dbmanager
from wrappers.binance import Binance, SIDE_BUY, SIDE_SELL, TIME_IN_FORCE_GTC
from wrappers.binance import ORDER_LIMIT, ORDER_MARKET, STATUS_FILLED, STATUS_NEW
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
        self.data = {}
        self._init_strategy(arguments)

        self._listener = Listener(self._tokens, self._db_manager)

        self._symbol_assets = {}
        self._set_base_quote_assets(arguments['symbols'])
        print(f'{Fore.GREEN}Loaded strategy: {self.data["name"]}')

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

    def _buy(self):
        # Perform new Market order for buy order
        quantity = 0.0
        price = self._get_price()
        binance_order_id = None
        if self._test_mode == 0:
            quantity = self._binance.get_asset_balance(self._symbol_assets['quote']['asset'])['free']
            market_order = self._binance.new_order(
                symbol=self.data['symbol'],
                side=SIDE_BUY,
                order_type=ORDER_MARKET,
                quote_order_qty=quantity
            )
            binance_order_id = market_order['orderId']

        market_order = dbmanager.Order(
            order_id=binance_order_id,
            side=SIDE_BUY,
            price=price,
            quantity=quantity,
            status=STATUS_FILLED,
            timestamp=datetime.utcnow(),
            strategy_id=self.data['name']
        )

        # Set Take Profit
        limit_price = price * ((100 + self.data['benefit']) / 100)
        limit_price = adjust_size(limit_price, tick_size=self._symbol_assets['tick_size'])
        quantity = 0.0

        binance_order_id = None
        if self._test_mode == 0:
            quantity = self._binance.get_asset_balance(self._symbol_assets['base']['asset'])['free']
            quantity = adjust_size(quantity, step_size=self._symbol_assets['step_size'])
            take_profit_order = self._binance.new_order(
                symbol=self.data['symbol'],
                side=SIDE_SELL,
                order_type=ORDER_LIMIT,
                price=limit_price,
                quantity=quantity,
                time_in_force=TIME_IN_FORCE_GTC
            )
            binance_order_id = take_profit_order['orderId']

        take_profit_order = dbmanager.Order(
            order_id=binance_order_id,
            side=SIDE_SELL,
            price=limit_price,
            quantity=quantity,
            status=STATUS_NEW,
            timestamp=datetime.utcnow(),
            strategy_id=self.data['name']
        )

        with self._db_manager.create_session() as session:
            session.add(market_order)
            session.add(take_profit_order)
            session.commit()
            stop_loss = adjust_size(
                price * ((100 - self.data['loss']) / 100),
                tick_size=self._symbol_assets['tick_size']
            )
            self._listener.attach(take_profit_order.id, stop_loss)

        print('{}{}: New entry point at {}. Take Profit: ~{} | Stop Loss: ~{}'.format(
            Fore.YELLOW,
            self.data['name'],
            price,
            limit_price,
            stop_loss
        ))
