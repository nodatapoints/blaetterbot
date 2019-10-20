#!/usr/bin/python3.7

from telegram import Bot

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

from blaetter.utils import config_file
from blaetter.fetchers import fetchers
from blaetter.subscription import subscribed_users

logger.info('Starting ...')

with config_file() as config_data:
    logger.setLevel(config_data['log_level'])

    bot = Bot(config_data['token'])
    for mirror in fetchers(config_data):
        pdf = mirror.fetch()
        if not pdf:
            logger.debug('skipping')
            continue

        for uid in subscribed_users(mirror.lecture_id):
            bot.send_document(
                chat_id=uid,
                document=mirror.process_pdf(pdf),
                filename=mirror.filename
            )

        logger.info(f'uploaded {mirror.filename}')

        mirror.n += 1
