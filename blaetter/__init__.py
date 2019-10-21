import logging

import yaml

with open('config.yaml') as fobj:
    config = yaml.full_load(fobj)

fetch_log = logging.getLogger('fetch')
subscr_log = logging.getLogger('subscr')
tel_log = logging.getLogger('telegram')

formatter = logging.Formatter(
    fmt='{asctime} [{levelname:^7s}] {msg}',
    datefmt='%m.%d. %Hh',
    style='{'
)

fetch_handler = logging.FileHandler('logs/fetch.log')
subscr_handler = logging.FileHandler('logs/subscriptions.log')

fetch_handler.setFormatter(formatter)
subscr_handler.setFormatter(formatter)

fetch_log.setLevel(config['log_level'])
subscr_log.setLevel(config['log_level'])

tel_log.addHandler(subscr_handler)
subscr_log.addHandler(subscr_handler)
fetch_log.addHandler(fetch_handler)
