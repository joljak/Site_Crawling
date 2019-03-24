from requests_html import HTMLSession
import os
import time
import csv
import sys


def collect_inven_document_link():
    session = HTMLSession(mock_browser=True)
    field_names = ['link']

    if os.path.exists(link_file_name) is False:
        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()

    for page in range(1, 101):
        r = session.get('http://www.inven.co.kr/search/webzine/article/' + SLANG + '/' + str(page))
        link_list = r.html.find('.news_list > li > h1 > a')
        for link in link_list:
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'link': link.attrs['href']})
        time.sleep(3)


def collect_inven_document_content(link: str):
    field_names = ['link', 'content']
    if os.path.exists(content_file_name) is False:
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()

    session = HTMLSession(mock_browser=True)
    r = session.get(link)
    content = r.html.find('.articleTitle', first=True).text

    for p in r.html.find('#powerbbsContent'):
        if p.text != "\n":
            content = content + " " + p.text.replace('\n', ' ')

    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow({'link': link, 'content': content})

    content = ""
    r.html.render()
    time.sleep(4.0)
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        for comment in r.html.find('div.cmtOne > div.comment > span'):
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'link': link, 'content': comment.text.replace('\n', ' ')})


if __name__ == '__main__':
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python ruliweb.py [Type] [Slang]')
        exit()

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_links.csv'
    content_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_contents.csv'

    if TYPE == 'link':
        collect_inven_document_link()

    elif TYPE == 'content':
        if os.path.exists(link_file_name) is False:
            print('FileNotFoundError: No such file!!')
            exit()

        with open(link_file_name, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            for link in reader:
                collect_inven_document_content(link[0])
    else:
        print("Context Error")
