from flask import Flask, render_template, request, flash, url_for, redirect, session, g, Blueprint
from flask_wtf import Form #Flask-WTF==0.12
from wtforms import TextField, SelectField
import pickle, os.path, json, logging
#from werkzeug.serving import run_simple
from processors import *
from sklearn.cluster import KMeans
#MINE:
from make_lemmas import load_lemma_cache
from fasttext import get_words_tags, transform_text, chooseTopNPs, load_model, getNPvecs
from fgraph2json import embedding_json


app=Flask(__name__, static_url_path='/Users/heather/Desktop/citesCyverse/static',  template_folder='templates')
#TODO: fix hard-coded paths in config file
app.config.from_pyfile('config.cfg', silent=False)

#logging
logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#load model once globally
model = load_model("17kmodel.vec")

#Form for Topic Modeling
class visOptions(Form):
    k_val = SelectField('k_val', choices=[(10,'k=10'),
										  (15, 'k=15'),(20, 'k=20'),(25, 'k=25'),
                                          (40, 'k=40'),(50, 'k=50')])
    w_words = SelectField('w_words', choices=[(4, 'w=4'),(5, 'w=5'),(6, 'w=6'), (7, 'w=7'),
											  (100, 'w=1-100'),(200, 'w=101-200'),(300, 'w=201-300'),(400, 'w=301-400')])
    y_years = SelectField('y_years', choices=[(201013, '2010-2013'), (201417, '2014-2017')])


#Form for Wordclouds
class nesOptions(Form):
    y_years = SelectField('y_years', choices=[(2011, '2011'), (2012, '2012'), (2013, '2013'), (2014, '2014'), (2015, '2015'),
                                   (2016, '2016'), (2017, '2017')])


@app.route("/home/")
def homeCyverse():
    return render_template("dashboard.html")


#TODO: collapse repeat/similar journal names
@app.route("/cy-journals/")
def cyJournals():
    filename = "/Users/heather/Desktop/citesCyverse/static/journalsvis.json"
    with open(filename) as f:
        journals = json.load(f)
    s_year = "2010" #start
    e_year = "2018" #end
    unique_pubs = "753"
    unique_journals = "467" #needs to be updated
    #journals = {}
    return render_template("journals.html", journals=journals, unique_pubs=unique_pubs,
                           unique_journals=unique_journals, s_year=s_year, e_year=e_year)


#TODO: what are we visualizing in the word-cloud? most frequent words?
#Maybe use TF-IDF to filter words instead of most frequent?
@app.route("/cy-wordcloud/")
def cyWordcloud():
    return render_template("wordcloud.html")


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

        path_to_lemma_samples = '/Users/heather/Desktop/citesCyverse/lemmas/'
        path_to_fgraphs = '/Users/heather/Desktop/citesCyverse/static/fgraphs/'

        filename = 'fgraph_' + str(query) + '_' + str(k_clusters) + '_' + str(window) + '_' + str(years) + '.json'

        full_filepath = os.path.join(path_to_fgraphs, filename) #check this filepath to see if frgaph json exists
        filepath = os.path.join('fgraphs', filename) #load from this filepath


        #if a file for this analysis doesn't already exist, run the analysis and make the json
        if not os.path.isfile(full_filepath):

            if years == "201013":
                year_interval = '2010_2013'
            elif years == "201417":
                year_interval = '2014_2017'
            else:
                logging.info("something didn't work right... year_interval is being set to 2010-2013")
                year_interval = '2010_2013' #if something funky happens just... set this to 2010-2013 :/

            filename = 'cyverse_lemmas_' + year_interval + '.pickle'
            load_file = os.path.join(path_to_lemma_samples, filename)
            logging.info(load_file)

            logging.info(" extracing words and tags ... ")
            flat_words, flat_tags = get_words_tags(load_file)
            logging.info(" extracting NounPhrases ... ")
            xformed_tokens = transform_text(flat_words, flat_tags)
            #TODO: Needs better filtering of cyverse-specific/publication stopwords ("figure", "table") etc.
            npDict = chooseTopNPs(xformed_tokens)

            #TODO: need to decide what the bins will be here for top NPs
            #top 100,200,300,400,500,1000,5000,10000, 25000, ??
            ### OPTIONAL FILTER npDICT ####
            if window == 100:
                logging.info("w=1-100")
                top = list(npDict.most_common(100))
            elif window == 200:
                logging.info("w=101-200")
                top_100 = list(npDict.most_common(101))
                top_200 = list(npDict.most_common(200))
                top = [item for item in top_200 if item not in top_100]
            elif window == 300:
                logging.info("w=201-300")
                top_200 = list(npDict.most_common(201))
                top_300 = list(npDict.most_common(300))
                top = [item for item in top_300 if item not in top_200]
            elif window == 400:
                logging.info("w=301-400")
                top_300 = list(npDict.most_common(301))
                top_400 = list(npDict.most_common(400))
                top = [item for item in top_400 if item not in top_300]
            else:
                top = list(npDict.most_common(window))


            logging.info("done collecting top NPs! ")
            matrix = getNPvecs(top, model)

            # do kmeans
            logging.info("clustering vectors ... ")
            kmeans = KMeans(n_clusters=k_clusters, random_state=2).fit(matrix)
            results = list(zip(kmeans.labels_, top))
            #save to json
            logging.info("saving results to json ... ")
            embedding_json(results, query, k_clusters, window, years)
            return render_template("embeddings.html", filepath=filepath)

        #if an analysis for this analysis already exists, just load it!
        if os.path.isfile(full_filepath):
            logging.info("A file already exists for this analysis!!")
            return render_template("embeddings.html", filepath=filepath)

    else:
        #Default data are my favorite topics found by algorithm in the top 300 topics for the top 30k words :')
        filename = "fgraph_cyverse_20_10kFAV.json"
        filepath = os.path.join('fgraphs', filename)
        return render_template("embeddings.html", filepath=filepath)


#The corpora for these live on geco
@app.route("/cy-textcompare/")
def cyTextCompare():
    return render_template("textcompare.html")

@app.route('/test/')
def testingStuff():
    return("test!!")

@app.errorhandler(404)
def page_not_found(e):
    return("you shouldn't be here!!")

#configuration settings
if __name__ == '__main__':
    #run_simple('0.0.0.0', 5000, app, use_reloader=True) #to run with Apache on geco
    app.run(host='0.0.0.0') #to run locally!
