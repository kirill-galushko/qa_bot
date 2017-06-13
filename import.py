import redis


def importation():
    r_server.lpush('qa_1', 'CRM')
    r_server.lpush('qa_1', 'Какой модуль?')

    r_server.lpush('qa_2', 'Консультация')
    r_server.lpush('qa_2', 'Техническая проблема или вопросы по оплате?')

    r_server.lpush('qa_3', 'Демо')
    r_server.lpush('qa_3', 'Демо какого проекта вы бы хотели получить?')

    r_server.lpush('qa_4', 'CRM')
    r_server.lpush('qa_4', 'Контакты')
    r_server.lpush('qa_4', 'Проблема со какими-то полями?')

    r_server.lpush('qa_5', 'Я бы хотел что-то там CRM')
    r_server.lpush('qa_5', 'Какой модуль?')

r_server = redis.Redis('localhost', decode_responses=True)
importation()





