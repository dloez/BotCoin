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
    def __init__(self, session, test_mode):
        self._session = session
        self._test_mode = test_mode

        self._indicators_map = {
            'MACD': MACD,
            'RSI': RSI,
            'STOCH_RSI': StochasticRSI
        }
        self._indicators = {}

    def get_indicator(self, indicator_name, table):
        '''Return an already defined indicator or reuse a predefined one if it requires the same data.'''
        interval = int(table.split('_')[2])
        indicator_key = f'{indicator_name}:{table}'
        try:
            indicator = self._indicators[indicator_key]
        except KeyError:
            if indicator_name not in self._indicators_map.keys():
                print(f'{Fore.RED}{indicator_name} indicator does not exists.')
                sys.exit()
            indicator = self._indicators_map[indicator_name](self._session, self._test_mode, table, interval)
            self._indicators[indicator_key] = indicator
        return indicator
