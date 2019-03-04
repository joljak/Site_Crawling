import csv
import datetime
import json
import os
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


def collect_fm_korea():
    session = HTMLSession(mock_browser=True)

    with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
        # Open slang.json to read slang words
        keyword = json.load(slang_file)

    print(keyword['slang'])


def collect_fm_korea_document_link():
    """
    FM 코리아 통합검색 크롤링
    :param page:
    :return:
    """

    page = 10
    keyword = '시발'

    # make csv file to save document link
    file_name = f'{TODAY_DATE}_FM_korea_{keyword}.csv'
    open(file_name, 'a').close()

    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    for i in range(page):
        # search link and text result via keyword
        time.sleep(4)
        fm_korea_docs = session.get(f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={i}')
        result_list = fm_korea_docs.html.find('#content > div > ul.searchResult > li > dl > dt > a')

        result_links = list(result.absolute_links.pop() for result in result_list)
        with open(file_name, 'a') as link_csv:
            link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
            link_writer.writerow(result_links)


def collect_fm_korea_comment(page):
    """
    FM 코리아 통합검색 크롤링
    :param page:
    :return:
    """

# collect_fm_korea()

collect_fm_korea_document_link()
