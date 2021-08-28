'''Comunicate REST APIs, strategies and databases'''
import threading
import time
import numpy as np
from colorama import Fore

from wrappers.binance import Binance


# pylint: disable=R0903
class Requester(threading.Thread):
    '''Recollect and store all data required by strategies.'''
    def __init__(self):
        threading.Thread.__init__(self)

        self._binance = Binance()

        self._strategies = []
        self._data = {}

        self.initialized = False

    def set_strategies(self, strategies):
        '''Set and clear requires strategies.'''
        requisites = []
        for strat in strategies:
            new_requisites = f"{strat.data['symbol']}:{strat.data['interval']}"
            if new_requisites not in requisites:
                self._strategies.append(strat)

    def run(self):
        print(f'{Fore.BLUE}Initializing requester...', end=' ')

        while True:
            threads = []
            for strat in self._strategies:
                thread = threading.Thread(target=self.request_data, args=(strat,))
                thread.daemon = True
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            if not self.initialized:
                print('✔️')
                self.initialized = True
            time.sleep(10)

    def request_data(self, strat):
        '''Request and store the data needed by a strategy.'''
        klines = self._binance.get_klines(strat.data['symbol'], f"{strat.data['interval']}m")

        if not klines:
            return False

        key = f"{strat.data['symbol']}:{strat.data['interval']}"
        self._data[key] = np.empty((1000, 4))

        for i, kline in enumerate(klines):
            del kline[0]
            # Open, High, Low, Closs
            for j in range(4):
                self._data[key][i][j] = kline[j]
        return True

    def get_data(self, symbol, interval):
        '''Return new numpy array with data from Exchange API depending on requirements.'''
        key = f'{symbol}:{interval}'

        if key not in self._data.keys():
            return None
        return np.array(self._data[key])
