from requests_html import HTMLSession
from lxml.etree import ParserError
import os
import sys
import time
import csv


def collect_clien_document_link():
    field_names = ['link']
    if os.path.exists(link_file_name) is False:
        with open(link_file_name, 'a', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()

    session = HTMLSession(mock_browser=True)

    for page in range(100):
        r = session.get('https://www.clien.net/service/search?q=' + SLANG + '&sort=recency&p=' + str(
            page) + '&boardCd=&isBoard=false')

        for item in r.html.find('#div_content > div.search_list > div > div.list_title > a'):
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'link': item.attrs['href']})


def collect_clien_document_content(link: str):
    field_names = ['link', 'content']
    if os.path.exists(content_file_name) is False:
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
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
    content = r.html.find('#div_content > div.post_title.symph_row > h3 > span', first=True).text
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'link': link, 'content': content})

    ### Post ###
    content = ""
    for post in r.html.find('#div_content > div.post_view > div.post_content > article > div'):
        content = content + post.text.replace('\n', ' ').replace('  ', ' ')
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'link': link, 'content': content})

    ### Comment ###
    r = session.get(link + '/comment?ps=200')
    try:
        comment_content = r.html.find('.comment_content')
    except ParserError:
        time.sleep(4)
        return
    for comment in comment_content:
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'link': link, 'content': comment.find('.comment_view', first=True).text.replace('\n', ' ')})
    time.sleep(4)


def test():
    link = 'https://www.clien.net/service/board/park/12942470/comment?ps=200'
    session = HTMLSession(mock_browser=True)
    r = session.get(link)
    comment_content = r.html.find('.comment_content')
    for comment in comment_content:
        print(comment.find('.comment_view', first=True).text.replace('\n', ' '))
    #time.sleep(4)


if __name__ == '__main__':
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python clien.py [Type] [Slang]')
        exit()

    TYPE = str(sys.argv[1])
    if TYPE == 'test':
        test()
        exit()
    SLANG = str(sys.argv[2])

    link_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_links.csv'
    content_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_content.csv'

    if TYPE == 'link':
        collect_clien_document_link()

    elif TYPE == 'content':
        if os.path.exists(link_file_name) is False:
            print('FileNotFoundError: No such file!!')
            exit()
        with open(link_file_name, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            for link in reader:
                collect_clien_document_content(link[0])

    else:
        print("Context Error")
