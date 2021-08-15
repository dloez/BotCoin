'''Handle binance open/closed/cancelled orders.'''
import time
import threading
from datetime import datetime
from colorama import Fore

import dbmanager
from wrappers.binance import SIDE_SELL, STATUS_FILLED, ORDER_MARKET
from wrappers.binance import Binance


STATUS_LISTENING = 'LISTENING'
STATUS_WAITING = 'WAITING'


class Listener(threading.Thread):
    '''Update orders status from binance.'''
    def __init__(self, tokens, session):
        threading.Thread.__init__(self)

        self._binance = Binance(tokens['binance_api_key'], tokens['binance_api_secret'])
        self._order = None
        self._loss = None
        self._strategy = None
        self._session = session

        self.status = STATUS_WAITING

    def run(self):
        '''Check order status.'''
        self._session = self._session()
        self._strategy = self._session.query(dbmanager.Strategy).filter(
            dbmanager.Strategy.name==self._order.strategy_id
        ).first()
        self._order = self._session.query(dbmanager.Order).filter(
            dbmanager.Order.id==self._order.id
        ).first()

        while self.status == STATUS_LISTENING:
            price = self._get_price()
            test_mode = not bool(self._order.order_id)

            if price <= self._loss:
                order_id = None
                quantity = 0.0
                if not test_mode:
                    take_profit_order = self._binance.get_order(
                        symbol=self._strategy.symbol,
                        order_id=self._order.order_id
                    )
                    self._binance.cancel_order(symbol=self._strategy.symbol, order_id=self._order.order_id)
                    stop_loss_order = self._binance.new_order(
                        symbol=self._strategy.symbol,
                        side=SIDE_SELL,
                        order_type=ORDER_MARKET,
                        quantity=take_profit_order['origQty']
                    )
                    order_id = stop_loss_order['orderId']
                    quantity = take_profit_order['origQty']

                stop_loss_order = dbmanager.Order(
                    order_id=order_id,
                    side=SIDE_SELL,
                    price=price,
                    quantity=quantity,
                    status=STATUS_FILLED,
                    timestamp=datetime.utcnow(),
                    strategy_id=self._order.strategy_id
                )
                self._session.query(dbmanager.Order).filter(dbmanager.Order.id==self._order.id).delete()
                self._session.add(stop_loss_order)
                self._session.commit()
                self.status = STATUS_WAITING
                print(f'{Fore.RED}{self._strategy.name}: Hit Stop Loss')
            else:
                if not test_mode:
                    take_profit_order = self._binance.get_order(
                        symbol=self._strategy.symbol,
                        order_id=self._order.order_id
                    )

                    if take_profit_order['status'] == STATUS_FILLED:
                        self._order.status = STATUS_FILLED
                        self._session.commit()
                        self.status = STATUS_WAITING
                        print(f'{Fore.GREEN}{self._strategy.name}: Hit Take Profit')
                else:
                    if price >= self._order.price:
                        self._order.status = STATUS_FILLED
                        self._session.commit()
                        self.status = STATUS_WAITING
                        print(f'{Fore.GREEN}{self._strategy.name}: Hit Take Profit')
            time.sleep(3)

    def attach(self, order, loss):
        '''Add order that needs to be retrieved to listener and start to listen for updates.'''
        self._order = order
        self._loss = loss
        self.status = STATUS_LISTENING

        self.start()

    def _get_price(self):
        return float(self._binance.get_ticker_24hr(self._strategy.symbol)['lastPrice'])
