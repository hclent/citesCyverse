import os.path, pickle, json, csv, re

path_to_lemmas = "/home/hclent/repos/citesCyverse/flask/lemmas"

def print_lemma_nes_samples(biodoc_data):
	lemma_samples = []
	#nes_samples = []

	print("len of biodoc_data: " +str(len(biodoc_data)) )
	for bd_dict in biodoc_data:
		pmcid = bd_dict["pmcid"]  # this is a string!
		lemmas = bd_dict["lemmas"]  # this is a list!
		tags = bd_dict["tags"]  # this is a list!

		lemmas.insert(0, pmcid)  
		lemmas.insert(2, tags)  # need the tags to be lemma_samples[2] for embedding vis

		lemma_samples.append(lemmas)

		# nes = bd_dict["nes"]  # list
		# nes.insert(0, pmcid)
		# nes_samples.append(nes)

		lemma_completeName = os.path.join(path_to_lemmas, ('lemma_samples_' + (str(pmcid)) + '.pickle'))
		with open(lemma_completeName, "wb") as lcn:
			pickle.dump(lemma_samples, lcn)
		print("lemma_samples dumped to pickle")

		# nes_completeName = os.path.join(path_to_lemmas, ('nes_' + (str(pmcid)) + '.pickle'))
		# with open(nes_completeName, "wb") as ncn:
		# 	pickle.dump(nes_samples, ncn)
		# print("nes_samples dumped to pickle")


def concat_lemma_nes_samples():
	lemma_files = [os.path.join(path_to_lemmas, f) for f in os.listdir(path_to_lemmas) if f.startswith('lemma_samples_')]
	print("number of lemma_files: " + str(len(lemma_files)))

	all_lemma_samples = []
	#all_nes_samples = []

	for lf in lemma_files:
		print(lf)
		with open(lf, 'rb') as f:
			lemma_list = pickle.load(f)
			for l in lemma_list:
				all_lemma_samples.append(l)
		#append the entire list [id, [words], [tags]]
		#all_lemma_samples.append(lemma_list)
		print("data appended to all_lemma_samples")

		# with open(nes_file, 'rb') as f2:
		# 	nes_list = pickle.load(f2)
		# for ns in nes_list:
		# 	all_nes_samples.append(ns)

	print("length of all_lemma_samples: " + str(len(all_lemma_samples)))
	set_of_lemmas = {json.dumps(d, sort_keys=True) for d in all_lemma_samples}
	lemma_samples = [json.loads(t) for t in set_of_lemmas]
	print("length of (unique) lemma_samples: " + str(len(lemma_samples)))

	# set_of_nes = {json.dumps(d, sort_keys=True) for d in all_nes_samples}
	# nes_samples = [json.loads(t) for t in set_of_nes]

	# Dump to pickle
	cyverse_lemmas = os.path.join(path_to_lemmas, "cyverse_lemmas_ALL.pickle")
	with open(cyverse_lemmas, "wb") as qlcn:
		pickle.dump(lemma_samples, qlcn)

	# with open(query_nes_completeName, "wb") as qncn:
	# 	pickle.dump(nes_samples, qncn)



concat_lemma_nes_samples()


def load_lemma_cache():
	l_name =  os.path.join(path_to_lemmas, "cyverse_lemmas_ALL.pickle")
	with open(l_name, "rb") as qlemma:
		lemma_samples = pickle.load(qlemma)
	return lemma_samples


# ls = load_lemma_cache()


