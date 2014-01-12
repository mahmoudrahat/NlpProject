import sys
from tools.HamshahriParser import *;

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

def extract_words(text):
    words = text.split(' ');
    words = map(lambda w: w.strip(), words)
    words = gen_ngrams(filter(lambda w: w != '', words), 1)
    words = {i[0][0]:i[1] for i in words.items()}
    return words
	
if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding("utf-8")

	hamshahri = load_hamshahri('E:/Mahmoud/Hamshahri/Corpus');
	for idx, doc in enumerate(hamshahri):
	    fout = open('output/out' + str(idx) + '.txt', 'w')
	    fout.write(doc.category + '\n__________________\n' + doc.text)
	    fout.close()
	    
	fin = open('input/Sample.txt', 'r' )
	fout = open('output/out.txt', 'w')
	content = fin.read()
	words = extract_words(content)
	for t, f in words.items():	
		fout.write(t + '-'+ str(f)+'\r\n')
	fout.close()