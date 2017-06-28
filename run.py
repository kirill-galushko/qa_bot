from flask import Flask, render_template, json
from flask_socketio import SocketIO, emit
from ml import preprocessing
from telebot import types, TeleBot
from telebot.util import async
import _thread
import redis
from functools import reduce
import operator
import config

# Создание объекта приложения Flask
app = Flask(__name__)

# Создание объекта SocketIO
socketio = SocketIO(app)

# Создание объекта TeleBot
bot = TeleBot(config.token)

# Массив для хранения сообщений диалога
answer_array = []

# Словарь для хранения json представления графа диалога
data = {}


def getFromDict(dataDict, mapList):
    """Функция получения ветви в json по массиву значений в каждом узле

    Keyword arguments:
    dataDict -- json дерево
    mapList -- массив значений

    """
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict, mapList, value):
    """Функция задания значения ветви в json по массиву значений в каждом узле

    Keyword arguments:
    dataDict -- json дерево
    mapList -- массив значений
    value -- новое значение

    """
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


def verbose_to_compact(verbose):
    """Функция для преобразования подробного представления json в компактное

    Keyword arguments:
    verbose -- подробный json

    """
    return { item['title']: verbose_to_compact(item['properties']) for item in verbose }


def compact_to_verbose(compact):
    """Функция для преобразования компактного представления json в подробное

    Keyword arguments:
    compact -- компактный json

    """
    return [{'title': key, 'properties': compact_to_verbose(value)} for key, value in compact.items()]


def update_json(answers, client_id):
    """Функция для обновления объекта графа и id клиента

    Keyword arguments:
    answers -- массив диалога
    client_id -- id клиента

    """
    global current_chat_id
    current_chat_id = client_id
    result = preprocessing(answers)
    branch = {'title': answers[-1],
              'properties':
                  [{'title': key, 'properties': []} for key in result]
              }

    if len(answer_array) == 1:
        get_view.data = branch
    else:
        new = verbose_to_compact([get_view.data])
        new_branch = verbose_to_compact([branch])
        setInDict(new, answer_array[:-1], new_branch)
        get_view.data = compact_to_verbose(new)[0]

    socketio.emit('update json', json.dumps(get_view.data, indent=2, separators=(', ', ': ')), namespace='/socket')


# ВЫВОД ЛОГОВ
print(bot.get_me())


def log(message, answer):
    """Функция-логгер

    Keyword arguments:
    message -- объект полученного сообщения
    answer -- текст ответа

    """
    print("\n --------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) "
          "\n Текст - {3}". format(message.from_user.first_name,
                                   message.from_user.last_name,
                                   str(message.from_user.id),
                                   message.text))
    print(answer)


@socketio.on('connect', namespace='/socket')
def handler_connect():
    """Функция обработчика подключения клиента

    """
    emit('Connect response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/socket')
def handler_disconnect():
    """Функция обработчика отключения клиента

    """
    print('Client disconnected')


@socketio.on('receive answer', namespace='/socket')
def get_javascript_data(text):
    """Функция обработчика полученного ответа с веб-клиента

    Keyword arguments:
    text -- текст сообщения

    """
    answer_array.append(text)

    r_server = redis.StrictRedis('localhost', charset="utf-8", decode_responses=True)
    qty = r_server.dbsize()
    for ans in answer_array:
        r_server.lpush('qa_' + str(qty + 1), ans)

    tg_send(text)


@async()
def tg_send(text):
    """Функция асинхронной отправки сообщения

    Keyword arguments:
    text -- текст сообщения

    """
    bot.send_message(current_chat_id, text)


@app.route('/viewer/')
def get_view():
    """Функция рендеринга начального экрана

    """
    get_view.data = {
        "title": "Ожидание диалога"
    }
    return render_template('index.html',
                           context=json.dumps(get_view.data, indent=2, separators=(', ', ': ')))


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Функция обработчика запуска бота

    Keyword arguments:
    message -- объект сообщения

    """
    answer = "Начало диалога"
    log(message, answer)
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton('Начать диалог')])
    bot.send_message(message.chat.id,
                     """Здравствуйте, вас приветствует система консультации.""",
                     reply_markup=keyboard,
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == 'Начать диалог', content_types=['text'])
def handle_begin(message):
    """Функция обработчика сообщения "Начать диалог"

    Keyword arguments:
    message -- объект сообщения

    """
    keyboard = types.ReplyKeyboardRemove()
    answer = """Что вас интересует?"""
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=keyboard,
                     parse_mode="Markdown")

    log(message, answer)


@bot.message_handler(func=lambda message: message.text != '', content_types=['text'])
def handle_text(message):
    """Функция обработчика сообщения

    Keyword arguments:
    message -- объект сообщения

    """
    answer_array.append(message.text)
    answer = """Пожалуйста, подождите."""
    bot.send_message(message.chat.id, answer)

    log(message, answer)

    update_json(answer_array, message.chat.id)


def bot_thread():
    """Функция для запуска треда бота

    """
    bot.polling(none_stop=True)


if __name__ == "__main__":
    _thread.start_new_thread(bot_thread, ())
    socketio.run(app)