#Going to make a lemma_samples for 2010-2014 and 2015-2017, and 2011-2017
def lemma_samples_by_year():
	# step 1: extract years and journals from the spreadsheet
	potential_years_list = []
	potential_filename_list = []

	with open('spreadsheet.tsv', 'r') as tsvin:
		tsv = csv.reader(tsvin, delimiter='\t')

		for row in tsv:
			try:
				year = (row[4])
				potential_years_list.append(year)
			except Exception as e1:
				# no year
				pass
			try:
				filename = (row[10])
				potential_filename_list.append(filename)
			except Exception as e2:
				# no filename
				pass

	# step 2: clean the data (empty lines or filenames without years)
	combo = list(zip(potential_years_list, potential_filename_list))
	keep_combo = []  # 753
	for c in combo:
		possible_year = c[0]
		possible_file = c[1]
		# MUST have a year AND a not-blank journal
		year = re.search('\d{4}', possible_year)
		if year and possible_file.endswith('.txt'):  # possible_journal must not be empty
			y = int(year.group(0))
			f = str(possible_file)
			tup = (y, f)
			keep_combo.append(tup)
	#print(keep_combo[:10])

	lemmas_2010 = []
	lemma_samples_2010_14 = []
	lemma_samples_2015_17 = []
	i = 0
	j = 0
	for k in keep_combo:
		year = k[0]
		file = k[1]
		json_file = re.sub('\.txt', '.pickle', file)
		json_file = 'lemma_samples_' + str(json_file)
		load_file = os.path.join(path_to_lemmas , json_file)

		if year == 2017:
			i += 1
			try:
				with open(load_file, 'rb') as f:
					lemma_list = pickle.load(f)
				print(str(year) + ": " + str(f))
				for l in lemma_list:
					lemmas_2010.append(l)
			except Exception as e:
				print(e)
		else:
			j += 1


		# if year in range(2010, 2014 + 1):
		# 	i += 1
		# 	try:
		# 		with open(load_file, 'rb') as f:
		# 			lemma_list = pickle.load(f)
		# 		i += 1
		# 		print(str(year) + ": " + str(f))
		# 		for l in lemma_list:
		# 			lemma_samples_2010_14.append(l)
		# 	except Exception as e:
		# 		print(e)
        #
		# if year in range(2015, 2017 + 1):
		# 	j += 1
			# try:
			# 	with open(load_file, 'rb') as f:
			# 		lemma_list = pickle.load(f)
			# 		print(str(year) + ": " + str(f))
			# 		for l in lemma_list:
			# 			lemma_samples_2015_17.append(l)
			# except Exception as e:
			# 	print(e)


	print("EARLIER: " + str(i))
	print("LATER: " + str(j))


	print("length of lemma_samples 2010: " + str(len(lemmas_2010)))
	set_of_lemmas_2010 = {json.dumps(d, sort_keys=True) for d in lemmas_2010}
	ls_2010 = [json.loads(t) for t in set_of_lemmas_2010]
	print("length of (unique) lemma_samples 2010: " + str(len(ls_2010)))
	#
	# Dump to pickle
	lemmas_2010_file = os.path.join(path_to_lemmas, "cyverse_lemmas_2017.pickle")
	with open(lemmas_2010_file, "wb") as fw:
		pickle.dump(ls_2010 , fw)
	print("2017 dumped to pickle!")


	# Print 2010-2014 lemma samples
	# print("length of lemma_samples 2010-2014: " + str(len(lemma_samples_2010_14)))
	# set_of_lemmas_2014 = {json.dumps(d, sort_keys=True) for d in lemma_samples_2010_14}
	# ls_2010_14 = [json.loads(t) for t in set_of_lemmas_2014]
	# print("length of (unique) lemma_samples 2010-2014: " + str(len(ls_2010_14)))
    # #
	# # Dump to pickle
	# lemmas_2010_14 = os.path.join(path_to_lemmas, "cyverse_lemmas_2010_2014.pickle")
	# with open(lemmas_2010_14, "wb") as fw:
	# 	pickle.dump(ls_2010_14, fw)
	# print("2010-2014 dumped to pickle!")

	#Print 2015-2017 lemma samples
	# print("length of lemma_samples 2015-2017: " + str(len(lemma_samples_2015_17)))
	# set_of_lemmas_2017 = {json.dumps(d, sort_keys=True) for d in lemma_samples_2015_17}
	# ls_2017 = [json.loads(t) for t in set_of_lemmas_2017]
	# print("length of (unique) lemma_samples 2015-2017: " + str(len(ls_2017)))
    # #
	# # # Dump to pickle
	# path_to_lemmas_2015_17 = os.path.join(path_to_lemmas, "cyverse_lemmas_2015_2017.pickle")
	# with open(path_to_lemmas_2015_17, "wb") as fw:
	# 	pickle.dump(ls_2017, fw)
	# print("2015-2017 dumped to pickle!")


#lemma_samples_by_year()


def extractStuff(filename):
	filepath = "/home/hclent/repos/citesCyverse/flask/lemmas/"
	openfile = filepath + filename
	with open(openfile, "rb") as f:
		lemma_samples = pickle.load(f)

	for i, l in enumerate(lemma_samples):
		print(str(i) + ": " + str(type(l)) + " " + str(l[:15]))
	#words = [' '.join(l[1]) for l in lemma_samples]


#extractStuff("cyverse_lemmas_2015_2017.pickle")