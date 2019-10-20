import logging

import yaml

with open('config.yaml') as fobj:
    config = yaml.full_load(fobj)

log = logging.getLogger('bot')
logging.basicConfig(level=logging.INFO)

formatter = logging.Formatter(
    fmt='{asctime} [{levelname:^7s}] {msg}',
    datefmt='%m.%d. %Hh',
    style='{'
)
handler = logging.FileHandler('bot.log')

handler.setFormatter(formatter)
log.addHandler(handler)

log.setLevel(config['log_level'])

