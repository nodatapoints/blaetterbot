from contextlib import contextmanager

from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest

from .database import subscribed_users, subscriptions, \
    previous_start_message, insert_new_user, update_init_msg
from . import config

import logging
log = logging.getLogger('subscr')

initial_text = """\
```
==================
 _             
|_)|._._|__|_ _  _ 
|_)|(_| |_ |_(/_| 
  weniger Krampf
      v1.1
==================
```
Wähle deine Vorlesungen aus und erhalte alle neuen Übungsblätter.

_Deine Vorlesung nicht dabei? Schreib mich an (@nodatapoints)_
"""

def generate_keyboard(subscriptions=set()):
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
    init_msg = previous_start_message(uid)
    new_user = init_msg is None

    if not new_user:
        try:
            update.message.reply_text(
                text='Bitte nutze die Start-Nachricht. ☝️',
                reply_to_message_id=init_msg)

        # When the user is already in the database but deleted
        # the initial message
        except BadRequest:
            with subscriptions(uid) as subscr:
                # FIXME duplicated code
                kbd = generate_keyboard(subscr)
                init_msg = update.message.reply_text(
                    initial_text,
                    reply_markup=kbd,
                    parse_mode='Markdown'
                )
                update_init_msg(uid, init_msg.message_id)

    else:
        kbd = generate_keyboard()
        init_msg = update.message.reply_text(
            initial_text,
            reply_markup=kbd,
            parse_mode='Markdown'
        )
        insert_new_user(uid, init_msg.message_id)


def callback_handler(update: Update, context: CallbackContext):
    uid = update.callback_query.message.chat_id
    lecture = update.callback_query.data

    with subscriptions(uid) as subscr:
        subscr ^= {lecture}

    kbd = generate_keyboard(subscr)
    update.callback_query.message.edit_reply_markup(reply_markup=kbd)

