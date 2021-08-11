'''Strategy indicator.'''
import time
from datetime import datetime, timedelta

from indicators.indicator import Indicator


class MACD(Indicator):
    '''Implements MACD trading indicator.'''
    # pylint: disable=duplicate-code
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

    def run(self):
        '''Implementation of indicator.'''
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

                if len(init_prices) == 0:
                    self.initialized = True
            else:
                price = self._get_last_price()

            ema_12 = 0.15 * price + (1 - 0.15) * ema_12
            ema_26 = 0.07 * price + (1 - 0.07) * ema_26
            self.macd = ema_12 - ema_26
            macds.append(self.macd)
            macds = macds[-9:]

            if len(macds) == 9:
                if not self.ema_macd_9:
                    self.ema_macd_9 = sum(macds) / 9
                else:
                    self.ema_macd_9 = 0.2 * macds[-1] + (1 - 0.2) * self.ema_macd_9
                self.result = self.macd - self.ema_macd_9

                if self._test_mode:
                    self._plotter.add_data((self.macd, self.ema_macd_9))

                if self.initialized:
                    now = datetime.now().replace(second=0, microsecond=0)
                    limit = now + timedelta(seconds=self._interval * 60 + 2)
                    while datetime.now() <= limit:
                        time.sleep(0.5)
                self.last_result = self.result
