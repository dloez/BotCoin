'''Parent of strategies.'''
import threading
import random
from colorama import init, Fore


class Strategy(threading.Thread):
    '''Define structure of all strategies.'''
    def __init__(self, name, pair):
        threading.Thread.__init__(self)
        init(autoreset=True)

        self._pair = pair
        self._requisites = {
            'pair': self._pair
        }

        if '_' not in name:
            self._name = f'{name}_{str(random.randint(100000, 999999))}'
        else:
            self._name = name

        print(f'{Fore.GREEN}Strat name: {self.name}')

    def get_requisites(self):
        '''Return requisites.'''
        return self._requisites
