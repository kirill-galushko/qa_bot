from flask import Flask, render_template, json
from main import main
from telebot import types, TeleBot
import os
app = Flask(__name__)
bot = TeleBot('343114871:AAH7VQdTnblr9szIKwH_CtibzWrQVv-qajU')
tags = ['CRM', 'Тестирование', 'Коммерция', 'Консалтинг', 'Сервер', 'Интеграция', 'Телефония', 'Сайт']


@app.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url="https://ссылка на приложение/токен вашего бота")
    return "CONNECTED", 200

@app.route('/hello')
def hello():
    return 'Hello World'


@app.route('/viewer')
def viewer():
    return render_template('index.html')


@app.route('/viewer/<string:question_text>')
def get_view(question_text):
    data = {"title": "Здравствуйте, что вас интересует?",
            "type": "object",
            "properties": {question_text: {
                "type": main(question_text)[0]},
                question_text + "2": {
                "type": main(question_text)[1]},
                question_text + "3": {
                "type": main(question_text)[2]}
            }
            }
    return render_template('index.html', context=json.dumps(data, indent=2, separators=(', ', ': ')))


@bot.message_handler(commands=['start'])
def handle_text(message):
    answer = "Начало диалога"
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

    log(message, answer)


# if __name__ == '__main__':
#     app.run()
#     bot.polling(none_stop=True)

app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
