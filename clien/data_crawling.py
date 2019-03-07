import csv
import datetime
import os
import time

from requests_html import HTMLSession
from lxml.etree import ParserError

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../datafile"))
TODAY_DATE = datetime.date.today().isoformat()
file_name = FILE_DIRECTORY + f'/{TODAY_DATE}_Clien_Data.csv'
group = ['community', 'allinfo', 'allreview', 'allsell']
link_list = []
session = HTMLSession(mock_browser=True)


def data_crawling(url: str):
    # POST
    r = session.get("https://www.clien.net" + url)
    post_nickname = r.html.find('.nickname', first=True)
    img = post_nickname.find('img', first=True)
    if img is not None:
        nickname = img.attrs['alt']
    else:
        nickname = post_nickname.text
    post_p = r.html.find('.post_content', first=True).find('p')
    for i in post_p:
        if i.text != "":
            with open(file_name, 'a', encoding='utf-8', newline='\n') as link_csv:
                csv.writer(link_csv).writerow(["https://www.clien.net" + url, "post", nickname, i.text])

    # COMMENT
    r = session.get("https://www.clien.net" + url.split("?")[0] + "/comment?ps=1000")

    try:
        comment_row = r.html.find('.comment_row')
    except ParserError:
        return

    for comment in comment_row:
        # except '삭제되었습니다.'
        if comment.find('.blocked', first=True) is not None:
            continue
        nickname = comment.find('.nickname', first=True)
        img = nickname.find('img', first=True)
        if img is not None:
            nickname = img.attrs['alt']
        else:
            nickname = nickname.text

        comment_view = comment.find('.comment_view')
        for comment in comment_view:
            ps = comment.find('p')
            for p in ps:
                if p.text != "":
                    with open(file_name, 'a', encoding='utf-8', newline='\n') as link_csv:
                        csv.writer(link_csv, dialect='excel').writerow(
                            ["https://www.clien.net" + url, "comment", nickname, p.text])


def getLink(group: str, start_page: int, end_page: int):
    for page in range(start_page, end_page):
        r = session.get('https://www.clien.net/service/group/' + group + "?po=" + str(page))
        list_subject = r.html.find('.symph_row > .list_title > .list_subject')
        for subject in list_subject:
            link_list.append(subject.attrs['href'])

    for link in link_list:
        data_crawling(link)
    time.sleep(10)


for group in group:
    getLink(group, 0, 10)
    getLink(group, 11, 20)
    getLink(group, 21, 30)
