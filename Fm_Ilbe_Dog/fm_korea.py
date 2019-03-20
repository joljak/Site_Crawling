import csv
import json
import os
import re
import sys
import time

import telegram

from progress.bar import Bar
from requests_html import HTMLSession

# FM Korea
# https://www.fmkorea.com/index.php?act=IS&is_keyword={}&mid=home&where=document&page=1

# Ilbe
# http://www.ilbe.com/?act=IS&where=document&is_keyword={}

# Dogdrip
# https://www.dogdrip.net/


FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))


def collect_fm_korea_document_link(keyword):
    """
    FM 코리아 통합검색 링크 크롤링
    :param keyword: 욕설키워드
    :return:
    """

    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    # Check page for each keyword
    pages_text = session.get(
        f'https://www.fmkorea.com/index.php?act=IS&is_keyword={keyword}&mid=home&where=document&page=0').html.find(
        '#content > div > h3 > span', first=True)
    result_pages = int(re.sub("[^0-9]", "", pages_text.text))
    pages = result_pages if result_pages < 1000 else 1000

    print(f'Crawling page: {pages}')

    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'Keyword: {keyword} Crawling page: {pages}')

    # Make csv file to save document link
    file_name = f'fm_korea/FM_korea_{keyword}_links.csv'
    # if os.path.exists(file_name):
    #     # remove file if exists and make over
    #     os.remove(file_name)
    #     open(file_name, 'a').close()

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    if os.path.exists(file_name) is False:
        open(file_name, 'a').close()

    bar = Bar('Processing', max=pages)
    for number in range(pages):
        try:
            # Search link and text result via keyword
            time.sleep(12)
            bar.next()
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
                            text=e)
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'FM_Korea {content_type} {keyword}({slang_choice}) link Done!\n')
    bar.finish()
    session.close()


def collect_fm_korea_document_content(keyword):
    """
    FM 코리아 통합검색 내용 크롤링
    :param keyword: 욕설키워드
    :return:
    """

    # HTMLSession with mock_browser
    session = HTMLSession(mock_browser=True)

    link_file_name = f'FM_korea_{keyword}_links.csv'
    content_file_name = f'FM_korea_{keyword}_contents.csv'
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

        for line in line_reader:
            # Crawl content data from each link_line
            try:
                link = ''.join(line)
                print(f'get {link}')
                page_result = session.get(link).html

                with open(content_file_name, 'a') as content_csv:

                    content_writer = csv.DictWriter(content_csv, fieldnames=field_name)

                    # Title
                    title_content = page_result.find(
                        '#bd_capture > div.rd_hd.clear > div.board.clear > div.top_area.ngeb > h1 > span',
                        first=True).text
                    if title_content == '':
                        # If the content is not blank
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'link_id: {link[24:]} title empty')
                    else:
                        content_writer.writerow({'link': link, 'content': title_content})

                    # Content
                    body_content = page_result.find(
                        '#bd_capture > div.rd_body.clear > article', first=True).text.replace("\n", " ")
                    print(body_content)
                    if body_content == '':
                        # If the content is not blank
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'link_id: {link[24:]} body empty')
                    else:
                        content_writer.writerow({'link': link, 'content': body_content})

                    # Comment text
                    comments = page_result.find('ul.fdb_lst_ul > li > div:nth-of-type(2) > div.xe_content')
                    if len(comments) == 0:
                        # Send Telegram if the content is None
                        bot.sendMessage(chat_id=CHAT_ID,
                                        text=f'link_id: {link[24:]} comment empty')
                    for comment in comments:
                        # Replace line change into blank
                        comment_content = comment.text.replace("\n", " ")
                        if comment_content != '':
                            # If the content is not blank
                            content_writer.writerow({'link': link, 'content': comment_content})
                    time.sleep(13)

            except Exception as e:
                bot.sendMessage(chat_id=CHAT_ID,
                                text=e)
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'FM_Korea {content_type} {keyword}({slang_choice}) content Done!\n')
    session.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Exit if number of argument is incorrect
        print('가져올 데이터 [link, content]')
        print('단어 선택 unordered: [0 - 180] | namu_wiki: [0-156]\n')
        print('usage: python fm_korea.py link namu_wiki 0')
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

    print(f'FM_Korea {content_type} Crawling start!!\n')
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f'FM_Korea {content_type} {keyword}({slang_choice}) Crawling start!!\n')

    if content_type == 'link':
        collect_fm_korea_document_link(keyword)

    elif content_type == 'content':
        collect_fm_korea_document_content(keyword)
