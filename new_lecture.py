#!/usr/bin/python3.7

from telegram import Bot
import sys

from blaetter.database import all_start_messages, subscriptions
from blaetter.subscription import generate_keyboard
from blaetter import config

bot = Bot(config['token'])

update_message = sys.argv[1]

for uid, message_id in all_start_messages():
    with subscriptions(uid) as subscr:
        pass

    kbd = generate_keyboard(subscr)
    bot.edit_message_reply_markup(
        chat_id=uid,
        message_id=message_id,
        reply_markup=kbd)

    bot.send_message(
        chat_id=uid,
        text=update_message,
        reply_to_message_id=message_id)
