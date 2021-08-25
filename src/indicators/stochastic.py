'''Strategy indicator.'''
from indicators.indicator import Indicator


class StochasticRSI(Indicator):
    '''Implement Stochastic RSI trading indicator.'''
    # pylint: disable=C0103
    def __init__(self, test_mode, requester, arguments):
        Indicator.__init__(self, test_mode, requester, arguments)

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
        prices = self._get_prices()
        init_prices = [price[3] for price in prices]
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
                        self._store.append((self.k, self.d))
                        if len(self._store) == 100 or self.initialized:
                            self._queue.put(self._store)
                            self._store = []

                    if self.initialized:
                        self._wait_until_interval()
