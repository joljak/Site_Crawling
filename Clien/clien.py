from requests_html import HTMLSession
from lxml.etree import ParserError

import os
import sys
import time
import csv
import json
import telegram


def collect_clien_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")
    session = HTMLSession(mock_browser=True)
    print("link function 1")
    for page in range(100):
        r = session.get('https://www.clien.net/service/search?q=' + SLANG + '&sort=recency&p=' + str(
            page) + '&boardCd=&isBoard=false')
        print(r.html.html)
        for item in r.html.find(
                '#div_content > div.contents_jirum > div.list_item.symph_row.jirum > .list_title.oneline > .list_subject > a'):
            print(item)
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
                if item.attrs['href'].split('?')[0][-8:] == num:
                    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer = csv.DictWriter(link_file, fieldnames=field_names)
                writer.writerow(({'num': item.attrs['href'].split('?')[0][-8:], 'link': 'https://www.clien.net' + item.attrs['href']}))
        time.sleep(3)
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_clien_document_content(num: str, link: str):

    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Exception ###
    # 404 Error
    if r.html.find('#div_content > .content_serviceError', first=True) is not None:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: 404 Error, {link}")
        return
    # Login Error
    if r.html.find('.content_signin', first=True) is not None:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Need to login, {link}")
        return

    ### Title ###
    try:
        content = r.html.find('#div_content > div.post_title.symph_row > h3 > span', first=True).text
    except AttributeError as e:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: {e}")
        return
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
        writer = csv.DictWriter(content_file, fieldnames=field_names)
        writer.writerow({'num': num, 'type': 'title', 'content': content})

    ### Post ###
    for p in r.html.find('.content_view > div.post_view > div.post_content > article > div', first=True).find('p'):
        if p.text == '':
            continue
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
            writer = csv.DictWriter(content_file, fieldnames=field_names)
            writer.writerow({'num': num, 'type': 'post', 'content': p.text.replace('\n',' ')})

    ### Comment ###
    r = session.get(link.split('?')[0] + '/comment?ps=200')
    try:
        comment_content = r.html.find('.comment_content')
    except ParserError:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: No Comment")
        time.sleep(3)
        return
    for comment in comment_content:
        if comment.find('.comment_view', first=True).text == '':
            continue
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
            writer = csv.DictWriter(content_file, fieldnames=field_names)
            writer.writerow(
                {'num': num, 'type': 'comment', 'content': comment.find('.comment_view', first=True).text.replace('\n', '')})
    time.sleep(3)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python clien.py [Type] [Slang]')
        exit()

    CRAWLER_NAME = "Clien"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../Clien"))
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "../../token.json"))

    # Telegram Setting
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_content.csv'

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
        collect_clien_document_link(num)

    elif TYPE == 'content':
        field_names = ['num', 'type', 'content']
        if os.path.exists(link_file_name) is False:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: FileNotFoundError: No such file!")
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
                collect_clien_document_content(row[0], row[1])
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Sucessfully collected {SLANG} content data")
    else:
        print("Context Error. Please retry input")
