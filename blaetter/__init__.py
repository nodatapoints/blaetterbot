import logging

from .utils import config_file


with config_file(readonly=True) as cfg:
    config = cfg

log = logging.getLogger('bot')

formatter = logging.Formatter(
    fmt='{asctime} [{levelname:^7s}] {msg}',
    datefmt='%m.%d. %Hh',
    style='{'
)
handler = logging.FileHandler('bot.log')

handler.setFormatter(formatter)
log.addHandler(handler)

log.setLevel(config['log_level'])

