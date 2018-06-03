from flask import Flask, request
from LofterAnalyze import *
import json

app = Flask(__name__)
lofter = Lofter()

@app.route('/api/v1.0/lofter/download/<path:author_link>', methods=['GET', 'POST'])
def hello_world(author_link):
	authorAndLink = author_link.split('/')
	if len(authorAndLink) == 2:
		author, link = authorAndLink
		if request.method == 'GET':
			title, content = lofter.download('http://'+ author +'.lofter.com/post/' + link)
			return json.dumps([title, content])
		else:
			return 'error'
	else:
		author = author_link
		if request.method == 'GET':
			returnList = lofter.multiArticleDownload(author)
			if len(returnList) != 0:
				articles = list(returnList.values())
				finalContent = lofter.selectedArticlesDownload({"author": author, "target": articles})
				return json.dumps(finalContent)
			else:
				return 'no articles of the author: ' + author
		else:
			pass

@app.route('/api/v1.0/lofter/stories/<author>', methods=['GET'])
def hello(author):
	keyWord = request.args.get('key')
	if keyWord and len(keyWord.strip()) != 0:
		return lofter.multiArticleDownload(author, keyWord)
	else:
		return lofter.multiArticleDownload(author)
