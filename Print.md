# Crawling Code

## 클리앙
```python

from requests_html import HTMLSession
from lxml.etree import ParserError

import os
import sys
import time
import csv
import json
import telegram

def collect_clien_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")
    session = HTMLSession(mock_browser=True)
    for page in range(50):
        r = session.get('https://www.clien.net/service/search?q=' + SLANG + '&sort=recency&p=' + str(
            page) + '&boardCd=&isBoard=false')
        for item in r.html.find(
                '#div_content > div.contents_jirum > div.list_item.symph_row.jirum > .list_title.oneline > .list_subject > a'):
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
                if item.attrs['href'].split('?')[0].split('/')[-1] == num:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer = csv.DictWriter(link_file, fieldnames=field_names)
                writer.writerow(({'num': item.attrs['href'].split('?')[0].split('/')[-1],
                                  'link': 'https://www.clien.net' + item.attrs['href']}))
        time.sleep(3)
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_clien_document_content(num: str, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Exception ###
    # 404 Error
    if r.html.find('#div_content > .content_serviceError', first=True) is not None:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: 404 Error, {link}")
        return
    # Login Error
    if r.html.find('.content_signin', first=True) is not None:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Need to login, {link}")
        return

    ### Title ###
    try:
        content = r.html.find('#div_content > div.post_title.symph_row > h3 > span', first=True).text
    except AttributeError as e:
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: {e}, {link}")
        return
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
        writer = csv.DictWriter(content_file, fieldnames=field_names)
        writer.writerow({'num': num, 'type': 'title', 'content': content})

    ### Post ###
    for p in r.html.find('.content_view > div.post_view > div.post_content > article > div', first=True).find('p'):
        if p.text == '':
            continue
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
            writer = csv.DictWriter(content_file, fieldnames=field_names)
            writer.writerow({'num': num, 'type': 'post', 'content': p.text.replace('\n', ' ')})

    ### Comment ###
    r = session.get(link.split('?')[0] + '/comment?ps=200')
    try:
        comment_content = r.html.find('.comment_content')
    except ParserError:
   #     bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: No Comment, {link}")
        time.sleep(3)
        return
    for comment in comment_content:
        if comment.find('.comment_view', first=True).text == '':
            continue
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
            writer = csv.DictWriter(content_file, fieldnames=field_names)
            writer.writerow(
                {'num': num, 'type': 'comment',
                 'content': comment.find('.comment_view', first=True).text.replace('\n', '')})
    time.sleep(3)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python clien.py [Type] [Slang]')
        exit()

    CRAWLER_NAME = "Clien"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../Clien"))
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "../../token.json"))

    # Telegram Setting
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Clien_{SLANG}_content.csv'

    if TYPE == 'link':
        if os.path.exists(link_file_name) is True:
            os.remove(link_file_name)

        field_names = ['num', 'link']

        if os.path.exists(content_file_name) is True:
            with open(content_file_name, 'r', encoding='utf-8') as content_file:
                reader = csv.reader(content_file)
                next(reader, None)
                try:
                    num = list(reader)[-1][0]
                except ValueError:
                    num = None
                except IndexError:
                    num = None
        else:
            num = None

        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
            writer = csv.DictWriter(link_file, fieldnames=field_names)
            writer.writeheader()
        try:
            collect_clien_document_link(num)
        except:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")

    elif TYPE == 'content':
        field_names = ['num', 'type', 'content']
        if os.path.exists(link_file_name) is False:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: FileNotFoundError: No such file!")
            exit()

        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
                writer = csv.DictWriter(content_file, fieldnames=field_names)
                writer.writeheader()

        with open(link_file_name, 'r', encoding='utf-8') as link_file:
            reader = csv.reader(link_file)
            next(reader, None)
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} content data")
            for row in reversed(list(reader)):
                try:
                    collect_clien_document_content(row[0], row[1])
                except:
                    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Sucessfully collected {SLANG} content data")
    else:
        print("Context Error. Please retry input")
```

## DC Inside

