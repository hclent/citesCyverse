import os, pickle
from biodoc_preproc import retrieveBioDocs, loadBioDoc
#from make_lemmas import print_lemma_nes_samples, concat_lemma_nes_samples, load_lemma_cache
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


#Get fasttexts vecs
# filename = 'cyverse_lemmas_' + "2010" + '.pickle'
# path = os.path.join("/home/hclent/repos/citesCyverse/flask/lemmas", filename)
# print(path)
#
# with open(path, "rb") as f:
#     lemma_samples = pickle.load(f)

# flat_words, flat_tags = get_words_tags(path)
# print(flat_words[:10])
# print(flat_tags[:10])
# print(type(flat_words))
# print(type(flat_tags))


#
# xformed_tokens = transform_text(flat_words, flat_tags)
# npDict = chooseTopNPs(xformed_tokens)
# #print("LEN NPDICT BEFORE FILTERING: " + str(len(npDict.keys()))) #There are 249,199 noun phrases in the 760 documents
#
# ### OPTIONAL FILTER npDICT ####
# top = list(npDict.most_common(1000))
# other_top = list(npDict.most_common(1100))
# keep_top = [item for item in other_top if item not in top]

'''
for ALL 
count=1 under the top 30,000/249199 NPs. :/
At the 10 k range,  the words are about 4 frequency 
# BREAKING THE LEMMA SAMPLES BY DATE MIGHT MAKE THE TOPICS BETTER :D 
Above 4k the results aren't looking terrible and the counts are at 7
'''

# # ######
model = load_model("17kmodel.vec")
# matrix = getNPvecs(keep_top, model) #top or npDict can go here
#
# #do kmeans
# kmeans = KMeans(n_clusters=20, random_state=2).fit(matrix)
# results = list(zip(kmeans.labels_, keep_top))
# #
#
# query = "cyverse"
# for i in range(0, 21):
#    topic = [tup for tup in results if tup[0] == i]
#    print(topic)
#    print("#" * 20)




def generateFiles():
   possible_ks = [10, 15, 20, 25]
   possible_years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 201014, 201517]
   possible_windows = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

   for year in possible_years:
       if year == 201014:
           save_year = "2010_2014"
       if year == 201517:
           save_year = "2015_2017"
       else:
           save_year = year

       filename = 'cyverse_lemmas_' + str(save_year) + '.pickle'
       path = os.path.join("/home/hclent/repos/citesCyverse/flask/lemmas", filename)
       print(path)
       print(os.path.isfile(path))
       for window in possible_windows:
           try:
               flat_words, flat_tags = get_words_tags(path)
               xformed_tokens = transform_text(flat_words, flat_tags)
               npDict = chooseTopNPs(xformed_tokens)
               if window == 100:
                   top = list(npDict.most_common(100))
               elif window == 200:
                   top_100 = list(npDict.most_common(101))
                   top_200 = list(npDict.most_common(200))
                   top = [item for item in top_200 if item not in top_100]
               elif window == 300:
                   top_200 = list(npDict.most_common(201))
                   top_300 = list(npDict.most_common(300))
                   top = [item for item in top_300 if item not in top_200]
               elif window == 400:
                   top_300 = list(npDict.most_common(301))
                   top_400 = list(npDict.most_common(400))
                   top = [item for item in top_400 if item not in top_300]
               elif window == 500:
                   top_half = list(npDict.most_common(401))
                   bottom_half = list(npDict.most_common(500))
                   top = [item for item in bottom_half if item not in top_half]
               elif window == 600:
                   top_half = list(npDict.most_common(501))
                   bottom_half = list(npDict.most_common(600))
                   top = [item for item in bottom_half if item not in top_half]
               elif window == 700:
                   top_half = list(npDict.most_common(601))
                   bottom_half = list(npDict.most_common(700))
                   top = [item for item in bottom_half if item not in top_half]
               elif window == 800:
                   top_half = list(npDict.most_common(701))
                   bottom_half = list(npDict.most_common(800))
                   top = [item for item in bottom_half if item not in top_half]
               elif window == 900:
                   top_half = list(npDict.most_common(801))
                   bottom_half = list(npDict.most_common(900))
                   top = [item for item in bottom_half if item not in top_half]
               elif window == 1000:
                   top_half = list(npDict.most_common(901))
                   bottom_half = list(npDict.most_common(1000))
                   top = [item for item in bottom_half if item not in top_half]

               else:
                   top = list(npDict.most_common(window))

               matrix = getNPvecs(top, model)  # top or npDict can go here


               for k in possible_ks:
                   kmeans = KMeans(n_clusters=k, random_state=2).fit(matrix)


                   results = list(zip(kmeans.labels_, top))


                   #FILTERING OUT SMALL TOPICS:
                   labels = [r[0] for r in results]

                   delete_topics = []
                   for i in range(0, k):
                       if labels.count(i) < 2: #clean out topics with less than 3 words in them
                           delete_topics.append(i)

                   keep_results = []

                   for combo in results:
                       if combo[0] not in delete_topics:
                           keep_results.append(combo)

                   embedding_json(keep_results, "cyverse", k, window, year)
                   print("PRINTED A FILE TO FGRAPHS!")
           except Exception as e:
               print(e)




