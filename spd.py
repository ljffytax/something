#coding=utf-8

#从民政局网站上获取近十年的结婚数据
#做出图表后会有有意思的发现
#ljffytax 2018-06-10

import requests
import socket
import re
from bs4 import BeautifulSoup


def get_content(url , data = None):
	#print "Connect to:" + url
	timeout = 2
	header={
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'zh-CN,zh;q=0.8',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
	}
	while True:
		try:
			rep = requests.get(url,headers = header,timeout = timeout)
			rep.encoding = 'utf-8'
			break
		except:
			break
	return rep.text

def get_urls(html_text):
	regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9.]+shtml"
	pattern = re.compile(regular)
	match = re.findall(pattern,html_text)
	return match

def get_real_urls(html_text):
	regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9.]+html"
	pattern = re.compile(regular)
	match = re.findall(pattern,html_text)
	if len(match) == 0 :
		#print "Note!!"
		regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9.]+htm"
		pattern = re.compile(regular)
		match = re.findall(pattern,html_text)
	if len(match) == 0:
		regular = r"files2.mca.gov.cn/[a-z]+/[0-9]+/[0-9.]+htm"
		pattern = re.compile(regular)
		match = re.findall(pattern,html_text)
	if len(match) == 0:
		regular = r"www.mca.gov.cn/accessory/[a-z]+/[0-9]+/[0-9.]+htm"
		pattern = re.compile(regular)
		match = re.findall(pattern,html_text)
	if len(match)>0:
		if match[0][0] != '/':
			match[0] = "http://" + match[0]
		else:
			match[0] = "http://www.mca.gov.cn" + match[0]
	return match

def get_data(html_text):
	regular = r"\>[0-9. ]+\<"
	regularTag = ur'结婚登记'
	final = ""
	bs = BeautifulSoup(html_text, "html.parser")
	body = bs.body
	data = body.find('table')
	trs = data.find_all('tr')
	if trs is None:
		return 0
	i = len(trs)
	while i > len(trs)-50:
		m = trs[i-1]
		if m:
			pattern = re.compile(regularTag)
			match = re.findall(pattern,unicode(str(m),'utf-8'))
			if match:
				if str(m).find('\r') >= 0:
					HTMLStr = str(m).replace('\r\n','')
				else:
					HTMLStr = str(m).replace('\n','')
				HTMLStr = HTMLStr + '\n'
				pattern = re.compile(regular)
				match = re.findall(pattern,HTMLStr)
				if match:
					for munber in match:
						munber = munber.replace(' ','')
						if len(munber) > 2:
							final = munber[1:len(munber)-1]
							break
		i = i - 1
	return final

main_urls = ["http://www.mca.gov.cn/article/sj/tjjb/qgsj","http://www.mca.gov.cn/article/sj/tjjb/qgsj/?2","http://www.mca.gov.cn/article/sj/tjjb/qgsj/?3"]
for main_url in main_urls:
	htm = get_content(main_url)
	urls = get_urls(htm)
	for u in urls:
		uu = "http://www.mca.gov.cn" + u
		htm = get_content(uu)
		ruu = get_real_urls(htm)
		if ruu:
			htm = get_content(ruu[0])
		datas = get_data(htm)
		print datas
print "===Done!==="
