'''Store all necesary strategies and communicate them with database, data collectors, etc.'''
import sys
import random
from colorama import Fore

from dbmanager import DBManager
from wrappers.binance import Binance
from strategies.strat_1 import Strat1
from strategies.strat_2 import Strat2
from requester import Requester
from indicators.idmanager import IndicatorManager


# pylint: disable=R0903
class Manager:
    '''Interface between strategies and db, collectores, etc.'''
    def __init__(self, storage_path, config):
        self._db_manager = DBManager(storage_path, config)
        self._requester = None
        self._strategies = []
        self._strategies_map = {
            'strat1': Strat1,
            'strat2': Strat2
        }

        self._indicator_manager = IndicatorManager(self._db_manager, config.test_mode)

        binance = Binance()
        symbols = binance.get_exchange_info()['symbols']

        for strat in config.strategies:
            if strat['strat'].lower() not in self._strategies_map.keys():
                print(f"{Fore.RED}{strat['strat']} does not exists.")
                sys.exit()

            arguments = {}
            arguments['symbols'] = symbols
            for field, value in strat.items():
                if field == 'name' and not value:
                    value = f"{strat['strat']}_{random.randint(100000, 999999)}"
                arguments[field] = value

            strat = self._strategies_map[strat['strat']](
                self._db_manager,
                self._indicator_manager,
                arguments,
                config.test_mode
            )
            self._strategies.append(strat)
        self._requester = Requester(self._db_manager, self._strategies)

    def start(self):
        '''Init strategies and requester.'''
        self._execute_strategies()

    def _execute_strategies(self):
        self._requester.start()

        # wait until all indicators have their respective data.
        while not self._requester.initialized:
            continue

        for strat in self._strategies:
            strat.start()
