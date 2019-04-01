from requests_html import HTMLSession
import os
import time
import csv
import sys
import telegram
import json


def collect_inven_document_link(idx: int):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")
    session = HTMLSession(mock_browser=True)

    if os.path.exists(link_file_name) is False:
        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()

    for page in range(1, 51):
        r = session.get('http://www.inven.co.kr/search/webzine/article/' + SLANG + '/' + str(page))
        link_list = r.html.find('.news_list > li > h1 > a')
        for link in link_list:
            idx = idx + 1
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'idx': idx, 'link': link.attrs['href']})
        time.sleep(5.0)
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")

def collect_inven_document_content(idx: int, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    try:
        content = r.html.find('.articleTitle', first=True).text
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'idx': idx, 'link': link, 'type': 'title', 'content': content})
    except AttributeError:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Failed to get Title")
        return

    ### Post ###
    content = ""
    for p in r.html.find('#powerbbsContent'):
        if p.text != "\n":
            content = content + " " + p.text.replace('\n', ' ')
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'idx': idx, 'link': link, 'type': 'post', 'content': content})

    # r.html.render(sleep=4, timeout=32)
    # ### Comment ###
    #
    # with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
    #     comments = r.html.find('div.cmtOne > div.comment > span')
    #
    #     for comment in comments:
    #         writer = csv.DictWriter(csv_file, fieldnames=field_names)
    #         writer.writerow({'idx': idx, 'link': link, 'type': 'comment','content': comment.text.replace('\n', ' ')})


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python ruliweb.py [Type] [Slang]')
        exit()
    CRAWLER_NAME = "InvenCrawler"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\..\\datafile"))
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "..\\..\\token.json"))
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])

    link_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_links.csv'
    content_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_contents.csv'

    if TYPE == 'link':
        field_names = ['idx', 'link']
        if os.path.exists(link_file_name) is False:
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writeheader()
            idx = 0
        else:
            with open(link_file_name, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)
                try:
                    idx = int(list(reader)[-1][0])
                except ValueError:
                    idx = 0
                except IndexError:
                    idx = 0
        collect_inven_document_link(idx)

    elif TYPE == 'content':
        field_names = ['idx', 'link', 'type', 'content']
        if os.path.exists(link_file_name) is False:
            print('FileNotFoundError: No such file!!')
            exit()
        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writeheader()
                idx = 0
        else:
            with open(content_file_name, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)
                try:
                    idx = int(list(reader)[-1][0])
                except IndexError:
                    idx = 0
                except ValueError:
                    idx = 0

        with open(link_file_name, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} content data")
            for row in reader:
                if idx == int(row[0]) - 1:
                    collect_inven_document_content(row[0], row[1])
                    idx += 1
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Sucessfully collected {SLANG} content data")
    else:
        print("Context Error")
