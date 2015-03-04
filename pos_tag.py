__author__ = 'sriganesh'

import re


f = open('treebank_sentences.txt', 'r')
sentences = []
for line in f:
    L = line.split()
    for x in range(len(L)):
        m = re.search('[\w,*]/.*', L[x])
        if m is not None:
            L[x] = L[x][0:m.start() + 1]
    sentences.append(L[1:])

