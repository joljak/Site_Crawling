import json
import os
import csv
import telegram
import re
import sys


csv.field_size_limit(sys.maxsize) # for linux
hangul = re.compile('[^ .,\u3131-\u3163\uac00-\ud7a3]+')

def preprocessing(origin_path: str, processed_path: str):
    if os.path.exists(origin_path) is False:
        return f'{origin_path}: Error. Not exists file'
    field_name = ['num', 'type', 'content']
    if os.path.exists(processed_path) is False:
        with open(processed_path, 'w', encoding='utf-8', newline='\n') as processed_file:
            writer = csv.DictWriter(processed_file, fieldnames=field_name)
            writer.writeheader()
    with open(origin_path, 'r', encoding='utf-8', newline='\n') as origin_file:
        reader = csv.reader(origin_file)
        next(reader, None)
        for field in list(reader):
            re_content = hangul.sub('',''.join(field[2:])).strip()
            if re_content !="":
                with open(processed_path, 'a', encoding='utf-8', newline='\n') as processed_file:
                   writer = csv.DictWriter(processed_file, fieldnames=field_name)
                   writer.writerow({'num': field[0], 'type': field[1], 'content': re_content})


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))

    # Telegram Setting
    TOKEN_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, "token.json"))
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    # Keyword Setting
    SLANG_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, 'slang.json'))
    with open(SLANG_FILE, 'r', encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']
    
    if len(sys.argv) < 2:
        exit('''
                Argument Error
                Choice Site [Clien, Inven, Ruliweb]
                Choice Type [link, content]
                usage) exec_crawler.py [Site] [Type]
            ''')
    site = sys.argv[1] if sys.argv[1] in ['Inven', 'Clien', 'Ruliweb'] else exit("Please. Retry input site:['Inven', 'Clien', 'Ruliweb'].")
    idx = SLANG.index(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[2] in SLANG else 0

    bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Start Preprocessing')
    for slang in SLANG[idx:]:
        file_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{slang}_content.csv'))
        processed_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{slang}_processed.csv'))
        preprocessing(file_path, processed_path)

    bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Compleated to preprocessing')
