from flask import Flask, redirect

app = Flask(__name__)

@app.route('/time')
def time_page():
    return redirect('https://time.is/')

@app.route('/test')
def test_page():
    return '<h1>Test OK!</h1><p>Flask is working!</p>'

@app.route('/')
def home():
    return '<h1>Home Page</h1><p><a href="/time">Time</a> | <a href="/test">Test</a></p>'

@app.route('/<path:path>')
def catch_all(path):
    return f'<h1>Catch All</h1><p>Path: {path}</p><p><a href="/">Home</a></p>'

if __name__ == '__main__':
    app.run(debug=True)
