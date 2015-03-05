__author__ = 'sriganesh'

import re

import nltk
from nltk.tag.sequential import BigramTagger


def bigram_train(tr):
    unigram_tagger = nltk.UnigramTagger(train=tr, backoff=nltk.DefaultTagger('NN'))
    tagger = BigramTagger(train=tr, backoff=unigram_tagger)
    return tagger


def bigram_tag(tagger, test):
    result = []
    for x in test:
        L = tagger.tag(x)
        result.append(L)
    return result


def separate(line, keep=True):
    L = line.split()
    for x in range(len(L)):
        m = re.search('[^\\\\ ]/.*', L[x])
        if m is not None:
            if keep:
                L[x] = (L[x][0:m.start() + 1], L[x][m.start() + 1:])
            else:
                L[x] = L[x][0:m.start() + 1]
    return L[1:]


def extract():
    f = open('treebank_sentences.txt', 'r')
    train = []
    test = []
    test_check = []
    i = 0
    for line in f:
        if i >= 500:
            test.append(separate(line, keep=False))
            test_check.append(separate(line, keep=True))
        else:
            train.append(separate(line, keep=True))
        i += 1
    return (train, test, test_check)


def coarse_grain(tags):
    coarse_tags = {"NN": "SNN", "NNS": "SNN", "NNP": "SNN", "NNPS": "SNN", "PRP": "SNN", "PRPS": "SNN", "VB": "SVB",
                   "VBP": "SVB", "VBD": "SVB", "VBN": "SVB", "VBZ": "SVB", "VBG": "SVB", "JJ": "SJJ", "JJR": "SJJ",
                   "JJS": "SJJ", "RB": "SRB", "RBR": "SRB", "RBS": "SRB"}
    for x in range(len(tags)):
        for y in range(len(tags[x])):
            k = len(tags[x][y][1].split('/')) - 1
            temp = tags[x][y][1].split('/')[k]
            if temp in coarse_tags:
                tags[x][y] = (tags[x][y][0], '/' + coarse_tags[temp])


def get_TagMap(result, test_check):
    tag = {}
    for i in range(len(result)):
        for j in range(len(result[i])):
            k = len(result[i][j][1].split('/')) - 1
            r = result[i][j][1].split('/')[k]
            t = test_check[i][j][1].split('/')[1]
            if r == t:
                if t not in tag:
                    other = {}
                    other[r] = 1
                    tag[t] = other
                else:
                    if r not in tag[t]:
                        tag[t][r] = 1
                    else:
                        tag[t][r] += 1
            else:
                if t not in tag:
                    other = {}
                    other[r] = 1
                    tag[t] = other
                else:
                    if r not in tag[t]:
                        tag[t][r] = 1
                    else:
                        tag[t][r] += 1
    return tag


def get_Matrix(tag):
    tag_index = {}
    pos_index = {}
    i = 0
    for x in tag.keys():
        for y in tag[x].keys():
            if y not in tag_index:
                tag_index[y] = i
                pos_index[i] = y
                i += 1
        if x not in tag_index:
            tag_index[x] = i
            pos_index[i] = x
            i += 1
    mat = [[0 for j in range(len(tag_index.keys()))] for i in range(len(tag_index.keys()))]
    for i in range(len(mat)):
        for j in range(len(mat)):
            if pos_index[i] in tag and pos_index[j] in tag[pos_index[i]]:
                mat[i][j] = tag[pos_index[i]][pos_index[j]]
    return mat, pos_index


def get_accuracy(tag, pos):
    count = sum(tag)
    print float(tag[pos]) / float(count)


def display(result):
    if isinstance(result, list):
        for x in result:
            print x
        return
    if isinstance(result, str):
        print result


if __name__ == '__main__':
    train, test, test_check = extract()
    # Train using Fine-grained
    tagger = bigram_train(train)
    # Train using Coarse-grained
    result = bigram_tag(tagger, test)
    # Checking for fine grained
    tag = get_TagMap(result, test_check)
    # Get the confusion matrix
    mat, pos_index = get_Matrix(tag)
    # Overall Accuracy for fine grained parser
    print "Overall Accuracy:", tagger.evaluate(test_check)
    # Convert training tags to coarse grained
    coarse_grain(train)
    # Convert test data tags to coarse grained
    coarse_grain(test_check)
    # Convert Result tags to coarse grained
    coarse_grain(result)
    # Converting Result and test_check to coarse-grain and then checking
    tag = get_TagMap(result, test_check)
    # Get Confusion matrix for the checking part
    mat, pos_index = get_Matrix(tag)
    # train using bigram tagger for the coarse grained tags
    tagger = bigram_train(train)
    # test the bigram tagger using coarse tags
    result = bigram_tag(tagger, test)
    # checking for coarse-grained tags
    tag = get_TagMap(result, test_check)
    # Get Confusion matrix for the checking part
    mat, pos_index = get_Matrix(tag)
    print "Overall Accuracy:", tagger.evaluate(test_check)