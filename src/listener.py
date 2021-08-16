'''Handle binance open/closed/cancelled orders.'''
import time
import threading
from datetime import datetime
from colorama import Fore

import dbmanager
from wrappers.binance import SIDE_SELL, STATUS_FILLED, ORDER_MARKET
from wrappers.binance import Binance


STATUS_WAITING = 'WAITING'
STATUS_LISTENING = 'LISTENING'


class Listener(threading.Thread):
    '''Update orders status from binance.'''
    def __init__(self, tokens, db_manager):
        threading.Thread.__init__(self)

        self._binance = Binance(tokens['binance_api_key'], tokens['binance_api_secret'])
        self._order_id = None
        self._loss = None
        self._strategy = None
        self._db_manager = db_manager

        self.status = STATUS_WAITING

    def run(self):
        '''Check order status.'''
        session = self._db_manager.create_session()
        order = session.query(dbmanager.Order).filter(
            dbmanager.Order.id==self._order_id
        ).first()
        self._strategy = session.query(dbmanager.Strategy).filter(
            dbmanager.Strategy.name==order.strategy_id
        ).first()

        while self.status == STATUS_LISTENING:
            price = self._get_price()
            test_mode = not bool(order.order_id)

            if price <= self._loss:
                order_id = None
                quantity = 0.0
                if not test_mode:
                    take_profit_order = self._binance.get_order(
                        symbol=self._strategy.symbol,
                        order_id=order.order_id
                    )
                    self._binance.cancel_order(symbol=self._strategy.symbol, order_id=order.order_id)
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
                    strategy_id=order.strategy_id
                )

                session.query(dbmanager.Order).filter(dbmanager.Order.id==order.id).delete()
                session.add(stop_loss_order)
                session.commit()

                self.status = STATUS_WAITING
                print(f'{Fore.RED}{self._strategy.name}: Hit Stop Loss')
            else:
                if not test_mode:
                    take_profit_order = self._binance.get_order(
                        symbol=self._strategy.symbol,
                        order_id=order.order_id
                    )

                    if take_profit_order['status'] == STATUS_FILLED:
                        order.status = STATUS_FILLED
                        session.commit()
                        self.status = STATUS_WAITING
                        print(f'{Fore.GREEN}{self._strategy.name}: Hit Take Profit')
                else:
                    if price >= order.price:
                        order.status = STATUS_FILLED
                        session.commit()
                        self.status = STATUS_WAITING
                        print(f'{Fore.GREEN}{self._strategy.name}: Hit Take Profit')
            if self.status == STATUS_LISTENING:
                time.sleep(3)

        session.close()
        threading.Thread.__init__(self)

    def attach(self, order_id, loss):
        '''Add order that needs to be retrieved to listener and start to listen for updates.'''
        self._order_id = order_id
        self._loss = loss
        self.status = STATUS_LISTENING

        self.start()

    def _get_price(self):
        return float(self._binance.get_ticker_24hr(self._strategy.symbol)['lastPrice'])
