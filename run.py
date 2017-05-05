from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/viewer')
def viewer():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()