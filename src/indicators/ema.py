'''Strategy indicator.'''
from indicators.indicator import Indicator

class EMA(Indicator):
    '''Implement EMA trading indicator.'''
    def __init__(self, test_mode, requester, arguments):
        Indicator.__init__(self, test_mode, requester, arguments)

        self.ema = 0
        if self._test_mode:
            functions = (
                {
                    'name': 'Exponential Moving Average',
                    'color': 'b',
                    'type': '-'
                },
            )
            self._plotter.setup_plot(functions)
        self.start()

    def run(self):
        '''Implementation of indicator.'''
        length = self._arguments['length']
        smoothing = self._arguments['smoothing']
        multiplier = smoothing / (1 + length)

        prices = self._get_prices()
        init_prices = [price[3] for price in prices]

        while True:
            if init_prices:
                price = init_prices[0]
                del init_prices[0]

                if len(init_prices) == 0:
                    self.initialized = True
            else:
                price = self._get_last_price()[3]

            self.ema = price * multiplier + self.ema * (1 - multiplier)
            if self._test_mode:
                self._store.append((self.ema,))
                if len(self._store) == 100 or self.initialized:
                    self._queue.put(self._store)
                    self._store = []

            if self.initialized:
                self._wait_until_interval()
