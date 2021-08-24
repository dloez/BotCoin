'''Strategy indicator.'''
import time
from datetime import datetime, timedelta

from indicators.indicator import Indicator


class RSI(Indicator):
    '''Implement RSI trading indicator.'''
    # pylint: disable=duplicate-code
    def __init__(self, session, test_mode, prices_table, interval):
        super().__init__(session, test_mode, prices_table, interval)

        self.rsi = 0
        if self._test_mode:
            functions = (
                {
                    'name': 'rsi',
                    'color': 'b',
                    'type': '-'
                },
            )
            self._plotter.setup_plot(functions)
        self.start()

    def run(self):
        '''Implementation of indicator.'''
        prices = self._get_prices()
        init_prices = [price[3] for price in prices]
        prices = []
        avg_gain = 1
        avg_loss = 1

        while True:
            if init_prices:
                prices.append(init_prices[0])
                del init_prices[0]

                if len(init_prices) == 0:
                    self.initialized = True
            else:
                prices.append(self._get_last_price()[3])

            prices = prices[-2:]
            if len(prices) >= 2:
                result = prices[-1] - prices[0]
                gain = 0
                loss = 0
                if result >= 0:
                    gain = result
                else:
                    loss = (-1) * result

                avg_gain = (avg_gain * 13 + gain) / 14
                avg_loss = (avg_loss * 13 + loss) / 14
                relative_strength = avg_gain / avg_loss
                self.rsi = 100 - 100 / (1 + relative_strength)

                if self._test_mode:
                    self._store.append((self.rsi,))
                    if len(self._store) == 100 or self.initialized:
                        self._queue.put(self._store)
                        self._store = []

                if self.initialized:
                    now = datetime.now().replace(second=0, microsecond=0)
                    limit = now + timedelta(seconds=self._interval * 60 + 2)
                    while datetime.now() <= limit:
                        time.sleep(0.5)
