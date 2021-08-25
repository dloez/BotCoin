'''Base class for indicators.'''
import threading
import time
from datetime import datetime, timedelta
from multiprocessing import Queue

from plotter import Plotter


# pylint: disable=R0902
class Indicator(threading.Thread):
    '''Implementation of parent class for indicators.'''
    def __init__(self, test_mode, requester, arguments):
        threading.Thread.__init__(self)

        self._test_mode = False
        self._requester = requester
        self._arguments = arguments
        self.initialized = False

        if test_mode == 2:
            self._test_mode = True
            self._queue = Queue()
            self._plotter = Plotter(self._queue, 1)
            self._store = []

    def _wait_until_interval(self):
        now = datetime.now().replace(second=0, microsecond=0)
        limit = now + timedelta(seconds=self._arguments['interval'] * 60 + 2)
        while datetime.now() <= limit:
            time.sleep(0.5)

    def _get_prices(self):
        return self._requester.get_data(self._arguments['symbol'], self._arguments['interval'])

    def _get_last_price(self):
        return self._requester.get_data(self._arguments['symbol'], self._arguments['interval'])[-1]
