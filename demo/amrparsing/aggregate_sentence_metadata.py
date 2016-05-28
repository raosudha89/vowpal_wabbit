import sys, os
import cPickle as pickle
import re

argv = sys.argv[1:]
if len(argv) < 4:
	print "usage: aggregate_sentence_metadata.py <amr_file> <sentence_file> <pos_file> <ner_file> <dep_parse_file> <output_file_name>"
	sys.exit()
amr_file = open(argv[0])
sentence_file = open(argv[1])
pos_file = open(argv[2])
ner_file = open(argv[3])
dep_parse_file = open(argv[4])
output_file_name = argv[5]
k = 1

amr_aggregated_metadata = {}
dep_parse = {}

def read_dep_parse_to_list(id):
	line = dep_parse_file.readline()
	parse_list = {}
	while line:
		line = line.strip("\n")
		if line == "":
			#line = dep_parse_file.readline()
			return parse_list
		else:
			#dobj(Establishing-1, Models-2)
			[rel, line] = line.split("(", 1)
			line = line[:-1] #remove ) at the end
			[src, tgt] = line.split(", ", 1)
			src_word, src_index = src.rsplit("-", 1)
			tgt_word, tgt_index = tgt.rsplit("-", 1) 
			rel = rel.strip()
			src_index = int(src_index.replace("'", ""))
			tgt_index = int(tgt_index.replace("'", ""))
			if parse_list.has_key(src_index):
				if not (tgt_index, rel) in parse_list[src_index]:
					parse_list[src_index].append((tgt_index, rel))
			else:
				parse_list[src_index] = [(tgt_index, rel)]
		line = dep_parse_file.readline()  

for amr_line in amr_file.readlines():
	if amr_line.startswith("# ::id"):
		id = amr_line.split("::")[1].strip("# ::id").strip()
		sentence = sentence_file.readline()
		sentence = sentence.lower()
		pos = pos_file.readline()
		ner = ner_file.readline()
		parse_list = read_dep_parse_to_list(id)
		amr_aggregated_metadata[id] = [sentence.rstrip("\n"), pos.rstrip("\n"), ner.rstrip("\n")]
		dep_parse[id] = parse_list

pickle.dump(amr_aggregated_metadata, open(output_file_name+".amr_aggregated_metadata.p", "wb"))
pickle.dump(dep_parse, open(output_file_name+".dep_parse.p", "wb"))
	
