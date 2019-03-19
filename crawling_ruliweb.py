from requests_html import HTMLSession
import os
import time
import csv

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "..\\datafile"))
SLANG = '씨발'
FILE_NAME = FILE_DIRECTORY + f'/Ruli_{SLANG}.csv'
LINK_LIST = []


def getLink(start: int = 1, end: int = 2):
    for page in range(start, end):
        print(page)

        SESSION = HTMLSession(mock_browser=True)
        r = SESSION.get('http://bbs.ruliweb.com/search?q=' + SLANG + '#gsc.q=' + SLANG + '&gsc.page=' + str(page))
        r.html.render(sleep=3, wait=3)
        SESSION.close()
        link_list = r.html.find('div.gsc-thumbnail-inside > div > a')
        for link in link_list[:-1]:
            LINK_LIST.append(link.attrs['data-ctorig'])


getLink(4, 6)
for link in LINK_LIST:
    print(link)
