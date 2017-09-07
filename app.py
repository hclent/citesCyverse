from flask import Flask, render_template, request, flash, url_for, redirect, session, g, Blueprint
from flask_wtf import Form
from wtforms import TextField, SelectField
import pickle, os.path, json
#from werkzeug.serving import run_simple
from processors import *

#TODO: fix hard-coded paths

app=Flask(__name__, static_url_path='/Users/heather/Desktop/citesCyverse/static',  template_folder='templates')

#Form for Topic Modeling
class visOptions(Form):
    k_val = SelectField('k_val', choices=[(2,'k=2'),(3,'k=3'),(4,'k=4'),(5,'k=5'),(6, 'k=6'),
										  (7, 'k=7'),(8, 'k=8'),(9, 'k=9'),(10,'k=10'),
										  (11, 'k=11'),(12, 'k=12'),(13, 'k=13')])
    w_words = SelectField('w_words', choices=[(4, 'w=4'),(5, 'w=5'),(6, 'w=6'), (7, 'w=7'),
											  (100, 'w=1-100'),(200, 'w=101-200'),(300, 'w=201-300'),(400, 'w=301-400')])
    y_years = SelectField('y_years', choices=[(201115, '2011-2015'), (201617, '2016-2017')])

#Form for Wordclouds
class nesOptions(Form):
    y_years = SelectField('y_years', choices=[(2011, '2011'), (2012, '2012'), (2013, '2013'), (2014, '2014'), (2015, '2015'),
                                   (2016, '2016'), (2017, '2017')])


@app.route("/home/")
def homeCyverse():
    return render_template("dashboard.html")


@app.route("/blah/")
def blah():
    return render_template("dashboard.html")


@app.route("/cy-journals/")
def cyJournals():
    filename = "/path/to/journals/vis"
    # with open(filename) as f:
    #     journals = json.load(f)
    s_year = "2010" #start
    e_year = "2018" #end
    unique_pubs = "760"
    unique_journals = "200" #needs to be updated
    journals = {}
    return render_template("journals.html", journals=journals, unique_pubs=unique_pubs,
                           unique_journals=unique_journals, s_year=s_year, e_year=e_year)

@app.route("/cy-wordcloud/")
def cyWordcloud():
    return render_template("wordcloud.html")

@app.route("/cy-embeddings/", methods=["GET","POST"])
def cyEmbeddings():
    query = "cyverse"
    filename = "path/to/default/file"
    filepath = os.join('fgraphs', filename)
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
    #run_simple('0.0.0.0', 5000, app, use_reloader=True) #to run with Apache
    app.run(host='0.0.0.0') #to run locally!
