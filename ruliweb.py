from requests_html import HTMLSession
import os
import time
import csv
import sys


def collect_ruliweb_document_link(idx: int, board: str):
    session = HTMLSession(mock_browser=True)
    page = 1
    count = 0
    search_pos = ""
    url = 'http://bbs.ruliweb.com/community/board/' + board + '/list?search_type=subject&search_key=' + SLANG + '&page='

    while count < 50:
        time.sleep(3)
        r = session.get(url + str(page) + search_pos)
        notice = len(r.html.find('.table_body.notice'))

        if r.html.find('.empty_result', first=True) is None:
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
                idx += 1
                link = table_body.find('.subject > div > a', first=True).attrs['href']
                writer.writerow({'idx': idx, 'link': link})
    return idx


def collect_ruliweb_document_content(idx: int, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    content = r.html.find('div.board_main_top > div.user_view > div:nth-child(1) > h4 > span', first=True).text[5:]
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow(
            {'idx': idx, 'link': link, 'type': 'title', 'content': content.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Post ###
    content = ""
    for p in r.html.find('#board_read > div > div.board_main > div.board_main_view > div.view_content > p'):
        content = content + p.text
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writerow(
            {'idx': idx, 'link': link, 'type': 'post', 'content': content.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Comment ###
    for comment in r.html.find('.comment_element.normal > td.comment > div.text_wrapper > span.text'):
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'idx': idx, 'link': link, 'type': 'comment', 'content': comment.text.replace('\n', ' ')})
    time.sleep(4)


if __name__ == '__main__':
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python ruliweb.py [Type] [Slang]')
        exit()

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])

    BOARD_LIST = {'300148': '유머', '300143': '정치유머'}  # 300143 유머게시판 , 300148 정치게시판
    link_file_name = FILE_DIRECTORY + f'/Ruli_{SLANG}_links.csv'
    content_file_name = FILE_DIRECTORY + f'/Ruli_{SLANG}_contents.csv'

    if TYPE == 'link':
        field_names = ['idx', 'link']
        if os.path.exists(link_file_name) is False:
            with open(link_file_name, 'a', newline='\n', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writeheader()
            idx = 0
        else:
            with open(link_file_name, 'r', encoding='utf=8', newline='\n') as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)
                try:
                    idx = int(list(reader)[-1][0])
                except ValueError:
                    idx = 0

        for BOARD in BOARD_LIST:
            idx = collect_ruliweb_document_link(idx, BOARD)

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
            for row in reader:
                if idx == int(row[0]) - 1:
                    collect_ruliweb_document_content(row[0], row[1])
                    idx += 1
    else:
        print("Context Error")