```python
import os
import time
import csv
import json
import boto3

from progress.bar import Bar
from requests_html import HTMLSession

# STORE FILE INFORMATION
FILE_DIRECTORY = os.path.abspath(os.path.join(__file__,"../../datafile"))
SLANG_FILE = os.path.abspath(os.path.join(__file__,"../../slang.json"))
BUCKET = "dankook-hunminjeongeum-data-bucket"
S3 = ""

# UPLOAD AWS_S3 - BOTO3
def upload(s3, local_file_path, bucket, obj):
	s3.upload_file(local_file_path, bucket, obj)


# [S]KEYWORD SEARCH AND COLLECT LINK
def collect_document_link(keyword, pages):
	
	collect_link_num = 0
	
	# HTMLSession with mock_browser 
	session = HTMLSession(mock_browser=True)

	# CREATE LINKS FILE
	links_file = FILE_DIRECTORY + f'/dc_inside_{keyword}_links.csv'	
	if os.path.exists(links_file):
		os.remove(links_file)
	open(links_file,'a').close()

	# Progressing Bar	
	bar = Bar(f'Processing : Link Crawling [{keyword}]', max = pages)

	# Crawl Link
	for i in range(pages):
		time.sleep(5)
		bar.next()
		r = session.get(f'https://search.dcinside.com/post/p/{i + 1}/sort/latest/q/{keyword}')
		dummy_links = r.html.find('#container > div > section.center_content > div.inner > div.integrate_cont.sch_result.result_all > ul > li > a')
		with open(links_file,'a', encoding='utf-8',newline='') as link:
			wr = csv.writer(link)
			for i in dummy_links:
				wr.writerow([i.attrs['href']])
				collect_link_num += 1

	# Close
	bar.finish()
	session.close()
	
	return collect_link_num
# [E]KEYWORD SEARCH AND COLLECT LINK


# [S]COLLECT DOCUMENT CONTENT BY LINK
def collect_document_content(keyword, num):
		
	# HTMLSession with mock browser
	session = HTMLSession(mock_browser=True)

	# CREATE CONTENTS FILE
	contents_file = FILE_DIRECTORY + f'/dc_inside_{keyword}_contents.csv'
	if os.path.exists(contents_file):
		os.remove(contents_file)
	content = open(contents_file,'a', encoding = 'utf-8')
	wr_contents = csv.writer(content)
	
	# OPEN LINKS FILE
	links_file = FILE_DIRECTORY + f'/dc_inside_{keyword}_links.csv'
	if os.path.exists(links_file) is False:
		print("Link file is not exist\n")
		exit()	
	link = open(links_file,'r',newline='')
	rd_links = csv.reader(link)
	
	# Progressing Bar
	bar = Bar(f'Processing : Content Crawling [{keyword}]', max =num)

	# Crawl Contents
	for rd_link in rd_links:
		store = []
		time.sleep(5)
		r = session.get(rd_link[0])
		# error handler
		if(r.html.find('.box_infotxt delet',first=True)) is not None:
			return
		
		title = r.html.find('#container > section > article:nth-child(3) > div.view_content_wrap > header > div > h3 > span.title_subject')
		post = r.html.find('.writing_view_box',first =True)
		for i in ['div','p','span']:
			posts = post.find(i)
			for p in posts:
				store.append(p.text.replace("\n"," "))
		wr_contents.writerow([rd_link[0],title[0].text]+store)	
		bar.next()	
		
	# UPLOAD TO S3
	upload(S3,contents_file,BUCKET,"DC_INSIDE"+f"/dc_inside_{keyword}_contents.csv")

	# Close
	bar.finish()
	content.close()
	link.close()	
	session.close()	
	os.remove(links_file)
# [E]COLLECT DOCUMENT BY LINK


if __name__ == '__main__':
	
	S3 = boto3.client('s3')
	
	with open(SLANG_FILE) as slang_file:
		slangs = json.load(slang_file)["unordered"]
	
	for slang in slangs:
		num = collect_document_link(slang,4)
		collect_document_content(slang,num)

```
## 개드립
```python
import csv
import json
import os
import sys
import time

import boto3
import telegram

from requests_html import HTMLSession

from s3_bucket_manage import upload_s3

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))

# Keyword that doesn't exist
KEYWORD_NOT_EXIST = []

# S3 bucket config
OBJ_FOLDER = "dog_drip"

with open(os.path.join('bucket_name.json')) as slang_file:
    S3_BUCKET = json.load(slang_file)['bucket']
s3 = boto3.client('s3')


# 개드립 사이트는 자료수가 비교적 많이 적고 딱히 막히는 부분이 없는 것으로 판단하여
# 모든 키워드 한번에 실행

def collect_dog_drip_document_link(keyword):
    file_name = f'links/dog_drip_{keyword}_links.csv'

    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    if os.path.exists(file_name) is False:
        open(file_name, 'a').close()

    page_sum = 0
    for number in range(5000):
        try:
            # Repeat for 5000 pages on each keyword
            time.sleep(4)

            # Make a new session for crawling
            session = HTMLSession(mock_browser=True)

            search_page = session.get(f'https://www.dogdrip.net/index.php?'
                                      f'_filter=search&mid=dogdrip&search_target=title_content&'
                                      f'search_keyword={keyword}&page={number + 1}').html

            # Check if the list is empty
            is_empty_text = search_page.find(
                'div.eq.section.secontent.background-color-content > div > div.ed.board-list'
                ' > table > tbody > tr > td > p', first=True)

            # If the list is not empty, start crawling
            if is_empty_text is None:
                link_list = search_page.find(
                    'div.eq.section.secontent.background-color-content > div > div.ed.board-list'
                    ' > table > tbody > tr > td.title > a')

                if len(link_list) == 0:
                    # Send log if the length is 0
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f'Dog_drip {keyword}_page_{number + 1} : {len(link_list)} failed')
                    continue
                else:
                    print(f'{keyword}:Page {number + 1} - {len(link_list)} links')

                    with open(file_name, 'a') as link_csv:
                        link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
                        for link in link_list:
                            # Write links to CSV file
                            link_writer.writerow(link.absolute_links)
            else:
                # Exit if the list doesn't exist
                print(f"{keyword}:Page {number + 1} empty. Next keyword..")
                break
            page_sum += len(link_list)

            # Close session
            session.close()

        except Exception as e:
            breakpoint()
            bot.sendMessage(chat_id=CHAT_ID,
                            text=str(e))

    # Return page number of keyword for logging
    session.close()
    return page_sum


def collect_dog_drip_document_content(keyword):
    link_file_name = f'links/dog_drip_{keyword}_links.csv'
    content_file_name = f'contents/dog_drip_{keyword}_contents.csv'

    field_name = ['link', 'content']

    keyword_page_count = 0

    if os.path.exists(link_file_name) is False:
        # If the link CSV file doesn't exist, skip the keyword
        print(f'{keyword} CSV not found. returning..')
        KEYWORD_NOT_EXIST.append(keyword)
        return 0

    with open(link_file_name, 'r') as link_csv:
        # If the link CSV is empty, skip the keyword
        if len(link_csv.readlines()) == 0:
            print(f'{keyword} link CSV empty! Deleting the file..')
            KEYWORD_NOT_EXIST.append(keyword)
            return 0

    if os.path.exists(content_file_name) is False:
        # Make CSV file for content
        open(content_file_name, 'a').close()

    with open(link_file_name, 'r') as link_csv:
        # Line count for link CSV
        row_count = sum(1 for row in link_csv)

    if row_count == 0:
        # Check if the number of link is 0, then return 0
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"{keyword} keyword link does not exist. Something went wrong!")
        return 0
    else:
        with open(content_file_name, 'a') as content_csv:
            # Write field name on header of CSV
            content_writer = csv.DictWriter(content_csv, fieldnames=field_name)
            content_writer.writeheader()
            content_csv.close()
        with open(link_file_name, 'r') as link_csv:
            line_reader = csv.reader(link_csv)

            for line in line_reader:
                # For each line from link CSV
                try:
                    # Get text from the link
                    link = ''.join(line)

                    # Make a new session for crawling
                    session = HTMLSession(mock_browser=True)

                    page_result = session.get(link).html

                    with open(content_file_name, 'a') as content_csv:
                        content_writer = csv.DictWriter(content_csv, fieldnames=field_name)

                        # Check if the page is deleted
                        deleted = page_result.find('#access > div.login-header > h1', first=True)
                        if deleted == '삭제된 게시물 입니다.':
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link} content deleted')
                            # Skip the line
                            continue

                        # Title
                        title = page_result.find(
                            'div.ed.article-wrapper.inner-container > div.ed > '
                            'div.ed.article-head.margin-bottom-large > h4 > a',
                            first=True)
                        if title is None:
                            # If the content is not blank
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link} title empty or deleted')
                            continue
                        else:
                            # Write into CSV
                            content_writer.writerow({'link': link, 'content': title.text})

                        # Body divided by <br>
                        body = page_result.find('#article_1 > div', first=True)
                        if body is None:
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link} body empty or deleted')
                            continue
                        else:
                            body_divide = body.text.split('\n')
                        if len(body_divide) == 0:
                            # If the content is blank
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link[-9:]} body empty')
                        else:
                            # Write body into CSV without line change
                            for body in body_divide:
                                if body == '':
                                    continue
                                else:
                                    content_writer.writerow({'link': link, 'content': body.replace("\n", "")})

                        # Comment text
                        comments = page_result.find('div.comment-list > div.comment-item > div.comment-content > '
                                                    'div > div:nth-of-type(2) > div.xe_content')
                        if len(comments) == 0:
                            # Save log if no comments
                            print(f'link_id: {link[24:]} comment empty')
                            continue
                        else:
                            for comment in comments:
                                # TODO: 댓글도 나눠서 넣을 필요 있음.
                                # Replace line change into blank
                                comment_content = comment.text.replace("\n", " ")
                                if comment_content == '':
                                    continue
                                else:
                                    # If the content is not blank
                                    content_writer.writerow({'link': link, 'content': comment_content})
                                    print(f'Comment: {comment_content}')

                    # Sleep 8 secs for next link
                    time.sleep(8)
                    # Count on keyword link
                    keyword_page_count += 1

                    # Close session
                    session.close()

                except Exception as e:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=str(e))

    # Send log through Telegram
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'{keyword} keyword {keyword_page_count} out of {row_count} Done.')
    session.close()
    upload_s3(s3, S3_BUCKET, content_file_name, '/'.join([OBJ_FOLDER, content_file_name]))
    return keyword_page_count


if __name__ == '__main__':
    if len(sys.argv) < 1:
        # Exit if number of argument is incorrect
        print('가져올 데이터 [link, content]')
        # print('단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]\n')
        print('usage: python dog_drip.py link')
        exit()

    # 가져올 데이터 [link, content]
    content_type = sys.argv[1]
    # 카테고리 [unordered, namu_wiki]
    slang_category = sys.argv[2]
    # TODO: namu_wiki에서 애매한 비속어 제거 후 업데이트

    with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
        # Open slang.json to read slang words
        keyword = json.load(slang_file)[slang_category]

    with open(os.path.join(FILE_DIRECTORY, 'token.json')) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 345007326

    print(f'Dog_Drip {content_type} Crawling start!!\n')

    keyword_count_log = {}

    if content_type == 'link':
        # Start crawling for whole keyword
        for word in keyword:
            time.sleep(6)
            link_page_number = collect_dog_drip_document_link(word)
            keyword_count_log[word] = link_page_number
        # Send log through Telegram after finishing crawling
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"DOG_DRIP link crawling log\n {keyword_count_log}")

    elif content_type == 'content':
        for word in keyword:
            content_page_number = collect_dog_drip_document_content(word)
            keyword_count_log[word] = content_page_number
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"DOG_DRIP content crawling log\n {keyword_count_log}")
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"DOG_DRIP KEYWORD_DOES_NOT_EXIST: {KEYWORD_NOT_EXIST}")

```

