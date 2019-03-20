from requests_html import HTMLSession
import os
import time
import csv
import sys

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
SLANG = str(sys.argv[1])
FILE_NAME = FILE_DIRECTORY + f'/Ruli_{SLANG}.csv'
BOARD_LIST = {'300143': '정치유머', '300148': '유머'}  # 300143 유머게시판 , 300148 정치게시판



def crawling(board:str):
    page =1
    count = 0
    SESSION = HTMLSession(mock_browser=True)
    search_pos = ""
    url = 'http://bbs.ruliweb.com/community/board/' + board + '/list?search_type=subject&search_key=' + SLANG + '&page='

    while(count< 5):
        time.sleep(5)
        r = SESSION.get(url + str(page) + search_pos)
        empty = True if r.html.find('.empty_result') else False
        notice = len(r.html.find('.table_body.notice'))
        table_body_list = r.html.find('.table_body')
        if empty is True:
            page = 1
            search_pos = r.html.find('.search_more > a', first=True).attrs['href'][-20:]
            r = SESSION.get(url + str(page) + search_pos)
            table_body_list = r.html.find('.table_body')
            count = count + 1
        for table_body in table_body_list[notice:]:
            subject = table_body.find('.subject > div > a', first=True)
            link = subject.attrs['href']
            title = subject.text.replace('뿅뿅', SLANG)
            nickname = table_body.find('.writer.text_over > a', first=True).text
            with open(FILE_NAME, 'a', encoding='utf-8', newline='\n') as data_csv:
                csv.writer(data_csv).writerow([link, nickname, title])
        page = page + 1


for BOARD in BOARD_LIST:
    crawling(BOARD)


