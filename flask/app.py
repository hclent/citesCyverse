#!/usr/bin/env python
from flask import Flask, render_template, request, flash, url_for, redirect, session, g, Blueprint
from flask_wtf import Form #Flask-WTF==0.12
from wtforms import TextField, SelectField
import pickle, os.path, json, logging
from werkzeug.serving import run_simple
from processors import *
from sklearn.cluster import KMeans
#MINE:
from fasttext import get_words_tags, transform_text, chooseTopNPs, load_model, getNPvecs
from fgraph2json import embedding_json
from wordcloud import *
from naive_cosineSim import load_corpus, load_datasamples, get_cosine_list, add_urls, prepare_for_histogram



app=Flask(__name__, static_url_path='/hclent/citesCyverse/flask/static', template_folder='templates')
app.config.from_pyfile('config.cfg', silent=False)

#logging
logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#load model once globally
logging.info("* LOADING FASTTEXT MODEL... THIS TAKES A WHILE...")
model = load_model("cyverse_lower.vec") #"cyverseModel.vec
logging.info("!!! DONE LOADING FASTTEXT MODEL :')")

#Form for Topic Modeling
class visOptions(Form):
    k_val = SelectField('k_val', choices=[(10,'k=10'),
										  (15, 'k=15'),(20, 'k=20'),(25, 'k=25'),
                                          (40, 'k=40'),(50, 'k=50')])
    w_words = SelectField('w_words', choices=[(4, 'w=4'),(5, 'w=5'),(6, 'w=6'), (7, 'w=7'),
											  (100, 'w=1-100'),(200, 'w=101-200'),(300, 'w=201-300'),(400, 'w=301-400'),
                                              (500, 'w=401-500'),(600, 'w=501-600'),(700, 'w=601-700'),(800, 'w=701-800'),
                                              (900, 'w=801-900'),(1000, 'w=901-1,000')])


    y_years = SelectField('y_years', choices=[(201014, '2010-2014'), (201517, '2015-2017'), (2010, '2010'),
                                              (2011, '2011'),(2012, '2012'),(2013, '2013'),(2014, '2014'),
                                              (2015, '2015'), (2016, '2016'), (2017, '2017'), (201017, "PubMedCentral 2010-2017")])

#Form for Wordclouds
class wordCloudWord(Form):
	searchWord = TextField('searchWord')


@app.route("/home/")
def homeCyverse():
    return render_template("dashboard.html")


@app.route("/cy-journals-freq/")
def cyJournalsFreq():
    s_year = "2010" #start
    e_year = "2017" #end
    unique_pubs = "753"
    unique_journals = "344"
    filename = "/home/hclent/repos/citesCyverse/flask/static/journalsvis_freq.json"
    with open(filename) as f:
        journals = json.load(f)
    return render_template("journals.html", journals=journals, unique_pubs=unique_pubs,
                       unique_journals=unique_journals, s_year=s_year, e_year=e_year)

@app.route("/cy-journals-alpha/")
def cyJournalsAlpha():
    s_year = "2010"  # start
    e_year = "2017"  # end
    unique_pubs = "753"
    unique_journals = "344"
    filename_alpha = "/home/hclent/repos/citesCyverse/flask/static/journalsvis_alpha.json"
    with open(filename_alpha) as f:
        journals = json.load(f)
    return render_template("journals.html", journals=journals, unique_pubs=unique_pubs,
                           unique_journals=unique_journals, s_year=s_year, e_year=e_year)


