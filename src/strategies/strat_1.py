'''Define bot strategy.'''
import time
from datetime import datetime, timedelta

import dbmanager
from strategies.strategy import Strategy
from indicators.idmanager import INDICATOR_MACD
from wrappers.binance import SIDE_BUY, SIDE_SELL


# pylint: disable=R0903
class Strat1(Strategy):
    '''Implements MACD trading algorithm.'''
    def __init__(self, session, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, session, indicator_manager, arguments, test_mode)

        self._macd = None
        self._indicators = ()
        self.__session = None

    # pylint: disable=C0103
    def run(self):
        self.__session = self._session_maker()

        self._macd = self._indicator_manager.get_indicator(INDICATOR_MACD, self.prices_table)
        self._indicators = (self._macd,)

        initialized = False
        while not initialized:
            initialized = True
            for indicator in self._indicators:
                if not indicator.initialized:
                    initialized = False
                    break

        while True:
            order = self.__session.query(dbmanager.Order).order_by(dbmanager.Order.id.desc()).first()
            if self._macd.last_result <= 0 <= self._macd.result:
                if not order or order.side == 'sell':
                    self._new_order(SIDE_BUY)
            elif self._macd.result <= 0 <= self._macd.last_result:
                if order and order.side == 'buy':
                    self._new_order(SIDE_SELL)
            now = datetime.now().replace(second=0, microsecond=0)
            to = now + timedelta(seconds=self.data.interval * 60 + 4)
            while datetime.now() <= to:
                time.sleep(0.5)
