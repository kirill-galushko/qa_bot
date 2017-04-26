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
import heapq
import numpy as np

# Регулярное выражение для латинских букв
latin_pattern = r'[A-Za-z]+'
# MorphAnalyzer для нормализации слов
morph = MorphAnalyzer()

# Класс для вопросов
class Question(object):
    def __init__(self, answer, id, text):
        self.answer = answer
        self.id = id
        self.text = text

# Обработчик строк. Удаление лишних символов, детранслитерация, нормализация(приведение к инфинитиву).
def str_handler(in_string):
    tokens = tokenizers.simple_word_tokenize(re.sub('[!?,.%]', '', in_string))
    new_strng = ''
    for word_in in tokens:
        if re.search(latin_pattern, word_in):
            word_in = translit.detranslify(word_in)
        new_strng += morph.parse(word_in)[0].normal_form + ' '
    return new_strng


class Admin(object):
    def main(self):

        parser = argparse.ArgumentParser(description='modeling Q&A system')

        args = parser.parse_args()

        # Импорт csv базы вопросов
        try:
            qa = []
            with open('new_qa_sample.csv', 'r') as f:
                reader = csv.reader(f)
                i = 0
                for row in reader:
                    i += 1
                    qa.append(Question(row[1], i, row[0]))

            # print(data)
            analyze(qa)

        except:
            traceback.print_exc()

# Функция анализа базы вопросов и последующего предсказания
def analyze(question):
    # Создание TFID векторайзера
    vectorizer = TfidfVectorizer(min_df=1)

    # Обработка строк вопросов
    corpus = []
    for qst in question:
        corpus.append(str_handler(qst.text))

    # Обучение векторайзера на уже подготовленной базе
    corpus = corpus
    vectorizer.fit_transform(corpus)
    print(vectorizer.get_feature_names()[0:100])

    # Перемешивание выборки для внесения элемента случайности
    data_target_tuples = []
    for qst in question:
        data_target_tuples.append((str_handler(qst.text), qst.answer))

    shuffle(data_target_tuples)

    # Трансформация вопросов в матричный вид, на основе TFID критерия
    x_data = []
    y_target = []
    # print(data_target_tuples)
    for t in data_target_tuples:
        v = (vectorizer.transform([t[0]]).toarray())[0]
        # print(v, ' ', t[0], ' ')
        x_data.append(v)
        y_target.append(t[1])

    x_data = np.asarray(x_data)
    y_target = np.asarray(y_target)
    # Тестовая валидация

    # rand_forest_scorer = RandomForestClassifier(max_depth=15, n_estimators=36, max_features=6)
    # scores = cross_val_score(OneVsRestClassifier(rand_forest_scorer), x_data, y_target)
    # print("Random Forest", scores.mean(), scores.std() * 2, 5)


    # Обучение случайного леса с заданными параметрами
    behavioral_profiler = RandomForestClassifier(max_depth=15, n_estimators=36, max_features=6)
    behavioral_profiler.fit(x_data, y_target)

    # Инициализация тестовой выборки
    x_test = []
    test_data = [
        'Какова стоимость и сроки услуг интеграции Vtiger CRM с внешними системами, платформами?',
        'Какова стоимость и сроки услуг интеграции Vtiger CRM с платформами?',
        'Какова стоимость услуг интеграции Vtiger CRM с внешними системами?',
        'Каковы сроки интеграции Vtiger CRM с внешними системами?',
        'Сколько будет стоить интеграция с внешними платформами?',
        'Какова стоимость интеграции с Asterisk?',
        'Какова стоимость интеграции с Астериском?'
    ]

    # Обработка тестовой выборки
    for t in test_data:
        v = (vectorizer.transform([str_handler(t)]).toarray())[0]
        x_test.append(v)

    # Предсказание вероятностей каждого ответа для каждого вопроса из тестовой выборки
    predict_data = behavioral_profiler.predict_proba(x_test)

    # Вывод 3 наиболее вероятных ответов
    for i in predict_data:
        # print(heapq.nlargest(3,  i))
        for j in i:
            if (j in heapq.nlargest(3, i)):
                print(behavioral_profiler.classes_[i.tolist().index(j)])
        print('\n')

if __name__ == "__main__":
    Admin().main()
