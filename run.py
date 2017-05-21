from flask import Flask, render_template, json, request
from main import preprocessing
from telebot import types, TeleBot
from telebot.util import async
import _thread
import os

tkn = '343114871:AAH7VQdTnblr9szIKwH_CtibzWrQVv-qajU'
app = Flask(__name__)
bot = TeleBot(tkn)
tags = ['CRM', 'Тестирование', 'Коммерция', 'Консалтинг', 'Сервер', 'Интеграция', 'Телефония', 'Сайт']


class curr_conf:
    current_chat_id = 0
    current_tag = []

@app.route('/hello')
def hello():
    return 'Hello World'


@app.route('/getmethod/<jsdata>')
def get_javascript_data(jsdata):
    test_send(jsdata)
    return jsdata


@app.route('/update_json', methods=['POST'])
def update_json(json_var):
    return json.dumps(json_var)


@async()
def test_send(text):
    bot.send_message(curr_conf.current_chat_id, text)  # номер чата с десктопного приложения


@app.route('/viewer/')
def get_view(tag, question_text):
    data = {"title": "Здравствуйте, что вас интересует?",
            "type": "object",
            "properties": {tag: {
                "type": preprocessing(tag, question_text)[0]},
                tag + "2": {
                "type": preprocessing(tag, question_text)[1]},
                tag + "3": {
                "type": preprocessing(tag, question_text)[2]}
            }
            }
    print(data)
    return render_template('index.html', context=json.dumps(data, indent=2, separators=(', ', ': ')))


@bot.message_handler(commands=['start'])
def handle_text(message):
    answer = "Начало диалога"
    curr_conf.current_chat_id = message.chat.id
    log(message, answer)
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton('Начать диалог')])
    bot.send_message(message.chat.id,
                     """Здравствуйте, вас преведствует система консультации Salesplatform.""",
                     reply_markup=keyboard, parse_mode="Markdown")

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
    answer = """Выберете интересующую вас тему."""
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton(tag) for tag in tags])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode="Markdown")

    log(message, answer)


@bot.message_handler(func=lambda message: message.text in tags, content_types=['text'])
def handle_text(message):
    answer = """Хорошо. Задайте ваш вопрос."""
    keyboard = types.ReplyKeyboardMarkup(True, False)
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)

    curr_conf.current_tag = message.text
    print(curr_conf.current_tag)
    log(message, answer)


@bot.message_handler(func=lambda message: message.text[-1:] == '?', content_types=['text'])
def handle_text2(message):
    answer = """Пожалуйста подождите."""
    keyboard = types.ReplyKeyboardMarkup(True, False)
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)

    log(message, answer)
    print(curr_conf.current_tag)
    get_view(curr_conf.current_tag, message.text)


def flask_thread():
    app.run()

if __name__ == "__main__":
    _thread.start_new_thread(flask_thread, ())
    bot.polling(none_stop=True)





