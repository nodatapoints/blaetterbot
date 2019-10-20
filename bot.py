#!/usr/bin/python3.7

from telegram import Bot

from blaetter.fetchers import fetchers
from blaetter.subscription import subscribed_users
from blaetter import config

import logging
log = logging.getLogger('bot')

log.info('Starting ...')

bot = Bot(config['token'])
for mirror in fetchers(config):
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
