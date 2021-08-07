'''Handle binance open/closed/cancelled orders.'''
import time
import threading
from datetime import datetime, timedelta

from wrappers.binance import Binance


class Listener(threading.Thread):
    '''Update orders status from binance.'''
    def __init__(self, tokens, session, order_orm):
        threading.Thread.__init__(self)

        self._binance = Binance(tokens['binance_api_key'], tokens['binance_api_secret'])
        self._order = None
        self._seconds = None
        self._session = session
        self._order_orm = order_orm

    def run(self):
        '''Update order and cancell it if it is not completed after self._seconds.'''
        start = datetime.now()
        stop = start + timedelta(seconds=self._seconds)

        # Wait until pause time completed
        while datetime.now() <= stop:
            time.sleep(0.5)

        print('Cheking for last order...')
        order_data = self._binance.get_order(self._order.symbol, self._order.order_id)
        self._order.status = order_data['status']
        self._order.amount = order_data['executedQty']
        self._order.price = order_data['price']
        self._session.commit()

        # - If order is PARTIALLY_FILLED:
        #   * For buy side orders: Cancel order and mark order as FILLED.
        #   * For sell side orders: Execute market sell order.
        # - If order is NEW:
        #   * For buy side orders: Cancel order.
        #   * For sell side orders: Execute market sell order.
        # - If order is FILLED: We fcking did it, keep that pretty damn hot code running.
        if self._order.status == 'PARTIALLY_FILLED':
            print('PARTIALLY_FILLED, MANUAL REVIEW OF ORDERS PLEASE')
        elif self._order.status == 'NEW':
            if self._order.side == 'buy':
                self._binance.cancel_order(self._order.symbol, self._order.order_id)
                self._order.status = 'FILLED'
            else:
                order_data = self._binance.new_order(
                    self._order.symbol,
                    side='SELL',
                    price=0,
                    order_type='MARKET',
                    quantity=self._order.amount
                )

                new_order = self._order_orm(
                    order_id=order_data['orderId'],
                    side='sell',
                    symbol=order_data['symbol'],
                    price=order_data['price'],
                    amount=order_data['executedQty'],
                    status=order_data['status'],
                    timestamp=datetime.utcnow()
                )
                self._session.add(new_order)
        self._session.commit()

    def attach(self, order, seconds):
        '''Add order that needs to be retrieved to listener and start to listen for updates.'''
        self._order = order
        self._seconds = seconds

        self.start()
