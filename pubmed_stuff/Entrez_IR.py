from __future__ import print_function
import time, sys, os.path, logging
import xml.etree.ElementTree as ET
from Bio import Entrez


#Entrez Information Retrieval
#This code uses BioPython to access NCBI's API (Entrez)
#From the NCBI API, this code references PubMed and PubMedCentral
#With an input PubMed ID's (pmids), the code will retrieve information about the original pmid,
#and information about pubplications that cite this pmid via PubMedCentral ID's (pmcids)


Entrez.email = "hclent1@gmail.com" 
Entrez.tool = "MyInfoRetrieval"


logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Started')

#Input: XML string of PMC entry generated with getContentPMC
#Output: Abstract and journal text
def parsePMC(xml_string):
	main_text = []
	root = ET.fromstring(xml_string) #parsed
	abstract_check = [] #did it get the abstract? yes/no?
	whole_article_check = [] #did it get the whole text? yes/no?

	#Get abstract and add to doc
	try:
		#check for new line!
		abstract = root.find('.//abstract')
		full_abs = ("".join(abstract.itertext()))
		logging.info("* Got abstract")
		main_text.append(full_abs)
		if full_abs: #if the abstract exists
			abstract_check.append('yes')
	except Exception as e:
		logging.info("The following PMCID has no abstract")
		string = "Some data"
		main_text.append(string)
		abstract_check.append('no')
	try:
		#Get main text and add to doc
		text = root.findall('.//p')
		#problem: will return an empty list if there is no text :(
		#error handling here:
		if not text:
			logging.info("main text is empty!!!!!!!!!")
			whole_article_check.append('no')
		#if the text really does exist:
		if text:
			whole_article_check.append('yes')
			for t in text:
				full_text = ("".join(t.itertext()))
				main_text.append(full_text)
			logging.info("* Got main text")
	except Exception as e:
		logging.info("The following PMCID has no main text")
		string = "data"
		main_text.append(string)
		whole_article_check.append('no')
	logging.info("ABSTRACT CHECK")
	logging.info(abstract_check)
	logging.info("WHOLE_ARTICLE CHECK")
	logging.info(whole_article_check)
	return main_text, abstract_check, whole_article_check



#Input: the list of pmcids citing some pmid
#For each citing pmc_id, this function gest the xml, which is then parsed by parsePMC()
#Output: Those texts for each pmcid saved as pmcid.txt to the folder pmcid[:3]/pmicd[3:6] for better organization
def getContentPMC(pmcids_list, save_spot):
	t0 = time.time()
	i = 1

	for citation in pmcids_list:

		logging.info(str(i)+" paper")
		logging.info("CITATION: " +str(citation))
		handle = Entrez.efetch(db="pmc", id=citation, rettype='full', retmode="xml")
		xml_record = handle.read() #xml str
		#print(xml_record)
		logging.info("* got xml record")
		main_text, abstract_check, whole_article_check = parsePMC(xml_record)
		
		#print
		logging.info("* ready to print it")
		completeName = os.path.join("/Users/heather/Desktop/citesCyverse/papers", (str(citation)+'.txt'))  #pmcid.txt #save to suffix path
		#print(completeName)
		sys.stdout = open(completeName, "w")
		print(main_text)
		i += 1
		time.sleep(3)

	logging.info("got documents: done in %0.3fs." % (time.time() - t0))
	return contentDictList




