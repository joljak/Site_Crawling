from requests_html import HTMLSession

group = ['community', 'allinfo', 'allreview', 'allsell']
link_list = []
session = HTMLSession(mock_browser=True)

def post_crawling(url:str):
    
    url = "https://www.clien.net" + url
    r = session.get(url)
    post_content = r.html.find('.post_content', first=True)
    post_p = post_content.find('p', first=False)
    print(url)
    for i in post_p:
        if i.text != "":
            print(i.text)

def comment_crawling(url:str):
    url = "https://www.clien.net" + url
    print(url)
    r = session.get(url)
    r.html.render(wait=10)
    comment_view = r.html.find('.comment_view', first=False)
    for comment in comment_view:
        ps = comment.find('p')
        for p in ps:
            if p.text != "":
                print(p.text)

def getLink(group: str, start_page:int, end_page: int):
    for page in range(start_page, end_page):
        r = session.get('https://www.clien.net/service/group/'+ group + "?po="+ str(page))
        list_subject = r.html.find('.symph_row > .list_title > .list_subject')
        for subject in list_subject:
            link_list.append(subject.attrs['href'])

    for link in link_list:
        comment_crawling(link)
        #post_crawling(link)
getLink(group[0], 7, 8)

