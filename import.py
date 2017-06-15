import redis


def importation():
    r_server.lpush('qa_1', 'CRM')
    r_server.lpush('qa_1', 'Какой модуль?')

    r_server.lpush('qa_2', 'Консультация')
    r_server.lpush('qa_2', 'Техническая проблема или вопросы по оплате?')

    r_server.lpush('qa_3', 'Демо')
    r_server.lpush('qa_3', 'Демо какого проекта вы бы хотели получить?')

    r_server.lpush('qa_4', 'Я бы хотел что-то там CRM')
    r_server.lpush('qa_4', 'Какой модуль?')

    r_server.lpush('qa_5', 'CRM')
    r_server.lpush('qa_5', 'Какой модуль?')
    r_server.lpush('qa_5', 'Модуль контакты')
    r_server.lpush('qa_5', 'Проблема со какими-то полями?')

    r_server.lpush('qa_6', 'CRM')
    r_server.lpush('qa_6', 'Какой модуль?')
    r_server.lpush('qa_6', 'Контакты')
    r_server.lpush('qa_6', 'Проблема с экспортом?')

    r_server.lpush('qa_7', 'CRM')
    r_server.lpush('qa_7', 'Какой модуль?')
    r_server.lpush('qa_7', 'у меня проблема с контактами')
    r_server.lpush('qa_7', 'Проблема с импортом?')

    r_server.lpush('qa_8', 'CRM')
    r_server.lpush('qa_8', 'Какой модуль?')
    r_server.lpush('qa_8', 'Контрагенты')
    r_server.lpush('qa_8', 'Проблема с импортом?')

    r_server.lpush('qa_9', 'CRM')
    r_server.lpush('qa_9', 'Какой модуль?')
    r_server.lpush('qa_9', 'Контакты')
    r_server.lpush('qa_9', 'Проблема с экспортом?')
    r_server.lpush('qa_9', 'Да')
    r_server.lpush('qa_9', 'В чем она заключается?')

    r_server.lpush('qa_10', 'CRM')
    r_server.lpush('qa_10', 'Какой модуль?')
    r_server.lpush('qa_10', 'Контакты')
    r_server.lpush('qa_10', 'Проблема с экспортом?')
    r_server.lpush('qa_10', 'Да, что-то не работает.')
    r_server.lpush('qa_10', 'Что именно?')

    r_server.lpush('qa_11', 'CRM')
    r_server.lpush('qa_11', 'Какой модуль?')
    r_server.lpush('qa_11', 'Контакты')
    r_server.lpush('qa_11', 'Проблема с экспортом?')
    r_server.lpush('qa_11', 'Да, все сломалось')
    r_server.lpush('qa_11', 'Можно подробнее описать проблему?')




r_server = redis.Redis('localhost', decode_responses=True)
importation()





