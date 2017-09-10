import os, json, string
from collections import defaultdict
from processors import *


#TODO: depending on year files
#maybe user optionsc an be like... top "most frequent", "middle frequent"...
#or use train embeddings and do like "genetics cloud", "plant cloud", "ocean cloud", "animal cloud" ??

### oooh, what about type in a key word, and use that word to generate a word cloud? ...
# eh... seems easier to force them into some categories ...

def preprocess_wordcloud(path_to_file, user_option):
    pass


#TODO: modify this! Since we are not using category_list, we will need to do something else here..
#Make dictionary with NES counts {'gluten': 5, 'span': 9}
def frequency_dict(nes_list, category_list):
    nesDict = defaultdict(lambda:0)
    for docs in nes_list: #docs is dict
        for key in docs: #key of dict
            for category in category_list: #no error with category 'Potato'
                if key == category:
                    nes = (docs[key])
                    for n in nes:
                        nesDict[n] += 1
    return nesDict

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