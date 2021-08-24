'''Indicator management.'''
import sys
from colorama import Fore

from indicators.macd import MACD
from indicators.rsi import RSI
from indicators.stochastic import StochasticRSI


INDICATOR_MACD = 'MACD'
INDICATOR_RSI = 'RSI'
INDICATOR_STOCHASTIC_RSI = 'STOCH_RSI'


# pylint: disable=R0903
class IndicatorManager:
    '''Manages the instantiation of new indicators of none available with same data requisites.'''
    def __init__(self, requester, test_mode):
        self._requester = requester
        self._test_mode = test_mode

        self._indicators_map = {
            'MACD': MACD,
            'RSI': RSI,
            'STOCH_RSI': StochasticRSI
        }
        self._indicators = {}

    def get_indicator(self, indicator_name, symbol, interval):
        '''Return an already defined indicator or reuse a predefined one if it requires the same data.'''
        indicator_key = f'{indicator_name}:{symbol}:{interval}'
        try:
            indicator = self._indicators[indicator_key]
        except KeyError:
            if indicator_name not in self._indicators_map.keys():
                print(f'{Fore.RED}{indicator_name} indicator does not exists.')
                sys.exit()
            indicator = self._indicators_map[indicator_name](self._test_mode, self._requester, symbol, interval)
            self._indicators[indicator_key] = indicator
        return indicator
