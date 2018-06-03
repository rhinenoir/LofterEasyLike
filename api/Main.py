from flask import Flask, request
app = Flask(__name__)

@app.route('/api/v1.0/lofter/download/<path:author_link>', methods=['GET', 'POST'])
def hello_world(author_link):
	authorAndLink = author_link.split('/')
	if len(authorAndLink) == 2:
		author, link = authorAndLink
		if request.method == 'GET':
			return author + ' | ' + link
		else:
			return 'error'
	else:
		author = author_link
		if request.method == 'GET':
			return 'GET ' + author
		else:
			return 'POST ' + author

@app.route('/api/v1.0/lofter/stories/<author>', methods=['GET'])
def hello(author):
	return 'Hello, World! ' + author + '|' + request.args.get('key')