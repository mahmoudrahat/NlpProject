#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Mahmoud Rahat
# Version 1.3

from sets import Set
from preprocessing.farsi import *
from preprocessing import general
from normalizer import *
from time import clock, time
import time
import redis
import sys

start = clock()

# splits input text and returns a tuple(concatination of all words in text, a list of starting index of all words in text)
def split_text(text):
    words = text.split(' ')
    idx = 0
    l = []
    for w in words:
        l.append(idx)
        idx += len(w) + 1
    return l

# fills coincedent array as described in the paper A new method of ngram statistics ... by Makoto Nagao
def get_coincidence_old(safe_text, l):
    coincidence = []
    length = len(safe_text)
    for i in xrange(len(l)-1):
        coincidence_num = 0
        for k in xrange(100):
            if l[i]+k>=length or l[i+1]+k>=length or safe_text[l[i]+k] != safe_text[l[i+1]+k]:
                break
            if safe_text[l[i]+k] == ' ':
                coincidence_num += 1
        coincidence.append(coincidence_num)
    
    # add zero coincidence for the last entry
    coincidence.append(0)
    return coincidence

# fills coincedent array as described in the paper A new method of ngram statistics ... by Makoto Nagao
def get_coincidence(safe_text, l):
    coincidence = []
    length = len(safe_text)
    for i in xrange(len(l)-1):
        coincidence_num = 0
        coincidence_length = 0
        for k in xrange(15):
            (token1, idx1) = get_next_token(safe_text, l[i] + coincidence_length)
            (token2, idx2) = get_next_token(safe_text, l[i+1] + coincidence_length)
            coincidence_length += len(token1) + 1
            if token1 == '' or token2 == '' or token1 != token2:
                break
            coincidence_num += 1
        coincidence.append(coincidence_num)
    
    # add zero coincidence for the last entry
    coincidence.append(0)
    return coincidence

# gets next token starting from <startIdx> using <text>
def get_next_token(text, startIdx):
    token = ''
    i = startIdx
    while i<len(text):
        if text[i] == ' ':
            break
        token += text[i]
        i += 1
    return (token, i)

# gets as long as <length> tokens starting from <startIdx> using <text>
def get_token(text, startIdx, length):
    token = ''
    count = 0
    i = startIdx
    while i<len(text) and count<length:
        token += text[i]        
        i=i+1
        if i==len(text) or text[i]==' ':
            count+=1
    if i == len(text) and count != length:
        token = None
    return token

# this function has been written to test nagao implimantation
def display_nagao_internal_variables(text, l, coincidence):
    counter = 0
    for idx in l:
        print idx,
        for i in reversed(range(1,6)):
            token = get_token(text, idx, i)
            if token != None:
                print token,
                break
        print coincidence[counter]
        print '________________________________________________'
        counter += 1

# using text, l (sorted list of all normalized tokens), coincidence and n computes ngrams
def get_ngram(text, l, coincidence, n):
    i = 0
    ngrams = {}
    while i < len(coincidence):
        iteration = 0
        while i+iteration<len(coincidence) and coincidence[i+iteration]>=n:
            iteration += 1
        ngram = get_token(text, l[i], n)
        if ngram != None:
            freq = iteration + 1
            ngrams[get_token(text, l[i], n)] = freq
            i += iteration
        i+=1
    # sorting the result based on the iteration
    ngrams = sorted(ngrams.iteritems(), key=lambda (k,v):(v,k))
    
    #for key,value in ngrams:
    #    print key, value
    return ngrams

# normalizes input text. make a list of all tokens. sorts them. computes
# coincidence array. saves this data in redis for using with get_ngram function
# inorder to save data on redis we need to save text + l + coincidence in redis
def nagao_ngrams_redis(text, red):
    l = split_text(text)
    print 'end of making list of all words ...'
    l.sort(key=lambda i: text[i:i+40])
    print 'end of sorting ...'
    coincidence = get_coincidence(text, l)
    print 'end of filling coincidence array ...'
    
    # saving text + l + coincidence in redis
    red.flushdb()
    
    red.set('text', text)
    print 'end of putting text on redis ...'
    
    for index in l:    
        red.rpush("l", index)
    print 'end of putting index array on redis ...'
    
    for value in coincidence:
        red.rpush("coincidence", value)
    print 'end of putting coincidence array on redis ...'
    
    return (text, l, coincidence)

# makes a list of all tokens. sorts them. computes coincidence array. 
def nagao_ngrams_doc_based(text, red):
    l = split_text(text)
    print 'end of making list of all words ...'
    l.sort(key=lambda i: text[i:i+100])
    print 'end of sorting ...'
    coincidence = get_coincidence(text, l)
    print 'end of filling coincidence array ...'
                
    return (text, l, coincidence)

