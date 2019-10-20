from contextlib import contextmanager
from pathlib import Path
from typing import Union

from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

from . import config

import logging
logger = logging.getLogger('bot')

subscribers_dir = Path('subscribers')


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
    uid = str(update.message.from_user.id)
    with subscription_file(uid, readonly=True) as subscriptions:
        kbd = generate_keyboard(subscriptions)
        update.message.reply_text('Choose', reply_markup=kbd)


def callback_handler(update: Update, context: CallbackContext):
    uid = str(update.callback_query.message.chat_id)
    lecture_id = update.callback_query.data

    with subscription_file(uid) as subscriptions:
        subscriptions ^= {lecture_id}

        kbd = generate_keyboard(subscriptions)
        update.callback_query.message.edit_reply_markup(reply_markup=kbd)

@contextmanager
def subscription_file(uid: Union[str, Path], readonly=False):
    if isinstance(uid, str):
        user_file = subscribers_dir / uid

    if not user_file.exists():
        user_file.touch()
        logger.debug(f'Created {user_file.as_posix()}')

    fobj = user_file.open('r' if readonly else 'r+')

    try:
        subscriptions = set(map(str.strip, fobj.readlines()))

        yield subscriptions

        if not readonly:
            fobj.seek(0)
            fobj.write('\n'.join(subscriptions))
            fobj.truncate()

    finally:
        fobj.close()
