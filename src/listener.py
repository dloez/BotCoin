'''Handle binance open/closed/cancelled orders.'''
import time
import threading
from datetime import datetime, timedelta

from wrappers.binance import Binance


class Listener(threading.Thread):
    '''Update orders status from binance.'''
    def __init__(self, tokens, session):
        threading.Thread.__init__(self)

        self._binance = Binance(tokens['binance_api_key'], tokens['binance_api_secret'])
        self._order = None
        self._seconds = None
        self._session = session

    def run(self):
        '''Update order and cancell it if it is not completed after self._seconds.'''
        start = datetime.now()
        stop = start + timedelta(seconds=self._seconds)

        order_data = {}
        while start <= stop:
            order_data = self._binance.get_order(self._order.symbol, self._order.orderId)
            self._order.status = order_data['status']
            self._order.amount = order_data['amount']
            self._order.price = order_data['price']
            self._order.save()
            self._session.commit()

            if order_data['status'] == 'FILLED':
                break
            time.sleep(1)

        # - If order is PARTIALLY_FILLED:
        #   * For buy side: Cancel order.
        #   * For sell side: Execute market sell order.
        # - If order is NEW:
        #   * For buy side orders: Cancel order.
        #   * For sell side orders: Execute market sell order.
        # - If order is FILLED: We fcking did it, keep that pretty damn hot code running.
        if self._order.status == 'PARTIALLY_FILLED':
            if self._order.side == 'buy':
                self._binance.cancel_order(self._order.symbol, self._order.order_id)
            else:
                # place new order
                pass
        elif self._order.status == 'NEW':
            pass

    def attach(self, order, seconds):
        '''Add order that needs to be retrieved to listener and start to listen for updates.'''
        self._order = order
        self._seconds = seconds

        self.start()
