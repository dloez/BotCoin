'''Base class for indicators.'''
import threading
from multiprocessing import Queue

from indicators.plotter import Plotter


# pylint: disable=R0902
class Indicator(threading.Thread):
    '''Implementation of parent class for indicators.'''
    def __init__(self, session, test_mode, prices_table, interval):
        threading.Thread.__init__(self)

        self._session = session()
        self._test_mode = False
        self._prices_table = prices_table
        self._interval = interval
        self.initialized = False

        if test_mode == 2:
            self._test_mode = True
            self._queue = Queue()
            self._plotter = Plotter(self._queue, 1)
            self._store = []

    def _get_prices(self):
        prices = self._session.execute(f'SELECT value FROM {self._prices_table}')
        prices = [price[0] for price in prices]
        return prices

    def _get_last_price(self):
        price = list(self._session.execute(f'SELECT value FROM {self._prices_table} ORDER BY id DESC LIMIT 1'))
        return price[0][0]
