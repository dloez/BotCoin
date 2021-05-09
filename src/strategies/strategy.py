'''Parent of strategies.'''
import threading
from datetime import datetime
from colorama import Fore

from wrappers.binance import Binance


def sync(interval):
    '''Return ammount of seconds until next min.'''
    secs = int(datetime.now().strftime('%S'))
    return interval - secs


class Strategy(threading.Thread):
    '''Define structure of all strategies.'''
    def __init__(self, dbmanager, orm, arguments):
        threading.Thread.__init__(self)

        tokens = arguments['tokens']
        self._dbmanager = dbmanager
        self._session = self._dbmanager.session()
        self._binance = Binance(key=tokens['binance_api_key'], secret=tokens['binance_api_secret'])
        self._name = arguments['name']
        self.arguments = arguments

        self.price = orm[0]
        self.order = orm[1]
        print(f'{Fore.GREEN}Loading strategy: {self.name}')

    def _get_prices(self):
        prices = self._session.query(self.price).all()
        clean_prices = []
        for price in prices:
            clean_prices.append(price.price)
        return clean_prices

    def _purchase(self):
        price = float(self._binance.get_avg_price(self.arguments['pair'])['price']) + self.arguments['offset']
        order = self.order(side='buy', price=price, timestamp=datetime.utcnow())
        self._session.add(order)
        self._session.commit()

        with threading.Lock():
            print(f"{Fore.MAGENTA}{self.arguments['name']}: Buying at {price}")

    def _sell(self):
        price = float(self._binance.get_avg_price(self.arguments['pair'])['price']) - self.arguments['offset']
        order = self.order(side='sell', price=price, timestamp=datetime.utcnow())
        self._session.add(order)
        self._session.commit()

        with threading.Lock():
            print(f"{Fore.LIGHTBLUE_EX}{self.arguments['name']}: Selling at {price}")
