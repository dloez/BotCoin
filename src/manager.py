'''Store all necesary strategies and communicate them with database, data collectors, etc.'''
import sys
from colorama import init, Fore

from dbmanager import DBManager
from strategies.macd import MACD
from requester import Requester
from wrappers.binance import Binance


# pylint: disable=R0903
class Manager:
    '''Interface between strategies and db, collectores, etc.'''
    def __init__(self, storage_path, args):
        init(autoreset=True)

        self._dbmanager = None
        self._binance = None
        self._requester = None
        self._strategies = []
        self._strategies_map = {
            'MACD': MACD
        }

        if args.strat.upper() not in self._strategies_map.keys():
            print(f'{Fore.RED}{args.strat} does not exists.')
            sys.exit()

        tokens = args.tokens.split('#')
        self._binance = Binance(tokens)
        self._dbmanager = DBManager(storage_path, args.id)
        if '_' not in args.strat_name:
            strat = self._strategies_map[args.strat.upper()](
                args.strat.upper(),
                args.pair,
                self._dbmanager,
                self._binance
            )
        else:
            strat = self._strategies_map[args.strat.upper()](
                args.strat_name,
                args.pair,
                self._dbmanager,
                self._binance
            )
        self._strategies.append(strat)

        self._requester = Requester(self._dbmanager, self._strategies, self._binance)
        self._requester.start()
        self._execute_strategies()

    def _execute_strategies(self):
        for strat in self._strategies:
            strat.start()
