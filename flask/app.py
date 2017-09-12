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

'''
TEST TEST TEST
'''

app=Flask(__name__, static_url_path='/hclent/citesCyverse/flask/static', template_folder='templates')
#TODO: fix hard-coded paths in config file
app.config.from_pyfile('config.cfg', silent=False)

#logging
logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#load model once globally
#TODO: re-un-comment this
#model = load_model("17kmodel.vec")

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
    filename = "/home/hclent/repos/citesCyverse/flask/static/journalsvis.json"
    with open(filename) as f:
        journals = json.load(f)
    s_year = "2010" #start
    e_year = "2018" #end
    unique_pubs = "753"
    unique_journals = "467" #needs to be updated
    #journals = {}
    return render_template("journals.html", journals=journals, unique_pubs=unique_pubs,
                           unique_journals=unique_journals, s_year=s_year, e_year=e_year)


#TODO: add form and button to generate wordcloud for a given keyword
#TODO: fix caching
#Maybe use TF-IDF to filter words instead of most frequent?
@app.route("/cy-wordcloud/")
def cyWordcloud():
    # filename = "/Users/heather/Desktop/citesCyverse/static/wordclouds/ocean.json"
    # with open(filename, "r") as f:
    #     wordcloud_data = json.load(f)

    #wordcloud_data = [{"text": "geochemical", "size": 3}, {"text": "groundwater", "size": 15}, {"text": "sunlit", "size": 7}, {"text": "seafloor", "size": 28}, {"text": "chemolithoautotrophic", "size": 1}, {"text": "metacommunity", "size": 3}, {"text": "inhabit", "size": 28}, {"text": "shallow-water", "size": 1}, {"text": "plankton", "size": 32}, {"text": "lake", "size": 99}, {"text": "marine", "size": 339}, {"text": "biogeographical", "size": 39}, {"text": "sediment", "size": 45}, {"text": "microclimate", "size": 20}, {"text": "pond", "size": 85}, {"text": "rhizosphere", "size": 9}, {"text": "phytoplankton", "size": 94}, {"text": "seawater.", "size": 1}, {"text": "heterotrophically", "size": 1}, {"text": "hydrothermally", "size": 1}, {"text": "geothermal", "size": 1}, {"text": "estuarine", "size": 2}, {"text": "low-water", "size": 1}, {"text": "subsurface", "size": 16}, {"text": "ecological", "size": 653}, {"text": "reef", "size": 13}, {"text": "alpine", "size": 28}, {"text": "methane", "size": 2}, {"text": "metagenome", "size": 340}, {"text": "mesopelagic", "size": 25}, {"text": "submarine", "size": 4}, {"text": "biome", "size": 53}, {"text": "pelagic", "size": 11}, {"text": "agroecosystem", "size": 10}, {"text": "zooplankton", "size": 45}, {"text": "microbial", "size": 601}, {"text": "volcanic", "size": 11}, {"text": "agro-ecosystem", "size": 11}, {"text": "high-water", "size": 1}, {"text": "plume", "size": 12}, {"text": "biosphere", "size": 22}, {"text": "deep-sea", "size": 10}, {"text": "habitation", "size": 2}, {"text": "watershed", "size": 55}, {"text": "anoxygenic", "size": 2}, {"text": "wastewater", "size": 2}, {"text": "mycoheterotrophic", "size": 1}, {"text": "community", "size": 4098}, {"text": "soil", "size": 822}, {"text": "ecosystem", "size": 692}, {"text": "bedrock", "size": 7}, {"text": "anthropogenic", "size": 98}, {"text": "arctic", "size": 23}, {"text": "ocean", "size": 318}, {"text": "fauna", "size": 20}, {"text": "mariner", "size": 4}, {"text": "palaeoclimate", "size": 1}, {"text": "biosphere.", "size": 1}, {"text": "hypersaline", "size": 13}, {"text": "bathypelagic", "size": 8}, {"text": "ice-water", "size": 1}, {"text": "aquifer", "size": 2}, {"text": "oceanography", "size": 25}, {"text": "virioplankton", "size": 1}, {"text": "headwater", "size": 4}, {"text": "upwelled", "size": 1}, {"text": "habitat", "size": 562}, {"text": "chimney", "size": 3}, {"text": "archipelago", "size": 61}, {"text": "freshwater", "size": 44}, {"text": "anoxic", "size": 6}, {"text": "metagenomic", "size": 379}, {"text": "euphotic", "size": 2}, {"text": "ecosystem-level", "size": 1}, {"text": "geochemistry", "size": 6}, {"text": "metaproteome", "size": 4}, {"text": "mangrove", "size": 5}, {"text": "surface-water", "size": 1}, {"text": "grassland", "size": 58}, {"text": "ecosystem.", "size": 2}, {"text": "lagoon", "size": 72}, {"text": "glacier", "size": 28}, {"text": "atmospheric", "size": 84}, {"text": "terrain", "size": 75}, {"text": "subseafloor", "size": 2}, {"text": "epipelagic", "size": 38}, {"text": "shallow", "size": 37}, {"text": "waterfall", "size": 1}, {"text": "estuary", "size": 9}, {"text": "sea-ice", "size": 1}, {"text": "subtropical", "size": 34}, {"text": "inhabitant", "size": 5}, {"text": "aquatic", "size": 94}, {"text": "mud", "size": 23}, {"text": "seawater", "size": 55}, {"text": "salinity", "size": 60}, {"text": "biogeographic", "size": 55}, {"text": "ecologic", "size": 3}, {"text": "gyre", "size": 3}, {"text": "solar", "size": 102}, {"text": "picoplankton", "size": 24}, {"text": "deep-ocean", "size": 2}, {"text": "bacterioplankton", "size": 2}, {"text": "sewage", "size": 7}, {"text": "brackish", "size": 4}, {"text": "underwater", "size": 6}, {"text": "heterotroph", "size": 2}, {"text": "limnic", "size": 2}, {"text": "coastal", "size": 108}, {"text": "biodiversity", "size": 1035}, {"text": "ecology", "size": 801}, {"text": "coast", "size": 68}, {"text": "riverine", "size": 4}, {"text": "pelagibacter", "size": 2}, {"text": "savannah", "size": 3}, {"text": "river", "size": 147}, {"text": "habitats.", "size": 1}, {"text": "mixotrophic", "size": 1}, {"text": "metagenomics", "size": 2}, {"text": "planktonic", "size": 8}, {"text": "offshore", "size": 1}, {"text": "oceanic", "size": 54}, {"text": "biogeochemical", "size": 23}, {"text": "assemblage", "size": 178}, {"text": "muddy", "size": 1}, {"text": "heterotrophy", "size": 1}, {"text": "deepwater", "size": 1}, {"text": "temperate", "size": 228}, {"text": "microclimatic", "size": 3}, {"text": "borehole", "size": 9}, {"text": "planet", "size": 57}, {"text": "shore", "size": 6}, {"text": "cosmopolitan", "size": 8}, {"text": "mountainous", "size": 14}, {"text": "photic", "size": 9}, {"text": "deep-water", "size": 10}, {"text": "oxic", "size": 2}, {"text": "heterotrophic", "size": 20}, {"text": "terrestrial", "size": 108}, {"text": "high-latitude", "size": 1}, {"text": "biogeochemistry", "size": 15}, {"text": "wetland", "size": 28}, {"text": "autotrophic", "size": 4}, {"text": "hydrothermal", "size": 12}, {"text": "arid", "size": 47}, {"text": "microhabitat", "size": 2}, {"text": "open-ocean", "size": 1}, {"text": "intertidal", "size": 4}, {"text": "horizon", "size": 27}, {"text": "metaproteomic", "size": 6}, {"text": "pelagiphage", "size": 1}, {"text": "oligotrophic", "size": 3}, {"text": "picophytoplankton", "size": 2}, {"text": "photoautotrophic", "size": 2}, {"text": "sedimentary", "size": 5}, {"text": "depths", "size": 66}, {"text": "cyanobacterial", "size": 15}, {"text": "upwelling", "size": 8}, {"text": "oceanographic", "size": 12}, {"text": "basaltic", "size": 4}, {"text": "ephemeral", "size": 12}]
    #wordcloud_data = [{"size": 10, "text": "carcinogenesis"}, {"size": 10, "text": "invasively"}, {"size": 10, "text": "malignancy"}, {"size": 10, "text": "cancer-type"}, {"size": 92, "text": "patient"}, {"size": 37, "text": "incidence"}, {"size": 10, "text": "chemotherapeutic"}, {"size": 11, "text": "metastatic"}, {"size": 10, "text": "pancreatic"}, {"size": 10, "text": "anti-metastasis"}, {"size": 10, "text": "prostate"}, {"size": 10, "text": "prognosis"}, {"size": 10, "text": "recurrence"}, {"size": 10, "text": "colorectal"}, {"size": 143, "text": "aggressive"}, {"size": 10, "text": "small-cell"}, {"size": 10, "text": "melanoma"}, {"size": 3222, "text": "cell"}, {"size": 10, "text": "colon"}, {"size": 10, "text": "carcinoma"}, {"size": 10, "text": "malignant"}, {"size": 10, "text": "gastric"}, {"size": 10, "text": "adenocarcinoma"}, {"size": 10, "text": "invasiveness"}, {"size": 24, "text": "tumor"}, {"size": 12, "text": "metastasis"}, {"size": 266, "text": "cancer"}, {"size": 10, "text": "cervical"}, {"size": 127, "text": "invasive"}, {"size": 10, "text": "tumorigenesis"}, {"size": 10, "text": "stromal"}, {"size": 10, "text": "abreast"}, {"size": 20, "text": "lung"}, {"size": 10, "text": "cell-line"}, {"size": 59, "text": "progression"}, {"size": 10, "text": "bladder"}, {"size": 10, "text": "breast-cancer"}, {"size": 10, "text": "men"}, {"size": 42, "text": "breast"}, {"size": 80, "text": "oral"}, {"size": 10, "text": "hepatocellular"}]
    #wordcloud_data = [{"size": 24, "text": "optics"}, {"size": 106, "text": "photograph"}, {"size": 10, "text": "semi-automatically"}, {"size": 261, "text": "optical"}, {"size": 66, "text": "zoom"}, {"size": 18, "text": "time-lapse"}, {"size": 10, "text": "cropped"}, {"size": 10, "text": "gray-scale"}, {"size": 873, "text": "digital"}, {"size": 20, "text": "semi-automatic"}, {"size": 10, "text": "fiducial"}, {"size": 87, "text": "laser"}, {"size": 15, "text": "top-view"}, {"size": 11, "text": "multi-view"}, {"size": 4039, "text": "image"}, {"size": 10, "text": "autofluorescence"}, {"size": 10, "text": "visualizer"}, {"size": 32, "text": "brightness"}, {"size": 10, "text": "field-of-view"}, {"size": 11, "text": "slider"}, {"size": 457, "text": "camera"}, {"size": 23, "text": "convolutional"}, {"size": 18, "text": "grayscale"}, {"size": 10, "text": "dual-color"}, {"size": 10, "text": "side-view"}, {"size": 77, "text": "overlay"}, {"size": 21, "text": "confocal"}, {"size": 11, "text": "20x"}, {"size": 21, "text": "photographic"}, {"size": 10, "text": "micrometer"}, {"size": 10, "text": "imager"}, {"size": 106, "text": "microscopy"}, {"size": 21, "text": "digitally"}, {"size": 125, "text": "fluorescence"}, {"size": 70, "text": "imagery"}, {"size": 86, "text": "scanner"}, {"size": 16, "text": "photography"}, {"size": 10, "text": "tomographic"}, {"size": 19, "text": "eclipse"}, {"size": 10, "text": "holographic"}, {"size": 10, "text": "photographed"}, {"size": 10, "text": "microsite"}, {"size": 10, "text": "multiphoton"}, {"size": 27, "text": "bright"}, {"size": 547, "text": "imaging"}, {"size": 10, "text": "zoom-in"}, {"size": 19, "text": "image."}, {"size": 62, "text": "microscope"}, {"size": 10, "text": "lapse"}, {"size": 250, "text": "video"}, {"size": 10, "text": "in-focus"}, {"size": 10, "text": "deconvolute"}, {"size": 10, "text": "camera."}, {"size": 10, "text": "barcode-scanner"}, {"size": 10, "text": "deconvolution"}, {"size": 10, "text": "3-dimensional"}, {"size": 94, "text": "plane"}, {"size": 10, "text": "flatbed"}, {"size": 717, "text": "visualization"}, {"size": 10, "text": "captured"}, {"size": 10, "text": "greyscale"}, {"size": 10, "text": "brightest"}, {"size": 31, "text": "imagej"}, {"size": 12, "text": "epifluorescence"}, {"size": 10, "text": "scanner."}, {"size": 29, "text": "semi-automated"}, {"size": 10, "text": "stereomicroscope"}, {"size": 243, "text": "stack"}, {"size": 16, "text": "magnification"}, {"size": 10, "text": "8-bit"}, {"size": 78, "text": "scanning"}, {"size": 10, "text": "40x"}, {"size": 10, "text": "16-bit"}]
    wordcloud_data = [{"text": "predisposed", "size": 10}, {"text": "undiagnosed", "size": 10}, {"text": "fatal", "size": 13}, {"text": "manifestation", "size": 16}, {"text": "neurological", "size": 10}, {"text": "cure", "size": 25}, {"text": "disease.", "size": 10}, {"text": "symptomatology", "size": 10}, {"text": "development", "size": 3205}, {"text": "misdiagnosed", "size": 10}, {"text": "autoimmune", "size": 31}, {"text": "diagnose", "size": 44}, {"text": "disease", "size": 692}, {"text": "antecedent", "size": 10}, {"text": "disorder", "size": 72}, {"text": "asymptomatic", "size": 10}, {"text": "chronic", "size": 23}, {"text": "severity", "size": 84}, {"text": "diabetes", "size": 14}, {"text": "illness", "size": 10}, {"text": "pathotype", "size": 10}, {"text": "progression", "size": 59}, {"text": "superinfection", "size": 10}, {"text": "causative", "size": 15}, {"text": "cardiovascular", "size": 17}, {"text": "deteriorating", "size": 10}, {"text": "risk", "size": 301}, {"text": "pathological", "size": 20}, {"text": "deterioration", "size": 10}, {"text": "autoimmunity", "size": 20}, {"text": "neurodegenerative", "size": 10}, {"text": "devastating", "size": 10}, {"text": "preventable", "size": 10}, {"text": "neurologic", "size": 10}, {"text": "disability", "size": 10}, {"text": "dementia", "size": 10}, {"text": "management", "size": 2631}, {"text": "recurrence", "size": 10}, {"text": "suffering", "size": 10}, {"text": "causally", "size": 10}, {"text": "severe", "size": 100}, {"text": "clinically", "size": 10}, {"text": "diseased", "size": 26}, {"text": "pathogenesis", "size": 10}, {"text": "recurrent", "size": 25}, {"text": "patient", "size": 92}, {"text": "etiology", "size": 10}, {"text": "diagnosis", "size": 68}, {"text": "outcome", "size": 353}, {"text": "pathology", "size": 47}, {"text": "recurrently", "size": 10}, {"text": "malignancy", "size": 10}, {"text": "prevention", "size": 27}, {"text": "sclerosis", "size": 10}, {"text": "treat", "size": 261}, {"text": "systemic", "size": 76}, {"text": "symptomatic", "size": 10}, {"text": "clinical", "size": 146}, {"text": "disease-", "size": 10}, {"text": "asymptomatically", "size": 10}, {"text": "complication", "size": 30}, {"text": "pathophysiology", "size": 10}, {"text": "neurologically", "size": 10}, {"text": "susceptibility", "size": 70}, {"text": "progressive", "size": 31}, {"text": "predisposition", "size": 10}, {"text": "early-onset", "size": 10}, {"text": "threatening", "size": 10}, {"text": "ulcerative", "size": 10}, {"text": "late-onset", "size": 10}, {"text": "incidence", "size": 37}, {"text": "disease-resistance", "size": 10}, {"text": "early-stage", "size": 10}, {"text": "prevalence", "size": 54}, {"text": "prognosis", "size": 10}, {"text": "pathogenic", "size": 38}]
    return render_template("wordcloud.html", wordcloud_data=wordcloud_data)


#TODO: Needs better filtering of cyverse-specific/publication stopwords ("figure", "table") etc.
#TODO: need to decide what the bins will be here for top NPs (only the top 400 is probably not ideal)
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
        path_to_fgraphs = '/home/hclent/repos/citesCyverse/static/flask/fgraphs/'

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
            npDict = chooseTopNPs(xformed_tokens)

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
    return("you shouldn't be here!! Heather's custom 404 error. ")

#configuration settings
if __name__ == '__main__':
    run_simple('0.0.0.0', 9192, app, use_reloader=True) #to run with Apache on geco
    #app.run(host='0.0.0.0') #to run locally!
