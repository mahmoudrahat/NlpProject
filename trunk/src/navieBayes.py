import sys
import math
from tools.HamshahriParser import *;
from preprocessing.farsi import *
from preprocessing import general

def extract_words(text):
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    x = normalize(general.safeunicode(text))
    words = remove_puncts(x.replace(HALF_SPACE, ' ')).split(' ')
    words = map(lambda w: w.strip(), words)
    words = gen_ngrams(filter(lambda w: w != '', words), 1)
    words = {i[0][0]:i[1] for i in words.items()}
    return words

class NaiveBayes(object):
    def __init__(self):
        self.catsn = {}
        self.n = 0
        self.catsfreq = {}
        self.voc = set()

    def train(self, cat, docterms):
        self.n += 1
        self.catsn[cat] = self.catsn.get(cat, 0) + 1
        if cat not in self.catsfreq:
            self.catsfreq[cat] = {}
        for t, f in docterms.items():
            self.voc.add(t)
            self.catsfreq[cat][t] = self.catsfreq[cat].get(t, 0) + f

    def classify(self, docterms, floatlog=True):
        if floatlog:
            log = math.log
        else:
            log = lambda x: x

        cats = self.catsn.keys()
        score = {}
        for c in cats:
            score[c] = log(float(self.catsn[c]) / self.n)
            textc = sum(self.catsfreq[c].itervalues())
            denom = float(textc + len(self.voc))
            for t, f in docterms.items():
                if str(t) not in self.voc:
                    continue
                num = float(self.catsfreq[c].get(str(t), 0)) + 1
                if floatlog:
                    score[c] += log((num / denom)) * f
                else:
                    score[c] *= (num / denom) ** f

        for c, v in score.items():
            print '%s %f'%(c, v)		    
        mm = max(score.items(), key=lambda x: x[1])
        print mm[0]
        return mm[0]
    
if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")

	nb = NaiveBayes()
	hamshahri = load_hamshahri('D:/Hamshahri/Corpus');
	print 'Training...'
	#fout = open('output/out' + '.txt', 'w')
	for idx, doc in enumerate(hamshahri):
	    #fout.write('\n__________________\n' + doc.category + '\n__________________\n' + doc.file_path + '\n__________________\n' + doc.text)
	    print 'Training Document Num:' + str(idx) + " in " + doc.file_path

	    #fout.write('\n__________________\n' + doc.category + '\n__________________\n' + doc.file_path + '\n__________________\n')
	    WORDS = extract_words(doc.text)
	    #for w,t in WORDS.items():
	    #    fout.write(str(t) + ':' + w + '\n')
	    

	    nb.train(doc.category, WORDS)
	#fout.close()
	
	keyboard_input = ""
	while keyboard_input != "e":
	    keyboard_input = raw_input("Press Enter to continue(e:Exit)...")	
	    fin = open('input/Sample.txt', 'r' )
	    content = fin.read()
	    nb.classify(extract_words(content))
	    fin.close()
	
	fin = open('input/Sample.txt', 'r' )
	fout = open('output/out.txt', 'w')
	content = fin.read()
	words = extract_words(content)
	for t, f in words.items():	
		fout.write(t + '-'+ str(f)+'\r\n')
	fout.close()