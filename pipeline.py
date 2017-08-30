from biodoc_preproc import retrieveBioDocs, loadBioDoc
from make_lemmas import print_lemma_nes_samples, concat_lemma_nes_samples, load_lemma_cache
from fasttext import get_words_tags, transform_text, chooseTopNPs, load_model, getNPvecs
from sklearn.cluster import KMeans
from fgraph2json import embedding_json


#Step 1: annotate all txt files on geco
#Step 2: scp the jsons back to /papers

#Step3: retrieve info from BioDocs
#biodocs = retrieveBioDocs()
#biodoc_data = loadBioDoc(biodocs)

#Step4: make lemma_samples and concat into cyverse_lemmas
#print_lemma_nes_samples(biodoc_data)
#concat_lemma_nes_samples()

#Step5: load the cyverse_lemmas
cyverse_samples = load_lemma_cache()


#Get fasttexts vecs
flat_words, flat_tags = get_words_tags()
xformed_tokens = transform_text(flat_words, flat_tags)
npDict = chooseTopNPs(xformed_tokens)
### OPTIONAL FILTER npDICT ####
top = list(npDict.most_common(1000))
######
model = load_model("17kmodel.vec")
matrix = getNPvecs(top, model) #top or npDict can go here

#do kmeans
kmeans = KMeans(n_clusters=50, random_state=2).fit(matrix)
results = list(zip(kmeans.labels_, top))

for i in range(1, 51):
	topic = [tup for tup in results if tup[0] == i]
	print(topic)
	print("#" * 20)


query = "cyverse"


#Make file for vis to use 
#embedding_json(results, QUERY, 50, TOP_N)
embedding_json(results, query, 20, 100)