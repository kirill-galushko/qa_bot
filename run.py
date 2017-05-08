from flask import Flask, render_template, jsonify, json
from main import main

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


@app.route('/viewer/<string:question_text>')
def get_view(question_text):
    res = main(question_text)
    print(res)
    data = {"title": "Здравствуйте, что вас интересует?",
            "type": "object",
            "properties": {question_text:{
                "type": main(question_text)[0]},
            question_text+"2":{
                "type": main(question_text)[1]},
            question_text+"3":{
                "type": main(question_text)[2]}
            }
            }
    return render_template('index.html', context=json.dumps(data, indent=2, separators=(', ', ': ')))

if __name__ == '__main__':
    app.run()