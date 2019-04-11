import json
import os
import csv
import telegram
import sys

csv.field_size_limit(sys.maxsize)


def labeling(processed_path, labeled_path):
    if os.path.exists(processed_path) is False:
        exit(f'{processed_path}: Error. Not exists file')
    field_name = ['num', 'type', 'content', 'label']

    if os.path.exists(labeled_path) is False:
        with open(labeled_path, 'w', encoding='utf-8', newline='\n') as labeled_file:
            writer = csv.DictWriter(labeled_file, fieldnames=field_name)
            writer.writeheader()

    with open(processed_path, 'r', encoding='utf-8', newline='\n') as processed_file:
        reader = csv.reader(processed_file)
        next(reader, None)
        for field in list(reader):
            label = 1 if field[2].find(slang) != -1 else None
            with open(labeled_path, 'a', encoding='utf-8', newline='\n') as labeled_file:
                writer = csv.DictWriter(labeled_file, fieldnames=field_name)
                writer.writerow({'num': field[0], 'type': field[1], 'content': field[2], 'label': label})


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
    if len(sys.argv) <2:
        exit('''
                Argument Error
                Choice Site [Clien, Inven, Ruliweb
                Choice Type [link, content]
                usage) exec_crawler.py [Site] [Type]
                ''')
    site = sys.argv[1] if sys.argv[1] in ['Inven', 'Clien', 'Ruliweb'] else exit(
        "Please. Retry input site:['Inven', 'Clien', 'Ruliweb'].")
    idx = SLANG.index(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[2] in SLANG else 0

    bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Start to labeling')
    for slang in SLANG[idx:]:
        processed_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{slang}_processed.csv'))
        labeled_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, site, f'{site}_{slang}_labeled.csv'))
        labeling(processed_path, labeled_path)

    bot.sendMessage(chat_id=CHAT_ID, text=f'{site}: Completed to labeling')
