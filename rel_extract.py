import re
import operator

from sklearn import svm
from nltk.corpus import stopwords
from sklearn.metrics import accuracy_score

from parser import Parser
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


def manualExtract(train_data, test_data):
    # data, all_tokens = generate_arff.parse_data('train.tsv', None)
    words = wordDistribution(train_data)
    sorted_words = sorted(words.items(), key=operator.itemgetter(1), reverse=True)
    expression = sorted_words[:5]
    # data, all_tokens = generate_arff.parse_data('test.tsv', None)
    manual_predict = []
    ground_truth = []
    for x in test_data:
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


def constructTokens(data, length=200):
    words = wordDistribution(data)
    sorted_words = sorted(words.items(), key=operator.itemgetter(1), reverse=True)
    expression = sorted_words[:length]
    tokens = []
    for x in expression:
        tokens.append(x[0])
    return tokens


def constructBrownTokens():
    f = open('paths', 'r')
    words = {}
    for line in f:
        line = line.split()
        words[line[1].lower()] = int(line[0], 2)
    f.close()
    return words


def bowSVM(train_data, test_data, tokens, brown=False):
    # data, tokens = generate_arff.parse_data('train.tsv', 'test.tsv')
    # train_data, train_tokens = generate_arff.parse_data('train.tsv', None)
    #test_data, test_tokens = generate_arff.parse_data('test.tsv', None)
    feature_vector = None
    if brown:
        brown_tokens = constructBrownTokens()
        #tokens = constructTokens(data, length=500)
        feature_vector = generate_arff.create_feature_vectors(train_data, tokens, brown=brown_tokens)
    else:
        #tokens = constructTokens(data)
        feature_vector = generate_arff.create_feature_vectors(train_data, tokens)
    clf = svm.SVC(C=10.0, kernel='linear')
    label = []
    feature = []
    for x in range(len(train_data)):
        label.append(train_data[x][2])
        feature.append(feature_vector[x][:-1])
    clf.fit(feature, label)
    label = []
    if brown:
        feature_vector = generate_arff.create_feature_vectors(test_data, tokens, brown=brown_tokens)
    else:
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


def constructFV(dep, person, instit, sent):
    print "Sentence", sent, "\n"
    print "Person:", person, "Institute:", instit, "\n"
    print "Tree:", dep, "\n"


def dep_parser(train_data):
    stfParser = Parser()
    for x in train_data[34:36]:
        depend = stfParser.parseToStanfordDependencies(x[0] + ' ' + x[4] + ' ' + x[1])
        print "\n"
        result = [(rel, gov.text, dep.text) for (rel, gov, dep) in depend.dependencies]
        print "Judgement", x[2], "\n"
        print "Complete Sentence:\n"
        print x[3], "\n"
        constructFV(result, x[0], x[1], x[4])


if __name__ == "__main__":
    train_data, train_tokens = generate_arff.parse_data('train.tsv', None)
    # test_data, test_tokens = generate_arff.parse_data('test.tsv', None)
    # data, tokens = generate_arff.parse_data('train.tsv', 'test.tsv')
    #manualExtract(train_data, test_data)
    #tokens = constructTokens(data)
    #bowSVM(train_data, test_data, tokens, brown=False)
    #tokens = constructTokens(data,length=500)
    #bowSVM(train_data, test_data, tokens, brown=True)
    dep_parser(train_data)
