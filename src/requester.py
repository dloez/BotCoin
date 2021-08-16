'''Comunicate REST APIs, strategies and databases'''
import threading
import asyncio
from sqlalchemy import text
from colorama import Fore

from wrappers.binance import Binance


# pylint: disable=R0903
class Requester(threading.Thread):
    '''Recollect and store all data required by strategies.'''
    def __init__(self, db_manager, strategies):
        threading.Thread.__init__(self)

        self._db_manager = db_manager
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
                new_requisites = (strat.data['symbol'], strat.data['interval'])

                if new_requisites not in requisites:
                    tasks.append(asyncio.create_task(self._request_data(strat)))
                    requisites.append(new_requisites)
            await asyncio.wait(tasks)
            self.initialized = True
            await asyncio.sleep(30)

    async def _request_data(self, strat):
        '''Request and store the data needed by a strategy.'''
        klines = await self._binance.get_klines(strat.data['symbol'], f"{strat.data['interval']}m")

        with self._db_manager.create_session() as session:
            session.execute(f'DELETE FROM {strat.prices_table}')
            statement = text(f'INSERT INTO {strat.prices_table}(id, value) VALUES(:id, :value)')
            for kline in klines:
                mapping = {'id': kline[0], 'value': kline[4]}
                session.execute(statement, mapping)
            session.commit()
        return True