@app.route("/cy-wordcloud/", methods=["GET", "POST"])
def cyWordcloud():
    form = wordCloudWord()
    if request.method == "POST":
        searchWord = str(form.searchWord.data)
        searchWord = searchWord.lower()
        logging.info(searchWord)
        #check for file

        message = "Displaying cloud for words in citing papers most relating to: " + str(searchWord)

        try:
            path_to_wordcloud = "/home/hclent/repos/citesCyverse/flask/static/wordclouds"
            filename = searchWord + ".json"
            path = os.path.join(path_to_wordcloud, filename)

            with open(path) as f:
                wordcloud_data = json.load(f)
                return render_template("wordcloud.html", wordcloud_data=wordcloud_data, message=message)

        except Exception as e:
            logging.info("no file for this one...")
            logging.info("making nesDict .. ")

            try:
                blah = model[searchWord] #if it fails here, the word has no vector
                nesDict = frequency_dict("cyverse_lemmas_ALL.pickle")
                wordcloud_words = filter_by_embeddings(searchWord, nesDict)
                logging.info(wordcloud_words)
                wordcloud_data = wordcloud(searchWord, nesDict, wordcloud_words)
                return render_template("wordcloud.html", wordcloud_data=wordcloud_data, message=message)
            except Exception as e2:
                return("So sorry! The word " + str(searchWord) + " has no vector, so we can't generate a word cloud. Please refresh the page and try again!")

    else:
        path_to_wordcloud = "/home/hclent/repos/citesCyverse/flask/static/wordclouds"
        filename = "cyverseTop100.json" #this is saved as top 100 but its really the top 200 oops
        path = os.path.join(path_to_wordcloud, filename)
        message = "Cloud for top 200 words in all citing papers"
        with open(path) as f:
            wordcloud_data = str(json.load(f))
            return render_template("wordcloud.html", wordcloud_data=wordcloud_data, message=message)


