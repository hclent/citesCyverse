import os, json, pickle
from collections import defaultdict
from processors import *
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from fasttext import load_model


#load model once globally
model = load_model("17kmodel.vec")


# vectors_dict = "/Users/heather/Desktop/citesCyverse/wordvecDict.pickle"
# path_to_lemma_samples = "/Users/heather/Desktop/citesCyverse/lemmas"
# path_to_wordcloud = "/Users/heather/Desktop/citesCyverse/static/wordclouds"

vectors_dict = "/home/hclent/tmp/citesCyverse/wordvecDict.pickle"
path_to_lemma_samples = "/home/hclent/tmp/citesCyverse/lemmas"
path_to_wordcloud = "/home/hclent/tmp/citesCyverse/static/wordclouds"

lemmas_samples_ALL = "cyverse_lemmas_ALL.pickle"

cyverse_stop_words = ['university', '%', 'table', 'figure', '\\u', '\\\\', '\\', 'author', 'publication', 'appendix',
                      'table', 'author', 'skip', 'main', '.', 'title', 'u2009', 'publisher',
                      'www.plantphysiol.org', 'copyright']


#use train embeddings and do like "genetics cloud", "plant cloud", "ocean cloud", "animal cloud" ??
#load pickle wordvecDict.pickle {'word': vector}
def flatten(listOfLists):
    return list(chain.from_iterable(listOfLists))

#Step 1: Make dictionary with word counts for ALL cyverseDocs {'gluten': 5, 'span': 9}
def frequency_dict(lemma_file):
    nesDict = defaultdict(lambda: 0) # can't pickle a default dict, but seems fast enought o generate..

    full_filename = os.path.join(path_to_lemma_samples, lemma_file) #pickle
    with open(full_filename, "rb") as f:
        lemma_samples = pickle.load(f)

    words = [l[1] for l in lemma_samples]
    flat_words = flatten(words)
    keep_words =  [w for w in flat_words if w not in cyverse_stop_words]

    for word in keep_words: #for word in keep_words list
        nesDict[word] += 1

    return nesDict


def filter_by_embeddings(query, nesDict):
    wc_words = []
    try:
        query_vec = sparse.csr_matrix(model[query])
        #print(query_vec)
        for word in nesDict.keys():
            try:
                word_vec = sparse.csr_matrix(model[word])
                sim = (cosine_similarity(query_vec, word_vec))[0][0] #cosine_similarity results in [[0.123]]
                if sim > 0.65: #50?
                    wc_words.append(word)
            except Exception as e:
                #print("no vector for word: " + str(word))
                pass #no vector for that word
    except Exception as e:
        raise Exception("the query word does not have a vector! Please use another word!!")
    return wc_words


#D3 wordcloud, where nesDict is a frequency dict and x is our threshold
def wordcloud(query, nesDict, wordcloud_words):
    wordcloud_list = [] #will dump this to json

    for word in wordcloud_words:
        entry = {"text": word, "size": nesDict[word]}
        wordcloud_list.append(entry)

    wordcloud_json = json.dumps(wordcloud_list)

    filename = query + ".json"
    path = os.path.join(path_to_wordcloud, filename)

    with open(path, "wb") as out:
        json.dumps(wordcloud_json, out)

    return wordcloud_json


nesDict = frequency_dict("cyverse_lemmas_ALL.pickle")
wordcloud_words = filter_by_embeddings("ocean", nesDict)
print(wordcloud_words)
wordcloud("ocean", nesDict, wordcloud_words)
