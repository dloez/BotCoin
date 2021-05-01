'''Store all necesary strategies and communicate them with database, data collectors, etc.'''
import sys
from colorama import init, Fore

from dbmanager import DBManager
from strategies.macd import MACD
from requester import Requester


# pylint: disable=R0903
class Manager:
    '''Interface between strategies and db, collectores, etc.'''
    def __init__(self, storage_path, config):
        init(autoreset=True)

        self._dbmanager = None
        self._requester = None
        self._strategies = []
        self._strategies_map = {
            'MACD': MACD
        }

        self._dbmanager = DBManager(storage_path, config.id)
        for strat in config.strategies:
            if strat['strat'].upper() not in self._strategies_map.keys():
                print(f"{Fore.RED}{strat['strat']} does not exists.")
                sys.exit()

            tokens = strat['tokens']
            arguments = {}
            arguments['interval'] = strat['interval']
            arguments['pair'] = strat['pair']

            if '_' not in strat['name']:
                strat = self._strategies_map[strat['strat'].upper()](
                    self._dbmanager,
                    tokens,
                    strat['strat'].upper(),
                    arguments
                )
            else:
                strat = self._strategies_map[strat['strat'].upper()](
                    self._dbmanager,
                    tokens,
                    strat['name'].upper(),
                    arguments
                )
            self._strategies.append(strat)

        self._requester = Requester(self._dbmanager, self._strategies)
        self._requester.start()
        self._execute_strategies()

    def _execute_strategies(self):
        for strat in self._strategies:
            strat.start()