@app.route("/cy-embeddings/", methods=["GET","POST"])
def cyEmbeddings():
    query = "cyverse"
    form = visOptions()
    if request.method == 'POST':
        window = int(form.w_words.data)
        logging.info(window)
        k_clusters = int(form.k_val.data)
        logging.info(k_clusters)
        years = str(form.y_years.data)
        logging.info(years)

        path_to_lemma_samples = '/home/hclent/repos/citesCyverse/flask/lemmas/'
        path_to_fgraphs = '/home/hclent/repos/citesCyverse/flask/static/fgraphs/'
        if years == "201017":
            years = "pubmed"

        filename = 'fgraph_' + str(query) + '_' + str(k_clusters) + '_' + str(window) + '_' + str(years) + '.json'

        full_filepath = os.path.join(path_to_fgraphs, filename) #check this filepath to see if frgaph json exists
        filepath = os.path.join('fgraphs', filename) #load from this filepath


        #if a file for this analysis doesn't already exist, run the analysis and make the json
        if not os.path.isfile(full_filepath):

            if years == "201014":
                year_interval = '2010_2014'
                message_years = "2010-2014"
            elif years == "201517":
                year_interval = '2015_2017'
                message_years = "2015-2017"
            if years == "201017":
                year_interval = "pubmed"
                message_years = "2010-2017"
            else:
                year_interval = str(years)
                message_years = str(years)

            filename = 'cyverse_lemmas_' + year_interval + '.pickle'
            load_file = os.path.join(path_to_lemma_samples, filename)
            logging.info(load_file)

            logging.info(" extracing words and tags ... ")
            flat_words, flat_tags = get_words_tags(load_file)
            logging.info(type(flat_tags))
            logging.info(type(flat_tags[0]))
            logging.info("extracting NounPhrases ... ")
            xformed_tokens = transform_text(flat_words, flat_tags)
            npDict = chooseTopNPs(xformed_tokens)

            #top 100,200,300,400,500,1000,5000,10000, 25000, ??
            ### OPTIONAL FILTER npDICT ####
            if window == 100:
                logging.info("w=1-100")
                top = list(npDict.most_common(100))
                message_window = "1-100"
            elif window == 200:
                logging.info("w=101-200")
                top_100 = list(npDict.most_common(101))
                top_200 = list(npDict.most_common(200))
                top = [item for item in top_200 if item not in top_100]
                message_window = "101-200"
            elif window == 300:
                logging.info("w=201-300")
                top_200 = list(npDict.most_common(201))
                top_300 = list(npDict.most_common(300))
                top = [item for item in top_300 if item not in top_200]
                message_window = "201-300"
            elif window == 400:
                logging.info("w=301-400")
                top_300 = list(npDict.most_common(301))
                top_400 = list(npDict.most_common(400))
                top = [item for item in top_400 if item not in top_300]
                message_window = "301-400"
            elif window == 500:
                top_half = list(npDict.most_common(401))
                bottom_half = list(npDict.most_common(500))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "401-500"
            elif window == 600:
                top_half = list(npDict.most_common(501))
                bottom_half = list(npDict.most_common(600))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "501-600"
            elif window == 700:
                top_half = list(npDict.most_common(601))
                bottom_half = list(npDict.most_common(700))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "601-700"
            elif window == 800:
                top_half = list(npDict.most_common(701))
                bottom_half = list(npDict.most_common(800))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "701-800"
            elif window == 900:
                top_half = list(npDict.most_common(801))
                bottom_half = list(npDict.most_common(900))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "801-900"
            elif window == 1000:
                top_half = list(npDict.most_common(901))
                bottom_half = list(npDict.most_common(1000))
                top = [item for item in bottom_half if item not in top_half]
                message_window = "901-1,000"
            else:
                top = list(npDict.most_common(window))


            logging.info("done collecting top NPs! ")
            matrix = getNPvecs(top, model)

            # do kmeans
            logging.info("clustering vectors ... ")
            kmeans = KMeans(n_clusters=k_clusters, random_state=2).fit(matrix)
            results = list(zip(kmeans.labels_, top))

            #filter topics
            labels = [r[0] for r in results]

            delete_topics = []
            for i in range(0, k):
                if labels.count(i) < 3:  # clean out topics with less than 3 words in them
                    delete_topics.append(i)

            keep_results = []

            for combo in results:
                if combo[0] not in delete_topics:
                    keep_results.append(combo)


            #save to json
            logging.info("saving results to json ... ")
            embedding_json(keep_results, query, k_clusters, window, years)
            message =  str(k_clusters) + " topics from the top " + str(message_window) + " noun phrases from " + str(message_years)
            return render_template("embeddings.html", filepath=filepath, message=message)

        #if an analysis for this analysis already exists, just load it!
        if os.path.isfile(full_filepath):
            logging.info("A file already exists for this analysis!!")

            if years == "201014":
                message_years = "2010-2014"
            elif years == "201517":
                message_years = "2015-2017"
            elif years == "201017":
                message_years = "2010-2017"
            else:
                message_years = str(years)
            if window == 100:
                message_window = "1-100"
            if window == 200:
                message_window = "101-200"
            if window == 300:
                message_window = "201-300"
            if window == 400:
                message_window = "301-400"
            if window == 500:
                message_window = "401-500"
            if window == 600:
                message_window = "501-600"
            if window == 700:
                message_window = "601-700"
            if window == 800:
                message_window = "701-800"
            if window == 900:
                message_window = "801-900"
            if window == 1000:
                message_window = "901-1,000"

            message = str(k_clusters) + " topics from the top " + str(message_window) + " noun phrases from " + str(message_years)
            return render_template("embeddings.html", filepath=filepath, message=message)

    else:
        #Default data are my favorite topics found by algorithm in the top 300 topics for the top 30k words :')
        #filename = "fgraph_cyverse_20_10kFAV.json"
        filename = "fgraph_cyverse_20_10kFAV_all.json"
        filepath = os.path.join('fgraphs', filename)
        message = "Our favorite 20 topics from the top 300,000 noun phrases from 2010-2017"
        return render_template("embeddings.html", filepath=filepath, message=message)


#The corpora for these live on geco
@app.route("/cy-textcompare/")
def cyTextCompare():
    corpus_vec, color = load_corpus("darwin")
    data_vecs_list, pmcids_list = load_datasamples()
    cosine_list = get_cosine_list(corpus_vec, data_vecs_list)
    sorted_combos = add_urls(cosine_list, color, pmcids_list)
    x, y, names, color = prepare_for_histogram(sorted_combos)
    title = "DARWIN OR WHATEVER"
    return render_template("textcompare.html", x=x, y=y, title=title, color=color, names=names)


@app.errorhandler(404)
def page_not_found(e):
    return("you shouldn't be here!! Heather's custom 404 error. ")

#configuration settings
if __name__ == '__main__':
    run_simple('0.0.0.0', 9192, app, use_reloader=True) #to run with Apache on geco
    #app.run(host='0.0.0.0') #to run locally!
