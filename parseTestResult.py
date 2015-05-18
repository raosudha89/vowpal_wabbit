from sys import argv
dict = {}
for data in open(argv[3]).readlines():
	dict[data.strip().split()[1]] = data.strip().split()[0]
annotation  = open(argv[2]).readlines()
for idx, line in enumerate(open(argv[1]).readlines()):
	item = line.split()
	# conll07
	if len(item) ==10:
		item[-4] = annotation[idx].strip().split(":")[0]
		item[-3] = dict[annotation[idx].strip().split(":")[1]]
	# wsj corpus
	elif len(item) >0:
		item[-2] = annotation[idx].strip().split(":")[0]
		item[-1] = dict[annotation[idx].strip().split(":")[1]]
	print "\t".join(item)

