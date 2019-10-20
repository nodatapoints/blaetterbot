from contextlib import contextmanager

from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

from .database import subscribed_users, subscriptions
from . import config

import logging
log = logging.getLogger('bot')

def generate_keyboard(subscriptions):
    keyboard = []
    for lecture_id, lecture in config['mirrors'].items():
        line = lecture['name']
        if lecture_id in subscriptions:
            line += ' ✅'

        keyboard.append(
            InlineKeyboardButton(text=line, callback_data=lecture_id))

    return InlineKeyboardMarkup.from_column(keyboard)


def start_handler(update: Update, context: CallbackContext):
    uid = update.message.from_user.id
    with subscriptions(uid, init_msg_id=update.message.message_id) as subscr:
        kbd = generate_keyboard(subscr)
        update.message.reply_text('Choose', reply_markup=kbd)


def callback_handler(update: Update, context: CallbackContext):
    uid = update.callback_query.message.chat_id
    lecture = update.callback_query.data

    with subscriptions(uid) as subscr:
        subscr ^= {lecture}

    kbd = generate_keyboard(subscr)
    update.callback_query.message.edit_reply_markup(reply_markup=kbd)