## FM Korea

```python
import csv
import json
import os
import re
import sys
import time
import random

import boto3
import telegram

from progress.bar import Bar
from requests_html import HTMLSession

from s3_bucket_manage import upload_s3

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))

# S3 bucket config
OBJ_FOLDER = "fm_korea"

with open(os.path.join('bucket_name.json')) as slang_file:
    S3_BUCKET = json.load(slang_file)['bucket']
s3 = boto3.client('s3')


def collect_fm_korea_document_link(keyword, start_page, end_page):
    """
    FM 코리아 통합검색 링크 크롤링
    :param keyword: 욕설키워드
    :return:
    """

    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    # Check page for each keyword
    # pages_text = session.get(
    #     f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page=0').html.find(
    #     '#content > div > h3 > span', first=True)
    # result_pages = int(re.sub("[^0-9]", "", pages_text.text))
    # pages = result_pages if result_pages < 1000 else 1000

    print(f'Crawling page: {start_page} to {end_page}')

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'Keyword: {keyword} Crawling page: {start_page} to {end_page}')

    # Close session for list pages
    session.close()

    # Make csv file to save document link
    file_name = f'links/fm_korea_{keyword}_{start_page}-{end_page}_links.csv'

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    if os.path.exists(file_name) is False:
        open(file_name, 'a').close()

    session = HTMLSession(mock_browser=True)
    bar = Bar('Processing', max=end_page-start_page)

    for number in range(start_page, end_page):
        try:
            # Search link and text result via keyword
            time.sleep(random.randrange(14, 19))
            bar.next()

            fake_session_page = session.get('https://www.fmkorea.com/')

            fm_korea_docs = session.get(
                f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={number + 1}').html

            is_empty_text = fm_korea_docs.find(
                '#content > div > span', first=True)

            if is_empty_text is None:

                result_list = fm_korea_docs.find('#content > div > ul.searchResult > li > dl > dt > a')

                result_links = list(result.absolute_links.pop() for result in result_list)

                with open(file_name, 'a') as link_csv:
                    link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
                    if len(result_links) == 0:
                        # if no result
                        print(f' : {len(result_links)} failed')
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'FM_Korea {keyword}_page_{number + 1} : {len(result_links)} failed')
                        continue
                    else:
                        link_writer.writerow(result_links)
            else:
                # Exit if the list doesn't exist
                print(f"{keyword}:Page {number + 1} empty. Finishing keyword..")
                bot.sendMessage(chat_id=CHAT_ID,
                                text=f"{keyword}:Page {number + 1} empty. Finishing keyword..")
                break

        except Exception as e:
            bot.sendMessage(chat_id=CHAT_ID,
                            text=str(e))

    # Close session
    session.close()

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'fm_Korea {content_type} {keyword}({slang_choice}) {start_page}-{end_page} link Done!\n')
    bar.finish()
    session.close()


def collect_fm_korea_document_content(keyword, start_page, end_page):
    """
    FM 코리아 통합검색 내용 크롤링
    :param keyword: 욕설키워드
    :return:
    """

    link_file_name = f'links/fm_korea_{keyword}_{start_page}-{end_page}_links.csv'
    content_file_name = f'contents/fm_korea_{keyword}_contents.csv'
    if os.path.exists(link_file_name) is False:
        # Check CSV file exists
        print('No CSV file found! Exiting...')
        exit()

    if os.path.exists(content_file_name) is False:
        # Make content CSV file
        open(content_file_name, 'a').close()

    with open(link_file_name, newline='') as csv_file:
        # Open csv file to read link
        line_reader = csv.reader(csv_file)

        with open(content_file_name, 'a') as content_csv:
            # Write field name on header of CSV
            field_name = ['link', 'content']
            content_writer = csv.DictWriter(content_csv, fieldnames=field_name)
            content_writer.writeheader()
            content_csv.close()

        # Make a new session for crawling
        session = HTMLSession(mock_browser=True)

        bar = Bar('Processing', max=end_page - start_page)

        for line in line_reader:
            # Crawl content data from each link_line
            try:
                time.sleep(random.randrange(15, 19))
                bar.next()
                link = ''.join(line)

                page_result = session.get(link).html

                with open(content_file_name, 'a') as content_csv:

                    content_writer = csv.DictWriter(content_csv, fieldnames=field_name)

                    # Title
                    title = page_result.find(
                        '#bd_capture > div.rd_hd.clear > div.board.clear > div.top_area.ngeb > h1 > span',
                        first=True)
                    if title is None:
                        # If the title is blank, pass the line
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'link_id: {link[24:]} title empty or deleted')
                        continue
                    else:
                        content_writer.writerow({'link': link, 'content': title.text})

                    # Content
                    body_divide = page_result.find(
                        '#bd_capture > div.rd_body.clear > article', first=True).text.split('\n')
                    if len(body_divide) == 0:
                        # If the content is not blank
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'link_id: {link[24:]} body empty')
                        continue
                    else:
                        for body in body_divide:
                            if body == '':
                                continue
                            else:
                                content_writer.writerow({'link': link, 'content': body.replace("\n", "")})

                    # Comment text
                    comments = page_result.find('ul.fdb_lst_ul > li > div:nth-of-type(2) > div.xe_content')
                    if len(comments) == 0:
                        # Save log if the content is None
                        print(f'link_id: {link[24:]} comment empty')
                        continue
                    for comment in comments:
                        # Replace line change into blank
                        comment_content = comment.text.replace("\n", " ")
                        if comment_content == '':
                            continue
                        elif '[삭제된 댓글입니다.]' in comment_content:
                            continue
                        else:
                            # If the content is not blank
                            content_writer.writerow({'link': link, 'content': comment_content})

            except Exception as e:
                bot.sendMessage(chat_id=CHAT_ID,
                                text=str(e))

        # Close session
        session.close()
        bar.finish()

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'fm_Korea {content_type} {keyword}({slang_choice}) content Done!\n')
    upload_s3(s3, S3_BUCKET, content_file_name, '/'.join([OBJ_FOLDER, content_file_name]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Exit if number of argument is incorrect
        print('가져올 데이터 [link, content]')
        print('비속어 선정 [slang, unordered]')
        print('단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]\n')
        print('페이지 ')
        print('usage: python fm_korea.py link namu_wiki 0')
        exit()

    # 가져올 데이터 [link, content]
    content_type = sys.argv[1]
    # 카테고리 [unordered, namu_wiki]
    slang_category = sys.argv[2]
    # TODO: namu_wiki에서 애매한 비속어 제거 후 업데이트
    # 단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]
    slang_choice = int(sys.argv[3])

    start_page = int(sys.argv[4])
    end_page = int(sys.argv[5])

    with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
        # Open slang.json to read slang words
        keyword = json.load(slang_file)[slang_category][slang_choice]

    with open(os.path.join(FILE_DIRECTORY, 'token.json')) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 345007326

    print(f'FM_Korea {content_type} Crawling start!!\n')
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'fm_Korea {content_type} {keyword}({slang_choice}) {start_page}-{end_page} Crawling start!!\n')

    if content_type == 'link':
        collect_fm_korea_document_link(keyword, start_page, end_page)

    elif content_type == 'content':
        collect_fm_korea_document_content(keyword, start_page, end_page)

```
## 일베
```python
import csv
import json
import os
import re
import random
import sys
import time

import boto3
import telegram

from progress.bar import Bar
from requests_html import HTMLSession

from s3_bucket_manage import upload_s3

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))

# Keyword that doesn't exist
KEYWORD_NOT_EXIST = []

# S3 bucket config
OBJ_FOLDER = "ilbe"

with open(os.path.join('bucket_name.json')) as slang_file:
    S3_BUCKET = json.load(slang_file)['bucket']

s3 = boto3.client('s3')


def collect_ilbe_document_link(keyword):
    """
        FM 코리아 통합검색 링크 크롤링
        :param keyword: 욕설키워드
        :return:
        """
    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    # Check page for each keyword
    result_text = session.get(
        f'http://www.ilbe.com/index.php?act=IS&where=document&is_keyword={keyword}&mid=index&page=1').html

    # Check if the result is empty
    is_empty_text = result_text.find(
        '#content > div.content_margin > span', first=True)
    if is_empty_text is None:
        # Close existing session
        session.close()
        # If the list exists
        result_page_number = result_text.find(
            '#content > div.content_margin > h3 > span', first=True).text
        if result_page_number is None:
            bot.sendMessage(chat_id=CHAT_ID,
                            text=f'Keyword: {keyword} result not found.')
        print(result_page_number)
        # Find pages on result
        result_pages = int(re.sub("[^0-9]", "", result_page_number)) // 10
        print(result_pages)
        pages = result_pages if result_pages < 100 else 100

        print(f'Crawling page: {pages}')

        bot.sendMessage(chat_id=CHAT_ID,
                        text=f'Keyword: {keyword} Crawling page: {pages}')

        # Make csv file to save document link
        file_name = f'links/ilbe_{keyword}_links.csv'

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        if os.path.exists(file_name) is False:
            open(file_name, 'a').close()

        bar = Bar('Processing', max=pages)
        for number in range(pages):
            try:
                # Search link and text result via keyword
                time.sleep(random.randrange(4, 6))
                bar.next()

                # Make a new session for crawling
                session = HTMLSession(mock_browser=True)

                ilbe_docs = session.get(
                    f'http://www.ilbe.com/index.php?act=IS&where=document&'
                    f'is_keyword={keyword}&mid=index&page={number + 1}').html

                is_empty_text = ilbe_docs.find(
                    '#content > div.content_margin > span', first=True)

                if is_empty_text is None:
                    # If the list is not empty
                    result_list = ilbe_docs.find('#content > div > ul.searchResult > li > dl > dt > a')

                    result_links = [result.absolute_links.pop() for result in result_list
                                    if result.absolute_links.pop()[:56]
                                    != 'http://www.ilbe.com/index.php?where=document&is_keyword=']

                    with open(file_name, 'a') as link_csv:
                        link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
                        if len(result_links) == 0:
                            # if no result
                            print(f' : {len(result_links)} failed')
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'Ilbe {keyword}_page_{number + 1}:{len(result_links)} failed')
                            continue
                        else:
                            link_writer.writerow(result_links)
                else:
                    # Exit if the list doesn't exist
                    print(f"{keyword}:Page {number + 1} empty. Finishing keyword..")
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{keyword}:Page {number + 1} empty. Finishing keyword..")
                    break

                # Close session
                session.close()

            except Exception as e:
                breakpoint()
                bot.sendMessage(chat_id=CHAT_ID,
                                text=str(e))

    else:
        # If the link list is empty, finish keyword
        print(f"Ilbe {keyword} empty. Finishing keyword..")
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"Ilbe {keyword} result empty. Finishing keyword..")
        return 0

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'Ilbe {content_type} {keyword}({slang_choice}) link Done!\n')
    bar.finish()
    session.close()


def collect_ilbe_document_content(keyword):
    link_file_name = f'links/ilbe_{keyword}_links.csv'
    content_file_name = f'contents/ilbe_{keyword}_contents.csv'

    field_name = ['link', 'content']

    keyword_page_count = 0

    if os.path.exists(link_file_name) is False:
        # If the link CSV file doesn't exist, skip the keyword
        print(f'{keyword} CSV not found. returning..')
        KEYWORD_NOT_EXIST.append(keyword)
        return 0

    with open(link_file_name, 'r') as link_csv:
        # If the link CSV is empty, skip the keyword
        if len(link_csv.readlines()) == 0:
            print(f'{keyword} link CSV empty! Deleting the file..')
            KEYWORD_NOT_EXIST.append(keyword)
            return 0

    if os.path.exists(content_file_name) is False:
        # Make CSV file for content
        open(content_file_name, 'a').close()

    with open(link_file_name, 'r') as link_csv:
        # Line count for link CSV
        row_count = sum(1 for row in link_csv)

    if row_count == 0:
        # Check if the number of link is 0, then return 0
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"{keyword} keyword link file does not exist. Something went wrong!")
        return 0
    else:
        bot.sendMessage(chat_id=CHAT_ID,
                        text=f"{keyword} Row: {row_count}")
        with open(content_file_name, 'a') as content_csv:
            # Write field name on header of CSV
            content_writer = csv.DictWriter(content_csv, fieldnames=field_name)
            content_writer.writeheader()
            content_csv.close()
        with open(link_file_name, 'r') as link_csv:
            line_reader = csv.reader(link_csv)

            for line in line_reader:
                # For each line from link CSV
                try:
                    # Get text from the link
                    link = ''.join(line)

                    # Make a new session for crawling
                    session = HTMLSession(mock_browser=True)

                    page_result = session.get(link).html

                    with open(content_file_name, 'a') as content_csv:
                        content_writer = csv.DictWriter(content_csv, fieldnames=field_name)

                        # Title
                        title = page_result.find(
                            'div.title > h1 > a',
                            first=True).text
                        if title is None:
                            # If the content is not blank
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link} title empty or deleted')
                            continue
                        else:
                            # Write into CSV
                            print(f'Title: {title}')
                            content_writer.writerow({'link': link, 'content': title})

                        # Body divided by <br>
                        body = page_result.find(
                            '#copy_layer_1',
                            first=True)
                        if body is None:
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link} body empty or deleted')
                            continue
                        else:
                            body_divide = body.text.split('\n')
                        if len(body_divide) == 0:
                            # If the content is blank
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link[-9:]} body empty')
                        else:
                            # Write body into CSV without line change
                            for body in body_divide:
                                if body == '':
                                    continue
                                else:
                                    print(f'Body: {body}')
                                    content_writer.writerow({'link': link, 'content': body.replace("\n", "")})

                        # Comment text
                        comments = page_result.find(
                            'div.xe_content'
                        )
                        if len(comments) == 0:
                            # Save log if no comments
                            print(f'link_id: {link[24:]} comment empty')
                            continue
                        else:
                            for comment in comments:
                                if "[숨김 또는 삭제된 댓글입니다]" in comment.text:
                                    print('Empty comment. Skip..')
                                    continue
                                # TODO: 댓글도 나눠서 넣을 필요 있음.
                                # Replace line change into blank
                                comment_content = comment.text.replace("\n", " ")
                                if comment_content == '':
                                    continue
                                else:
                                    # If the content is not blank
                                    content_writer.writerow({'link': link, 'content': comment_content})
                                    print(f'Comment: {comment_content}')

                    # Sleep 8 secs for next link
                    time.sleep(random.randrange(8, 10))
                    # Count on keyword link
                    keyword_page_count += 1

                    # Close session
                    session.close()

                except Exception as e:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=str(e))

    upload_s3(s3, S3_BUCKET, content_file_name, '/'.join([OBJ_FOLDER, content_file_name]))

    # Send log through Telegram
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'{keyword} keyword {keyword_page_count} out of {row_count} Done.')
    return keyword_page_count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Exit if number of argument is incorrect
        print('가져올 데이터 [link, content]')
        print('단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]\n')
        print('usage: python ilbe.py link namu_wiki 0')
        exit()

    # 가져올 데이터 [link, content]
    content_type = sys.argv[1]
    # 카테고리 [unordered, namu_wiki]
    slang_category = sys.argv[2]
    # TODO: namu_wiki에서 애매한 비속어 제거 후 업데이트
    # 단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]
    slang_choice = int(sys.argv[3])

    with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
        # Open slang.json to read slang words
        keyword = json.load(slang_file)[slang_category][slang_choice]

    with open(os.path.join(FILE_DIRECTORY, 'token.json')) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 345007326

    print(f'Ilbe {content_type} Crawling start!!\n')
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'Ilbe {content_type} {keyword}({slang_choice}) Crawling start!!\n')

    if content_type == 'link':
        collect_ilbe_document_link(keyword)

    elif content_type == 'content':
        collect_ilbe_document_content(keyword)

```

