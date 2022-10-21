#coding=utf-8

#从民政局网站上获取近十年的结婚数据，注意：从2021年第4季度及以后，季度结婚数据变成了全年累计数
#做出图表后会有有意思的发现
#ljffytax 2018-06-10, 2022-10-21

import requests
import socket
import re
from bs4 import BeautifulSoup


def get_content(url , data = None):
	#print ("Connect to:",url)
	timeout = 5
	header={
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'zh-CN,zh;q=0.8',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
	}
	try:
		rep = requests.get(url,headers = header,timeout = timeout)
		rep.encoding = 'utf-8'
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	return rep.text

def get_urls(html_text):
	regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9.]+shtml"
	pattern = re.compile(regular)
	match = re.findall(pattern,html_text)
	return match

def get_real_urls(html_text):
	#regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9.]+shtml"
	regular = r"/article/sj/tjjb/[0-9]+/[0-9]+[a-z]{4}\.html"
	pattern = re.compile(regular)
	match = re.findall(pattern,html_text)
	if len(match) == 0 :
		#regular = r"/article/sj/tjjb/qgsj/[0-9]+/[0-9a-z.]+html"
		regular = r"/article/sj/tjjb/qgsj/[0-9]{4,}/[0-9a-z]+\.htm[l]?"
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
	regularTag = r'结婚登记'
	regularTagQuarter = r'[0-9]{4}年[1-4]{1}季度'
	final = ["",0]

	pattern = re.compile(regularTagQuarter)
	match = re.findall(pattern,html_text)
	if match :
		final[0] = match[0]
	bs = BeautifulSoup(html_text, "html.parser")
	body = bs.body
	data = body.find('table')
	if data is None:
		print (html_text)
		print ("***ERROR!!!***")
		return final
	trs = data.find_all('tr')
	if trs is None:
		return final
	i = len(trs)
	while i > len(trs)-50:
		m = trs[i-1]
		if m:
			pattern = re.compile(regularTag)
			match = re.findall(pattern,str(m))
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
							final[1] = munber[1:len(munber)-1]
							break
		i = i - 1
	return final

if __name__ == "__main__":
	main_urls = ["http://www.mca.gov.cn/article/sj/tjjb/qgsj","http://www.mca.gov.cn/article/sj/tjjb/qgsj/?2",\
		"http://www.mca.gov.cn/article/sj/tjjb/qgsj/?3","http://www.mca.gov.cn/article/sj/tjjb/qgsj/?4"]
	isFailed = 0
	print ("时间：季度  |单位：万对")
	for main_url in main_urls:
		htm = get_content(main_url)
		if htm is None or isFailed == 1:
			break
		urls = get_urls(htm)
		#print  ("urls:",urls)
		for u in urls:
			uu = "http://www.mca.gov.cn" + u
			htm = get_content(uu)
			if htm is None:
				isFailed = 1
				break
			ruu = get_real_urls(htm)
			if ruu:
				htm = get_content(ruu[0])
			datas = get_data(htm)
			print (datas[0],"|",datas[1])
	print ("===Done!===")
