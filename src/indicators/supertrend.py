'''Strategy indicator.'''
import numpy as np

from indicators.indicator import Indicator


class SuperTrend(Indicator):
    '''Implement SuperTrend trading indicator.'''
    def __init__(self, test_mode, requester, arguments):
        Indicator.__init__(self, test_mode, requester, arguments)

        self.super_trend = 0
        self.trend = False
        if self._test_mode:
            functions = (
                {
                    'name': 'SuperTrend',
                    'color': 'g',
                    'type': '-'
                },
            )
            self._plotter.setup_plot(functions)
        self.start()

    # pylint: disable=R0912,R0915
    def run(self):
        '''Implementation of indicator.'''
        length = self._arguments['length']
        factor = self._arguments['factor']

        init_prices = self._get_prices()
        prices = []
        true_ranges = []
        final_upper_bands = [0]
        final_lower_bands = [0]
        while True:
            if len(init_prices) > 0:
                prices.append(init_prices[0])
                init_prices = np.delete(init_prices, 0, 0)

                if len(init_prices) == 0:
                    self.initialized = True
            else:
                prices.append(self._get_last_price())

            prices = prices[-2:]
            if len(prices) == 2:
                true_range = max((
                    prices[-1][1] - prices[-1][2],
                    abs(prices[-1][1] - prices[0][3]),
                    abs(prices[-1][2] - prices[0][3])
                ))
                true_ranges.append(true_range)

            true_ranges = true_ranges[-length:]
            if len(true_ranges) == length:
                avg_true_range = sum(true_ranges) / length
                basic_uppper_band = (prices[-1][1] + prices[-1][2]) / 2 + avg_true_range * factor
                basic_lower_band = (prices[-1][1] + prices[-1][2]) / 2 - avg_true_range * factor

                if basic_uppper_band < final_upper_bands[0] or prices[0][3] > final_upper_bands[0]:
                    final_upper_bands.append(basic_uppper_band)
                else:
                    final_upper_bands.append(final_upper_bands[-1])
                final_upper_bands = final_upper_bands[-2:]

                if basic_lower_band > final_lower_bands[0] or prices[0][3] < final_lower_bands[0]:
                    final_lower_bands.append(basic_lower_band)
                else:
                    final_lower_bands.append(final_lower_bands[-1])
                final_lower_bands = final_lower_bands[-2:]

                if len(final_upper_bands) == 2:
                    if self.super_trend == final_upper_bands[0] and prices[-1][3] < final_upper_bands[-1]:
                        self.super_trend = final_upper_bands[-1]
                        self.trend = True
                    elif self.super_trend == final_upper_bands[0] and prices[-1][3] > final_upper_bands[-1]:
                        self.super_trend = final_lower_bands[-1]
                        self.trend = False
                    elif self.super_trend == final_lower_bands[0] and prices[-1][3] < final_lower_bands[-1]:
                        self.super_trend = final_upper_bands[-1]
                        self.trend = True
                    elif self.super_trend == final_lower_bands[0] and prices[-1][3] > final_lower_bands[-1]:
                        self.super_trend = final_lower_bands[-1]
                        self.trend = False

                if self._test_mode:
                    self._store.append((self.super_trend,))
                    if len(self._store) == 100 or self.initialized:
                        self._queue.put(self._store)
                        self._store = []

                if self.initialized:
                    self._wait_until_interval()
