'''Define bot strategy.'''
import time
from datetime import datetime, timedelta

from strategies.strategy import Strategy
from indicators.idmanager import INDICATOR_MACD, INDICATOR_RSI, INDICATOR_STOCHASTIC_RSI
from listener import STATUS_WAITING


# pylint: disable=R0903
class Strat1(Strategy):
    '''Implements Stochastic RSI + RSI + MACD trading algorithm.'''
    def __init__(self, db_manager, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, db_manager, indicator_manager, arguments, test_mode)

        self._macd = None
        self._rsi = None
        self._stochastic = None
        self._indicators = ()

    # Can be much more efficient but I preffer readability in this case.
    # pylint: disable=R0914,R0915,R0912
    def run(self):
        common_args = {
            'symbol': self.data['symbol'],
            'interval': self.data['interval'],
        }
        self._macd = self._indicator_manager.get_indicator(INDICATOR_MACD, common_args)
        self._rsi = self._indicator_manager.get_indicator(INDICATOR_RSI, common_args)
        self._stochastic = self._indicator_manager.get_indicator(INDICATOR_STOCHASTIC_RSI, common_args)
        self._indicators = (self._macd, self._rsi, self._stochastic)

        initialized = False
        while not initialized:
            initialized = True
            for indicator in self._indicators:
                if not indicator.initialized:
                    initialized = False
                    break

        # We are only going to take Long positions, so we do not need short entries
        same_entry = False
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
            result = self._macd.result
            last_result = self._macd.last_result

            # Stochastic RSI
            if stoch_k > 80 and stoch_d > 80:
                overbought = True
                oversold = False

            if stoch_k < 20 and stoch_d < 20:
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
            if overbought and result <= 0 <= last_result:
                # downward_trend = True
                upward_trend = False

            if oversold and last_result <= 0 <= result:
                upward_trend = True
                # downward_trend = False

            # Signals
            # if overbought and confirm_overbought and downward_trend:
            #     sell_signal = True

            if oversold and confirm_oversold and upward_trend:
                buy_signal = True

            if buy_signal and self._listener.status == STATUS_WAITING and not same_entry:
                self._buy()
                same_entry = True

            now = datetime.utcnow().replace(second=0, microsecond=0)
            limit = now + timedelta(seconds=self.data['interval'] * 60 + 4)
            while datetime.utcnow() <= limit:
                time.sleep(0.5)
