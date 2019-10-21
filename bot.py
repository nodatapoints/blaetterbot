#!/usr/bin/python3.7

from telegram import Bot

from blaetter.fetchers import fetchers
from blaetter.subscription import subscribed_users
from blaetter.database import subscribed_users
from blaetter import config

import logging
log = logging.getLogger('bot')

log.info('Starting ...')

bot = Bot(config['token'])
for mirror in fetchers(config):
    try:
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

        mirror.increment()
        log.info(f'uploaded {mirror.filename}')

    except Exception as e:
        log.exception(f'failed {mirror.lecture_id}')
