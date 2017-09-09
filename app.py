from flask import Flask, render_template, request, flash, url_for, redirect, session, g, Blueprint
from flask_wtf import Form
from wtforms import TextField, SelectField
import pickle, os.path, json, logging
#from werkzeug.serving import run_simple
from processors import *
#MINE:
from make_lemmas import load_lemma_cache
from fasttext import get_words_tags, transform_text, chooseTopNPs, load_model, getNPvecs
from sklearn.cluster import KMeans
from fgraph2json import embedding_json

#TODO: fix hard-coded paths

app=Flask(__name__, static_url_path='/Users/heather/Desktop/citesCyverse/static',  template_folder='templates')

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



#TODO: fix repeat/similar journal names, and include 2010 papers as legitimate column
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

@app.route("/cy-wordcloud/")
def cyWordcloud():
    return render_template("wordcloud.html")

#TODO: there are too many NPs in the lemmas_ALL file! if we go based on most_common, then basically only plant stuff gets though.
@app.route("/cy-embeddings/", methods=["GET","POST"])
def cyEmbeddings():
    query = "cyverse"
    form = visOptions()
    if request.method == 'POST':
        window = int(form.w_words.data)
        logging.info(window)
        k_clusters = int(form.k_val.data)

        #check if the json embeddings vis file exists
        #TODO: add user option for years

        #TODO: split up the cyverse lemmas by 2010-2013 and 2014-2017 and make it a user option. (This ALL file is too cluttered!)
        path_to_lemma_samples = "/Users/heather/Desktop/citesCyverse/lemmas/cyverse_lemmas_ALL.pickle"
        flat_words, flat_tags = get_words_tags(path_to_lemma_samples) # the cyverse_lemmas_ALL.pickle file is hard-coded in this method
        xformed_tokens = transform_text(flat_words, flat_tags)
        #TODO: FILTER THIS OMG!!!!
        npDict = chooseTopNPs(xformed_tokens) #249,199 Noun Phrases!

        #TODO: need to decide what the bins will be here for top NPs
        #top 100,200,300,400,500,1000,5000,10000, 25000, ??
        ### OPTIONAL FILTER npDICT ####
        if window == 100:
            logging.info("w=1-100")
            top = list(npDict.most_common(100))
        elif window = 200:
            logging.info("w=2001-")
            top_200 = list(npDict.most_common(201))
            top_300 = list(npDict.most_common(300))
            top = [item for item in top_300 if not in top_201]
        else:
            top = list(npDict.most_common(window))
        logging.info("done collecting top NPs! ")

        matrix = getNPvecs(top, model)  # top or just npDict can go here

        # do kmeans
        kmeans = KMeans(n_clusters=k_clusters, random_state=2).fit(matrix)
        results = list(zip(kmeans.labels_, keep_top))
        #save to json
        embedding_json(results, query, k_clusters, window)

        filename = 'fgraph_' + str(query) + '_' + str(k_clusters) + '_' + str(window) + '.json'
        filepath = os.path.join('fgraphs', filename)
        return render_template("embeddings.html", filepath=filepath)

    else:
        #Default data are my favorite topics found in the top 30k words :')
        filename = "fgraph_cyverse_20_10kFAV.json"
        filepath = os.path.join('fgraphs', filename) #template tells it to look in /static
        return render_template("embeddings.html", filepath=filepath)


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
