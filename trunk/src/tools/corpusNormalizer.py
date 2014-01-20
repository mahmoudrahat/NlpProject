#!/usr/bin/env python

from HamshahriParser import *
from preprocessing.farsi import *
from preprocessing.general import *

SPLITER = "_________________________________\n"

def make_normal(text):
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = normalize(general.safeunicode(text))
    text = remove_puncts(text.replace(HALF_SPACE, ' '))
    return text

def normalize_corpus(corpus, path):
    myFile = None
    doc_counter = 1
    file_counter = 1
    for doc in corpus:
        if file_counter % 100 == 1 and doc_counter % 100 == 1:
            dir_counter = (file_counter/100) + 1
            directory = path + '/' + str(dir_counter)
            if not os.path.exists(directory):
                os.makedirs(directory)
        if doc_counter % 100 == 1:
            if myFile != None:
                myFile.close()
            file_path = directory + '/' + str((file_counter%100)+1) + ".txt"
            myFile = open(file_path, 'w')
            file_counter += 1
        myFile.write(doc.file_path + "\n")
        myFile.write(SPLITER)
        myFile.write(doc.category + "\n")
        myFile.write(SPLITER)
        myFile.write(make_normal(doc.text) + "\n")
        myFile.write(SPLITER)
        doc_counter += 1
        
def load_corpus(path, num_doc_to_read = -1):
    corpus = []
    doc_counter = 0
    for folder in os.listdir(path):
      folder_path = path + '/' + folder
      if os.path.isdir(folder_path):
          for folder_content in os.listdir(folder_path):
              file_path = folder_path + '/' + folder_content
              if os.path.isfile(file_path) and str(file_path).endswith('.txt'):
                try:
                    line_number = 0
                    with open(file_path, 'r') as f:
                        for line in f:
                            if num_doc_to_read!= -1 and doc_counter >= num_doc_to_read:
                                return corpus
                            if line_number % 6 == 0:
                                doc = Document("","",line)
                            elif line_number % 6 == 2:
                                doc.category = line
                            elif line_number % 6 == 4:
                                doc.text = line
                                corpus.append(doc)
                                doc_counter += 1
                            line_number += 1
                except Exception:
                    pass    
    return corpus


