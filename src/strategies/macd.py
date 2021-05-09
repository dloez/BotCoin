'''Define bot strategy.'''
import time

from strategies.strategy import Strategy
from strategies.strategy import sync


# pylint: disable=R0903
class MACD(Strategy):
    '''Implements MACD trading algorithm.'''
    def __init__(self, dbmanager, orm, arguments):
        Strategy.__init__(self, dbmanager, orm, arguments)

    # pylint: disable=C0103
    def run(self):
        time.sleep(sync(60))

        A_1 = 0.15
        A_2 = 0.07
        A_3 = 0.2

        ema_12 = 0
        ema_26 = 0
        ema_macd_9 = 0
        macds = []

        last_result = 0
        init_prices = self._get_prices()

        # init ema_12 and ema_26
        ema_12 = sum(init_prices[:12]) / 12
        ema_26 = sum(init_prices[:26]) / 26

        init_prices = init_prices[26:]
        initialized = False
        while True:
            if init_prices:
                price = init_prices[0]
                del init_prices[0]

                if len(init_prices) == 1:
                    initialized = True
            else:
                price = self._get_prices()[-1]

            ema_12 = A_1 * price + (1 - A_1) * ema_12
            ema_26 = A_2 * price + (1 - A_2) * ema_26
            macd = ema_12 - ema_26
            macds.append(macd)
            macds = macds[-9:]

            if len(macds) == 9:
                if not ema_macd_9:
                    ema_macd_9 = sum(macds) / 9
                else:
                    ema_macd_9 = A_3 * macds[-1] + (1 - A_3) * ema_macd_9
                result = macds[-1] - ema_macd_9

                if initialized:
                    last_order = self._session.query(self.order).order_by(self.order.id.desc()).first()
                    if last_result <= 0 <= result:
                        if not last_order or last_order.side == 'sell':
                            self._purchase()
                    elif result <= 0 <= last_result:
                        if last_order and last_order.side == 'buy':
                            self._sell()
                    time.sleep(sync(61))
                last_result = result
