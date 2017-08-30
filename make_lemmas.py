import os.path, pickle, json


path_to_lemmas = "/Users/heather/Desktop/citesCyverse/lemmas"


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



#print_lemma_nes_samples(biodoc_data)

def concat_lemma_nes_samples():
	lemma_files = [os.path.join(path_to_lemmas, f) for f in os.listdir(path_to_lemmas) if f.startswith('lemma_samples_')]
	print("number of lemma_files: " + str(len(lemma_files)))

	all_lemma_samples = []
	#all_nes_samples = []

	for lf in lemma_files:
		with open(lf, 'rb') as f:
			lemma_list = pickle.load(f)
		for ls in lemma_list:
			all_lemma_samples.append(ls)

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
	cyverse_lemmas = os.path.join(path_to_lemmas, "cyverse_lemmas.pickle")
	with open(cyverse_lemmas, "wb") as qlcn:
		pickle.dump(lemma_samples, qlcn)

	# with open(query_nes_completeName, "wb") as qncn:
	# 	pickle.dump(nes_samples, qncn)



#concat_lemma_nes_samples()


def load_lemma_cache():
	l_name =  os.path.join(path_to_lemmas, "cyverse_lemmas.pickle")
	with open(l_name, "rb") as qlemma:
		lemma_samples = pickle.load(qlemma)
	return lemma_samples


# ls = load_lemma_cache()
# print(type(ls))
# print(len(ls))



# def load_nes_cache(query):
# 	n_name = os.path.join(path_to_lemmas, "cyverse_nes.pickle")


# 		with open(n_name, "rb") as qnes:
# 			nes_samples = pickle.load(qnes)
# 	return nes_samples