# loads text, l, coincidence from redis
# befor using first first use function nagao_ngrams(text, red) to save data on redis
def load_ngram_data_from_redis(red):
    text = red.get('text')
    print 'end of loading text data from redis'
    
    length = red.llen('l')
    l = red.lrange('l', 0, length)    
    l = map(lambda x: int(x), l)    
    print 'end of loading list (l) from redis'
        
    coincidence = red.lrange('coincidence', 0, length)
    coincidence = map(lambda x:int(x), coincidence)
    print 'end of loading list (coincidence) from redis'    
    return (text, l, coincidence)

# store ngram on redis as a hash table. variables text,l,coincidence must be loaded from redis before calling
# this procidure
def store_ngram_on_redis(n, redis, text, l, coincidence):
    print 'storing ' + str(n) + 'gram on redis' 
    ngrams = get_ngram(text, l, coincidence, n)
    for key, value in reversed(ngrams):
        red.hset(str(n)+'gram', key, value)
        
# store ngram on file name:<"data/output" + str(n) + "-gram">
def store_ngram_on_file(n, redis, text, l, coincidence):
    print 'storing ' + str(n) + 'gram on file data/output ' + str(n) + '-gram'
    ngrams = get_ngram(text, l, coincidence, n)
    f = open('data/output ' + str(n) + '-gram', 'w')
    for key, value in reversed(ngrams):
        f.write(key  + ' ' + str(value) + '\n')
    f.close()
    print 'end of storing ' + str(n) + 'gram on file data/output ' + str(n) + '-gram'

# input is a text. output is a bag of ngrams containing all the ngrams and frequencies on the text
# ************ IMPORTANT ************
# the idea of -bag of ngrams- has a problem. for instance, suppose we have this line in the text 'sepahe pasdaran enghelabe eslami'
# as we know, our algorithm for bag of ngrams returns one 4gram for this text. but if we ask our algorithm to return TFIDF for this
# ('sepahe pasdaran') 2gram. it will return 0. and this is incorrect. because the result should be 1. to sove he problem we
# defined a new <get_all_ngrams_on_text> function named <get_all_ngrams_on_text>
def get_bag_of_ngrams_model(text, redis):
    # compute list of all tokens in the text    
    ngrams = get_all_ngrams_on_text(text, redis)
    
    # computing bag of ngrams model
    bag_of_ngrams = {}
    for gram in ngrams:
        if gram in bag_of_ngrams:
            bag_of_ngrams[gram] += 1
        else:
            bag_of_ngrams[gram] = 1
    
    return bag_of_ngrams

# input is a normalized text and redis connection to an ngram database. output is all the ngrams on the text
def get_all_ngrams_on_text(text, red):
    startIdx = 0
    max_n_to_search = 10
    ngrams = []
    
    while True:
        if startIdx >= len(text)-1:
            break
        for i in reversed(range(2,max_n_to_search)):
            tokens = get_token(text,startIdx ,i)
            if tokens == None:
                continue		    
            name = str(i)+'gram'
            if red.hexists(name, tokens.strip()):
                startIdx = startIdx + len(tokens)
                ngrams.append(tokens.strip())
                i = 1
                break
        
        if i != 1:
            tokens = get_token(text,startIdx ,1)
            ngrams.append(tokens.strip())
            startIdx = startIdx + len(tokens)
    return ngrams

# corpus is a list of documents body. This function reads each documents, computes bag of ngrams for it, stores this data on redis
# befor calling this function first use store_ngram_on_redis to store all ngrams on the redis
def store_corpus_ngrams_on_redis(corpus, red):    
    print 'start of computes bag of ngrams model for each document and biulding corpus hash table on redis size of corpus is:' + str(len(corpus))
    
    # set information of corpus 
    #red.hset('corpus', 'information', 'test corpus containing 7 docs from nasim database')

    # set the number of docuents in the corpus    
    red.hset('corpus', 'count', len(corpus))

    index = 0
    for doc in corpus:
        print 'computing bag of ngrams model for document number ' + str(index) + '/' + str(len(corpus))
        model = get_bag_of_ngrams_model(doc, red)
        
        # put doc body in the redis
        red.hset('corpus', 'doc'+str(index), doc)

        for key, value in model.items():
            # put ngram value and keys on redis
            red.hset('corpus', 'doc'+str(index)+':' + key, value)
        index += 1
    print 'end of biulding corpus hash table on redis'
            
# applies nagao ngrams on corpus. stores it's data and all [1..9] grams on redis
# it uses the corpus to build ngrams first and then uses this ngrams to compute bag of ngram model for each document
def apply_nagao_ngrams_store_on_redis(corpus, red):
    
    # concatinating all docs to form text variable which is all the docs in the corpus
    text = u''.join(corpus)
    
    # appling nagao alghorithm on the corpus
    print 'start appling nagao alghorithm on the corpus size:' + str(len(text)) + ' of characters'    
    (text, l, coincidence) = nagao_ngrams_redis(text, red)
    
    # display nagao internal variables    
    #display_nagao_internal_variables(text, l, coincidence)    

    # store computed ngrams on redis
    print 'start storing computed ngrams on redis'
    for i in range(1,10):
        store_ngram_on_redis(i, red, text, l, coincidence)
    
    # builds corpus has table on redis
    store_corpus_ngrams_on_redis(corpus, red)
    
