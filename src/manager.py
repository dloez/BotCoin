'''Store all necesary strategies and communicate them with database, data collectors, etc.'''
import sys
from colorama import init, Fore

from dbmanager import DBManager
from strategies.macd import MACD
from requester import Requester


# pylint: disable=R0903
class Manager:
    '''Interface between strategies and db, collectores, etc.'''
    def __init__(self, storage_path, args):
        init(autoreset=True)

        self._dbmanager = None
        self._requester = None
        self._strategies = []
        self._strategies_map = {
            'MACD': MACD
        }

        if args.strat.upper() not in self._strategies_map.keys():
            print(f'{Fore.RED}{args.strat} does not exists.')
            sys.exit()

        if '_' not in args.strat_name:
            strat = self._strategies_map[args.strat.upper()](args.strat.upper(), args.pair)
        else:
            strat = self._strategies_map[args.strat.upper()](args.strat_name, args.pair)
        self._strategies.append(strat)

        tokens = args.tokens.split('#')
        self._dbmanager = DBManager(storage_path, args.id)
        self._requester = Requester(self._dbmanager, self._strategies, tokens)
