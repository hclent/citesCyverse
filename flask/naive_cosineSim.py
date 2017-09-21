import string, pickle, csv, re
import naive_makeVecs as makeVecs #mine

#TODO: get the citation labels and axis labels from the tsv
#from database_management import db_citations_mini_hyperlink, db_citations_hyperlink_retrieval, db_pmid_axis_label, db_pmid_hyperlink_retrieval #mine
#from cache_lemma_nes import load_lemma_cache #mine


#Load from pickled data_samples instead of filename
def loadFromDataSamples(data_samples):
    vecs_list = []

    for document in data_samples:
        vectorCounter = makeVecs.text2vec(document)
        vecs_list.append(vectorCounter)
    return vecs_list


#Load txt file and make it into a vector
def loadMessages(filename):
    fcorpus = open(filename, 'r')
    fcorpus = fcorpus.read() #str
    vectorCounter = makeVecs.text2vec(fcorpus)
    return (vectorCounter)


# Print cosine similarity scores
def cosineSimilarityScore(vector1, vector2):
    cosine_sim_score_1_2 = (makeVecs.cosine(vector1, vector2))
    return cosine_sim_score_1_2


#only load eligible_papers into load_corpus
def load_corpus(corpus):
    if corpus == 'startrek':
        raw = "/home/hclent/data/corpora/startrek/105.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(63, 100, 168)'
    if corpus == 'darwin':
        raw = "/home/hclent/data/corpora/darwin.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(8, 114, 32)'
    if corpus == 'brain_speech':
        raw = "/home/hclent/data/corpora/brain_speech.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(8, 114, 32)'
    if corpus == 'grecoroman':
        raw = "/home/hclent/data/corpora/grecoroman_med.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(8, 114, 32)'
    if corpus == 'mouse':
        raw = "/home/hclent/data/corpora/mouse.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(8, 114, 32)'
    if corpus == 'yeast':
        raw = "/home/hclent/data/corpora/yeast.txt"
        corpus_vec = loadMessages(raw)
        color = 'rgb(8, 114, 32)'
    return corpus_vec, color


#Updated to use new cache :) yay
def load_datasamples():
    with open("/home/hclent/repos/citesCyverse/flask/lemmas/cyverse_lemmas_ALL.pickle", "rb") as f:
        lemma_samples = pickle.load(f)
    lemma_list = [l[1] for l in lemma_samples]
    pmcids_list = [l[0] for l in lemma_samples]
    list_data_strings = [' '.join(map(str, l)) for l in lemma_list] #['string string', 'string string string']
    data_vecs_list = loadFromDataSamples(list_data_strings)
    return data_vecs_list, pmcids_list


def get_cosine_list(corpus_vec, data_vecs_list):
    cosine_list = []
    for vec_n in data_vecs_list:
        cosine_sim_score_1_2 = cosineSimilarityScore(corpus_vec, vec_n)
        score = float("{0:.4f}".format(float(cosine_sim_score_1_2)))
        score = float(score * 100) #.25 --> 25%
        cosine_list.append(score)
    return cosine_list




#take the list cosines and match scores with the url to the paper
#Updated with new titles, making sure there's no repeats :)
def add_urls(cosine_list, color, pmcids_list):

    histogram_labels = [] #this is what will be in the visualization
    apa_labels = []

    tsvDict = {}
    #{'id': [author, pubdate, title, journal]}

    #apa = str(author+' ('+pubdate+'). '+title+'. '+journal+'. Retrieved from '+url)
    potential_ids = []
    potential_authors = []
    potential_years_list = []
    potential_titles = []
    potential_journals_list = []

    # TODO: check for bio status
    with open('journalsNoDuplicates.tsv', 'r') as tsvin:
        tsv = csv.reader(tsvin, delimiter='\t')
        next(tsv)
        next(tsv) #skip the first two rows

        for row in tsv:
            try:
                id = (row[10]) #get rid of .txt
                fixed_id = re.sub('\.txt', '', id)
                potential_ids.append(fixed_id)
            except Exception as e0:
                #text file
                pass
            try:
                author = (row[0])
                potential_authors.append(author)
            except Exception as e1:
                #no author
                pass
            try:
                year = (row[4])
                potential_years_list.append(year)
            except Exception as e2:
                # no year
                pass
            try:
                title = (row[1])
                potential_titles.append(title)
            except Exception as e3:
                #no title
                pass
            try:
                journal = (row[2])
                potential_journals_list.append(journal)
            except Exception as e4:
                # no journal
                pass

    combo = list(zip(potential_ids, potential_authors, potential_years_list, potential_titles, potential_journals_list))

    for c in combo:
        possible_id = c[0]
        possible_author = c[1]
        possible_year = c[2]
        possible_title = c[3]
        possible_journal = c[4]
        year = re.search('\d{4}', possible_year)
        if year and possible_journal != '' and possible_id != '' and possible_author != '' and possible_title != '':  # if all the stuff isn't empty
            y = str(year.group(0))
            j = str(possible_journal)
            tsvDict[possible_id] = [possible_author, y, possible_title, j]

    for i, pmcid in enumerate(pmcids_list):
        try:
            list_for_apa = tsvDict[pmcid]
            auth = list_for_apa[0]
            year = list_for_apa[1]
            title = list_for_apa[2]
            journal = list_for_apa[3]
            label = str(auth+' ('+year+'). '+title+'. '+journal)

            graph_label = "Paper " + str(i)
            histogram_labels.append(graph_label)
            apa_labels.append(label)
        except Exception as e:
            pass
            #maybe I don't have the file? idk
    #
    colors_list = [color] * int(len(histogram_labels))
    #print(len(histogram_labels))
    #print(len(apa_labels))

    #
    #need to sort the histogram_labels to match that order
    combined = list(zip(cosine_list, histogram_labels, apa_labels, colors_list))
    sorted_combos = sorted(combined,  key=lambda x: x[0], reverse=False)
    #print(len(sorted_combos))
    return sorted_combos


def prepare_for_histogram(sorted_combos):
    x = [] #url labels
    y = [] #data points
    names = []
    color = []
    for combo in sorted_combos:
        x.append(combo[1]) #append url label to x
        y.append(combo[0]) #append cosine score to y
        names.append(combo[2])
        color.append(combo[3])
    return x, y, names, color



# corpus_vec, color = load_corpus("darwin")
# data_vecs_list, pmcids_list = load_datasamples()
# cosine_list = get_cosine_list(corpus_vec, data_vecs_list)
# sorted_combos = add_urls(cosine_list, color, pmcids_list)
# x, y, names, color = prepare_for_histogram(sorted_combos)