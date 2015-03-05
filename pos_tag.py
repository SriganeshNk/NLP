__author__ = 'sriganesh'

import re

import nltk
from nltk.tag.sequential import BigramTagger


def bigramTrain(tr, default):
    unigram_tagger = nltk.UnigramTagger(train=tr, backoff=nltk.DefaultTagger(default))
    tagger = BigramTagger(train=tr, backoff=unigram_tagger)
    return tagger


def bigramTag(tagger, test):
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
    f.close()
    return (train, test, test_check)


def coarseGrain(tags):
    coarse_tags = {"NN": "SNN", "NNS": "SNN", "NNP": "SNN", "NNPS": "SNN", "PRP": "SNN", "PRPS": "SNN", "VB": "SVB",
                   "VBP": "SVB", "VBD": "SVB", "VBN": "SVB", "VBZ": "SVB", "VBG": "SVB", "JJ": "SJJ", "JJR": "SJJ",
                   "JJS": "SJJ", "RB": "SRB", "RBR": "SRB", "RBS": "SRB"}
    for x in range(len(tags)):
        for y in range(len(tags[x])):
            k = len(tags[x][y][1].split('/')) - 1
            temp = tags[x][y][1].split('/')[k]
            if temp in coarse_tags:
                tags[x][y] = (tags[x][y][0], '/' + coarse_tags[temp])


def getTagMap(result, test_check):
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


def getMatrix(tag):
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


def getIndividualAccuracy(mat, pos, perm):
    f = open('Report', perm)
    line = "        "
    needed = {'JJ': 1, 'NN': 1, 'NNP': 1, 'NNPS': 1, 'RB': 1, 'RP': 1, 'IN': 1, 'VB': 1, 'VBD': 1, 'VBN': 1, 'VBP': 1,
              'SNN': 1, 'SVB': 1, 'SJJ': 1, 'SRB': 1}
    for x in pos.keys():
        if pos[x] in needed:
            line += str(pos[x]) + ' '
    line.strip()
    print>> f, line
    for i in range(len(mat)):
        if pos[i] in needed:
            line = pos[i] + "       "
            for j in range(len(mat)):
                if pos[j] in needed:
                    line += ' ' + str(mat[i][j])
            line.strip()
            print>> f, line
    print>> f, '\n\n\n\n'
    print>> f, 'Tags' + '      ' + 'Accuracy'
    for x in pos.keys():
        print>> f, str(pos[x]) + '     ' + str(getAccuracy(mat[x], x))
    total = 0
    correct = 0
    for x in pos.keys():
        total += sum(mat[x])
        correct += mat[x][x]
    print>> f, "Overall      " + str(float(correct) / float(total))
    print>> f, '\n\n\n\n'
    f.close()
    return float(correct) / float(total)


def getAccuracy(tag, pos):
    count = sum(tag)
    return float(tag[pos]) / float(count)


def writeFile(filename, test, result):
    f = open(filename, 'w')
    k = 0
    for i in range(len(test)):
        line = str(k)
        temp = ""
        for j in range((len(test[i]))):
            temp += test[i][j][0] + test[i][j][1] + ' '
        temp.strip()
        line += '   ' + temp + '    '
        temp = ""
        for j in range((len(test[i]))):
            temp += result[i][j][0] + result[i][j][1] + ' '
        temp.strip()
        line += temp
        print>> f, line
        k += 1
    f.close()


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
    tagger = bigramTrain(train, '/NN')
    # Train using Coarse-grained
    result = bigramTag(tagger, test)
    # Write to file
    writeFile('Part-I', test_check, result)
    # Checking for fine grained
    tag = getTagMap(result, test_check)
    # Get the confusion matrix
    mat, pos_index = getMatrix(tag)
    # Overall Accuracy for fine grained parser
    print "Overall Accuracy: Part - I: ", tagger.evaluate(test_check)
    # Get individual accuracy
    getIndividualAccuracy(mat, pos_index, 'w')
    # Convert training tags to coarse grained
    coarseGrain(train)
    # Convert test data tags to coarse grained
    coarseGrain(test_check)
    # Convert Result tags to coarse grained
    coarseGrain(result)
    # Write to file
    writeFile('Method-A', test_check, result)
    # Converting Result and test_check to coarse-grain and then checking
    tag = getTagMap(result, test_check)
    # Get Confusion matrix for the checking part
    mat, pos_index = getMatrix(tag)
    # Get individual accuracy
    print "Overall Accuracy: Method A: ", getIndividualAccuracy(mat, pos_index, 'a')
    # train using bigram tagger for the coarse grained tags
    tagger = bigramTrain(train, '/SNN')
    # test the bigram tagger using coarse tags
    result = bigramTag(tagger, test)
    # Write to file
    writeFile('Method-B', test_check, result)
    # checking for coarse-grained tags
    tag = getTagMap(result, test_check)
    # Get Confusion matrix for the checking part
    mat, pos_index = getMatrix(tag)
    # Get individual accuracy
    getIndividualAccuracy(mat, pos_index, 'a')
    # Overall Accuracy for fine grained parser
    print "Overall Accuracy: Method B: ", tagger.evaluate(test_check)