# reads corpus data from a txt file. uses new line character ('\n') as delimiter between docs. returns corpus which is a
# list of all normalized docs on the text file
def read_corpus_from_file(filepath):
    print 'reading corpus from file: ' + filepath
    corpus = []
    # reading the file. each document should be in a line. so doc delimiter is \n character
    f = open(filepath, 'r')
    while True:        
        doc =f.readline()
        # eliminating '\n' characters from doc
        doc = doc.replace('\n', ' ')
        doc = doc.strip()
        if doc == '':
            break
        corpus.append(doc)
    f.close()
    print 'end of reading corpus from file. size of corpus is ' + str(len(corpus)) + ' documents'
    return corpus

# just like store_ngram_on_redis but it is modified to update data on redis rather than replace it
def store_ngram_on_redis_doc_based(n, redis, text, l, coincidence):
    print 'storing ' + str(n) + 'gram on redis' 
    ngrams = get_ngram(text, l, coincidence, n)
    for key, value in ngrams:
        v = red.hget(str(n)+'gram', key)
        if v == None:
            red.hset(str(n)+'gram', key, value)
        else:
            red.hset(str(n)+'gram', key, int(v) + value)
# applies nagao ngrams on doc. adds it's data and all [1..9] grams on redis
# it uses the doc to build ngrams first. NOTE that the diffrece between this method and <apply_nagao_ngrams_store_on_redis> is that this method
# is able to handle one stand alone document and updates redis data for this document. 
# call this method for each document of the corpus.
def apply_nagao_ngrams_store_on_redis_doc_based(doc, red):
    text = doc
    # appling nagao alghorithm on the doc
    print 'start appling nagao alghorithm on the document size:' + str(len(text)) + ' of characters'    
    (text, l, coincidence) = nagao_ngrams_doc_based(text, red)
    
    # display nagao internal variables    
    #display_nagao_internal_variables(text, l, coincidence)  

    # store computed ngrams on redis
    print 'start storing computed ngrams on redis'
    for i in range(1,10):
        store_ngram_on_redis_doc_based(i, red, text, l, coincidence)
    
    

if __name__ == '__main__':    
    reload(sys)
    sys.setdefaultencoding("utf-8")
        
    filename = 'delete'
    db = '6'
    corpus = read_corpus_from_file('data/' + filename)
    # connecting to redis
    red = redis.Redis(host='localhost', port=6379, db=db)

    # flush away previus data from redis
    s = raw_input('Do you want to erase all data from database number '+ db + '?(y or n) --> ')
    if s == 'y':
        red.flushdb()

    startIdx = 0
    for i in range(startIdx, len(corpus)):
        doc = corpus[i]
        print '__________________________________________________________________'
        print "processing document number " + str(i)
        apply_nagao_ngrams_store_on_redis_doc_based(doc, red)
        # save the id of last proccessed document        
        red.set('document idx', i, 1, 1)

    # set database information after this function <apply_nagao_ngrams_store_on_redis> because it flushes the db
    # befor any insertion hapens
    red.set('information', 'corpus name is <' + filename + '> number of news in the corpus is ' + str(len(corpus)))

    sys.exit(0)
    
    # reading normalized text from input
    # to normalize the raw text first use text_normailizer function in normalizer.py 
    f = open('data/input1', 'r')
    text = f.read()
    f.close()
    
    # connecting to redis
    red = redis.Redis(host='localhost', port=6379, db='4')

    # ****WARNING**** comment this line if you do not want to save new data on redis otherwise redis data will be flushed away
    # data base 3 has data for 108M input text which is all data in newsplaintext file
    # red.set('information', 'this database has 2.5 MegaByte of processed text data from newsplaintext2.5M')
    # nagao_ngrams_redis(text, red)
    
    
    #(text, l, coincidence) = load_ngram_data_from_redis(red)
    
    #store_ngram_on_file(2, redis, text, l, coincidence)
    
    #store_ngram_on_redis(3, red, text, l, coincidence)
    
    elapsed = (clock() - start)
    print elapsed


    f = open('data/normalized', 'r')
    text = f.read()
    f.close()
    text = text_normalizer(text).strip()
        
    corpus = []
    temp = ''
    for c in text:
        if c=='\t':
            if temp!='' and temp!='\n' and temp.strip()!='' and len(temp)>5:
                corpus.append(temp)            
            temp = ''
            continue
        temp+=c
        
    ngrams = store_corpus_ngrams_on_redis(corpus, red)





