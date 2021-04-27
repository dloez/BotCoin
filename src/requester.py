'''Comunicate REST APIs, strategies and databases'''
import threading
import asyncio
from colorama import init, Fore

from dbmanager import RecordGroup


# pylint: disable=R0903
class Requester(threading.Thread):
    '''Recollect and store all data required by strategies.'''
    def __init__(self, dbmanager, strategies, binance):
        threading.Thread.__init__(self)
        init(autoreset=True)

        self._dbmanager = dbmanager
        self._strategies = strategies
        self._binance = binance

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.ensure_future(self._handle_tasks())
        loop.run_forever()
        print(f'{Fore.BLUE}Initilizing requester...')

    async def _handle_tasks(self):
        '''Define and run multiple asyncio tasks.'''
        tasks = []
        for strat in self._strategies:
            tasks.append(asyncio.create_task(self._request_data(strat)))

        await asyncio.wait(tasks)
        asyncio.ensure_future(self._handle_tasks())

    async def _request_data(self, strat):
        '''Request and store the data needed by a strategy.'''
        requsites = strat.get_requisites()
        klines = await self._binance.get_klines(requsites['pair'])

        records = RecordGroup(strat.prices_table)
        for kline in klines:
            records.add_record(value=kline[4])

        self._dbmanager.truncate_table(strat.prices_table)
        self._dbmanager.insert(records)

        # set interval instead of fixed time
        await asyncio.sleep(1)
        return True
