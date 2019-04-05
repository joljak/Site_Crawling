import json
import os
import csv
import telegram
import re
import sys


def preprocessing(origin_path: str, processed_path: str):
    if os.path.exists(origin_path) is False:
        exit("No Such File!!")
    field_name = ['num', 'type', 'content']
    if os.path.exists(processed_path) is False:
        with open(processed_path, 'w', encoding='utf-8', newline='\n') as processed_file:
            writer = csv.DictWriter(processed_file, fieldnames=field_name)
            writer.writeheader()
    with open(origin_path, 'r', encoding='utf-8', newline='\n') as origin_file:
        reader = csv.reader(origin_file)
        next(reader, None)
        for field in list(reader):
            re_content = re.sub('[,-=+#@!$%^&*()_~><…\[\]:;`\'\"/?\d]', '', ''.join(field[2:]))
            with open(processed_path, 'a', encoding='utf-8', newline='\n') as processed_file:
                writer = csv.DictWriter(processed_file, fieldnames=field_name)
                writer.writerow({'num': field[0], 'type': field[1], 'content': re_content})


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))

    SITE = ['Inven', 'Clien', 'Ruliweb']
    # Telegram Setting
    TOKEN_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, "token.json"))
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    # Keyword Setting
    SLANG_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, 'slang.json'))
    with open(SLANG_FILE, 'r', encoding='utf-8') as slang_file:
        KEYWORD = json.load(slang_file)['unordered']

    for site in SITE:
        for keyword in KEYWORD:
            file_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{keyword}_content.csv'))
            processed_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{keyword}_processed.csv'))
            preprocessing(file_path, processed_path)
