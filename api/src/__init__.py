from flask import Flask, request, jsonify
from .LofterAnalyze import *
import os

app = Flask(__name__)
lofter = Lofter("redis://redis.default:80")
# lofter = Lofter("redis://localhost:6379")
print("redis connected")
print(lofter.redisCache)

@app.route('/', methods=['GET'])
def hello():
	return 'Hey there! You got available lofter API here now!'

@app.route('/api/v1.0/lofter/download/<path:author_link>', methods=['GET', 'POST'])
def downloadArticles(author_link):
	print("downloadArticles: ", author_link)
	authorAndLink = author_link.split('/')
	if len(authorAndLink) == 2:
		author, link = authorAndLink
		if request.method == 'GET':
			title, content = lofter.download('http://'+ author +'.lofter.com/post/' + link)
			return jsonify([title, content])
		else:
			return 'error'
	else:
		author = author_link
		if request.method == 'GET':
			returnList = lofter.multiArticleDownload(author)
			if len(returnList) != 0:
				articles = list(returnList.values())
				finalContent = lofter.selectedArticlesDownload({"author": author, "target": articles})
				return jsonify(finalContent)
			else:
				return 'no articles of the author: ' + author
		else:
			postData = request.get_json()
			lofter.getAllArticles(author)
			return jsonify(lofter.selectedArticlesDownload({"author": author, "target": postData}))

@app.route('/api/v1.0/lofter/stories/<author>', methods=['GET'])
def getStoriesListOfAuthor(author):
	print("getStoriesListOfAuthor: ", author)
	keyWord = request.args.get('key')
	if keyWord and len(keyWord.strip()) != 0:
		return jsonify(lofter.multiArticleDownload(author, keyWord))
	else:
		return jsonify(lofter.multiArticleDownload(author))

if __name__ == '__main__':
	app.run()
