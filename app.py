from flask import Flask, render_template, request, flash, url_for, redirect, session, g, Blueprint
# from flask_wtf import Form
# from wtforms import TExtField, SelectField
import gc, time, datetime, pickle, os.path, json, sys, csv
#from werkzeug.serving import run simple
from processors import *

#TODO: fix hard-coded paths

app=Flask(__name__, static_url_path='/Users/heather/Desktop/citesCyverse/static')

@app.route("/home/")
def citesCyverse():
    return("home page!")


@app.route("/cy-embeddings/", methods=["GET","POST"])
def cyEmbeddings():
    return("embeddings!")

@app.route("/cy-journals/")
def cyJournals():
    return("journals!!")

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
