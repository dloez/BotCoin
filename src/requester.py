'''Comunicate REST APIs, strategies and databases'''
import threading
import asyncio
from colorama import Fore

from wrappers.binance import Binance


# pylint: disable=R0903
class Requester(threading.Thread):
    '''Recollect and store all data required by strategies.'''
    def __init__(self, dbmanager, strategies):
        threading.Thread.__init__(self)

        self._dbmanager = dbmanager
        self._strategies = strategies
        self._binance = Binance()
        self._session = self._dbmanager.session()

    def run(self):
        print(f'{Fore.BLUE}Initializing requester...')
        asyncio.run(self._handle_tasks())

    async def _handle_tasks(self):
        '''Define and run multiple asyncio tasks.'''
        while True:
            tasks = []
            requisites = []
            for strat in self._strategies:
                strat_requisites = strat.arguments
                new_requisites = (strat_requisites['pair'], strat_requisites['interval'])

                if new_requisites not in requisites:
                    tasks.append(asyncio.create_task(self._request_data(strat)))
                    requisites.append(new_requisites)
            await asyncio.wait(tasks)

    async def _request_data(self, strat):
        '''Request and store the data needed by a strategy.'''
        requisites = strat.arguments
        klines = await self._binance.get_klines(requisites['pair'], f"{requisites['interval']}m")

        self._session.query(strat.price).delete()
        for kline in klines:
            price = strat.price(price=kline[4])
            self._session.add(price)
        self._session.commit()

        await asyncio.sleep(5)
        return True
