# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from pprint import pprint
from xml.etree.ElementTree import parse
from datetime import datetime
import urllib.request, re, requests, random, math, time

def longestCommonSubstring(s1, s2):
	len1, len2, maxLen = len(s1), len(s2), 0
	# dp = [[0] * len(s2)] * len(s1)
	dp = []
	for i in range(0, len1):
		dp.append([0] * len2)
	for i in range(0, len1):
		for j in range(0, len2):
			if s1[i] == s2[j]:
				if i > 0 and j > 0:
					dp[i][j] = dp[i - 1][j - 1] + 1
				else:
					dp[i][j] = 1
				if dp[i][j] > maxLen:
					maxLen = dp[i][j]
					maxIndex = i - maxLen + 1
			else:
				dp[i][j] = 0
	if maxLen != 0:
		return s1[maxIndex:maxIndex + maxLen]
	else:
		return ""

class Lofter(object):
	def __init__(self):
		self.articleList = {}
		self.timeRegex = 's([0-9]+)\.time=([0-9]+?);'
		self.titleRegex = 's([0-9]+)\.title="(.*?)";'
		self.linkRegex = 's([0-9]+)\.permalink="(.+?)";'
		self.contentRegex = 's([0-9]+)\.content="(.*?)";';
	
	def escape(self, content):
		content=content.getText()
		content=content.replace("&nbsp;","")
		return content
	
	def download(self, url):
		page = urllib.request.urlopen(url)
		content = page.read()
		prettyContent = BeautifulSoup(content, 'html.parser')
		typeFirst = prettyContent.findAll("div",{"class":"text"})
		typeSecond = prettyContent.findAll("div",{"class":"txtcont"})
		typeThird = prettyContent.findAll("div",{"class":"post-ctc box"})
		typeForth = prettyContent.findAll("div",{"class":"postdesc"})
		if len(typeFirst) != 0:
			result = typeFirst[1]
		elif len(typeSecond) != 0:
			result = typeSecond[0]
		elif len(typeThird) != 0:
			result = typeThird[0]
		elif len(typeForth) != 0:
			result = typeForth[0]
		else:
			print('error url: ' + url)
			return None
		result=[self.escape(x) for x in result.findAll('p')]
		return '\n'.join(result)
	
	def multiArticleDownload(self, url):
		self.getAllArticles(url)
		authorKeys = self.keyJoined(url)
		returnList = {"author": authorKeys[0], "articles": {}}
		authorList = self.articleList[authorKeys[0]]
		for articleLink in authorList:
			joinedTitle = authorList[articleLink][0] + " |" + authorList[articleLink][1]
			returnList["articles"][joinedTitle] = articleLink
		return returnList
	
	def blogIdAndTotal(self, viewUrl):
		page = requests.get(viewUrl)
		content = BeautifulSoup(page.content.decode('unicode_escape'), 'html.parser')
		iframe = content.find("iframe",{"id":"userIdCrossDomain_frame"})
		blogId = re.findall('blogId=([0-9]+)', iframe['src'])[0]
		total = content.select("body > div.g-bdfull.g-bdfull-show.ztag > \
		div.g-bdc.ztag > div.m-fbar.f-cb > div.schbtn.f-cb > \
		div:nth-of-type(1) > div > div.txt > a.ztag.currt > span")[0].text
		return [blogId, total]
	
	def getAllArticles(self, url):
		authorKeys = self.keyJoined(url)
		viewUrl = "http://" + authorKeys[0] + ".lofter.com/view"
		dwrUrl = 'http://'+ authorKeys[0] +'.lofter.com/dwr/call/plaincall/ArchiveBean.getArchivePostByTime.dwr'
		blogId, total = self.blogIdAndTotal(viewUrl)
		batchId, timestamp = random.randrange(100000,999999), math.floor(time.time() * 1000)
		data = "callCount=1\nscriptSessionId=${scriptSessionId}187\nhttpSessionId=\nc0-scriptName=ArchiveBean\nc0-methodName=getArchivePostByTime\nc0-id=0\nc0-param0=number:" + blogId + "\nc0-param1=number:" + str(timestamp) + "\nc0-param2=number:" + total + "\nc0-param3=boolean:false\nbatchId=" + str(batchId)
		headers = {'Host':authorKeys[0] + '.lofter.com', 
		'Proxy-Connection':'keep-alive', 
		'Pragma':'no-cache', 
		'Cache-Control':'no-cache', 
		'Origin':'http://' + authorKeys[0] +'.lofter.com', 
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) \
		AppleWebKit/537.36 (KHTML, like Gecko) \
		Chrome/66.0.3359.139 Safari/537.36', 
		'Content-Type':'text/plain', 
		'Accept':'*/*', 
		'Referer':'http://' + authorKeys[0] + '.lofter.com/view', 
		'Accept-Encoding':'gzip, deflate', 
		'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'}
		total = int(total)
		res = requests.post(url=dwrUrl, headers=headers, data=data)
		if res.status_code != 200:
			print('dwr error:', res.status_code)
			return None
		else:
			content = res.content.decode('unicode_escape')
			tmpList = {}
			timeOfArticles = re.findall(self.timeRegex, content)
			titleOfArticles = re.findall(self.titleRegex, content)
			linkOfArticles = re.findall(self.linkRegex, content)
			exertOfArticles = re.findall(self.contentRegex, content)
			self.articleList[authorKeys[0]] = {}
			for number, link in linkOfArticles:
				tmpList[number] = {'link': link}
			for number, title in titleOfArticles:
				tmpList[number]['title'] = title
			for number, exert in exertOfArticles:
				tmpList[number]['exert'] = exert
			for number, t in timeOfArticles:
				tmpList[str(int(number) + total)]['time'] = str(datetime.fromtimestamp(int(t)//1000))
			for number in tmpList:
				if 'title' in tmpList[number] and 'exert' in tmpList[number]:
					linkItem = tmpList[number]['link']
					titleItem = tmpList[number]['title']
					timeItem = tmpList[number]['time']
					exertItem = tmpList[number]['exert']
					self.articleList[authorKeys[0]][linkItem] = [titleItem, timeItem, exertItem]
			pprint(self.articleList)
	
	def selectedArticleDownload(self, selectedData):
		finalContent = ""
		authorName = selectedData['author']
		selectedList = selectedData['target']
		authorArticles = self.articleList[authorName]
		for link in selectedList:
			if link in authorArticles:
				description = authorArticles[link][2]
				title = authorArticles = authorArticles[link][0]
			finalContent = finalContent + title + '\n' + description + '\n'
		return finalContent
	
	def checkKeyWordExist(self, keyWord):
		for title in self.titleList:
			if keyWord in title:
				return True
		return False
	
	def multiChapterDownload(self, selectedData):
		authorName = selectedData['author']
		finalContent = ""
		authorArticles = self.articleList[authorName]
		chapters = selectedData['target']
		for link in chapters:
			title = authorArticles[link][0]
			description = authorArticles[link][2]
			finalContent = finalContent + title + '\n' + description + '\n'
		return finalContent
	
	def keyJoined(self, url):
		keys = re.search('http[s]*://(.+).lofter.com/(post/)*(.*)',url).groups()
		return keys

lofter = Lofter()
ss = lofter.multiArticleDownload('http://asgardfirenze.lofter.com/post/1d400d0e_12ca27c4')
print(ss)