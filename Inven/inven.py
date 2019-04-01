from requests_html import HTMLSession
import os
import time
import csv
import sys
import telegram
import json


def collect_inven_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")

    session = HTMLSession(mock_browser=True)

    for page in range(1, 51):
        r = session.get('http://www.inven.co.kr/search/webzine/article/' + SLANG + '/' + str(page))
        link_list = r.html.find('.news_list > li > h1 > a')
        for link in link_list:
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
                writer = csv.DictWriter(link_file, fieldnames=field_names)
                num_temp = link.attrs['href'].split('/')[-2] + link.attrs['href'].split('/')[-1]
                if num_temp == num:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer.writerow({'num': num_temp,
                                 'link': link.attrs['href']})
        time.sleep(5)

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_inven_document_content(num: str, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    try:
        content = r.html.find('.articleTitle', first=True).text
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'num': num, 'type': 'title', 'content': content})
    except AttributeError:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Failed to get Title")
        return
    ### Post ###
    for text in r.html.find('#powerbbsContent', first=True).text.split('\n'):
        if text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'post', 'content': text})


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python ruliweb.py [Type] [Slang]')
        exit()
    CRAWLER_NAME = "Inven"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\..\\Inven"))

    # Telegram Setting
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "..\\..\\token.json"))
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_contents.csv'

    if TYPE == 'link':
        if os.path.exists(link_file_name) is True:
            os.remove(link_file_name)

        field_names = ['num', 'link']

        if os.path.exists(content_file_name) is True:
            with open(content_file_name, 'r', encoding='utf-8') as content_file:
                reader = csv.reader(content_file)
                next(reader, None)
                try:
                    num = list(reader)[-1][0]
                except ValueError:
                    num = None
                except IndexError:
                    num = None
        else:
            num = None
        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
            writer = csv.DictWriter(link_file, fieldnames=field_names)
            writer.writeheader()
        collect_inven_document_link(num)

    elif TYPE == 'content':
        field_names = ['num', 'type', 'content']

        if os.path.exists(link_file_name) is False:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: FileNotFoundError: No such file!!")
            exit()

        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
                writer = csv.DictWriter(content_file, fieldnames=field_names)
                writer.writeheader()

        with open(link_file_name, 'r', encoding='utf-8') as link_file:
            reader = csv.reader(link_file)
            next(reader, None)
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} content data")
            for row in reversed(list(reader)):
                collect_inven_document_content(row[0], row[1])
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} content data.")
    else:
        print("Context Error. Please retry input")
