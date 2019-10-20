#!/usr/bin/python3.7

from telegram import Bot

from blaetter.utils import config_file
from blaetter.fetchers import fetchers
from blaetter.subscription import subscribed_users

import logging
log = logging.getLogger('bot')

log.info('Starting ...')

with config_file() as config_data:
    bot = Bot(config_data['token'])
    for mirror in fetchers(config_data):
        pdf = mirror.fetch()
        if not pdf:
            log.debug('skipping')
            continue

        for uid in subscribed_users(mirror.lecture_id):
            bot.send_document(
                chat_id=uid,
                document=mirror.process_pdf(pdf),
                filename=mirror.filename
            )

        log.info(f'uploaded {mirror.filename}')

        mirror.n += 1
