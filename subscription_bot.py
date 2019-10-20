#!/usr/bin/python3.7

from telegram.ext import CallbackQueryHandler, CommandHandler, Updater

from blaetter.subscription import start_handler, callback_handler
from blaetter import config

updater = Updater(config['token'], use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start_handler))
updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

updater.start_polling()
updater.idle()
