from __future__ import print_function
from processors import *
import nltk, json, os.path

#BIODOC HANDLING
eng_stopwords = nltk.corpus.stopwords.words('english') #remove default english stopwords

# Input: Pmid
# Output: list of dictionaries for all annotated citing pmcids ["pmcid": 123, ]
def retrieveBioDocs():
  #print("retrieving biodocs")
  biodocs = [] #list of strings

  filepath = "/Users/heather/Desktop/citesCyverse/papers"

  json_files = [f for f in os.listdir(filepath) if f.endswith('.json')]

  for j in json_files:
      j_path = os.path.join(filepath, j)
      biodict = {"pmcid": j.strip('.json'), "jsonpath": j_path}
      biodocs.append(biodict)
  return biodocs


def grab_lemmas_and_tags(biodoc):
  lemmas_list = biodoc.lemmas #list
  tags_list = biodoc.tags
  lemmas_with_tags = list(zip(lemmas_list, tags_list))
  keep = [lt for lt in lemmas_with_tags if lt[0].lower() not in eng_stopwords]

  keep_lemmas = [lt[0] for lt in keep]
  keep_tags = [lt[1] for lt in keep]
  return keep_lemmas, keep_tags


#Input: Processors annotated biodocs
#Output: List of named entities
def grab_nes(biodoc):
  ners_list = biodoc.nes
  return ners_list



# #Input: Processors annotated biodocs (from JSON)
# #Output: list of dicts containing {pmcid, lemmas, nes, num_sentences, num_tokens}
def loadBioDoc(biodocs):
  loadedBioDocs = []

  for doc in biodocs:
    pmcid = doc["pmcid"]
    jsonpath = doc["jsonpath"]

    #IMPORTANT NOTE: MAY 10, 2017: "data_samples" being replaced with "lemmas" for clarity!!!!
    #biodict = {"pmcid": pmcid, "lemmas": [], "nes": [], "num_sentences": [], "num_tokens": [], "tags": []}
    biodict = {"pmcid": pmcid, "jsonpath": jsonpath, "nes": [], "lemmas": []} # "tags": [] gets added

    token_count_list = []

    with open(jsonpath) as jf:
      data = Document.load_from_JSON(json.load(jf))
      #print(type(data))
      #print(type(data)) is <class 'processors.ds.Document'>
      num_sentences = data.size
      #print(num_sentences)
      #biodict["num_sentences"].append(num_sentences)
      biodict["num_sentences"] = num_sentences 
      #print(num_sentences)
      for i in range(0, num_sentences):
        s = data.sentences[i]
        num_tokens = s.length
        token_count_list.append(num_tokens)

      num_tokens = sum(token_count_list)
      #biodict["num_tokens"].append(num_tokens)
      biodict["num_tokens"] = num_tokens

      lemmas, tags = grab_lemmas_and_tags(data)
      #print(lemmas[:100])
      biodict["lemmas"].append(lemmas) #lemmas is a LIST
      # biodict["tags"].append(tags) #tags is a LIST
      biodict["tags"] = tags
      #print(tags[:100])

      nes = grab_nes(data)
      biodict["nes"].append(nes)

      loadedBioDocs.append(biodict)

  return loadedBioDocs

# biodocs = retrieveBioDocs()
# loadedBioDocs = loadBioDoc(biodocs)
