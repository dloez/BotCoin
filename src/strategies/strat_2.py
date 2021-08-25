'''Define bot strategy.'''
import time
from datetime import datetime, timedelta

from strategies.strategy import Strategy
from indicators.idmanager import INDICATOR_STOCHASTIC_RSI, INDICATOR_SUPERTREND, INDICATOR_EMA
from listener import STATUS_WAITING


# pylint: disable=R0903
class Strat2(Strategy):
    '''Implements RSI scalping trading algorithm.'''
    def __init__(self, db_manager, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, db_manager, indicator_manager, arguments, test_mode)

        self._stochastic = None
        self._super_trend_1 = None
        self._super_trend_2 = None
        self._super_trend_3 = None
        self._ema = None
        self._indicators = ()

    # pylint: disable=R0914,R0915
    def run(self):
        common_args = {
            'symbol': self.data['symbol'],
            'interval': self.data['interval']
        }

        supertrend_args_1 = dict(common_args)
        supertrend_args_1['length'] = 12
        supertrend_args_1['factor'] = 3

        supertrend_args_2 = dict(common_args)
        supertrend_args_2['length'] = 11
        supertrend_args_2['factor'] = 2

        supertrend_args_3 = dict(common_args)
        supertrend_args_3['length'] = 10
        supertrend_args_3['factor'] = 1

        ema_args = dict(common_args)
        ema_args['length'] = 200
        ema_args['smoothing'] = 2

        self._stochastic = self._indicator_manager.get_indicator(INDICATOR_STOCHASTIC_RSI, common_args)
        self._super_trend_1 = self._indicator_manager.get_indicator(INDICATOR_SUPERTREND, supertrend_args_1)
        self._super_trend_2 = self._indicator_manager.get_indicator(INDICATOR_SUPERTREND, supertrend_args_2)
        self._super_trend_3 = self._indicator_manager.get_indicator(INDICATOR_SUPERTREND, supertrend_args_3)
        self._ema = self._indicator_manager.get_indicator(INDICATOR_EMA, ema_args)
        self._indicators = (self._stochastic, self._super_trend_1, self._super_trend_2, self._super_trend_3, self._ema)

        initialized = False
        while not initialized:
            initialized = True
            for indicator in self._indicators:
                if not indicator.initialized:
                    initialized = False
                    break

        # We are only going to take Long positions, so we do not need short entries
        same_entry = False
        oversold = False
        while True:
            buy_signal = False
            stoch_k = self._stochastic.k
            stoch_d = self._stochastic.d
            trends = 0

            # Stochastic RSI

            cross_up = self._stochastic.result <= 0 <= self._stochastic.last_result
            cross_down = self._stochastic.last_result <= 0 <= self._stochastic.result

            if stoch_d < 20 and stoch_k < 20 and (cross_up or cross_down):
                oversold = True

            if stoch_d > 50 and stoch_d > 50:
                oversold = False
                same_entry = False

            # SuperTrend
            if self._super_trend_1.trend:
                trends += 1
            if self._super_trend_2.trend:
                trends += 1
            if self._super_trend_3.trend:
                trends += 1

            if oversold and trends >= 2 and self._get_price() > self._ema.ema:
                buy_signal = True

            if buy_signal and self._listener.status == STATUS_WAITING and not same_entry:
                self._buy()
                same_entry = True

            now = datetime.utcnow().replace(second=0, microsecond=0)
            limit = now + timedelta(seconds=self.data['interval'] * 60 + 4)
            while datetime.utcnow() <= limit:
                time.sleep(0.5)
