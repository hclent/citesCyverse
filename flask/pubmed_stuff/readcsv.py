import csv
from Entrez_IR import * 



def extractPmcids(filename):
	pmcid_list = []
	dois_list = []
	with open(filename) as f:
		lines = f.readlines()
		lis = [l.split(',') for l in lines]
		for l in lis:
			messy_pmcid = l[1]
			pmcid = messy_pmcid.strip("\"") #get rid of ugly double quotes
			doi = l[2]
			if pmcid.startswith("PMC"):
				keep_id = pmcid.strip("PMC")
				pmcid_list.append(keep_id)
			else:
				pmcid_list.append("x")
			
			dois_list.append(doi.strip("\"")) #get rid of ugly double quotes
	return pmcid_list, dois_list


p0, d0 = extractPmcids("1-x.csv")
p05, d05 = extractPmcids("1x-100.csv")
p1, d1 = extractPmcids("101-199.csv")
p2, d2 = extractPmcids("200-299.csv")
p3, d3 = extractPmcids("300-350.csv")
p35, d35 = extractPmcids("351-400.csv")
p4, d4 = extractPmcids("401-450.csv")
p45, d45 = extractPmcids("451-500.csv")
p5, d5 = extractPmcids("501-533.csv")

pmcid_list = p0 + p05 + p1 + p2 + p3 + p35 + p4 + p45 + p5
dois_list = d0 + d05 + d1 + d2 + d3 + d35 + d4 + d45 + d5



do_pmcids = [p for p in pmcid_list if p is not "x"]
pmcids = [p for p in do_pmcids if p != 'ID']


getContentPMC(pmcids, "/Users/heather/Desktop/citesCyverse/pmcids")
