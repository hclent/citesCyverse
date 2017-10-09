import os, json, pickle, nltk, logging, sys, math
from collections import defaultdict, Counter
from sklearn.metrics.pairwise import cosine_similarity
from processors import * #has the stuff necessary for chain
from scipy import sparse
sys.path.append('/home/hclent/repos/citesCyverse/flask/')
from app import model

#
# from fasttext import load_model
#
# print("about to load the model...")
# model = load_model("/home/hclent/tmp/fastText/cyverse_lower.vec")
# print("loaded the friggen model")

logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


#use train embeddings and do like "genetics cloud", "plant cloud", "ocean cloud", "animal cloud" ??
#load pickle wordvecDict.pickle {'word': vector}
def flatten(listOfLists):
    return list(chain.from_iterable(listOfLists))

#Step 1: Make dictionary with word counts for ALL cyverseDocs {'gluten': 5, 'span': 9}
def frequency_dict(lemma_file):
    #print("in frequency dict")
    #The Counter() is for if we want to get the top 100 words or w/e
    #nesDict = Counter(defaultdict(lambda: 0)) # can't pickle a default dict, but seems fast enought o generate..

    nesDict = defaultdict(lambda: 0) # can't pickle a default dict, but seems fast enought o generate..

    cyverse_stop_words = ['university', '%', 'table', 'figure', '\\u', '\\\\', '\\', 'author', 'publication',
                          'appendix',
                          'table', 'author', 'skip', 'main', '.', 'title', 'u2009', 'publisher',
                          'www.plantphysiol.org', 'copyright', '. . . .', '. .', ',', '.....', "\"", "1", ";", "3",
                          "one", "also", "=", "2", "4" "number", 'j.', 'm.', 's.', 'many', 'b', '6', '10', 'however',
                          'well', 'c', 'p.', '*', "'s", ':', "'", '0', '4', '-', 'three', 'may', 'non', 'could',
                          'would', 'two', 'one',
                          'e.g.', 'doi', 'case', 'follow', 'describe', 'name', 'see', 'among', 'single', 'several',
                          'run', 'additional',
                          'number', 'show', 'include', 'use', 'multiple', 'important', 'individual', 'like', 'exist',
                          'related', 'gateway', 'control', 'suggest', "within"]

    eng_stopwords = nltk.corpus.stopwords.words('english')
    for s in eng_stopwords:
        cyverse_stop_words.append(s)

    path_to_lemma_samples = "/home/hclent/repos/citesCyverse/flask/lemmas"
    full_filename = os.path.join(path_to_lemma_samples, lemma_file) #pickle
    #print(full_filename)
    with open(full_filename, "rb") as f:
        lemma_samples = pickle.load(f)

    #print("opened the pickle!")
    #print(len(lemma_samples))
    #print(lemma_samples[0])

    words = [l[1] for l in lemma_samples]
    flat_words = flatten(words)

    keep_words =  [w.lower() for w in flat_words if w.lower() not in cyverse_stop_words]

    for word in keep_words: #for word in keep_words list
        nesDict[word] += 1

    logging.info("made the dict!")
    return nesDict


def filter_by_embeddings(query, nesDict):
    logging.info("filtering by embeddings")
    logging.info(model)
    wc_words = []
    query = query.lower()
    try:
        query_vec = sparse.csr_matrix(model[query])
        for word in nesDict.keys():
            try:
                word_vec = sparse.csr_matrix(model[word])
                sim = (cosine_similarity(query_vec, word_vec))[0][0] #cosine_similarity results in [[0.123]]
                if sim > 0.65: #50?
                    wc_words.append(word)
            except Exception as e:
                pass #no vector for that word
    except Exception as e:
        logging.info(e)
        raise Exception("the query word does not have a vector! Please use another word!!")
    logging.info(wc_words)
    return wc_words


