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
		time.sleep(1)
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
#    if os.path.exists(contents_file):
#        os.remove(contents_file)
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
		try:
			time.sleep(1)
			r = session.get(rd_link[0])
			# error handle
			if(r.html.find('.box_infotxt delet',first=True)) is not None:
				return

			title = r.html.find('#container > section > article:nth-child(3) > div.view_content_wrap > header > div > h3 > span.title_subject')
			wr_contents.writerow([title[0].text])
        
			post = r.html.find('.writing_view_box',first =True)
			for i in ['p']:
				posts = post.find(i)
				for p in posts:
					if(p.text != ""):
						wr_contents.writerow([p.text])
			bar.next()
		except:
			pass	
#    # UPLOAD TO S3
#    upload(S3,contents_file,BUCKET,"DC_INSIDE"+f"/dc_inside_{keyword}_contents.csv")

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
		num = collect_document_link(slang,10)
		collect_document_content(slang,num)
	

