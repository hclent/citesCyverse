import os.path, pickle, nltk
from nltk import RegexpTokenizer
from collections import defaultdict
from gensim.models import Word2Vec #gensim=='0.13.2'
import numpy as np 


#words.pk is a list of lists. one list per doc and in each list we have (word, count)
#[[(the, 1),(words, 1),(in, 1),(doc, 1),],[]..[]]

#vectors.pk is a dictionary of the word vectors. 

tokenizer = RegexpTokenizer(r'\w+')
eng_stopwords = nltk.corpus.stopwords.words('english')
my_stopwords = ['abstract', 'background', 'methods', 'results', 'n', 'university', '%', 'table', 'figure', '\\u', '\\\\', '\\', 'author', 'publication', 'appendix',
                      'table', 'author', 'skip', 'main', '.', 'title', 'u2009', 'publisher',
                      'www.plantphysiol.org', 'copyright', 'san diego', 'california']
for m in my_stopwords:
	eng_stopwords.append(m)


def getFiles():
	path = "/Users/heather/Desktop/citesCyverse"
	file_list = [os.path.join(path, 'papers', f) for f in os.listdir(os.path.join(path, 'papers')) if f.endswith('.txt')]
	return file_list


def clean_text(unprocessed_text):
    lower = unprocessed_text.lower()
    word_list = tokenizer.tokenize(lower)
    clean_list = [w for w in word_list if w not in eng_stopwords]
    return clean_list


def makeWords():
	words = [] #dump this into a pickle 

	file_list = getFiles()
	for fi in file_list:
		
		doc_words = []

		doc_dict = defaultdict(int)

		with open(fi, "r") as f:
			text = f.read().replace('\n', '') #str 
			clean_list = clean_text(text)
			
			for word in clean_list:
				doc_dict[word] += 1

		for word, count in doc_dict.items():
			tup = (word, count)
			doc_words.append(tup)

		words.append(doc_words)

	with open("texts.pk", "wb") as p:
		pickle.dump(words, p)

		
def load_model(file):
	model = Word2Vec.load_word2vec_format(file, binary=False)  # C binary format
	model.init_sims(replace=True)
	return model


def makeVecs():
	vecs = {}

	model = load_model("17kmodel.vec")
	#model = load_model("cyverseMmodel.vec")

	oov = 0
	not_oov = 0

	file_list = getFiles()
	for fi in file_list:
		
		doc_words = []

		doc_dict = defaultdict(int)

		with open(fi, "r") as f:
			text = f.read().replace('\n', '') #str 
			clean_list = clean_text(text)
			clean_set = list(set(clean_list))

			for word in clean_set:
				try:
					np_vec = model[word] #(100,)
					vecs[word] = np_vec
					not_oov += 1
				except Exception as e:
					zeroes = [0.0] * 100
					empty_vec = np.asarray(zeroes).T #init empty column vector (100,)
					vecs[word] = empty_vec
					oov += 0

	#wordvec.pk for sHDP
	with open("wordvec.pk", "wb") as p:
		pickle.dump(vecs, p)

	print("NOT OOV: " + str(not_oov))
	print("OOV: " + str(oov))


# makeWords()
# print("done with words")
# makeVecs()
# print("done with vecs")
# print("printed!")

