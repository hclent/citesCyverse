import re, operator, json, csv
from collections import defaultdict


# step 1: extract years and journals from the spreadsheet
potential_years_list = []
potential_journals_list = []

#TODO: check for bio status
with open('journalsNoDuplicates.tsv', 'r') as tsvin:
	tsv = csv.reader(tsvin, delimiter='\t')

	for row in tsv:
		try:
			year = (row[4])
			potential_years_list.append(year)
		except Exception as e1:
			#no year
			pass
		try:
			journal = (row[2])
			potential_journals_list.append(journal)
		except Exception as e2:
			# no journal
			pass



#step 2: clean the data
def clean_combo(combo):
	keep_combo = [] #753 
	for c in combo:
		possible_year = c[0]
		possible_journal = c[1]
		# MUST have a year AND a not-blank journal
		year = re.search('\d{4}', possible_year)
		if year and possible_journal != '': #possible_journal must not be empty
			y = int(year.group(0))
			j = str(possible_journal)
			tup = (y, j)
			keep_combo.append(tup)


	years_list = [int(k[0]) for k in keep_combo]
	journals_list = [k[1] for k in keep_combo]

	return years_list, journals_list


def journal_dates_barchart(journals, years_list):
	x_vals = []
	y_vals = []

	yearDict = defaultdict(lambda: 0)

	years_range = (2010, 2018)

	# Associate journals with years
	journal_year = list(zip(journals, years_list))  # ('Scientific Reports', '2016')

	for year in range(int(years_range[0]), int(years_range[1]) + 1):
		for pair in journal_year:
			if year == int(pair[1]):
				yearDict[year] += 1

	for year in sorted(yearDict):
		x_vals.append(year)
		y_vals.append(yearDict[year])

	return x_vals, y_vals



#Makes the json for the Journals visualization :)
def journals_vis(years_range, years_list, journals):
	num_publications = len(journals) #UNIQUE publications only since duplicates have been flitered out
	print("THERE ARE " + str(num_publications)+ " PUBLICATIONS")

	#Associate journals with years
	journal_year = list(zip(journals, years_list)) #('Scientific Reports', '2016')


	#Dictionary with "Journal": [year, year]
	#For looking up the years
	jyDict = defaultdict(list)
	i = 0
	for j in journals:
		if j == (journal_year[i][0]):
			jyDict[j] += [journal_year[i][1]]
			i+=1
	#len(jyDict) is the amount of UNIQUE journals
	number_unique_journals = len(jyDict)
	print("IN "+str(number_unique_journals)+" UNIQUE JOURNALS")

	#Dictionary with "Journal": Number-of-publications
	#For looking up the total
	journalsTotalDict = defaultdict(lambda: 0)
	sum_j = 0
	for j in journals:
		journalsTotalDict[j] += 1
		sum_j +=1
	#print(journalsTotalDict)

	#This sourts by A --> Z journal names
	unique_journals = list(sorted(journalsTotalDict.keys(), key=str.lower))

	# Sorted by counts MOST --> LEAST
	#sorted_dict = sorted(journalsTotalDict.items(), key=operator.itemgetter(1), reverse=True)
	#unique_journals = [journal[0] for journal in sorted_dict]


	publication_data = []
	for j in unique_journals:
		#print(j)
		#Initiate the dictionary for this journal
		journal_data = {
			"name": str("(" + str(journalsTotalDict[j])+") " + j), #e.g. (7) Nature
			"articles": [], #[[year, number], [year, number]]
			"total": journalsTotalDict[j]   #total can get from journalsTotalDict with key (total is value)
		}
		#print("Years a paper was in this journal: "+ str(jyDict[j]))
		for year in range(int(years_range[0]), int(years_range[1]) + 1):
			#print("checking " +str(year) +" ...")
			sum_y = 0
			for entry in jyDict[j]:
				#print(" ... against "+str(entry))
				if year == int(entry):
					#print("The years match so I'm going to count now")
					sum_y+=1
				year_sum = [year, sum_y]
				#print(year_sum)
			journal_data["articles"].append(year_sum)

		publication_data.append(journal_data)

	range_info = [years_range, num_publications, number_unique_journals]
	#print(range_info)

	## add a TOTAL SUM row to the top of the journals visualization
	x, y = journal_dates_barchart(journals, years_list)
	total_sum = sum(y)
	total_articles = [[year, count] for year, count in zip(x, y)]
	total_name = "TOTAL"
	top_row = {
		"name": total_name,
		"articles": total_articles,
		"total": total_sum
	}

	publication_data = [top_row] + publication_data

	print("RANGE INFO: " + str(range_info))
	#Example range info: [('2008', '2016'), 165, 48] means years 2008-2016, 165 publications, 48 unique journals

	publication_data = json.dumps(publication_data)
	with open('/home/hclent/repos/citesCyverse/flask/static/journalsvis_alpha.json' ,'w') as outfile:
		json.dump(publication_data, outfile)

	return publication_data, range_info



# print(len(potential_years_list)) #787
# print(len(potential_journals_list)) #787
# combo = list(zip(potential_years_list, potential_journals_list)) #should be 1-1
# years_list, journals = clean_combo(combo)
# years_range = (2010, 2017) #CyVerse is 2010-2017; added extra yera to both side for padding.
# journals_vis(years_range, years_list, journals)