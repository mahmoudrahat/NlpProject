#!/usr/bin/env python

import sys
from nagao.nagao import *
from tools.HamshahriParser import *;
from preprocessing.farsi import *
from preprocessing import general

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    sys.stdout = open('output/out.txt', 'w')
    hamshahri = load_hamshahri('E:/Mahmoud/Hamshahri/Corpus')
    hamshahri = map(lambda x: x.text, hamshahri)
    my_nagao = nagao()
    my_nagao.apply_algorithm(hamshahri)
    ngrams = my_nagao.get_ngram(2, True)
    for key,value in ngrams:
        print key
        print 'freq:' + str(value[0])
        print 'num_of_docs_containing_phrase:' + str(value[1])
        print '________________________________'

