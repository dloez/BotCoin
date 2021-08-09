'''Define bot strategy.'''
import time
from datetime import datetime, timedelta

from indicators.indicator import Indicator


# pylint: disable=R0903
class MACD(Indicator):
    '''Implements MACD trading algorithm.'''
    def __init__(self, session, test_mode, prices_table, interval):
        Indicator.__init__(self, session, test_mode, prices_table, interval)

        self.macd = 0
        self.ema_macd_9 = 0
        self.result = 0 # difference between macd and ema_macd_9
        self.last_result = 0

        if self._test_mode:
            functions = (
                {
                    'name': 'macd',
                    'color': 'b',
                    'type': '-'
                },
                {
                    'name': 'ema_macd_9',
                    'color': 'r',
                    'type': '-'
                }
            )
            self._plotter.setup_plot(functions)
        self.start()

    # pylint: disable=C0103
    def run(self):
        '''Implementation of indicator.'''
        A_1 = 0.15
        A_2 = 0.07
        A_3 = 0.2

        ema_12 = 0
        ema_26 = 0
        macds = []

        init_prices = self._get_prices()

        # init ema_12 and ema_26
        ema_12 = sum(init_prices[:12]) / 12
        ema_26 = sum(init_prices[:26]) / 26

        init_prices = init_prices[26:]
        while True:
            if init_prices:
                price = init_prices[0]
                del init_prices[0]

                if len(init_prices) == 1:
                    self.initialized = True
            else:
                price = self._get_last_price()

            ema_12 = A_1 * price + (1 - A_1) * ema_12
            ema_26 = A_2 * price + (1 - A_2) * ema_26
            self.macd = ema_12 - ema_26
            macds.append(self.macd)
            macds = macds[-9:]

            if len(macds) == 9:
                if not self.ema_macd_9:
                    self.ema_macd_9 = sum(macds) / 9
                else:
                    self.ema_macd_9 = A_3 * macds[-1] + (1 - A_3) * self.ema_macd_9
                self.result = self.macd - self.ema_macd_9

                if self._test_mode:
                    self._plotter.add_data((self.macd, self.ema_macd_9))

                if self.initialized:
                    now = datetime.now().replace(second=0, microsecond=0)
                    to = now + timedelta(seconds=self._interval * 60 + 2)
                    while datetime.now() <= to:
                        time.sleep(0.5)
                self.last_result = self.result