generateFiles()


# favorite_results = [
# (0, ('analysis tool', 21)), (0, ('analysis datum', 13)), (0, ('analysis program', 9)), (0, ('analysis step', 6)), (0, ('regression analysis', 5)), (0, ('analysis pipeline', 5)),  (0, ('analysis software', 4)), (0, ('analysis workflow', 4)), (0, ('analysis publication', 3)),
# (1, ('bioinformatic tool', 20)), (1, ('bioinformatic pipeline', 11)), (1, ('pipeline framework', 9)), (1, ('bioinformatic software', 8)), (1, ('bioinformatic resource', 6)), (1, ('bioinformatic analysis', 5)), (1, ('bioinformatic project', 3)),
# (2, ('salt stress', 24)), (2, ('stress response', 19)), (2, ('dehydration stress', 16)), (2, ('drought stress', 15)), (2, ('drought treatment', 6)), (2, ('drought tolerance', 6)), (2, ('stress tolerance', 4)), (2, ('drought condition', 4)), (2, ('water stress', 4)), (2, ('stress treatment', 4)), (2, ('photoperiod response index', 3)),
# (3, ('perl script', 9)), (3, ('github repository', 7)), (3, ('custom script', 6)), (3, ('java interface', 5)), (3, ('spreadsheet program', 5)),  (3, ('python code', 4)), (3, ('wrapper script', 3)),
# (4, ('honey bee', 14)), (4, ('bee microbiome', 8)), (4, ('bee species', 5)), (4, ('bee health', 4)), (4, ('bee gut microbiome', 3)), (4, ('bee cornerstone', 2)), (4, ('flea beetle', 2)),
# (5, ('image datum', 9)), (5, ('image analysis', 8)), (5, ('image collection', 7)), (5, ('bioluminescence imaging', 6)), (5, ('image harvest', 6)), (5, ('imaging platform', 4)), (5, ('image processing step', 4)), (5, ('imaging technology', 3)),
# (6, ('d. oligosanthe', 26)), (6, ('a. palmerus', 16)), (6, ('f. pringleus', 16)), (6, ('f. prus', 13)), (6, ('a. pubescen', 9)), (6, ('s. viridi', 8)), (6, ('f. angustifolium', 8)), (6, ('a. sulca', 6)), (6, ('m. griffithsus', 6)), (6, ('s. mirarab', 5)),  (6, ('f. bidenti', 4)), (6, ('b. vulgari', 4)), (6, ('c. posadasius', 4)), (6, ('m. truncatulum', 3)), (6, ('s. aleutianus', 3)),
# (7, ('host prediction', 24)), (7, ('host genome', 23)), (7, ('host virus', 12)), (7, ('host prediction accuracy', 10)), (7, ('defense response', 10)), (7, ('host strain', 7)), (7, ('host taxonomy', 7)), (7, ('host sequence', 5)), (7, ('host contig', 5)), (7, ('host metabolism', 4)), (7, ('host health', 3)),
# (8, ('life science', 18)), (8, ('life cycle', 15)), (8, ('life history', 10)), (8, ('life technology', 7)), (8, ('life history ecotype', 4)), (8, ('life history strategy', 3)), (8, ('life stage', 3)),
# (9, ('arabidopsis thaliana', 27)), (9, ('maize genome', 20)), (9, ('rice genome', 13)), (9, ('sorghum bicolor', 12)), (9, ('brachypodium distachyon', 12)), (9, ('rice chromosome', 9)), (9, ('arabidopsis genome', 7)), (9, ('rice gene', 6)), (9, ('brachypodium genome', 5)), (9, ('arabidopsis protein', 5)), (9, ('maize anthocyanin phlobaphene', 5)),
# (10, ('cancer cell', 30)), (10, ('breast cancer cell', 6)), (10, ('lymphocyte apoptosis', 4)), (10, ('tumour cell', 3)), (10, ('cancer cell bica', 3)),
# (11, ('population size', 6)), (11, ('population analysis', 5)), (11, ('population m. guttatus', 5)), (11, ('population quality', 4)), (11, ('variation rna quality', 4)), (11, ('population community ontology', 4)), (11, ('variation datum', 4)), (11, ('population development', 3)),
# (12, ('model organism', 33)), (12, ('model species', 13)), (12, ('model system', 12)), (12, ('modeling framework', 9)), (12, ('markov model', 8)), (12, ('model condition', 7)), (12, ('model development', 4)), (12, ('model plant', 4)), (12, ('model parameter', 3)),
# (13, ('promoter region', 20)), (13, ('region genome', 15)), (13, ('region chromosome', 13)), (13, ('region sequence similarity', 11)), (13, ('region interest', 10)), (13, ('coding region', 8)), (13, ('element name', 7)), (13, ('centromere region', 6)), (13, ('arm deletion', 6)), (13, ('location genome', 5)),
# (14, ('human genome', 9)), (14, ('chicken line', 6)), (14, ('human genome project', 5)), (14, ('human blood', 4)), (14, ('human error', 4)), (14, ('human population', 4)), (14, ('human gut microbiota', 3)),
# (15, ('blood transcriptome', 19)), (15, ('flow cytometry', 6)), (15, ('blood sample', 5)), (15, ('plasma membrane', 5)), (15, ('fluid sample', 5)), (15, ('blood transcriptome analysis', 4)), (15, ('donor sample', 4)),
# (16, ('biodiversity datum', 28)), (16, ('informatics community', 7)), (16, ('biodiversity hotspot', 7)), (16, ('biodiversity information facility gbif', 7)), (16, ('biology community', 5)), (16, ('biodiversity community', 5)), (16, ('biodiversity science', 5)), (16, ('biodiversity domain', 4)),
# (17, ('venom composition', 6)), (17, ('venom potency', 4)), (17, ('venom transmission system', 3)),
# (18, ('bone colonization', 9)), (18, ('bone fragment', 6)), (18, ('bone microenvironment', 4)), (18, ('bone lesion', 4)), (18, ('metastasis model', 3)), (18, ('bone fragment drug concentration', 3)), (18, ('bone segment', 2)), (18, ('bone tissue', 2)),
# (19, ('coral sponge', 9)), (19, ('sea anemone', 7)), (19, ('seawater sample', 5)), (19, ('sea water', 3)), (19, ('coral density', 3)), (19, ('coral reef', 3)), (19, ('sediment m. griffithsi.', 2)), (19, ('sea canyon', 2)), (19, ('coral habitat', 2)), (19, ('sea pen', 2)), (19, ('submarine canyon', 2)), (19, ('sea ice', 2)), (19, ('nematocyst diversity', 2))]
# embedding_json(favorite_results, query, 20, '10kFAV', "all")
