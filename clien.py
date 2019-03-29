from requests_html import HTMLSession
from lxml.etree import ParserError
import os
import sys
import time
import csv


def collect_clien_document_link(idx: int):
    session = HTMLSession(mock_browser=True)
    for page in range(100):
        r = session.get('https://www.clien.net/service/search?q=' + SLANG + '&sort=recency&p=' + str(
            page) + '&boardCd=&isBoard=false')
        for item in r.html.find(
                '#div_content > div.contents_jirum > div.list_item.symph_row.jirum > .list_title.oneline > .list_subject > a'):
            idx = idx + 1
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'idx': idx, 'link': 'https://www.clien.net' + item.attrs['href']})


def collect_clien_document_content(idx: int, link: str):
    field_names = ['idx', 'link', 'type', 'content']
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Exception ###
    # 404 Error
    if r.html.find('#div_content > .content_serviceError', first=True) is not None:
        return
    # Login Error
    if r.html.find('.content_signin', first=True) is not None:
        return

    ### Title ###
    try:
        content = r.html.find('#div_content > div.post_title.symph_row > h3 > span', first=True).text
    except AttributeError:
        print(link)
        return
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'idx': idx, 'link': link, 'type': 'post', 'content': content})

    ### Post ###
    content = ""
    for post in r.html.find('#div_content > div.post_view > div.post_content > article > div'):
        content = content + post.text.replace('\n', ' ').replace('  ', ' ')
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'idx': idx, 'link': link, 'type': 'post', 'content': content})

    ### Comment ###
    r = session.get(link.split('?')[0] + '/comment?ps=200')
    try:
        comment_content = r.html.find('.comment_content')
    except ParserError:
        time.sleep(3)
        return
    for comment in comment_content:
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow(
                {'idx': idx, 'link': link, 'type': 'comment',
                 'content': comment.find('.comment_view', first=True).text.replace('\n', ' ')})
    time.sleep(3)


if __name__ == '__main__':
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python clien.py [Type] [Slang]')
        exit()

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])

    link_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_links.csv'
    content_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_content.csv'

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
        collect_clien_document_link(idx)

    elif TYPE == 'content':
        if os.path.exists(link_file_name) is False:
            print('FileNotFoundError: No such file!!')
            exit()
        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['idx', 'link', 'type', 'content'])
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
            for row in reader:
                if idx == int(row[0]) - 1:
                    collect_clien_document_content(row[0], row[1])
                    idx += 1
    else:
        print("Context Error")
