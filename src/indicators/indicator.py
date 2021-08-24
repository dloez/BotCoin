'''Base class for indicators.'''
import threading
from multiprocessing import Queue

from plotter import Plotter


# pylint: disable=R0902
class Indicator(threading.Thread):
    '''Implementation of parent class for indicators.'''
    def __init__(self, test_mode, requester, symbol, interval):
        threading.Thread.__init__(self)

        self._test_mode = False
        self._requester = requester
        self._symbol = symbol
        self._interval = interval
        self.initialized = False

        if test_mode == 2:
            self._test_mode = True
            self._queue = Queue()
            self._plotter = Plotter(self._queue, 1)
            self._store = []

    def _get_prices(self):
        return self._requester.get_data(self._symbol, self._interval)

    def _get_last_price(self):
        return self._requester.get_data(self._symbol, self._interval)[-1]
