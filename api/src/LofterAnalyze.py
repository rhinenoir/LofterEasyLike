# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
import urllib.request, re, requests, random, math, time, redis, os

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
	def __init__(self, redisUrl):
		self.redisCache = redis.from_url(redisUrl)
		self.articleList = {}
		self.limitOnce = 300
		self.timeRegex = 's([0-9]+)\.time=([0-9]+?);'
		self.titleRegex = 's([0-9]+)\.title="(.*?)";'
		self.linkRegex = 's([0-9]+)\.permalink="(.+?)";'
		self.contentRegex = 's([0-9]+)\.content="(.*?)";';
		self.likePublishTime = 's([0-9]+)\.publishTime=([0-9]+?);'
		self.likeBlogNickName = 's([0-9]+)\.blogName="(.+?)";.*?s([0-9]+)\.blogNickName="(.+?)";'
		self.likeBlogPageUrl = 's([0-9]+)\.blogPageUrl="http://(.+?)\.lofter.com/post/(.+?)";'
		self.likePageTagMap = 's([0-9]+?)\.tagList=s([0-9]+?);'
		self.likeTagList = 's([0-9]+?)\[([0-9]+?)\]="(.+?)";'
		self.likePostHot = 's([0-9]+)\.postHot=(.*?);'
	
	def escape(self, content):
		content = content.getText()
		content = content.replace("&nbsp;","")
		return content
	
	def download(self, url):
		print('download single url: ', url)
		page = urllib.request.urlopen(url)
		content = page.read()
		print('page opened, content read, len: ', len(content))
		prettyContent = BeautifulSoup(content, 'html.parser')
		title = prettyContent.title.text
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
		result = [self.escape(x) for x in result.findAll('p')]
		return [title, title + "\n" + "\n".join(result)]
	
	def multiArticleDownload(self, authorName, keyWord=None):
		print("multiArticleDownload, authorName: ", authorName, " keyWord: ",keyWord)
		self.getAllArticles(authorName)
		returnList = {}
		# authorArticles = self.articleList[authorName]
		authorArticles = eval(self.redisCache.get(authorName))
		for articleLink in authorArticles:
			if len(authorArticles[articleLink][0]) == 0:
				joinedTitle = "(无题)" + " -" + authorArticles[articleLink][1]
			else:
				joinedTitle = authorArticles[articleLink][0] + " -" + authorArticles[articleLink][1]
			returnList[joinedTitle] = articleLink
		if keyWord and len(keyWord.strip()) != 0:
			titles = list(returnList.keys())
			for titleItem in titles:
				titleForCheck = titleItem[:-21]
				for singleKey in keyWord:
					if singleKey not in titleForCheck:
						del returnList[titleItem]
						break
					else:
						titleForCheck = titleForCheck[titleForCheck.index(singleKey) + 1:]
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
	
	def getAllArticles(self, authorName):
		print("getAllArticles: ", authorName)
		viewUrl = "http://" + authorName + ".lofter.com/view"
		dwrUrl = 'http://'+ authorName +'.lofter.com/dwr/call/plaincall/ArchiveBean.getArchivePostByTime.dwr'
		blogId, total = self.blogIdAndTotal(viewUrl)
		batchId, timestamp = random.randrange(100000,999999), math.floor(time.time() * 1000)
		data = "callCount=1\nscriptSessionId=${scriptSessionId}187\nhttpSessionId=\nc0-scriptName=ArchiveBean\nc0-methodName=getArchivePostByTime\nc0-id=0\nc0-param0=number:" + blogId + "\nc0-param1=number:" + str(timestamp) + "\nc0-param2=number:" + total + "\nc0-param3=boolean:false\nbatchId=" + str(batchId)
		headers = {'Host':authorName + '.lofter.com', 
		'Proxy-Connection':'keep-alive', 
		'Pragma':'no-cache', 
		'Cache-Control':'no-cache', 
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) \
		AppleWebKit/537.36 (KHTML, like Gecko) \
		Chrome/66.0.3359.139 Safari/537.36', 
		'Content-Type':'text/plain', 
		'Accept':'*/*', 
		'Referer':'http://' + authorName + '.lofter.com/view', 
		'Accept-Encoding':'gzip, deflate', 
		'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'}
		total = int(total)
		res = requests.post(url=dwrUrl, headers=headers, data=data)
		print("requests.post finished, res: ", res)
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
			# self.articleList[authorName] = {}
			singleArticleList = {}
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
					# self.articleList[authorName][linkItem] = [titleItem, timeItem, exertItem]
					singleArticleList[linkItem] = [titleItem, timeItem, exertItem]
			self.redisCache.set(authorName, singleArticleList, ex = 60 * 60 * 24)
			print("redisCache set finished")

	def selectedArticlesDownload(self, selectedData):
		print("selectedArticlesDownload, data: ", selectedData)
		finalContent = ""
		authorName = selectedData['author']
		selectedList = selectedData['target']
		# if authorName not in self.articleList:
		# 	self.getAllArticles(authorName)
		# authorArticles = self.articleList[authorName]
		if not self.redisCache.exists(authorName):
			print(authorName + " not existed, try getAllArticles")
			self.getAllArticles(authorName)
		authorArticles = eval(self.redisCache.get(authorName))
		skipCount, tmpSelectedList = 0, []
		for link in selectedList:
			if link in authorArticles:
				tmpSelectedList.append(link)
			else:
				skipCount = skipCount + 1
		selectedList = sorted(tmpSelectedList, key = lambda link:authorArticles[link][1])
		if len(selectedList) == 0:
			return {"skip": skipCount}
		content, title = "", authorArticles[selectedList[0]][0]
		for link in selectedList:
			url = "http://" + authorName + ".lofter.com/post/" + link
			content = content + self.download(url)[1] + "\n"
			title = longestCommonSubstring(title, authorArticles[link][0])
		return {"title": title, "content": content, "skip": skipCount}
	
	def checkKeyWordExist(self, keyWord, authorName):
		# authorArticles = self.articleList[authorName]
		authorArticles = eval(self.redisCache.get(authorName))
		for link in authorArticles:
			if keyWord in authorArticles[link][0]:
				return True
		return False
	
	def keyJoined(self, url):
		keys = re.search('http[s]*://(.+).lofter.com/(post/)*(.*)',url).groups()
		return keys

	def analyzeLikeData(self, content):
		pageUrl = re.findall(self.likeBlogPageUrl, content)
		pageTagMap = re.findall(self.likePageTagMap, content)
		pageTagList = re.findall(self.likeTagList, content)
		pageHotPot = re.findall(self.likePostHot, content)
		titleList = re.findall(self.titleRegex, content)
		nickNameList = re.findall(self.likeBlogNickName, content)
		timeList = re.findall(self.likePublishTime, content)
		tagListArchive, finalData, tmpNameToId, tmpHotPots, linkCount = {}, {}, {}, {}, len(pageUrl)
		print(len(pageUrl), len(pageTagMap), len(pageTagList), len(pageHotPot), len(titleList), len(nickNameList), len(timeList))
		for item in nickNameList:
			tmpNameToId[item[1]] = item[3]
		for i in range(0, linkCount):
			item, postHotItem = pageUrl[i], int(pageHotPot[i][1])
			uIndex, authorId, url = item
			finalData[uIndex] = {'_id': url, 'blog': authorId, 'author': tmpNameToId[authorId]}
			finalData[uIndex]['hot'] = postHotItem
		for item in pageTagList:
			tIndex, tName = item[0], item[2]
			if tIndex not in tagListArchive:
				tagListArchive[tIndex] = [tName]
			else:
				tagListArchive[tIndex].append(tName)
		for item in pageTagMap:
			key, value = item
			if key in finalData and value in tagListArchive:
				finalData[key]['tags'] = tagListArchive[value]
		for item in titleList:
			tIndex, titleItem = item
			if tIndex in finalData:
				finalData[tIndex]['title'] = titleItem
		for item in timeList:
			finalData[item[0]]['time'] = int(item[1])
		return [finalData, linkCount]

	def likeGet(self, userId):
		total, batchId, dwrUrl = 0, random.randrange(100000,999999), 'http://www.lofter.com/dwr/call/plaincall/BlogBean.queryLikePosts.dwr'
		blogId = self.blogIdAndTotal('http://' + userId + '.lofter.com/view')[0]
		headers = {'Host':'www.lofter.com', 
		'Proxy-Connection':'keep-alive', 
		'Pragma':'no-cache', 
		'Cache-Control':'no-cache', 
		'Origin':'http://www.lofter.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) \
		AppleWebKit/537.36 (KHTML, like Gecko) \
		Chrome/66.0.3359.139 Safari/537.36', 
		'Content-Type':'text/plain', 
		'Accept':'*/*', 
		'Referer':'http://www.lofter.com/favblog/' + userId, 
		'Accept-Encoding':'gzip, deflate', 
		'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'}
		dataStart = "callCount=1\nscriptSessionId=${scriptSessionId}187\nhttpSessionId=\nc0-scriptName=BlogBean\nc0-methodName=queryLikePosts\nc0-id=0\nc0-param0=number:" + blogId + "\nc0-param1=number:" + str(self.limitOnce) + "\nc0-param2=number:"
		dataEnd = "\nc0-param3=string:\nbatchId=" + str(batchId)
		finalData = []
		while True:
			data = dataStart + str(total) + dataEnd
			res = requests.post(url=dwrUrl, headers=headers, data=data)
			if res.status_code != 200:
				print('dwr error:', res.status_code)
				return None
			else:
				content = res.content.decode('unicode_escape')
				oneTurnData, linkCount = self.analyzeLikeData(content)
				finalData = finalData + list(oneTurnData.values())
			total = total + linkCount
			print(linkCount, total)
			if linkCount == 0:
				break