from flask import Flask, request
app = Flask(__name__)

@app.route('/api/v1.0/lofter/story/<author>/<link>', methods=['GET'])
def hello_world(author, link):
	return 'Hello, World! ' + author + '|' + link

@app.route('/api/v1.0/lofter/stories/<author>', methods=['GET'])
def hello(author):
	return 'Hello, World! ' + author + '|' + request.args.get('key')