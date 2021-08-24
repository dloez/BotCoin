'''Define bot strategy.'''
import time
from datetime import datetime, timedelta

from strategies.strategy import Strategy
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
        self._rsi = self._indicator_manager.get_indicator(INDICATOR_RSI, self.data['symbol'], self.data['interval'])
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
