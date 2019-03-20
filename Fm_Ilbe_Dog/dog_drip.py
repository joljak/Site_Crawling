import csv
import json
import os
import sys
import time

import telegram

from requests_html import HTMLSession

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))


def collect_dog_drip_document_link(keyword):

    session = HTMLSession(mock_browser=True)

    file_name = f'dog_drip/Dog_drip_{keyword}_links.csv'

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    if os.path.exists(file_name):
        # remove file if exists and make over
        os.remove(file_name)
        open(file_name, 'a').close()

    if os.path.exists(file_name) is False:
        open(file_name, 'a').close()

    page_sum = 0
    for number in range(5000):
        # Repeat for 5000 pages on each keyword
        time.sleep(4)

        search_page = session.get(f'https://www.dogdrip.net/index.php?'
                                  f'_filter=search&mid=dogdrip&search_target=title_content&'
                                  f'search_keyword={keyword}&page={number+1}').html

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
                                text=f'FM_Korea {keyword}_page_{i + 1} : {len(link_list)} failed')
                continue
            else:
                print(f'{keyword}:Page {number+1} - {len(link_list)} links')

                with open(file_name, 'a') as link_csv:
                    link_writer = csv.writer(link_csv, dialect='excel', delimiter='\n')
                    for i in link_list:
                        # Write links to CSV file
                        link_writer.writerow(i.absolute_links)
        else:
            # Exit if the list doesn't exist
            print(f"{keyword}:Page {number+1} empty. Next keyword..")
            break
        page_sum += len(link_list)
    # Return page number of keyword for logging
    return page_sum


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
            page_number = collect_dog_drip_document_link(word)
            keyword_count_log[word] = page_number

    # Send log through Telegram
    bot.sendMessage(chat_id=CHAT_ID,
                    text=f"DOG_DRIP crawling log\n {keyword_count_log}")

    # elif content_type == 'content':
    #     collect_fm_korea_document_content(keyword)
