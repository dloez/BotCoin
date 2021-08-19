'''Define bot strategy.'''
import time
from datetime import datetime, timedelta
from colorama import Fore

import dbmanager
from strategies.strategy import Strategy, adjust_size
from wrappers.binance import SIDE_SELL, SIDE_BUY, ORDER_MARKET, ORDER_LIMIT, STATUS_FILLED, STATUS_NEW
from wrappers.binance import TIME_IN_FORCE_GTC
from indicators.idmanager import INDICATOR_RSI
from listener import STATUS_WAITING


# pylint: disable=R0903
class Strat2(Strategy):
    '''Implements RSI scalping trading algorithm.'''
    def __init__(self, db_manager, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, db_manager, indicator_manager, arguments, test_mode)

        self._rsi = None
        self._indicators = ()

    def run(self):
        self._rsi = self._indicator_manager.get_indicator(INDICATOR_RSI, self.prices_table)
        self._indicators = (self._rsi,)

        initialized = False
        while not initialized:
            initialized = True
            for indicator in self._indicators:
                if not indicator.initialized:
                    initialized = False
                    break

        # We are only going to take Long positions, so we do not need short entries
        same_entry = False

        while True:
            rsi = self._rsi.rsi

            # RSI
            oversold = bool(rsi < 30)
            # overbought = bool(rsi > 70)

            if 30 < rsi < 70 and same_entry:
                same_entry = False

            if oversold and self._listener.status == STATUS_WAITING and not same_entry:
                self._buy()
                same_entry = True

            now = datetime.utcnow().replace(second=0, microsecond=0)
            limit = now + timedelta(seconds=self.data['interval'] * 60 + 4)
            while datetime.utcnow() <= limit:
                time.sleep(0.5)

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
