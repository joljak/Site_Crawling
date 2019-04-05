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
OBJ_FOLDER = "FM_Ilbe_Dogdrip"

with open(os.path.join('bucket_name.json')) as slang_file:
    S3_BUCKET = json.load(slang_file)['bucket']
s3 = boto3.client('s3')


# 개드립 사이트는 자료수가 비교적 많이 적고 딱히 막히는 부분이 없는 것으로 판단하여
# 모든 키워드 한번에 실행

def collect_dog_drip_document_link(keyword):
    file_name = f'dog_drip/Dog_drip_{keyword}_links.csv'

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
    link_file_name = f'dog_drip/Dog_drip_{keyword}_links.csv'
    content_file_name = f'dog_drip/Dog_drip_{keyword}_contents.csv'

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
