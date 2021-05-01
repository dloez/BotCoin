'''Process init file.'''
from pathlib import Path
from types import SimpleNamespace
import yaml


DEFAULT_INTERVAL = 1 # minutes
DEFAULT_PAIR = 'XRPUSDT'


# pylint: disable=R0912
def read(init_file):
    '''Read and parse init file. Search for missing arguments/errors.'''
    init_file = Path(init_file)
    config = SimpleNamespace()

    # check that files exists
    if not init_file.exists():
        config.error = 'wrong init path'
        return config

    # load yaml
    with open(init_file, 'r') as file:
        init_content = yaml.load(file, Loader=yaml.FullLoader)

    # check strategies
    if 'strategies' not in init_content.keys():
        config.error = 'no strategies found'
        return config

    # check that config file has tokens or each strat has tokens
    tokens = ''
    if 'tokens' not in init_content.keys():
        for strat in init_content['strategies']:
            if 'tokens' not in strat.keys():
                config.error = 'missing tokens'
                return config
    else:
        tokens = init_content['tokens']

    # load all fields into config
    if 'id' in init_content.keys():
        config.id = init_content['id']
    else:
        config.id = None

    config.strategies = []
    for strat in init_content['strategies']:
        if 'strat' not in strat.keys():
            config.error = 'unspecified strategy'
            return config

        new_strat = {}
        new_strat['strat'] = strat['strat']

        if tokens:
            new_strat['tokens'] = tokens
        else:
            new_strat['tokens'] = strat['tokens']

        if 'name' not in strat.keys():
            new_strat['name'] = None
        else:
            new_strat['name'] = strat['name']

        if 'interval' not in strat.keys():
            new_strat['interval'] = DEFAULT_INTERVAL
        else:
            new_strat['interval'] = strat['interval']

        if 'pair' not in strat.keys():
            new_strat['pair'] = DEFAULT_PAIR
        else:
            new_strat['pair'] = strat['pair']

        config.strategies.append(new_strat)

    config.error = ''
    return config
