import argparse
import traceback
import glob
import string
import random
import json
from pytils import translit
from pymorphy2 import tokenizers, MorphAnalyzer
import re
import csv
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from random import shuffle
from heapq import nlargest
import numpy as np
import redis
from collections import defaultdict

# Регулярное выражение для латинских букв
latin_pattern = r'[A-Za-z]+'
# MorphAnalyzer для нормализации слов
morph = MorphAnalyzer()


# Класс для вопросов
class Question(object):
    """Объект для хранения вопросов и ответов к ним

    """
    def __init__(self, text, answer):
        self.text = text
        self.answer = answer


def str_handler(in_string):
    """Обработчик строк. Удаление лишних символов, детранслитерация, нормализация(приведение к инфинитиву).

    Keyword arguments:
    in_string -- строка для обработки

    """
    tokens = tokenizers.simple_word_tokenize(re.sub('[!?,.%]', '', in_string))
    new_string = ''
    for word_in in tokens:
        if re.search(latin_pattern, word_in):
            word_in = translit.detranslify(word_in)
        new_string += morph.parse(word_in)[0].normal_form + ' '
    return new_string


def get_most_probable(profiler, v):
    """Функция возвращает 3 наиболее вероятных ответа.

    Keyword arguments:
    profiler -- объект обученного случайного леса
    v -- вектор векторизированного вопроса

    """

    # Предсказание вероятностей каждого ответа для каждого вопроса из тестовой выборки
    predict_data = profiler.predict_proba(v)
    ans = []
    # Вывод 3 наиболее вероятных ответов
    for i in predict_data:
        for j in i:
            if j in nlargest(3, i):
                ans.append(profiler.classes_[i.tolist().index(j)])
                # ans.append(i.tolist().index(j))
    return ans


def preprocessing(answer_array):
    """Функция, которая подготавливает выборку в зависимости от выбранного тэга

    Keyword arguments:
    question -- Текст вопроса

    """
    r_server = redis.StrictRedis('localhost', charset="utf-8", decode_responses=True)

    qa = []
    for key in r_server.scan_iter():
        row = r_server.lrange(key, 0, r_server.llen(key))
        row.reverse()

        if len(answer_array) == 1:
            if len(row) == 2:
                qa.append(Question(row[-2], row[-1]))
        # elif len(answer_array) == 3:
        #     if answer_array[0:-1] == row[0:2] and len(row) == 4:
        #         qa.append(Question(row[-2], row[-1]))
        else:
            if answer_array[0:-1] == row[0:-2]:
                qa.append(Question(row[-2], row[-1]))

    return analyze(qa, answer_array[-1])


def analyze(questions, args):
    """Функция анализа базы вопросов и последующего предсказания

    Keyword arguments:
    questions -- вектор объектов вопрос-ответ
    args -- заданный вопрос

    """

    # Создание TFID векторайзера
    vectorizer = TfidfVectorizer(min_df=1)

    # Обработка строк вопросов
    corpus = []
    for qst in questions:
        corpus.append(str_handler(qst.text))

    # Обучение векторайзера на уже подготовленной базе
    corpus = corpus
    vectorizer.fit_transform(corpus)

    # Перемешивание выборки для внесения элемента случайности
    data_target_tuples = []
    for qst in questions:
        data_target_tuples.append((str_handler(qst.text), qst.answer))

    shuffle(data_target_tuples)

    # Трансформация вопросов в матричный вид, на основе TFID критерия
    x_data = []
    y_target = []
    for t in data_target_tuples:
        v = (vectorizer.transform([t[0]]).toarray())[0]
        x_data.append(v)
        y_target.append(t[1])

    x_data = np.asarray(x_data)
    y_target = np.asarray(y_target)

    # Обучение случайного леса с заданными параметрами
    profiler = RandomForestClassifier(max_depth=15, n_estimators=36, max_features=2)
    profiler.fit(x_data, y_target)

    v = (vectorizer.transform([str_handler(args)]).toarray())[0]

    return get_most_probable(profiler, v)
