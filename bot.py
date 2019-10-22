#!/usr/bin/python3.7

from itertools import chain

from telegram import Bot

from blaetter.fetchers import fetchers
from blaetter.subscription import subscribed_users
from blaetter.database import subscribed_users
from blaetter import config

import logging
log = logging.getLogger('fetch')

log.info('Starting ...')

bot = Bot(config['token'])
for mirror in fetchers(config):
    try:
        pdf = mirror.fetch()
        if not pdf:
            log.debug('skipping')
            continue

        chats = chain((config['channel'],),
            subscribed_users(mirror.lecture_id))

        doc = mirror.process_pdf(pdf)
        for chat in chats:
            bot.send_document(
                chat_id=chat,
                document=doc,
                filename=mirror.filename
            )
            doc.seek(0)  # to read the file again

        mirror.increment()
        log.info(f'uploaded {mirror.filename}')

    except Exception as e:
        log.exception(f'failed {mirror.lecture_id}')