## 인벤

```python
from requests_html import HTMLSession
import os
import time
import csv
import sys
import telegram
import json


def collect_inven_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")
    session = HTMLSession(mock_browser=True)
    r = session.get('http://www.inven.co.kr/search/webzine/article/' + SLANG + '/')
    max_page = int(r.html.find('.basetext > .pg')[-1].text) + 2
    for page in range(1, max_page):
        r = session.get('http://www.inven.co.kr/search/webzine/article/' + SLANG + '/' + str(page))
        link_list = r.html.find('.news_list > li > h1 > a')
        for link in link_list:
            with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
                writer = csv.DictWriter(link_file, fieldnames=field_names)
                num_temp = link.attrs['href'].split('/')[-2] + link.attrs['href'].split('/')[-1]
                if num_temp == num:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer.writerow({'num': num_temp,
                                 'link': link.attrs['href']})
        time.sleep(5)

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_inven_document_content(num: str, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    try:
        content = r.html.find('.articleTitle', first=True).text
        with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writerow({'num': num, 'type': 'title', 'content': content})
    except AttributeError:
        return
    ### Post ###
    for text in r.html.find('#powerbbsContent', first=True).text.split('\n'):
        if text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'post', 'content': text})

    time.sleep(3)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Argument Error')
        print('Choice Type [link, content] and Input Slang')
        print('usage) python ruliweb.py [Type] [Slang]')
        exit()
    CRAWLER_NAME = "Inven"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../Inven"))

    # Telegram Setting
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "../../token.json"))
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Inven_{SLANG}_content.csv'

    if TYPE == 'link':
        if os.path.exists(link_file_name) is True:
            os.remove(link_file_name)

        field_names = ['num', 'link']

        if os.path.exists(content_file_name) is True:
            with open(content_file_name, 'r', encoding='utf-8') as content_file:
                reader = csv.reader(content_file)
                next(reader, None)
                try:
                    num = list(reader)[-1][0]
                except ValueError:
                    num = None
                except IndexError:
                    num = None
        else:
            num = None
        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
            writer = csv.DictWriter(link_file, fieldnames=field_names)
            writer.writeheader()
        try:
            collect_inven_document_link(num)
        except:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")



    elif TYPE == 'content':
        field_names = ['num', 'type', 'content']

        if os.path.exists(link_file_name) is False:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: FileNotFoundError: No such file!!")
            exit()

        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
                writer = csv.DictWriter(content_file, fieldnames=field_names)
                writer.writeheader()

        with open(link_file_name, 'r', encoding='utf-8') as link_file:
            reader = csv.reader(link_file)
            next(reader, None)
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} content data")
            for row in reversed(list(reader)):
                try:
                    collect_inven_document_content(row[0], row[1])
                except:
                    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} content data.")
    else:
        print("Context Error. Please retry input")

```
## 뽐뿌
```python
import os
import time
import csv
import json
import boto3

from progress.bar import Bar
from requests_html import HTMLSession

# STORE FILE INFORMATION
FILE_DIRECTORY = os.path.abspath(os.path.join(__file__,"../../datafile"))
SLANG_FILE = os.path.abspath(os.path.join(__file__,"../../slang.json"))
BUCKET = "dankook-hunminjeongeum-data-bucket"
S3 = ""

# UPLOAD AWS_S3 - BOTO3
def upload(s3, local_file_path, bucket, obj):
	s3.upload_file(local_file_path, bucket, obj)

# [S]KEYWORD SEARCH AND COLLECT LINK
def collect_document_link(keyword, pages):
	
	collect_link_num = 0
	
	# HTMLSession with mock_browser 
	session = HTMLSession(mock_browser=True)

	# CREATE LINKS FILE
	links_file = FILE_DIRECTORY + f'/bbombu_{keyword}_links.csv'	
	if os.path.exists(links_file):
		os.remove(links_file)
	open(links_file,'a').close()

	# Progressing Bar	
	bar = Bar(f'Processing : Link Crawling [{keyword}]', max = pages)

	# Crawl Link
	for i in range(pages):
		time.sleep(5)
		bar.next()
		r = session.get(f'http://www.ppomppu.co.kr/search_bbs.php?page_no={i + 1}&keyword={keyword}')
		dummy_links = r.html.find('#result-tab1 > form > div > div > span > a')
		with open(links_file,'a',newline='') as link:
			wr = csv.writer(link)
			for i in dummy_links:
				wr.writerow([i.attrs['href']])
				collect_link_num += 1

	# Close
	bar.finish()
	session.close()
	
	return collect_link_num
# [E]KEYWORD SEARCH AND COLLECT LINK


# [S]COLLECT DOCUMENT CONTENT BY LINK
def collect_document_content(keyword, num):
	
	# HTMLSession with mock browser
	session = HTMLSession(mock_browser=True)

	# CREATE CONTENTS FILE
	contents_file = FILE_DIRECTORY + f'/bbombu_{keyword}_contents.csv'
	if os.path.exists(contents_file):
		os.remove(contents_file)
	content = open(contents_file,'a', encoding = 'utf-8')
	wr_contents = csv.writer(content)
	
	# OPEN LINKS FILE
	links_file = FILE_DIRECTORY + f'/bbombu_{keyword}_links.csv'
	if os.path.exists(links_file) is False:
		print("Link file is not exist\n")
		exit()	
	link = open(links_file,'r',newline='')
	rd_links = csv.reader(link)
	
	# Progressing Bar
	bar = Bar(f'Processing : Content Crawling [{keyword}]', max =num)

	# Crawl Contents
	for rd_link in rd_links:
		store = []
		time.sleep(5)
		r = session.get(rd_link[0])
		
		# error handler
		if(r.html.find('.error1',first=True)) is not None:
			return
		
		title = r.html.find('.view_title2',first=True)
		post = r.html.find('.ori_comment')
		for i in post:
			store.append(i.text.replace("\n"," "))
		wr_contents.writerow([rd_link[0],title.text]+store)
		bar.next()
		exit()	

	# UPLOAD TO S3
	upload(S3,contents_file,BUCKET,"BBOMBU"+f"/bbombu_{keyword}_contents.csv")

	# Close
	bar.finish()
	content.close()
	link.close()	
	session.close()	
	os.remove(links_file)
# [E]COLLECT DOCUMENT BY LINK

if __name__ == '__main__':

	S3 = boto3.client('s3')

	with open(SLANG_FILE) as slang_file:
		slangs = json.load(slang_file)["unordered"]
	
	for slang in slangs:
		num = collect_document_link(slang,4)
		collect_document_content(slang,num)

```
## 루리웹
```python
from requests_html import HTMLSession
import os
import time
import csv
import sys
import json
import telegram


def collect_ruliweb_document_link(num: str):
    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} link data")

    session = HTMLSession(mock_browser=True)
    page = 1
    count = 0
    search_pos = ""
    url = 'http://bbs.ruliweb.com/community/board/300143/list?search_type=subject&search_key=' + SLANG + '&page='

    while count < 10:
        time.sleep(3)
        r = session.get(url + str(page) + search_pos)
        notice = len(r.html.find('.table_body.notice'))

        if r.html.find('.empty_result', first=True) is None:
            if page > 15:
                page = 1
                search_pos = r.html.find('.search_more > a', first=True).attrs['href'][-20:]
                count += 1
                continue
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
                link = table_body.find('.subject > div > a', first=True).attrs['href']
                if link.split('?')[0][-8:] == num:
                    bot.sendMessage(chat_id=CHAT_ID,
                                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")
                    return
                writer.writerow({'num': link.split('?')[0][-8:], 'link': link})
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"{CRAWLER_NAME}: Successfully collected {SLANG} link data. Please start to collect content data.")


def collect_ruliweb_document_content(num: str, link: str):
    session = HTMLSession(mock_browser=True)
    r = session.get(link)

    ### Title ###
    content = r.html.find('div.board_main_top > div.user_view > div:nth-child(1) > h4 > span', first=True).text[5:]
    with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
        writer = csv.DictWriter(contnet_file, fieldnames=field_names)
        writer.writerow(
            {'num': num, 'type': 'title', 'content': content.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Post ###
    for p in r.html.find('#board_read > div > div.board_main > div.board_main_view > div.view_content > p'):
        if p.text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
                writer = csv.DictWriter(contnet_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'post', 'content': p.text.replace('뿅뿅', SLANG).replace('\n', ' ')})

    ### Comment ###
    for comment in r.html.find('.comment_element.normal > td.comment > div.text_wrapper > span.text'):
        if comment.text != '':
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as contnet_file:
                writer = csv.DictWriter(contnet_file, fieldnames=field_names)
                writer.writerow({'num': num, 'type': 'comment', 'content': comment.text.replace('\n', ' ')})
    time.sleep(4)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('''
               Argument Error
               Choice Type [link, content] and Input Slang
               usage) python ruliweb.py [Type] [Slang]
               usage) exec_crawler.py [Site] [Type]
               ''')

    CRAWLER_NAME = "Ruliweb"
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../Ruliweb"))
    TOKEN_FILE = os.path.abspath(os.path.join(__file__, "../../token.json"))

    # Telegram Setting
    with open(os.path.join(TOKEN_FILE)) as token_file:
        TELEGRAM_BOT_TOKEN = json.load(token_file)['token']
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    CHAT_ID = 620483333

    TYPE = str(sys.argv[1])
    SLANG = str(sys.argv[2])
    link_file_name = FILE_DIRECTORY + f'/Ruliweb_{SLANG}_link.csv'
    content_file_name = FILE_DIRECTORY + f'/Ruliweb_{SLANG}_content.csv'

    if TYPE == 'link':
        if os.path.exists(link_file_name) is True:
            os.remove(link_file_name)

        field_names = ['num', 'link']

        if os.path.exists(content_file_name) is True:
            with open(content_file_name, 'r', encoding='utf-8') as content_file:
                reader = csv.reader(content_file)
                next(reader, None)
                try:
                    num = list(reader)[-1][0]
                except ValueError:
                    num = None
                except IndexError:
                    num = None
        else:
            num = None
        with open(link_file_name, 'a', encoding='utf-8', newline='\n') as link_file:
            writer = csv.DictWriter(link_file, fieldnames=field_names)
            writer.writeheader()
        try:
            collect_ruliweb_document_link(num)
        except:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")

    elif TYPE == 'content':
        field_names = ['num', 'type', 'content']
        if os.path.exists(link_file_name) is False:
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: FileNotFoundError: No such file!!")
            exit()

        if os.path.exists(content_file_name) is False:
            with open(content_file_name, 'a', encoding='utf-8', newline='\n') as content_file:
                writer = csv.DictWriter(content_file, fieldnames=field_names)
                writer.writeheader()

        with open(link_file_name, 'r', encoding='utf-8') as link_file:
            reader = csv.reader(link_file)
            next(reader, None)
            bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Start collect {SLANG} content data")
            for row in reversed(list(reader)):
                try:
                    collect_ruliweb_document_content(row[0], row[1])
                except:
                    bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Error! Connection Closed")
        bot.sendMessage(chat_id=CHAT_ID, text=f"{CRAWLER_NAME}: Successfully collected {SLANG} content data.")
    else:
        print("Context Error. Please retry input")

```
# Preprocessing Code
```python
import json
import os
import csv
import telegram
import re
import sys


#csv.field_size_limit(sys.maxsize) # for linux
hangul = re.compile('[^ .,\u3131-\u3163\uac00-\ud7a3]+')


def preprocessing(origin_path: str, processed_path: str):
    if os.path.exists(origin_path) is False:
        return f'{origin_path}: Error. Not exists file'
    field_name = ['content', 'label']
    if os.path.exists(processed_path) is False:
        with open(processed_path, 'w', encoding='utf-8', newline='\n') as processed_file:
            writer = csv.DictWriter(processed_file, fieldnames=field_name)
            writer.writeheader()
    with open(origin_path, 'r', encoding='utf-8', newline='\n') as origin_file:
        reader = csv.reader(origin_file, quotechar='\"')
        next(reader, None)
        for field in list(reader):
            # 한글 전처리
            re_content = hangul.sub('', ''.join(field[2:])).strip()
            # 중복되는 .  ,  " 등 전처리
            re_content = ' '.join(re_content.split())
            re_content = '.'.join([x for x in re_content.split('.') if x])
            re_content = ','.join([x for x in re_content.split(',') if x])
            re_content = re_content.replace('\"', '')
            if re_content != "":
                with open(processed_path, 'a', encoding='utf-8', newline='\n') as processed_file:
                   writer = csv.DictWriter(
                       processed_file, fieldnames=field_name)
                   writer.writerow({'content': re_content, 'label': None})


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))


    # Keyword Setting
    SLANG_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, 'slang.json'))
    with open(SLANG_FILE, 'r', encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']

    if len(sys.argv) < 2:
        exit('''
                Argument Error
                Choice Site [clien, dc_inside, dog_drip, fm_korea, ilbe, inven, ppompu, ruliweb]
                usage) python preprocessing.py [Site] [Slang]
            ''')
    site = sys.argv[1] if sys.argv[1] in ['clien', 'dc_inside', 'dog_drip', 'fm_korea', 'ilbe',
                                          'inven', 'ppompu', 'ruliweb'] else exit("Please. Retry input site [clien, dc_inside, dog_drip, fm_korea, ilbe, inven, ppompu, ruliweb].")
    idx = SLANG.index(sys.argv[2]) if len(
        sys.argv) == 3 and sys.argv[2] in SLANG else 0

    for slang in SLANG[idx:]:
        file_path = '/'.join([ROOT_DIRECTORY, site,
                              'contents', f'{site}_{slang}_contents.csv'])
        processed_path = '/'.join([ROOT_DIRECTORY, site,
                                   'processed', f'{site}_{slang}_processed.csv'])
        preprocessing(file_path, processed_path)
```
# Modeling Code