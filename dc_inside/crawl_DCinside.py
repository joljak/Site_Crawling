import os
import time
import csv

from progress.bar import Bar
from requests_html import HTMLSession

# SLANG
SLANG = "씨발"

# STORE FILE INFORMATION
FILE_DIRECTORY = os.path.abspath(os.path.join(__file__,"../../datafile"))

# [S]KEYWORD SEARCH AND COLLECT LINK
def collect_dc_inside_document_link(keyword, pages):
	
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
		time.sleep(12)
		bar.next()
		dummy_links = session.get(f'https://search.dcinside.com/post/p/{i + 1}/sort/latest/q/{keyword}').html.find('#container > div > section.center_content > div.inner > div.integrate_cont.sch_result.result_all > ul > li > a')
		
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
def collect_dc_inside_document_content(keyword, num):
	
	# HTMLSession with mock browser
	session = HTMLSession(mock_browser=True)

	# CREATE CONTENTS FILE
	contents_file = FILE_DIRECTORY + f'/dc_inside_{keyword}_contents.csv'
	
	if os.path.exists(contents_file):
		os.remove(contents_file)
	
	content = open(contents_file,'a')
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
	print(len(rd_links))
	# Crawl Contents
	for rd_link in rd_links:
		store = []
		r = session.get(rd_link[0])
		title = r.html.find('#container > section > article:nth-child(3) > div.view_content_wrap > header > div > h3 > span.title_subject')
		post = r.html.find('.writing_view_box',first =True)
		for i in ['div','p','span']:
			posts = post.find(i)
			for p in posts:
				store.append(p.text.replace("\n"," "))
		wr_contents.writerow([rd_link[0],title[0].text]+store)	
		bar.next()
	
	
	# Close
	bar.finish()
	content.close()
	link.close()	
	session.close()	






# [E]COLLECT DOCUMENT BY LINK



dd = collect_dc_inside_document_link("씨발",1)
collect_dc_inside_document_content("씨발",dd)







