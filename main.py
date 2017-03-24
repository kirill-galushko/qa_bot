import argparse
import traceback
import glob
import nltk
import string
import random
import json
import csv
import traceback
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from random import shuffle
import sklearn
from sklearn.svm import SVC
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier


class Admin(object):
    """
    Main client for modeling customer profile data with text.
    """

    def main(self):

        parser = argparse.ArgumentParser(description='modeling customer profile data with text')
        parser.add_argument('-g', action='store_true', help="generate customer and behavioral profile data")
        parser.add_argument('-a', action='store_true', help="analyze behavioral profile data")

        args = parser.parse_args()

        try:
            qa = []
            with open('qa_sampl2.csv', 'r') as f:
                reader = csv.reader(f)
                i = 0
                for row in reader:
                    i += 1
                    qa.append(Question(row[1], i, row[0]))

            # print(data)
            analyze(qa)

        except:
            traceback.print_exc()


def analyze(question):

    vectorizer = TfidfVectorizer(min_df=1)

    corpus = []
    for qst in question:
        corpus.append(qst.text)

    vectorizer.fit_transform(corpus)

    print(vectorizer.get_feature_names()[0:100])

    # Randomize the observations
    data_target_tuples = []
    for qst in question:
        data_target_tuples.append((qst.text, qst.answer))

    shuffle(data_target_tuples)

    x_data = []
    y_target = []
    for t in data_target_tuples:
        v = (vectorizer.transform([t[0]]).toarray())[0]
        # print(v, ' ', t[1], ' ')
        x_data.append(v)
        y_target.append(t[1])

    x_data = np.asarray(x_data)
    y_target = np.asarray(y_target)
    rand_forest_scorer = RandomForestClassifier(max_depth=15, n_estimators=25, max_features=5)
    scores = cross_val_score(rand_forest_scorer, x_data, y_target)
    print("Random Forest", scores.mean(), scores.std() * 2, 5)

    behavioral_profiler = RandomForestClassifier(max_depth=15, n_estimators=25, max_features=5)
    behavioral_profiler.fit(x_data, y_target)

    print(behavioral_profiler.predict(vectorizer.transform(['Какова стоимость и сроки услуг интеграции Vtiger CRM с внешними системами, платформами?']).toarray()[0]))
    print(behavioral_profiler.predict(vectorizer.transform(['Какова стоимость и сроки услуг интеграции Vtiger CRM с платформами?']).toarray()[0]))
    print(behavioral_profiler.predict(vectorizer.transform(['Какова стоимость услуг интеграции Vtiger CRM с внешними системами?']).toarray()[0]))
    print(behavioral_profiler.predict(vectorizer.transform(['Каковы сроки интеграции Vtiger CRM с внешними системами?']).toarray()[0]))
    print(behavioral_profiler.predict(vectorizer.transform(['Сколько будет стоить интеграция с внешними платформами?']).toarray()[0]))
    print(behavioral_profiler.predict(vectorizer.transform(['Сколько стоит интеграция с Asterisk?']).toarray()[0]))


class Question(object):
    def __init__(self, answer, id, text):
        self.answer = answer
        self.id = id
        self.text = text

if __name__ == "__main__":
    Admin().main()
