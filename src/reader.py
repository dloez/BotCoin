'''Process init file.'''
from pathlib import Path
from types import SimpleNamespace
import yaml


DEFAULT_FIELDS = {
    'name': None,
    'interval': 1, # minutes
    'pair': 'XRPUSDT',
    'offset': 0
}


def load_yaml(init_file):
    '''Read and load yaml init file.'''
    # check that files exists
    if not init_file.exists():
        return 'wrong init path'

    # load yaml
    with open(init_file, 'r') as file:
        init_content = yaml.load(file, Loader=yaml.FullLoader)
    return init_content


def create_strat(tokens, strat):
    '''Create new strat that can be appended to config.'''
    if 'strat' not in strat.keys():
        return 'unspecified strategy'

    new_strat = {}
    new_strat['strat'] = strat['strat']

    if tokens:
        new_strat['tokens'] = tokens
    else:
        new_strat['tokens'] = strat['tokens']

    for field, value in DEFAULT_FIELDS.items():
        if field not in strat.keys():
            new_strat[field] = value
        else:
            value = strat[field]
            if field == 'name':
                value = value.lower().replace(' ', '')

            new_strat[field] = value
    return new_strat


def read_file(init_file):
    '''Read and parse init file and return config. Search for missing arguments/errors.'''
    init_file = Path(init_file)
    config = SimpleNamespace()

    init_content = load_yaml(init_file)
    if isinstance(init_content, str):
        config.error = init_content
        return config

    # check strategies
    if 'strategies' not in init_content.keys():
        config.error = 'missing strategies'
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
        new_strat = create_strat(tokens, strat)
        if isinstance(new_strat, str):
            config.error = new_strat
            return config

        config.strategies.append(new_strat)

    config.error = None
    return config


def read_arguments(args):
    '''Read arguments and return config.'''
    config = SimpleNamespace()
    config.id = args.id

    strat = {
        'strat': args.strat,
        'tokens': {
            'binance_api_key': args.tokens.split('#')[0],
            'binance_api_secret': args.tokens.split('#')[1]
        },
        'name': args.name,
        'pair': args.pair,
        'interval': args.interval,
        'offset': args.offset
    }
    config.strategies = []
    config.strategies.append(strat)

    return config
