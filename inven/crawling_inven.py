from requests_html import HTMLSession
import os
import time
import csv
import datetime


FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../datafile"))
TODAY_DATE = datetime.date.today().isoformat()
FILE_NAME = FILE_DIRECTORY + f'/{TODAY_DATE}_Inven_Data.csv'
SLANG = []
LINK_LIST = []

def getLink(slang:str, start_page:int=1, end_page:int=2):
    SESSION = HTMLSession(mock_browser=True)
    for page in range(start_page, end_page):
        r = SESSION.get('http://www.inven.co.kr/search/webzine/article/'+slang +'/'+str(page))
        items = r.html.find('.news_list > li > h1 > a')
        for item in items:
            LINK_LIST.append(item.attrs['href'])
    SESSION.close()


def crawling(url:str):
    SESSION = HTMLSession(mock_browser=True)
    r = SESSION.get(url)
    #r.html.render()
    try:
        post_nickname = r.html.find('.articleWriter', first=True).text
    except AttributeError:
        print(url, str(AttributeError))
        return

    post_content = r.html.find('.articleTitle', first=True).text
    contents = r.html.find('#powerbbsContent > div')

    ### 욕이 들어있는 데이터이기 때문에 본문의 내용을 합칠 필요가 있었음.###
    for content in contents:
        if content.text !="":
            post_content = post_content + " " + content.text
    with open(FILE_NAME, 'a', encoding='utf-8', newline='\n') as link_csv:
        csv.writer(link_csv).writerow([url, "post", post_nickname, post_content])
    ### 욕설이 들어있는 것은 Post뿐이므로 덧글은 굳이 크롤링 안해도 될거 같음. ###
    '''
    comments = r.html.find('.commentList1 > ul > li')
    for comment in comments:
        comment_nickname = comment.find('.nickname', first=True).text
        comment_content = comment.find('.comment', first=True).text
        with open(FILE_NAME, 'a', encoding='utf-8', newline='\n') as link_csv:
            csv.writer(link_csv).writerow([url, "comment", comment_nickname, comment_content])
    '''
    #SESSION.close()

getLink('씨발', 1, 100)
for link in LINK_LIST:
    crawling(link)
    time.sleep(1)




