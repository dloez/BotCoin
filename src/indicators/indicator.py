'''Base class for indicators.'''
import threading
from multiprocessing import Queue

from indicators.plotter import Plotter


# pylint: disable=R0902
class Indicator(threading.Thread):
    '''Implementation of parent class for indicators.'''
    def __init__(self, db_manager, test_mode, prices_table, interval):
        threading.Thread.__init__(self)

        self._db_manager = db_manager
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
        with self._db_manager.create_session() as session:
            prices = session.execute(f'SELECT value FROM {self._prices_table}')
            prices = [price[0] for price in prices]
            return prices

    def _get_last_price(self):
        with self._db_manager.create_session() as session:
            price = list(session.execute(f'SELECT value FROM {self._prices_table} ORDER BY id DESC LIMIT 1'))
            return price[0][0]
