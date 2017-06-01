import csv
import redis


def importation():
    with open('qa_sample.csv', 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            i = i + 1
            print(*row)
            if i == 156:
                row.append('qa_1')
            else:
                row.append('q')
            r_server.hmset('qa_'+str(i), {'q': row[0], 'a': row[1], 'tags': row[2], 'parent': row[3]})

r_server = redis.Redis('localhost', decode_responses=True)
importation()





