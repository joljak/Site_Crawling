import os
import time
import csv
import json

from progress.bar import Bar
from requests_html import HTMLSession

# STORE FILE INFORMATION
FILE_DIRECTORY = os.path.abspath(os.path.join(__file__,"../../datafile"))
SLANG_FILE = os.path.abspath(os.path.join(__file__,"../../slang.json"))

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
#		time.sleep(12)
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
#		time.sleep(5)
		r = session.get(rd_link[0])
		r.html.render()
		print(r.html.find('.view_title2',first=True))
		
		#print(test.text)
		post = r.html.find('table.pic_bg')	
		post2 = post[2].find('tbody > tr > td > table > td.board-contents')
		print(post2)		


	#	for i in test2:
	#		print(i.text)	
	
		exit()
		title = r.html.find('.view_title2',fisrt=True)
		post = r.html.find('.container',first =True)
		for i in ['td.board-contents']:
			posts = post.find(i)
			for p in posts:
				store.append(p.text.replace("\n"," "))
				print(p.text)
	#	wr_contents.writerow([rd_link[0],title[0].text]+store)	
		bar.next()	

	# Close
	bar.finish()
	content.close()
	link.close()	
	session.close()	
	os.remove(links_file)
# [E]COLLECT DOCUMENT BY LINK

if __name__ == '__main__':
	with open(SLANG_FILE) as slang_file:
		slangs = json.load(slang_file)["unordered"]
	
	for slang in slangs:
		num = collect_document_link(slang,1)
		collect_document_content(slang,num)
	






