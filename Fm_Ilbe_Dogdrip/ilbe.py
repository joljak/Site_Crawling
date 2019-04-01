import csv
import json
import os
import re
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
OBJ_FOLDER = "FM_Ilbe_Dogdrip"
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
        print(result_page_number)
        # Find pages on result
        result_pages = int(re.sub("[^0-9]", "", result_page_number)) // 10
        print(result_pages)
        pages = result_pages if result_pages < 500 else 500

        print(f'Crawling page: {pages}')

        bot.sendMessage(chat_id=CHAT_ID,
                        text=f'Keyword: {keyword} Crawling page: {pages}')

        # Make csv file to save document link
        file_name = f'ilbe/Ilbe_{keyword}_links.csv'

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        if os.path.exists(file_name) is False:
            open(file_name, 'a').close()

        bar = Bar('Processing', max=pages)
        for number in range(pages):
            try:
                # Search link and text result via keyword
                time.sleep(4)
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
    link_file_name = f'ilbe/Ilbe_{keyword}_links.csv'
    content_file_name = f'ilbe/Ilbe_{keyword}_contents.csv'

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
                            # content_writer.writerow({'link': link, 'content': title.text})

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
                                    # content_writer.writerow({'link': link, 'content': body.replace("\n", "")})

                        # Comment text
                        comments = page_result.find(
                            'div.xe_content'
                        )
                        if len(comments) == 0:
                            # Send Telegram if no comments
                            bot.sendMessage(chat_id=CHAT_ID,
                                            text=f'link_id: {link[24:]} comment empty')
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
                                    # content_writer.writerow({'link': link, 'content': comment_content})
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

    upload_s3(s3, S3_BUCKET, link_file_name, '/'.join([OBJ_FOLDER, link_file_name]))

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
