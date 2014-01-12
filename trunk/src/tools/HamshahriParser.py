import xml.etree.ElementTree as ET
import os

class Document():
  def __init__(self, cat, text):
    self.category = cat
    self.text = text

def load_hamshahri(corpus_path):
    corpus = []
    for folder in os.listdir(corpus_path):
        folder_path = corpus_path + '/' + folder
        if os.path.isdir(folder_path):
            for xmldoc in os.listdir(folder_path):
                file_path = folder_path + '/' + xmldoc
                if os.path.isfile(file_path) and str(xmldoc).endswith('.xml'):
                    root = ET.parse(file_path).getroot()
                    for doc in root.findall('DOC'):
                        new_doc = Document(doc.find('./CAT').text, doc.find('./TEXT').text)
                        corpus.append(new_doc)
                break
        break
    return corpus