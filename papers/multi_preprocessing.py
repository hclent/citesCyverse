from __future__ import print_function
from processors import *
import re, nltk, json, pickle, time
import os.path
from multiprocessing import Pool
import logging

logging.basicConfig(filename='.app.log', level=logging.DEBUG)
eng_stopwords = nltk.corpus.stopwords.words('english')

path = "/home/hclent/anaconda3/envs/py35/lib/python3.5/site-packages/processors/processor-server.jar"
api = ProcessorsAPI(port=4848, jar_path=path, keep_alive=False, jvm_mem="-Xmx500G")
rando_doc = api.bionlp.annotate("The mitochondria is the powerhouse of the cell.")

folder = "/home/hclent/tmp/citesCyverse"
pmcids = [f.strip('.txt') for f in os.listdir(folder) if not f.startswith('.app') and f.endswith('.txt')]
print(pmcids)
print(len(pmcids))
#keep_pmcids = [p for p in pmcids if not os.path.isfile(str(p)+".json") ]

docs = []

for pmcid in pmcids:
    txt = pmcid + ".txt"
    filename = os.path.join(folder, txt)
    docdict = {"pmcid": pmcid, "filepath": filename}
    docs.append(docdict)

#print(docs)

def preProcessing(text):
    clean_text = re.sub('\\\\n', ' ', text) #replace \n with a space
    clean_text = re.sub('\([ATGC]*\)', '', clean_text) #delete any DNA seqs
    clean_text = re.sub('(\(|\)|\'|\]|\[|\\|\,)', '', clean_text) #delete certain punctuation
    clean_text = re.sub('\\\\xa0\d*\.?\d?[\,\-]?\d*\,?\d*', '', clean_text) #delete formatting around figures
    clean_text = re.sub('et\sal\.', ' ', clean_text) #replace "et al." with a space
    clean_text = re.sub('\s\d{4}[\s\.\,\;\-]?(\d{4})?', '', clean_text) #delete years
    clean_text = re.sub('[\.\,]\d{1,2}[\,\-]?(\d{1,2})?\,?', '', clean_text) #delete citations
    clean_text = re.sub('Fig\.|Figure', '', clean_text) #delete 'fig.' and 'figure'
    clean_text = clean_text.lower()
    logging.debug('cleaned the text')
    return clean_text


def loadDocuments(doc):
    #a doc is a dict {"pmcid": 1234, "filename": /path/to/file/name}
    pmcid = doc["pmcid"]
    filepath = doc["filepath"]

    #logging.debug("NEW TASK")
    #api = connect_to_Processors(4343) #could connect each time if don't want a global var
    logging.debug('found the the file '+str(filepath))
    #read the text
    text = open(filepath, 'r')
    text = text.read()
    logging.debug('read text with text.read()')
    clean_text = preProcessing(text)
    logging.debug("* beginning annotation of "  + str(pmcid) )
    biodoc = api.bionlp.annotate(clean_text) #annotates to JSON  #thread safe?
    logging.debug('the biodoc of ' + str(pmcid) + ' is type ' + str(type(biodoc)))

  ### let's try some trouble shooting for documents that failed
    if "processors.ds.Document" not in str(type(biodoc)):
        logging.debug("annotating this document failed! :( Let's try again HALF SIZE .... ")
        logging.debug(clean_text)
        doc_length = len(clean_text)
        half_length = int(doc_length * 0.5)
        half_clean_text = clean_text[0:half_length]
        biodoc = api.bionlp.annotate(half_clean_text)
        logging.debug('SECOND TRY: the biodoc of ' + str(pmcid) + ' is type ' + str(type(biodoc)))
        #if it fails AGAIN
        if "processors.ds.Document" not in str(type(biodoc)):
          #cut into a quarter size
          doc_length = len(clean_text)
          qt_length = int(doc_length * 0.25)
          qt_clean_text = clean_text[0:qt_length]
          biodoc =  api.bionlp.annotate(qt_clean_text)
          logging.debug('THIRD TRY (QUARTER SIZE): the biodoc of ' + str(pmcid) + ' is type ' + str(type(biodoc)))
          #if that still fails, return a blank json dict
          if "processors.ds.Document" not in str(type(biodoc)):
            fake_clean_text = 'error annotating document'
            biodoc = api.bionlp.annotate(fake_clean_text)

    logging.debug("END OF TASK")
    return biodoc, pmcid


def multiprocess(docs):
    if len(docs) == 0: #if there are no docs, abort
        logging.info("no documents to annotate")
        pass
    else:
        t1 = time.time()
        pool = Pool(75)
        logging.debug('created worker pools')
        results = pool.map_async(loadDocuments, docs) #docs = ['17347674_1.txt', '17347674_2.txt', '17347674_3.txt', ...]
        logging.debug('initialized map_async to loadDocs function with docs')
        logging.debug('did map to loadDocs function with docs. WITH async')
        pool.close()
        logging.debug('closed pool')
        pool.join()
        logging.debug('joined pool')
        logging.info(results.get())

        for biodoc, pmcid in results.get():
            prefix = pmcid[0:3]
            suffix = pmcid[3:6]
            save_path = str(pmcid)+'.json' #look in folder that matches pmcid
            completeName = os.path.join(folder, save_path)

            with open(completeName, 'w') as out:
                out.write(biodoc.to_JSON())
                logging.debug('printed to json')

    logging.info("All biodoc creations: done in %0.3fs." % (time.time() - t1))
    logging.info('Finished')


#docs10 = docs[25:30] #FAILED
#docs10 = docs[:10]
#print(docs10)
#docs10 = [{"pmcid": "10.1007.978-1-4939-2175-1_12", "filepath": "/home/hclent/tmp/citesCyverse/10.1007.978-1-4939-2175-1_12.txt" }]
multiprocess(docs)
