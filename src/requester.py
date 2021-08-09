'''Comunicate REST APIs, strategies and databases'''
import threading
import asyncio
from sqlalchemy import text
from colorama import Fore

from wrappers.binance import Binance


# pylint: disable=R0903
class Requester(threading.Thread):
    '''Recollect and store all data required by strategies.'''
    def __init__(self, session, strategies):
        threading.Thread.__init__(self)

        self._session = session()
        self._strategies = strategies
        self._binance = Binance()
        self.initialized = False

    def run(self):
        print(f'{Fore.BLUE}Initializing requester...')
        asyncio.run(self._handle_tasks())

    async def _handle_tasks(self):
        '''Define and run multiple asyncio tasks.'''
        while True:
            tasks = []
            requisites = []
            for strat in self._strategies:
                new_requisites = (strat.data.symbol, strat.data.interval)

                if new_requisites not in requisites:
                    tasks.append(asyncio.create_task(self._request_data(strat)))
                    requisites.append(new_requisites)
            await asyncio.wait(tasks)
            self.initialized = True
            await asyncio.sleep(30)

    async def _request_data(self, strat):
        '''Request and store the data needed by a strategy.'''
        klines = await self._binance.get_klines(strat.data.symbol, f"{strat.data.interval}m")

        self._session.execute(f'DELETE FROM {strat.prices_table}')
        statement = text(f'INSERT INTO {strat.prices_table}(id, value) VALUES(:id, :value)')
        for kline in klines:
            mapping = {'id': kline[0], 'value': kline[4]}
            self._session.execute(statement, mapping)
        self._session.commit()
        return True
