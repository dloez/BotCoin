'''Strategy indicator.'''
import time
from datetime import datetime, timedelta

from indicators.indicator import Indicator


class StochasticRSI(Indicator):
    '''Implement Stochastic RSI trading indicator.'''
    # pylint: disable=C0103,R0801
    def __init__(self, session, test_mode, prices_table, interval):
        super().__init__(session, test_mode, prices_table, interval)

        self.k = 0
        self.d = 0
        if self._test_mode:
            functions = (
                {
                    'name': 'k',
                    'color': 'b',
                    'type': '-'
                },
                {
                    'name': 'd',
                    'color': 'r',
                    'type': '-'
                }
            )
            self._plotter.setup_plot(functions)
        self.start()

    def run(self):
        '''Implementation of indicator.'''
        init_prices = self._get_prices()
        prices = []
        avg_gain = 1
        avg_loss = 1
        rsi = []
        stochastic = {
            'k': [],
            'd': []
        }

        while True:
            if init_prices:
                prices.append(init_prices[0])
                prices = prices[-2:]
                del init_prices[0]

                if len(init_prices) == 0:
                    self.initialized = True
            else:
                prices.append(self._get_last_price())

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
                rsi.append(100 - 100 / (1 + relative_strength))
                rsi = rsi[-14:]

                if len(rsi) >= 14:
                    lowest = min(rsi)
                    highest = max(rsi)
                    stochastic['k'].append((rsi[-1] - lowest) / (highest - lowest) * 100)
                    stochastic['k'] = stochastic['k'][-3:]
                    self.k = sum(stochastic['k']) / len(stochastic['k'])

                    stochastic['d'].append(self.k)
                    stochastic['d'] = stochastic['d'][-3:]
                    self.d = sum(stochastic['d']) / len(stochastic['d'])

                    if self._test_mode:
                        self._plotter.add_data((self.k, self.d))

                    if self.initialized:
                        now = datetime.now().replace(second=0, microsecond=0)
                        limit = now + timedelta(seconds=self._interval * 60 + 2)
                        while datetime.now() <= limit:
                            time.sleep(0.5)
