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


if __name__ == '__main__':
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
    tagger = bigram_train(train)
    result = bigram_tag(tagger, test)
    print "Accuracy:", tagger.evaluate(test_check)