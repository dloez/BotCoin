'''Define bot strategy.'''
import time
from datetime import datetime, timedelta
from colorama import Fore

import dbmanager
from strategies.strategy import Strategy, adjust_size
from wrappers.binance import SIDE_SELL, SIDE_BUY, ORDER_MARKET, ORDER_LIMIT, STATUS_FILLED, STATUS_NEW
from wrappers.binance import TIME_IN_FORCE_GTC
from indicators.idmanager import INDICATOR_MACD, INDICATOR_RSI, INDICATOR_STOCHASTIC_RSI
from listener import STATUS_WAITING


# pylint: disable=R0903
class Strat1(Strategy):
    '''Implements MACD trading algorithm.'''
    def __init__(self, db_manager, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, db_manager, indicator_manager, arguments, test_mode)

        self._macd = None
        self._rsi = None
        self._stochastic = None
        self._indicators = ()

    # Can be much more efficient but I preffer readability in this case.
    # pylint: disable=R0914,R0915,R0912
    def run(self):
        self._macd = self._indicator_manager.get_indicator(INDICATOR_MACD, self.prices_table)
        self._rsi = self._indicator_manager.get_indicator(INDICATOR_RSI, self.prices_table)
        self._stochastic = self._indicator_manager.get_indicator(INDICATOR_STOCHASTIC_RSI, self.prices_table)
        self._indicators = (self._macd, self._rsi, self._stochastic)

        initialized = False
        while not initialized:
            initialized = True
            for indicator in self._indicators:
                if not indicator.initialized:
                    initialized = False
                    break

        overbought = False
        oversold = False
        # confirm_overbought = False
        confirm_oversold = False
        upward_trend = False
        # downward_trend = False
        buy_signal = False
        # sell_signal = False

        while True:
            stoch_k = self._stochastic.k
            stoch_d = self._stochastic.d
            rsi = self._rsi.rsi
            macd = self._macd.macd
            macd_signal = self._macd.ema_macd_9

            # Stochastic RSI
            if stoch_k >= 80 and stoch_d >= 80:
                overbought = True
                oversold = False

            if stoch_k <= 20 and stoch_d <= 20:
                oversold = True
                overbought = False

            # RSI
            if rsi < 50 and overbought:
                # confirm_overbought = True
                confirm_oversold = False

            if rsi > 50 and oversold:
                confirm_oversold = True
                # confirm_overbought = False

            # MACD
            if overbought and macd <= macd_signal:
                # downward_trend = True
                upward_trend = False

            if oversold and macd >= macd_signal:
                upward_trend = True
                # downward_trend = False

            # Signals
            # if overbought and confirm_overbought and downward_trend:
            #     sell_signal = True

            if oversold and confirm_oversold and upward_trend:
                buy_signal = True

            if buy_signal and self._listener.status == STATUS_WAITING:
                self._buy()

            # if sell_signal:
            #     if last_order and last_order.side == SIDE_BUY:
            #         self._new_order(SIDE_SELL)

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
