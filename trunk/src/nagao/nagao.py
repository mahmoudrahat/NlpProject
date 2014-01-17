#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Mahmoud Rahat
# Version 1.1

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import types
import sets
from config import *

class nagao:
    def __init__(self):
        pass

    # input is a list of documents (corpus). in case of having one doc, create a list with length one from it.
    # computes self.text that is all doc's concated together. self.l that is start index of all words in document
    def __split_corpus(self, corpus):
        # isinstance checks whether corpus is a list of documents or only one document
        # we expect corpus to be a list of documents
        if isinstance(corpus, types.ListType):
            self.text = u''
            # documents index
            idx_doc = 0
            self.doc_idx = {}
            # words start index
            idx_word = 0
            self.l = []
            for doc in corpus:
                doc = unicode(doc)
                self.text += doc + ' '
                words = doc.split(' ')
                for w in words:
                    self.l.append(idx_word)
                    # keeps track of document idenx
                    self.doc_idx[idx_word] = idx_doc
                    idx_word += len(w) + 1
                idx_doc += 1
            log( 'This document/chunk contains ' + str(len(self.l)) + ' words...' )
        else:
            raise Exception("corpus must be a list of documents. in a case of single doc, make a list with one member. like corpus = [doc]")
        

    # fills coincedent array as described in the paper A new method of ngram statistics ... by Makoto Nagao
    def __get_coincidence(self):
        coincidence = []
        length = len(self.text)
        for i in xrange(len(self.l)-1):
            coincidence_num = 0
            coincidence_length = 0
            for k in xrange(15):
                (token1, idx1) = self.__get_next_token(self.l[i] + coincidence_length)
                (token2, idx2) = self.__get_next_token(self.l[i+1] + coincidence_length)
                coincidence_length += len(token1) + 1
                if token1 == '' or token2 == '' or token1 != token2:
                    break
                coincidence_num += 1
            coincidence.append(coincidence_num)
        
        # add zero coincidence for the last entry
        coincidence.append(0)
        self.coincidence = coincidence

    # gets as long as <length> tokens starting from <startIdx> using <self.text>
    def __get_token(self, startIdx, length):
        token = ''
        count = 0
        i = startIdx
        while i<len(self.text) and count<length:
            token += self.text[i]        
            i=i+1
            if i==len(self.text) or self.text[i]==' ':
                count+=1
        if i == len(self.text) and count != length:
            token = None
        return token

    # gets next token starting from <startIdx> using <self.text>
    def __get_next_token(self, startIdx):
        token = ''
        i = startIdx
        while i<len(self.text):
            if self.text[i] == ' ':
                break
            token += self.text[i]
            i += 1
        return (token, i)

    # this function has been written to test nagao implimantation
    def __display_nagao_internal_variables(self):
        counter = 0
        for idx in self.l:
            print idx,
            for i in reversed(range(1,6)):
                token = __get_token(idx, i)
                if token != None:
                    print token,
                    break
            print self.coincidence[counter]
            print '________________________________________________'
            counter += 1
    
    # using text, l (sorted list of all normalized tokens), coincidence and n computes ngrams
    def get_ngram(self, n, sort_the_result_based_on_freq):
        i = 0
        ngrams = {}
        while i < len(self.coincidence):
            iteration = 0
            set_of_all_docs_having_token = set([])
            
            while i+iteration<len(self.coincidence) and self.coincidence[i+iteration]>=n:
                # keep track of doc having this phrase on them.
                doc_idx = self.doc_idx[self.l[i+iteration]]
                set_of_all_docs_having_token.add(doc_idx)
                
                # computing number of iterations
                iteration += 1
                
            # keep track of doc having this phrase on them.
            doc_idx = self.doc_idx[self.l[i+iteration]]
            set_of_all_docs_having_token.add(doc_idx)

            ngram = self.__get_token(self.l[i], n)
            # if ngram contains <.> character. that is not a valid ngram and skip it.
            if ngram != None and ngram.find('.') != -1:
                i += iteration
            elif ngram != None:
                freq = iteration + 1                
                num_of_docs_containing_phrase = len(set_of_all_docs_having_token)
                ngrams[self.__get_token(self.l[i], n)] = (freq, num_of_docs_containing_phrase)
                i += iteration
            i+=1
        
        # sorting the result based on the iteration
        if sort_the_result_based_on_freq:        
            ngrams = sorted(ngrams.iteritems(), key=lambda (k,v):(v,k))
        
        #for key,value in ngrams:
        #    print key, value
        return ngrams

    # applies nagao ngrams on corpus. corpus is list of all normalized documents it cannot be only one document
    def apply_algorithm(self, corpus):    
        # makes a list of all tokens. sorts them. computes coincidence array.
        log(  'start appling nagao alghorithm on the corpus' )
        self.__split_corpus(corpus)
        log( 'end of making list of all words ...')
        
        self.l.sort(key=lambda i: self.text[i:i + Config['nagao']['sort_parameter']])
        log( 'end of sorting ...')
        
        self.__get_coincidence()
        log( 'end of filling coincidence array ...')
                        
        # display nagao internal variables    
        #display_nagao_internal_variables()
    

if __name__ == '__main__':    
    reload(sys)
    sys.setdefaultencoding("utf-8")
    
    corpus=['salam man mahmoud hastam salam man mahmoud hastam', 'salam man ehsan hastam salam man ehsan hastam']    
    #database = redis_driver(dbname=11)        
    my_nagao = nagao()
    my_nagao.apply_algorithm(corpus)
    
    print 'start printing computed ngrams'
    for i in range(1,10):
        print '_____________________________________________________'
        print 'printing ' + str(i) + 'gram.', 
        ngrams = my_nagao.get_ngram(i, True)
        print 'size of ' + str(i) + 'gram is ' + str(len(ngrams))

        for key,value in ngrams:
            print key, value



