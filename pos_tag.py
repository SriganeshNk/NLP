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


def get_Accuracy(result, test_check):
    tag = {}
    for i in range(len(result)):
        for j in range(len(result[i])):
            k = len(result[i][j][1].split('/')) - 1
            r = result[i][j][1].split('/')[k]
            t = test_check[i][j][1].split('/')[1]
            if r == t:
                if r not in tag:
                    other = {}
                    other[t] = 1
                    tag[r] = other
                else:
                    if t not in tag[r]:
                        tag[r][t] = 1
                    else:
                        tag[r][t] += 1
            else:
                if r not in tag:
                    other = {}
                    other[t] = 1
                    tag[r] = other
                else:
                    if t not in tag[r]:
                        tag[r][t] = 1
                    else:
                        tag[r][t] += 1
    return tag


if __name__ == '__main__':
    train, test, test_check = extract()
    tagger = bigram_train(train)
    result = bigram_tag(tagger, test)
    # checking for fine grained
    tag = get_Accuracy(result, test_check)
    for x in tag.keys():
        for y in tag[x].keys():
            print x, y, tag[x][y],
        print
    print "Overall Accuracy:", tagger.evaluate(test_check)
    coarse_grain(train)
    tagger = bigram_train(train)
    coarse_grain(test_check)
    coarse_grain(result)
    # Converting Result and test_check to coarse-grain and then checking
    tag = get_Accuracy(result, test_check)
    result = bigram_tag(tagger, test)
    # checking for coarse-grained
    tag = get_Accuracy(result, test_check)
    for x in tag.keys():
        for y in tag[x].keys():
            print x, y, tag[x][y],
        print
    print "Overall Accuracy:", tagger.evaluate(test_check)