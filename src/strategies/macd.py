'''Define bot strategy.'''
from strategies.strategy import Strategy


# pylint: disable=R0903
class MACD(Strategy):
    '''Implements MACD trading algorithm.'''
    def __init__(self, name, pair):
        Strategy.__init__(self, name, pair)
