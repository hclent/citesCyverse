#clean dois

filename = "/Users/heather/Desktop/dois.txt"

with open(filename, "r") as f:
	dois_list = f.readlines()


true_dois = []

for possible_doi in dois_list:
	if possible_doi.startswith("doi"):
		cleaned = possible_doi.strip("doi: ").rstrip()
		true_dois.append(cleaned)

print(len(true_dois))

# i=0
# for doi in true_dois:
# 	while i >= 1 and i<100:
# 		print(true_dois[i])
# 		i+=1
# 	else:
# 		i+=1



i=0
for doi in true_dois:
	while i >= 100 and i<200:
		print(true_dois[i])
		i+=1
	else:
		i+=1


# i=0
# for doi in true_dois:
# 	while i >= 300 and i<400:
# 		print(true_dois[i])
# 		i+=1
# 	else:
# 		i+=1

# i=0
# for doi in true_dois:
# 	while i >= 400 and i<600:
# 		print(true_dois[i])
# 		i+=1
# 	else:
# 		i+=1