from keras.models import load_model
from telegram.ext import Updater, Dispatcher, MessageHandler, Filters
import os
import json
import re

# Telegram Setting
ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))
TOKEN_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, "token.json"))
with open(os.path.join(TOKEN_FILE)) as token_file:
    TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
updater = Updater(token=TELEGRAM_BOT_TOKEN)

# Preprocessing Setting
hangul = re.compile('[^ .,\u3131-\u3163\uac00-\ud7a3]+')

# Load Model
model = load_model('model_name.h5')
def get_message(bot, update):
    re_content = hangul.sub('', ''.join(update.message.text).strip())
    # 공백 전처리
    re_content = ' '.join(re_content.split())
    # . 전처리
    re_content = '.'.join([x for x in re_content.split('.') if x])
    # , 전처리
    re_content = ','.join([x for x in re_content.split(',') if x])
    # " 전처리
    re_content = re_content.replace('\"', '')
    
    # Predict  모델 완성 후 주석 해제, reply_text(pred) 입력
    # pred  = model.predict_classes(re_content)
    update.message.reply_text(re_content)

message_handler = MessageHandler(Filters.text, get_message)
updater.dispatcher.add_handler(message_handler)

updater.start_polling(timeout=3, clean=True)
updater.idle()

