from requests_html import HTMLSession
from lxml.etree import ParserError
import os
import time
import csv
import datetime

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../datafile"))
TODAY_DATE = datetime.date.today().isoformat()
FILE_NAME = FILE_DIRECTORY + f'/{TODAY_DATE}_Clien_Data.csv'
GROUP = ['community', 'allinfo', 'allreview', 'allsell']
LINK_LIST = []



def Crawling(url: str):
    ### POST ###
    SESSION = HTMLSession(mock_browser=True)
    r = SESSION.get("https://www.clien.net" + url)
    print("https://www.clien.net" + url)
    # Error Exception: '게시글 삭제되었을 때'
    if r.html.find('.error', first=True) is not None:
        return
    else:
        nickname = r.html.find('.nickname', first=True)
    # Image nickname check
    img = nickname.find('img', first=True)
    nickname = img.attrs['alt'] if img is not None else nickname.text
    # crawling post data
    post_p = r.html.find('.post_content', first=True).find('p')
    for i in post_p:
        if i.text != "":
            with open(FILE_NAME, 'a', encoding='utf-8', newline='\n') as link_csv:
                csv.writer(link_csv).writerow(["https://www.clien.net" + url, "post", nickname, i.text])

    ### COMMENT ###
    SESSION = HTMLSession(mock_browser=True)
    r = SESSION.get("https://www.clien.net" + url.split("?")[0] + "/comment?ps=1000")

    try:
        comment_row = r.html.find('.comment_row')
    except ParserError:
        return

    for comment in comment_row:
        if comment.find('.blocked', first=True) is not None:
            continue
        nickname = comment.find('.nickname', first=True)
        img = nickname.find('img', first=True)
        nickname = img.attrs['alt'] if img is not None else nickname.text

        comment_view = comment.find('.comment_view', first=True)
        p_list = comment_view.find('p')
        for p in p_list:
            if p.text != "":
                with open(FILE_NAME, 'a', encoding='utf-8', newline='\n') as link_csv:
                    csv.writer(link_csv).writerow(
                        ["https://www.clien.net" + url, "comment", nickname, p.text])


def getPostLink(group: str, start_page: int = 0, end_page: int = 1):
    SESSION = HTMLSession(mock_browser=True)
    for page in range(start_page, end_page):
        r = SESSION.get('https://www.clien.net/service/group/' + group + "?po=" + str(page))
        list_subject = r.html.find('.symph_row > .list_title > .list_subject')
        for subject in list_subject:
            LINK_LIST.append(subject.attrs['href'])
    print(LINK_LIST)
    for link in LINK_LIST:
        Crawling(link)



for group in GROUP:
    getPostLink(group, 0, 10)
    #getPostLink(group, 10, 20)
    #getPostLink(group, 20, 30)
