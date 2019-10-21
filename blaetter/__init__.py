import logging

import yaml

with open('config.yaml') as fobj:
    config = yaml.full_load(fobj)

fetch_log = logging.getLogger('fetch')
subscr_log = logging.getLogger('subscr')

formatter = logging.Formatter(
    fmt='{asctime} [{levelname:^7s}] {msg}',
    datefmt='%m.%d. %Hh',
    style='{'
)

fetch_handler = logging.FileHandler('logs/fetch.log')
subscr_handler = logging.FileHandler('logs/subscriptions.log')

fetch_handler.setFormatter(formatter)
subscr_handler.setFormatter(formatter)

logging.root.setLevel(config['log_level'])

logging.root.addHandler(subscr_handler)
fetch_log.addHandler(fetch_handler)
subscr_log.addHandler(subscr_handler)
