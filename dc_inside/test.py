from requests_html import HTMLSession

session = HTMLSession(mock_browser=True)

#[gallery id]
def crawl_gallery_id(url:str):
	ret = []
	r = session.get('https://gall.dcinside.com/m')
	gallerys = r.html.find('#categ_listwrap > div > div > div > ul > li > a')
	for i in gallerys:
		link = i.attrs['href']
		ret.append(link[len(url)-1:])
	return ret

def crawl_gallery():
	base_url = "https://gall.dcinside.com/mgallery/board/lists/?id="
	gallery_id = crawl_gallery_id(base_url) #
	gallery_id = ["girlgroup"]
	for gi in gallery_id:
		content = []
		post_id = crawl_gallery_post(gi,base_url) #
		post_id = ["3194515"]
		for pi in post_id:
			content.extend(crawl_gallery_contents(gi,pi))
		print(content)
			
		
#[contents] 제목 댓글
def crawl_gallery_contents(gi:str,pi:str):
	ret = []
	r = session.get('https://gall.dcinside.com/mgallery/board/view/?id='+gi+'&no='+pi)
	r.html.render()
	post_title = r.html.find('#container > section > article:nth-child(3) > div.view_content_wrap > header > div > h3 > span.title_subject')
	post_comment = r.html.find('div > div.clear.cmt_txtbox.btn_reply_write_all > p')
	for i in post_title:
		ret.append(i.text)
	for i in post_comment:
		ret.append(i.text)
	return ret


#[page 1-100] post 번호
def crawl_gallery_post(idx:str, url:str):
	ret = []
	for page in range(100):
		r = session.get(url+idx+"&page"+str(page))
		posts = r.html.find('#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr > td.gall_tit.ub-word > a.reply_numbox')	
		for post in posts:
			link = post.attrs['href']
			link = link[len(url+idx+"&no=")-1:]
			link = link[:-len("&t=cv&page="+str(page))]
			ret.append(str(link))
	return ret


crawl_gallery()
