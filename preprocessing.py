import json
import os
import csv
import telegram
import re
import sys


#csv.field_size_limit(sys.maxsize) # for linux
hangul = re.compile('[^ .,\u3131-\u3163\uac00-\ud7a3]+')


def preprocessing(origin_path: str, processed_path: str):
    if os.path.exists(origin_path) is False:
        return f'{origin_path}: Error. Not exists file'
    field_name = ['content', 'label']
    if os.path.exists(processed_path) is False:
        with open(processed_path, 'w', encoding='utf-8', newline='\n') as processed_file:
            writer = csv.DictWriter(processed_file, fieldnames=field_name)
            writer.writeheader()
    with open(origin_path, 'r', encoding='utf-8', newline='\n') as origin_file:
        reader = csv.reader(origin_file, quotechar='\"')
        next(reader, None)
        for field in list(reader):
            # 한글 전처리
            re_content = hangul.sub('', ''.join(field[2:])).strip()
            # 공백 전처리
            re_content = ' '.join(re_content.split())
            # . 전처리
            re_content = '.'.join([x for x in re_content.split('.') if x])
            # , 전처리
            re_content = ','.join([x for x in re_content.split(',') if x])
            # " 전처리
            re_content = re_content.replace('\"', '')
            if re_content != "":
                with open(processed_path, 'a', encoding='utf-8', newline='\n') as processed_file:
                   writer = csv.DictWriter(
                       processed_file, fieldnames=field_name)
                   writer.writerow({'content': re_content, 'label': None})


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))

    # Telegram Setting
    # TOKEN_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, "token.json"))
    # with open(os.path.join(TOKEN_FILE)) as token_file:
    #     TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    # bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    # CHAT_ID = 620483333

    # Keyword Setting
    SLANG_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, 'slang.json'))
    with open(SLANG_FILE, 'r', encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']

    if len(sys.argv) < 2:
        exit('''
                Argument Error
                Choice Site [clien, dc_inside, dog_drip, fm_korea, ilbe, inven, ppompu, ruliweb]
                usage) python preprocessing.py [Site] [Slang]
            ''')
    site = sys.argv[1] if sys.argv[1] in ['clien', 'dc_inside', 'dog_drip', 'fm_korea', 'ilbe',
                                          'inven', 'ppompu', 'ruliweb'] else exit("Please. Retry input site [clien, dc_inside, dog_drip, fm_korea, ilbe, inven, ppompu, ruliweb].")
    idx = SLANG.index(sys.argv[2]) if len(
        sys.argv) == 3 and sys.argv[2] in SLANG else 0

    #bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Start Preprocessing')
    for slang in SLANG[idx:]:
        file_path = '/'.join([ROOT_DIRECTORY, site,
                              'contents', f'{site}_{slang}_contents.csv'])
        processed_path = '/'.join([ROOT_DIRECTORY, site,
                                   'processed', f'{site}_{slang}_processed.csv'])
        preprocessing(file_path, processed_path)

    #bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Compleated to preprocessing')
