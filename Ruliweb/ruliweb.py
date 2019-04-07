from requests_html import HTMLSession
import os
import time
import csv
import sys
import json
import telegram


def collect_ruliweb_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")

    session = HTMLSession(mock_browser=True)
    page = 1
    count = 0
    search_pos = ""
    url = 'http://bbs.ruliweb.com/community/board/300143/list?search_type=subject&search_key=' + SLANG + '&page='

    while count < 10:
        time.sleep(3)
        r = session.get(url + str(page) + search_pos)
        notice = len(r.html.find('.table_body.notice'))

        if r.html.find('.empty_result', first=True) is None:
            if page > 15:
                page = 1
                search_pos = r.html.find('.search_more > a', first=True).attrs['href'][-20:]
                count += 1
                continue
            table_body_list = r.html.find('.table_body')
            page += 1
        else:
            page = 1
            search_pos = r.html.find('.search_more > a', first=True).attrs['href'][-20:]
            count += 1
            continue

        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            for table_body in table_body_list[notice:]:
                link = table_body.find('.subject > div > a', first=True).attrs['href']
                if link.split('?')[0][-8:] == num:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer.writerow({'num': link.split('?')[0][-8:], 'link': link})
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_ruliweb_document_content(num: str, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    content = r.html.find('div.board_main_top > div.user_view > div:nth-child(1) > h4 > span', first=True).text[5:]
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
        writer = csv.DictWriter(contnet_file, fieldnames=field_names)
        writer.writerow(
            {'num': num, 'type': 'title', 'content': content.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Post ###
    for p in r.html.find('#board_read > div > div.board_main > div.board_main_view > div.view_content > p'):
        if p.text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
                writer = csv.DictWriter(contnet_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'post', 'content': p.text.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Comment ###
    for comment in r.html.find('.comment_element.normal > td.comment > div.text_wrapper > span.text'):
        if comment.text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
                writer = csv.DictWriter(contnet_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'comment', 'content': comment.text.replace('\n', ' ')})
    time.sleep(4)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('''
               Argument Error
               Choice Type [link, content] and Input Slang
               usage) python ruliweb.py [Type] [Slang]
               usage) exec_crawler.py [Site] [Type]
               ''')

    CRAWLER_NAME = "Ruliweb"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../Ruliweb"))
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "../../token.json"))

    # Telegram Setting
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Ruliweb_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Ruliweb_{SLANG}_content.csv'

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
        try:
            collect_ruliweb_document_link(num)
        except:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")

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
                try:
                    collect_ruliweb_document_content(row[0], row[1])
                except:
                    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} content data.")
    else:
        print("Context Error. Please retry input")
