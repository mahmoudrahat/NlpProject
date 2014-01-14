#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Ali Alaee - May 16

import math

"""Farsi Preprocessing.

WARNING:
Result of these functions are designed for preprocessing layer of some classifiers,
clusterization and similarity models and algorithms. Its result should not used
for directly displaying to users.
Vector based and term independent models are best nominates.
These methods use aggressive algorithms and it may contain false positives.

This module specially tuned for PyPy JIT.
"""

import string
import general
import re

PUNCTS = r"""'".,/?\!@#$%^&*()_+~`:;{}"""
HALF_SPACE = u'\u200c'

# Common farsi unicode correction - yeh, keh, non-break space, ...
_farsi_unicode_norm = { u'\u064a':u'\u06cc', # yeh
                        u'\u0649':u'\u06cc', # yeh
                        u'\u0643':u'\u06a9', # keh
                        #u'\xa0':u' ', # non-break space
                        u'\u0651':u'', # tashdid
                        u'\u0652':u'', # sukon (gerd)
                        u'\u064b':u'', # fathatan
                        u'\u064f':u'', # oh
                        u'\u064e':u'', # fatha
                        u'\u0650':u'', # kasra
                        u'\u0640':u'', # kashida __
                        # half spaces'
                        #u'\u200c':u' ',
                        u'\u200e':u'\u200c',
                        u'\u200f':u'\u200c',
                        #u'\r':u'\n', # return     
                        # punct
                        u'،':u',', u'!':u'!', u'؟':u'?', u'؛':u';',
                        u'٪':u'%', u'٬':u'\"', u'ـ':u'_', u'»':u'\"',
                        u'«':u'\"', u'”':u'\"', u'“':u'\"', u'‘':'\"',
                        u'’':'\"', u'|':'',
                      }
                        
def normalize(t):
    """Return normalized of given farsi unicode text.
    
    Mapping all extra and non-important alphabets or punctuation to another
    char by _farsi_unicode_norm. Half-spaces are reserved.
    Also correcting '\\n' and '\\r' chars to '\\n'.
    """
    text = list(t)    
    lt = len(text)
    for i in range(lt):
        c = text[i]
        
        # correct \n, \r chars
        if i+1 < lt-1:
            c2 = text[i+1]
        else:
            c2 = None
        if c == u'\r' and c2 == u'\n':
            continue
        elif c == u'\r' and c2 != u'\n':
            c = u'\n'
        elif c == u'\n' and c2 == u'\r': # FFFFFUUUUUUUUUUUUUUuuuuu....
            continue
            
        text[i] = _farsi_unicode_norm.get(c, c)
    return u''.join(text)

def normalize_cpython(t):
    """Normalized for cpython.
    """
    c_text = map(lambda c:_farsi_unicode_norm.get(c, c), t)
    return u''.join(c_text)

def remove_puncts(text):
    """Replacing all punctuation of text with spaces.
    """
    # regex rocks
    return re.sub('[%s]'%PUNCTS, ' ', text)

def sentences(text, remove_puncts=True):
    """Return sentences of given text.
    
    Returned sentences are specially designed for extracting ngrams and defining
    domain of words and it's not equal to "lexical sentences". Also commas are 
    not considered sentence.
    For better result use slower sentences function from layer1 module.
    """
    if remove_puncts:
        ss = map(lambda c: c.strip(), re.split('[\":\n!?.;()-]', text))
    else:
        # XXX Implement this
        raise NotImplemented('sentences with punct is not implemented')
    return ss

def gen_ngrams(items, n):
    """Return dict of generated ngrams with number of occurences.
    
        >>> ngrams([1,2,5,1,2], 2)
        {(1, 2): 2, (2, 5): 1, (5, 1): 1}
    """
    ngs = {}
    ilen = len(items)
    for i in xrange(ilen-n+1):
        ng = tuple(items[i:i+n])
        ngs[ng] = ngs.get(ng, 0) + 1
    return ngs

def full_ngrams(items, n):
    """Return (n, n-1, ... , 1)grams.
       See Also ngrams
    """
    ngs = {}
    for i in xrange(1, n+1):
        ngs.update(gen_ngrams(items, i))
    return ngs

if __name__ == '__mainf__':

    import codecs
    from pymongo import Connection
    news = Connection(host='172.16.19.127')['newsCrawler']['news']
    
    ngrams = {}
    for n in news.find().limit(1000):
        x = normalize(general.safeunicode(n['body']))
        for s in filter(lambda x: x != '', sentences(x)):
            words = remove_puncts(s.replace(HALF_SPACE, ' ')).split(' ')
            words = map(lambda x: x.strip(), words)
            words = filter(lambda x: x != '', words)
            for n in full_ngrams(words, 4).items():
                ngrams[n[0]] = ngrams.get(n[0], 0) + n[1]
        
    f = open('testout/out', 'w')
    ngs = ngrams.items()
    ngs.sort(key=lambda x: x[1])
    for ng in ngs:
        if ng[1] > 2:
            f.write(general.safestr('%s:%d -- %s\n'%(u' '.join(ng[0]), ng[1], [ng[0]])))
    f.close()



