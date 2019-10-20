#!/usr/bin/python3.7

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('bot')

formatter = logging.Formatter(
    fmt='{asctime} [{levelname:^7s}] {msg}',
    datefmt='%m.%d. %Hh',
    style='{'
)
handler = RotatingFileHandler(
    'bot.log',
    maxBytes=10240,
    backupCount=9
)

handler.setFormatter(formatter)
logger.addHandler(handler)

from utils import config_file
from fetchers import fetchers
from telegram import Bot

logger.info('Starting ...')

with config_file('config.yaml') as config_data:
    logger.setLevel(config_data['log_level'])

    bot = Bot(config_data['token'])
    for mirror in fetchers(config_data):
        pdf = mirror.fetch()
        if not pdf:
            logger.debug('skipping')
            continue

        bot.send_document(
            chat_id=config_data['channel'],
            document=mirror.process_pdf(pdf),
            filename=mirror.filename
        )

        logger.info(f'uploaded {mirror.filename}')

        mirror.n += 1
