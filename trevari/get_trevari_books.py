#-*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8
# Scraping all of the book list on trevari meetings
# Run with python 2.7
# Author: Ji-Hun Kim (jihuun.k@gmail.com)
# v 0.1.1

import time
import urllib
import requests
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver

g_url='https://trevari.co.kr'
g_url_meetings='https://trevari.co.kr/meetings'
g_button_xpath="""//*[@id="__next"]/div/div[2]/div/div/div[2]/button"""
g_output_file='trevari_book_list'

def get_webdriver(url):
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('disable-gpu')

	drv = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
	#drv.implicitly_wait(10)	# Doesn't work at all
	time.sleep(2)
	drv.get(url)
	time.sleep(2)
	return drv

# For click the button "더 보기"
def click_next_btn(cnt, drv):
	while cnt > 0:
		# Copy xpath of the button from the chrome-dev mode
		drv.find_element_by_xpath(g_button_xpath).click()
		time.sleep(2)	# It needs a time to wait a page fully loaded
		cnt = cnt - 1

# For scrolling down to the end "cnt" times
def scroll_down(cnt, drv):
	while cnt > 0:
		drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		cnt = cnt - 1

def print_current_time():
	now = time.localtime()
	s = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
	return s

def print_subject(f):
	f.write("## 트레바리 클럽별 선정 도서 목록  \n")
	f.write("> Updated on %s  \n\n" %(print_current_time()))
	f.write("> The list has been generated automatically by %s which is open source project.  \n" %(md_make_hyperlink("a python script", "https://github.com/jihuun/web_crawlers/blob/master/trevari/get_trevari_books.py")))
	f.write("> Sharing this list, reporting bugs & ideas, %s are always welcome :)  \n" %(md_make_hyperlink("pull requests", "https://github.com/jihuun/web_crawlers")))
	f.write("> Maintained by @soopsaram  \n\n")
	f.write("---\n\n")
	f.write("| 선정 도서 | 클럽 | 아지트 | 날짜 |  \n")
	f.write("| --- | --- | --- | --- |  \n")

def md_make_hyperlink(src, link):
	return '[' + src + '](' + link + ')'

def get_href(meeting):
	href = meeting['href']
	return g_url + href

def split_place_date(word_list):
        str_by_list = ' '.join(word_list)
        split_str = str_by_list.split(u'2019년')
        return split_str

if __name__  == "__main__":

	driver = get_webdriver(g_url_meetings)
	scroll_down(40, driver)
	soup = BeautifulSoup(driver.page_source, "html.parser")

	f = open(g_output_file+'.md', 'w')
	print_subject(f)

	book_cnt = 0
	for meeting in soup.find_all('a', href=True):
		try:
			book = meeting.find('div', {'style':'font-weight: 600;'})
			if book != None:
				book_name = book.get_text()
			
			group = meeting.find('div', {'style':'font-weight: bold;'})
			if group != None:
				group_name = group.get_text()
				group_name_link = md_make_hyperlink(group_name, get_href(meeting))

			date = meeting.find('div', {'style':"color: rgb(123, 123, 123); font-size: 14px; margin-top: 4px;"})
			if date != None:
				date_text = date.get_text()
				date_simple = date_text.split(' ')
				split_data = split_place_date(date_simple)

			if book_name != u"읽을거리 정하는 중":
				infos = ("| %s | %s | %s | %s |  \n" %(book_name, group_name_link, split_data[0], split_data[1]))
				f.write(infos.encode('utf-8'))
				book_cnt = book_cnt + 1

		except:
			pass
		
	f.write("\n총 %d 개  \n\n" %(book_cnt))
	f.close()
	driver.quit()