#D3 wordcloud, where nesDict is a frequency dict and x is our threshold
def wordcloud(query, nesDict, wordcloud_words):
    logging.info("gonna make the wordcloud json now! :') ")
    wordcloud_list = [] #will dump this to json
    query = query.lower()

    """
    MinMaxScaler formula is:
    X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
    X_scaled = X_std * (max - min) + min
    """

    # numbers = [int(nesDict[word]) for word in wordcloud_words]
    # print(numbers)
    # mySorted = list(sorted(numbers))
    # print(mySorted)
    # max = mySorted[-1] + 100
    # print("max: "+ str(max))
    # min = mySorted[0] - 100
    # print("min: " + str(min))
    for word in wordcloud_words:
        size = nesDict[word]
        if size < 10:
            entry = {"text": word, "size": 10}
        else:
            # s = int(nesDict[word])
            # X_std = (s - min) / (max - min)
            # print(X_std)
            # X_scaled = X_std * (max - min) + min
            # entry = {"text": word, "size": int(X_scaled)}
            # print(X_scaled)
            # print("#######")
            entry = {"text": word, "size": int(nesDict[word])} # if the size is too big (like 20,000) you MUST scale it or it will not show up in the vis

        wordcloud_list.append(entry)

    wordcloud_json = json.dumps(wordcloud_list)

    path_to_wordcloud = "/home/hclent/repos/citesCyverse/flask/static/wordclouds"
    filename = query + ".json"
    path = os.path.join(path_to_wordcloud, filename)
    logging.info(path)

    with open(path, "w") as out:
        json.dump(wordcloud_json, out)

    return wordcloud_json





# nesDict = frequency_dict("cyverse_lemmas_ALL.pickle")
# wordcloud_words = filter_by_embeddings("dna", nesDict)
# print(wordcloud_words)
# print("#"*20)
# wordcloud_json = wordcloud("disease", nesDict, wordcloud_words)



############################################################################
#instead of using embeddings, gonna get the top 100 words
# nesDict = frequency_dict("cyverse_lemmas.pickle")
# nesDict = frequency_dict("cyverse_lemmas_ALL.pickle")
# wordcloud_words = (Counter(nesDict).most_common(370))
# cyverse_stop_words = ['university', '%', 'table', 'figure', '\\u', '\\\\', '\\', 'author', 'publication',
#                           'appendix',
#                           'table', 'author', 'skip', 'main', '.', 'title', 'u2009', 'publisher',
#                           'www.plantphysiol.org', 'copyright', '. . . .', '. .', ',', '.....', "\"", "1", ";", "3",
#                           "one", "also", "=", "2", "4" "number", 'j.', 'm.', 's.', 'many', 'b', '6', '10', 'however',
#                           'well', 'c', 'p.', '*', "'s", ':', "'", '0', '4', '-', 'three', 'may', 'non', 'could',
#                           'would', 'two', 'one',
#                           'e.g.', 'doi', 'case', 'follow', 'describe', 'name', 'see', 'among', 'single', 'several',
#                           'run', 'additional',
#                           'number', 'show', 'include', 'use', 'multiple', 'important', 'individual', 'like', 'exist',
#                           'related', 'gateway', 'control', 'suggest', 'high', 'allow', 'first', 'list', 'define', 'set',
#                             'new', 'different', 'thus', 'small', 'year', 'due', 'i.e.', '...', 'low', 'per', 'big', 'via',
#                             '. . . . .', 'full', 'another', 'second', '100'
#                       ]
# eng_stopwords = nltk.corpus.stopwords.words('english')
# for s in eng_stopwords:
#     cyverse_stop_words.append(s)
#
# keep_words = []
# for w in wordcloud_words:
#     word = w[0]
#     if word.lower() not in cyverse_stop_words and not len(word)<3:
#         keep_words.append(word.lower())
#
# print(keep_words)
# print(len(keep_words))
#
# wordcloud_json = wordcloud("cyverseTop300", nesDict, keep_words)
