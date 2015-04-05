import re
import operator

from sklearn import svm
from nltk.corpus import stopwords
from sklearn.metrics import accuracy_score

import generate_arff


def wordDistribution(data, condition=False):
    stopSet = set(stopwords.words('english'))
    stopSet.add('He')
    stopSet.add('She')
    stopSet.add('born')
    words = {}
    for x in data:
        if condition or x[2] == 'yes':
            tokens = x[4].split()
            tokens = [w.strip('(').strip(')') for w in tokens if w.strip('(').strip(')') not in stopSet]
            for y in tokens:
                if y not in words:
                    words[y] = 1
                else:
                    words[y] += 1
    return words


def manualExtract():
    data, all_tokens = generate_arff.parse_data('train.tsv', None)
    words = wordDistribution(data)
    sorted_words = sorted(words.items(), key=operator.itemgetter(1), reverse=True)
    expression = sorted_words[:5]
    data, all_tokens = generate_arff.parse_data('test.tsv', None)
    manual_predict = []
    ground_truth = []
    for x in data:
        ground_truth.append(x[2])
        label = False
        for y in expression:
            m = re.search(y[0], x[3], flags=re.IGNORECASE)
            if m is not None:
                label = True
                break
        if label:
            manual_predict.append('yes')
        else:
            manual_predict.append('no')
    print accuracy_score(ground_truth, manual_predict)


def constructTokens(data):
    words = wordDistribution(data)
    sorted_words = sorted(words.items(), key=operator.itemgetter(1), reverse=True)
    expression = sorted_words[:200]
    tokens = []
    for x in expression:
        tokens.append(x[0])
    return tokens


def bowSVM():
    data, tokens = generate_arff.parse_data('train.tsv', 'test.tsv')
    tokens = constructTokens(data)
    train_data, train_tokens = generate_arff.parse_data('train.tsv', None)
    test_data, test_tokens = generate_arff.parse_data('test.tsv', None)
    feature_vector = generate_arff.create_feature_vectors(train_data, tokens)
    clf = svm.SVC(C=10.0, kernel='linear')
    label = []
    feature = []
    for x in range(len(train_data)):
        label.append(train_data[x][2])
        feature.append(feature_vector[x][:-1])
    clf.fit(feature, label)
    label = []
    feature_vector = generate_arff.create_feature_vectors(test_data, tokens)
    for x in feature_vector:
        label.append(clf.predict(x[:-1]))
    ground_truth = []
    for x in test_data:
        ground_truth.append(x[2])
    print accuracy_score(ground_truth, label)


"""
def makeSentences():
    data, all_tokens = generate_arff.parse_data('train.tsv', 'test.tsv')
    f = open('sentences.txt','w')
    for x in data:
        print>>f, x[3].encode('utf8')
    f.close()
"""


def brownCluster():
    return

if __name__ == "__main__":
    manualExtract()
    bowSVM()
    brownCluster()
