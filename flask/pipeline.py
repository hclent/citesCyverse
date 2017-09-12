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
#cyverse_samples = load_lemma_cache()

#TODO: where to put better text pre-processing?
path_to_lemma_samples = "/Users/heather/Desktop/citesCyverse/lemmas/cyverse_lemmas_ALL.pickle"
path_to_early = "/home/hclent/tmp/citesCyverse/lemmas/cyverse_lemmas_2010_2013.pickle" #made with for ls in lemma_samples .append(ls)
path_to_later = "/home/hclent/tmp/citesCyverse/lemmas/cyverse_lemmas_2014_2017.pickle" #made with .append(lemma_samples)

#Get fasttexts vecs
flat_words, flat_tags = get_words_tags(path_to_early)
xformed_tokens = transform_text(flat_words, flat_tags)
npDict = chooseTopNPs(xformed_tokens)
#print("LEN NPDICT BEFORE FILTERING: " + str(len(npDict.keys()))) #There are 249,199 noun phrases in the 760 documents

### OPTIONAL FILTER npDICT ####
top = list(npDict.most_common(300))
other_top = list(npDict.most_common(400))
keep_top = [item for item in other_top if item not in top]

'''
for ALL 
count=1 under the top 30,000/249199 NPs. :/
At the 10 k range,  the words are about 4 frequency 
# BREAKING THE LEMMA SAMPLES BY DATE MIGHT MAKE THE TOPICS BETTER :D 
Above 4k the results aren't looking terrible and the counts are at 7
'''

# # ######
model = load_model("17kmodel.vec")
matrix = getNPvecs(keep_top, model) #top or npDict can go here

#do kmeans
kmeans = KMeans(n_clusters=20, random_state=2).fit(matrix)
results = list(zip(kmeans.labels_, keep_top))
#

query = "cyverse"


#Make file for vis to use 
#embedding_json(results, QUERY, 50, TOP_N)
#embedding_json(results, query, 20, 100)
for i in range(1, 21):
   topic = [tup for tup in results if tup[0] == i]
   print(topic)
   print("#" * 20)

favorite_results = [
(1, ('analysis tool', 21)), (1, ('analysis datum', 13)), (1, ('analysis program', 9)), (1, ('analysis step', 6)), (1, ('regression analysis', 5)), (1, ('analysis pipeline', 5)),  (1, ('analysis software', 4)), (1, ('analysis workflow', 4)), (1, ('analysis publication', 3)),
(2, ('bioinformatic tool', 20)), (2, ('bioinformatic pipeline', 11)), (2, ('pipeline framework', 9)), (2, ('bioinformatic software', 8)), (2, ('bioinformatic resource', 6)), (2, ('bioinformatic analysis', 5)), (2, ('bioinformatic project', 3)),
(3, ('salt stress', 24)), (3, ('stress response', 19)), (3, ('dehydration stress', 16)), (3, ('drought stress', 15)), (3, ('drought treatment', 6)), (3, ('drought tolerance', 6)), (3, ('stress tolerance', 4)), (3, ('drought condition', 4)), (3, ('water stress', 4)), (3, ('stress treatment', 4)), (3, ('photoperiod response index', 3)),
(4, ('perl script', 9)), (4, ('github repository', 7)), (4, ('custom script', 6)), (4, ('java interface', 5)), (4, ('spreadsheet program', 5)),  (4, ('python code', 4)), (4, ('wrapper script', 3)),
(5, ('honey bee', 14)), (5, ('bee microbiome', 8)), (5, ('bee species', 5)), (5, ('bee health', 4)), (5, ('bee gut microbiome', 3)), (5, ('bee cornerstone', 2)), (5, ('flea beetle', 2)),
(6, ('image datum', 9)), (6, ('image analysis', 8)), (6, ('image collection', 7)), (6, ('bioluminescence imaging', 6)), (6, ('image harvest', 6)), (6, ('imaging platform', 4)), (6, ('image processing step', 4)), (6, ('imaging technology', 3)),
(7, ('d. oligosanthe', 26)), (7, ('a. palmerus', 16)), (7, ('f. pringleus', 16)), (7, ('f. prus', 13)), (7, ('a. pubescen', 9)), (7, ('s. viridi', 8)), (7, ('f. angustifolium', 8)), (7, ('a. sulca', 6)), (7, ('m. griffithsus', 6)), (7, ('s. mirarab', 5)),  (7, ('f. bidenti', 4)), (7, ('b. vulgari', 4)), (7, ('c. posadasius', 4)), (7, ('m. truncatulum', 3)), (7, ('s. aleutianus', 3)),
(8, ('host prediction', 24)), (8, ('host genome', 23)), (8, ('host virus', 12)), (8, ('host prediction accuracy', 10)), (8, ('defense response', 10)), (8, ('host strain', 7)), (8, ('host taxonomy', 7)), (8, ('host sequence', 5)), (8, ('host contig', 5)), (8, ('host metabolism', 4)), (8, ('host health', 3)),
(9, ('life science', 18)), (9, ('life cycle', 15)), (9, ('life history', 10)), (9, ('life technology', 7)), (9, ('life history ecotype', 4)), (9, ('life history strategy', 3)), (9, ('life stage', 3)),
(10, ('arabidopsis thaliana', 27)), (10, ('maize genome', 20)), (10, ('rice genome', 13)), (10, ('sorghum bicolor', 12)), (10, ('brachypodium distachyon', 12)), (10, ('rice chromosome', 9)), (10, ('arabidopsis genome', 7)), (10, ('rice gene', 6)), (10, ('brachypodium genome', 5)), (10, ('arabidopsis protein', 5)), (10, ('maize anthocyanin phlobaphene', 5)),
(11, ('cancer cell', 30)), (11, ('breast cancer cell', 6)), (11, ('lymphocyte apoptosis', 4)), (11, ('tumour cell', 3)), (11, ('cancer cell bica', 3)),
(12, ('population size', 6)), (12, ('population analysis', 5)), (12, ('population m. guttatus', 5)), (12, ('population quality', 4)), (12, ('variation rna quality', 4)), (12, ('population community ontology', 4)), (12, ('variation datum', 4)), (12, ('population development', 3)),
(13, ('model organism', 33)), (13, ('model species', 13)), (13, ('model system', 12)), (13, ('modeling framework', 9)), (13, ('markov model', 8)), (13, ('model condition', 7)), (13, ('model development', 4)), (13, ('model plant', 4)), (13, ('model parameter', 3)),
(14, ('promoter region', 20)), (14, ('region genome', 15)), (14, ('region chromosome', 13)), (14, ('region sequence similarity', 11)), (14, ('region interest', 10)), (14, ('coding region', 8)), (14, ('element name', 7)), (14, ('centromere region', 6)), (14, ('arm deletion', 6)), (14, ('location genome', 5)),
(15, ('human genome', 9)), (15, ('chicken line', 6)), (15, ('human genome project', 5)), (15, ('human blood', 4)), (15, ('human error', 4)), (15, ('human population', 4)), (15, ('human gut microbiota', 3)),
(16, ('blood transcriptome', 19)), (16, ('flow cytometry', 6)), (16, ('blood sample', 5)), (16, ('plasma membrane', 5)), (16, ('fluid sample', 5)), (16, ('blood transcriptome analysis', 4)), (16, ('donor sample', 4)),
(17, ('biodiversity datum', 28)), (17, ('informatics community', 7)), (17, ('biodiversity hotspot', 7)), (17, ('biodiversity information facility gbif', 7)), (17, ('biology community', 5)), (17, ('biodiversity community', 5)), (17, ('biodiversity science', 5)), (17, ('biodiversity domain', 4)),
(18, ('venom composition', 6)), (18, ('venom potency', 4)), (18, ('venom transmission system', 3)),
(19, ('bone colonization', 9)), (19, ('bone fragment', 6)), (19, ('bone microenvironment', 4)), (19, ('bone lesion', 4)), (19, ('metastasis model', 3)), (19, ('bone fragment drug concentration', 3)), (19, ('bone segment', 2)), (19, ('bone tissue', 2)),
(20, ('coral sponge', 9)), (20, ('sea anemone', 7)), (20, ('seawater sample', 5)), (20, ('sea water', 3)), (20, ('coral density', 3)), (20, ('coral reef', 3)), (20, ('sediment m. griffithsi.', 2)), (20, ('sea canyon', 2)), (20, ('coral habitat', 2)), (20, ('sea pen', 2)), (20, ('submarine canyon', 2)), (20, ('sea ice', 2)), (20, ('nematocyst diversity', 2))]


