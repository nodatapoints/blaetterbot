from contextlib import contextmanager

from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
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

def start_message(update, uid: int, subscriptions=set()):
    kbd = generate_keyboard(subscriptions)
    reply = update.message.reply_text(
        initial_text,
        reply_markup=kbd,
        parse_mode='Markdown'
    )
    update.message.delete()
    return reply

def start_handler(update: Update, context: CallbackContext):
    uid = update.message.from_user.id
    log.info(f'got start from uid={uid}')

    init_msg = previous_start_message(uid)
    new_user = init_msg is None

    if not new_user:
        log.debug(f'Got duplicate /start from uid={uid}')
        try:
            context.bot.delete_message(uid, init_msg)

        except BadRequest:
            log.warning(f'Could not delete init msg for uid={uid}')
            try:
                context.bot.edit_message_text(
                    chat_id=uid,
                    message_id=init_msg,
                    text='[deleted]')

            except BadRequest:
                log.warning(f'Could not edit init msg for uid={uid}')

        with subscriptions(uid) as subscr:
            init_msg = start_message(update, uid, subscr)
            log.debug(f'init message for {uid} reset to {init_msg.message_id}')
            update_init_msg(uid, init_msg.message_id)

    else:
        init_msg = start_message(update, uid)
        log.info(f'Added uid={uid}')
        insert_new_user(uid, init_msg.message_id)

def callback_handler(update: Update, context: CallbackContext):
    uid = update.callback_query.message.chat_id
    lecture = update.callback_query.data

    with subscriptions(uid) as subscr:
        subscr ^= {lecture}
        log.debug(f'changed lectures to {subscr} for uid={uid}')

    kbd = generate_keyboard(subscr)
    update.callback_query.message.edit_reply_markup(reply_markup=kbd)
