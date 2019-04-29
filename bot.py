#!/usr/bin/python3.7

from utils import fetchers, config
from telegram import Bot

with config('config.yaml') as config_data:
    bot = Bot(config_data['token'])
    for mirror in fetchers(config_data):
        pdf = mirror.fetch()
        if not pdf:
            continue

        bot.send_document(
            chat_id=config_data['channel'],
            document=mirror.process_pdf(pdf),
            filename=mirror.filename
        )

        mirror.n += 1
