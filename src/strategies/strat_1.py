'''Define bot strategy.'''
from strategies.strategy import Strategy
from indicators.idmanager import INDICATOR_MACD, INDICATOR_RSI, INDICATOR_STOCHASTIC_RSI


# pylint: disable=R0903
class Strat1(Strategy):
    '''Implements MACD trading algorithm.'''
    def __init__(self, session, indicator_manager, arguments, test_mode):
        Strategy.__init__(self, session, indicator_manager, arguments, test_mode)

        self._macd = None
        self._rsi = None
        self._stochastic = None
        self._indicators = ()
        self.__session = None

    # pylint: disable=C0103
    def run(self):
        # self.__session = self._session_maker()

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

        # implement strategy
