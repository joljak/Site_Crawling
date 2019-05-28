
from telegram.ext import Updater, MessageHandler, Filters
import os
import json
import re
import requests


# Telegram Setting
ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))
TOKEN_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, "token.json"))
with open(TOKEN_FILE) as token_file:
    TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
updater = Updater(token=TELEGRAM_BOT_TOKEN)

def get_message(bot, update):
    text = update.message.text
    res = requests.get('http://manuscript.roamgom.net', params= {'text': text})
    pred = res.json()['result']
    if(pred > 0.75):
        update.message.reply_text("거 참 말 좀 이쁘게 합시다.")
    else:
        update.message.reply_text(text)

message_handler = MessageHandler(Filters.text, get_message)
updater.dispatcher.add_handler(message_handler)
updater.start_polling(timeout=3, clean=True)
updater.idle()

