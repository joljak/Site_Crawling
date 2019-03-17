import csv
import datetime
import json
import logging
import os
import re
import sys
import time

from requests_html import HTMLSession

# FM Korea
# 문서
# https://www.fmkorea.com/index.php?act=IS&is_keyword={}&mid=home&where=document&page=1
# 댓글
# https://www.fmkorea.com/index.php?act=IS&is_keyword={}&mid=home&where=comment&page=1

# Ilbe
# http://www.ilbe.com/?act=IS&where=document&is_keyword={}

# Dogdrip
# https://www.dogdrip.net/

# lower directory to read slang.json
FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))
TODAY_DATE = datetime.date.today().isoformat()


def collect_fm_korea_document_link(keyword):
    """
    FM 코리아 통합검색 크롤링
    :param page:
    :return:
    """
    keyword='시발'

    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    # Check page for each keyword
    pages_text = session.get(
        f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page=0').html.find(
        '#content > div > h3 > span')[0]
    result_pages = int(re.sub("[^0-9]", "", pages_text.text))
    pages = result_pages if result_pages < 1000 else 1000
    print(f'Crawling page: {pages}')

    # Make csv file to save document link
    file_name = f'{TODAY_DATE}_FM_korea_{keyword}.csv'
    if os.path.exists(file_name):
        # remove file if exists and make over
        os.remove(file_name)
        open(file_name, 'a').close()

    elif os.path.exists(file_name) is False:
        open(file_name, 'a').close()

    for i in range(pages):
        # Search link and text result via keyword
        time.sleep(4)
        fm_korea_docs = session.get(
            f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={i+1}')
        result_list = fm_korea_docs.html.find('#content > div > ul.searchResult > li > dl > dt > a')

        result_links = list(result.absolute_links.pop() for result in result_list)

        with open(file_name, 'a') as link_csv:
            link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
            if len(result_links) == 0:
                # if no result
                print(f'page_{i+1}: {len(result_links)} failed')
                continue
            else:
                link_writer.writerow(result_links)
                print(f'page_{i+1}: {len(result_links)} complete')


def collect_fm_korea_document_content(page):
    """
    FM 코리아 통합검색 크롤링
    :param page:
    :return:
    """


if __name__ == '__main__':
    mylogger = logging.StreamHandler()

    if len(sys.argv) < 2:
        print('usage: python fm_korea.py link')
        exit()

    content_type = sys.argv[1]
    # TODO: check page_number as integer

    print(sys.argv[1])

    with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
        # Open slang.json to read slang words
        KEYWORD = json.load(slang_file)

    if content_type == 'link':
        collect_fm_korea_document_link('f')
    elif content_type == 'content':
        collect_fm_korea_document_content('f')
