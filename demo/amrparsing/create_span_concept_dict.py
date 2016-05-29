import sys
import cPickle as pickle
from collections import OrderedDict

argv = sys.argv[1:]
if len(argv) < 1:
	print "usage: create_span_concept_dict.py <span_concept_dataset.p> <output_filename>"
	sys.exit()

span_concept_dataset = pickle.load(open(argv[0], "rb"))
output_filename = argv[1]
output_file = open(output_filename, 'w')
span_concept_dict = {}

for id, span_concept_data in span_concept_dataset.iteritems():
	for [span, pos, concept, name, ner, nx_root, concept_idx] in span_concept_data:
		if span_concept_dict.has_key(span):
			if span_concept_dict[span].has_key(concept_idx):
				span_concept_dict[span][concept_idx] += 1
			else:
				span_concept_dict[span][concept_idx] = 1
		else:
			span_concept_dict[span] = {concept_idx:1}

#Sort the concepts for each span by their frequency
for span, concepts in span_concept_dict.iteritems():
	span_concept_dict[span] = OrderedDict(sorted(concepts.items(), key=lambda concepts: concepts[1], reverse=True))

for span, concepts in span_concept_dict.iteritems():
	line = span.replace(" ", "_") + " "
	for (concept_idx, count) in concepts.iteritems():
		line += str(concept_idx) + ":" + str(count) + " "
	output_file.write(line+"\n")
	
pickle.dump(span_concept_dict, open(output_filename + ".p", "wb"))
