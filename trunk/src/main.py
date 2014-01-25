#!/usr/bin/env python

import sys
from nagao.nagao import *
from tools.HamshahriParser import *;
from preprocessing.farsi import *
from preprocessing import general
from tools.corpusNormalizer import *
import redis

if __name__ == '__main__':
    red = redis.Connection('10.25.25.242')
    red.connect()
    red.send_command("ping")
    res = red.read_response()
    
    reload(sys)
    sys.setdefaultencoding("utf-8")
    #sys.stdout = open('output/out.txt', 'w')
    #hamshahri = load_hamshahri('d:/Hamshahri/Corpus')
    #normalize_corpus(hamshahri, 'D:/Hamshahri/Normalized')
    corpus = load_corpus('D:/Hamshahri/Normalized', 10)
    print 'End'

    """
    hamshahri = map(lambda x: remove_puncts(normalize(general.safeunicode(x.text.replace('\n', ' ').replace('\r', ' ').replace(HALF_SPACE, ' ')))), hamshahri)
    for idx, doc in enumerate(hamshahri):
        file = open("output/doc" + str(idx+1) + ".txt","w");
        file.write(doc);
        file.close();
    
    my_nagao = nagao()
    my_nagao.apply_algorithm(hamshahri)
    ngrams = my_nagao.get_ngram(4, True)
    for key,value in ngrams:
        print key
        print 'freq:' + str(value[0])
        print 'num_of_docs_containing_phrase:' + str(value[1])
        print '________________________________'
    """
