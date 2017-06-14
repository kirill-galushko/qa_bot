from flask import Flask, render_template, json, request, session
from flask_socketio import SocketIO, send, emit
from main import preprocessing
from telebot import types, TeleBot
from telebot.util import async
import _thread
import redis

tkn = '343114871:AAH7VQdTnblr9szIKwH_CtibzWrQVv-qajU'
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

socketio = SocketIO(app)
bot = TeleBot(tkn)


answer_array = []
data = {}


def find_value(dictt, sought_value, current_path, result):
    for key, value in dictt.items():
        current_path.pop()
        current_path.append(key)
        if sought_value in key:
            result.append(current_path[:])
        if type(value) == type(''):
            if sought_value in value:
                result.append(current_path+[value])
        else:
            current_path.append(key)
            result = find_value(value, sought_value, current_path, result)
    current_path.pop()
    return result


@app.route('/hello')
def hello():
    return 'Hello World'


def json_generator(array):
    result = {}
    for idx, val in enumerate(array):
        if val:
            result[str(val)] = '0'

    return result


def update_json(answers, client_id):
    global current_chat_id
    current_chat_id = client_id
    result = preprocessing(answers)
    get_view.data = {'title': "Вопрос: " + answers[-1],
                     'properties': {
                         '1': dict(title=result[0]),
                         '2': dict(title=result[1]),
                         '3': dict(title=result[2])
                     }
                     }

    socketio.emit('update json', json.dumps(get_view.data, indent=2, separators=(', ', ': ')), namespace='/socket')


@socketio.on('connect', namespace='/socket')
def handler_connect():
    emit('Connect response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/socket')
def handler_disconnect():
    print('Client disconnected')


@socketio.on('receive answer', namespace='/socket')
def get_javascript_data(text):
    r_server = redis.StrictRedis('localhost', charset="utf-8", decode_responses=True)
    qty = r_server.dbsize()
    for ans in answer_array:
        r_server.lpush('qa_' + str(qty + 1), ans)
    r_server.lpush('qa_' + str(qty + 1), text)

    # ll = find_value(get_view.data, text, [], [])
    tg_send(text)


@async()
def tg_send(text):
    print(current_chat_id)
    bot.send_message(current_chat_id, text)


@app.route('/viewer/')
def get_view():
    get_view.data = {
        "title": "Ожидание диалога",
        "type": "object"
    }
    return render_template('index.html',
                           context=json.dumps(get_view.data, indent=2, separators=(', ', ': ')))


@bot.message_handler(commands=['start'])
def handle_text(message):
    answer = "Начало диалога"
    log(message, answer)
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton('Начать диалог')])
    bot.send_message(message.chat.id,
                     """Здравствуйте, вас приветствует система консультации.""",
                     reply_markup=keyboard,
                     parse_mode="Markdown")

# ВЫВОД ЛОГОВ
print(bot.get_me())


def log(message, answer):
    print("\n --------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \n Текст - {3}". format(message.from_user.first_name,
                                                                    message.from_user.last_name,
                                                                    str(message.from_user.id),
                                                                    message.text))
    print(answer)


@bot.message_handler(func=lambda message: message.text == 'Начать диалог', content_types=['text'])
def handle_tags(message):
    keyboard = types.ReplyKeyboardRemove()
    answer = """Что вас интересует?"""
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=keyboard,
                     parse_mode="Markdown")

    log(message, answer)


@bot.message_handler(func=lambda message: message.text != '', content_types=['text'])
def handle_text2(message):
    answer_array.append(message.text)
    answer = """Пожалуйста, подождите."""
    bot.send_message(message.chat.id, answer)

    log(message, answer)

    update_json(answer_array, message.chat.id)


def bot_thread():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    _thread.start_new_thread(bot_thread, ())
    socketio.run(app)






