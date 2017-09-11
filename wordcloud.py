import os, json, string
from collections import defaultdict
from processors import *



vectors_dict = "/Users/heather/Desktop/citesCyverse/wordvecDict.pickle"
path_to_lemma_samples = "/Users/heather/Desktop/citesCyverse/lemmas"
path_to_wordcloud = "/Users/heather/Desktop/citesCyverse/static/wordclouds"
lemmas_samples_ALL = ""

cyverse_stop_words = ['university', '%', 'table', 'figure', '\\u', '\\\\', '\\', 'author', 'publication', 'appendix',
                      'table', 'author', 'skip', 'main', '.', 'title', 'u2009', 'publisher',
                      'www.plantphysiol.org', 'copyright', 'san diego', 'california']

#TODO: depending on year files
#use train embeddings and do like "genetics cloud", "plant cloud", "ocean cloud", "animal cloud" ??

#load pickle wordvecDict.pickle {'word': vector}


#Step 1: Make dictionary with word counts for ALL cyverseDocs {'gluten': 5, 'span': 9}
def frequency_dict(lemma_file):
    nesDict = defaultdict(lambda: 0)

    full_filename = os.path.join(path_to_lemma_samples, lemma_file) #pickle
    with open(full_filename, "rb") as f:
        lemma_samples = pickle.load(f)

    words = [l[1] for l in lemma_samples]
    flat_words = flatten(words)
    keep_words =  [w for w in flat_words if w not in cyverse_stop_words]

    for word in keep_words: #fof word in keep_words list
        nesDict[word] += 1

    output_file = "freqDict.pickle"
    write_to_file = os.path.join(path_to_wordcloud, output_file)
    with open(write_to_file, "wb") as w:
        pickle.dump(nesDict, w)

#maybe do the whole dict for 2010-2013 & 2014-2017 and pickle those.



#D3 wordcloud, where nesDict is a frequency dict and x is our threshold
def wordcloud(nesDict, x):
    wordcloud_list = []
    for nes in nesDict:
         if int(nesDict[nes]) > x:
            entry = {"text": nes, "size": nesDict[nes]} #no scaling
            #entry = {"text": nes, "size": nesDict[nes]*.25} #scaling
            wordcloud_list.append(entry)
    wordcloud_json = json.dumps(wordcloud_list)
    return wordcloud_json


#TODO: save the json files so we can re-load them?

frequency_dict("cyverse_lemmas_ALL.pickle")
print("dumped to pickle!")