#embedding_json(favorite_results, query, 20, '10kFAV')
#print("made results!!")
#(20, ('coral sponge', 9)), (20, ('sea anemone', 7)), (20, ('seawater sample', 5)), (20, ('sea water', 3)), (20, ('coral density', 3)), (20, ('coral reef', 3)), (20, ('sediment m. griffithsi.', 2)), (20, ('sea canyon', 2)), (20, ('coral habitat', 2)), (20, ('sea pen', 2)), (20, ('submarine canyon', 2)), (20, ('sea ice', 2)), (20, ('nematocyst diversity', 2))
#(710, ('ocean perch', 10)), (710, ('ocean basement', 9)), (710, ('ocean virome', 5)), (710, ('ocean sampling day', 4)), (710, ('phytoplankton bloom', 3)), (710, ('plume sample', 3)), (710, ('ocean water sampling', 2)), (710, ('plume metagenome', 2)), (710, ('ocean drilling program iodp u1362a u1362b', 2)), (710, ('current seafloor topography', 2)), (710, ('crust seafloor', 2)), (710, ('seafloor observatory', 2)), (710, ('bloom taxonomy', 2))
#(645, ('language processing', 9)), (645, ('learning gain', 7)), (645, ('language owl', 3)), (645, ('markup language', 3)), (645, ('learning survey', 3)), (645, ('language processing algorithm', 2)), (645, ('language description', 2)), (645, ('learning benefit', 2)), (645, ('skill category', 2)), (645, ('scalum language language java', 2)), (645, ('autism spectrum disorder asd', 2)), (645, ('call format', 2)), (645, ('phone call', 2)), (645, ('language setting', 2))
#(19, ('climate change', 13)), (19, ('land area', 10)), (19, ('coral sponge', 9)), (19, ('habitat area', 8)), (19, ('climate stability', 5)), (19, ('habitat class', 5)), (19, ('fish habitat', 4)), (19, ('fauna flora', 4)), (19, ('mammal park aquarium', 3)), (19, ('fishing gear', 3)), (19, ('coral density', 3)), (19, ('weather datum', 3)),
