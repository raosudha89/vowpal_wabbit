import sys
import cPickle as pickle
import networkx as nx
import string
from collections import OrderedDict
import re
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pdb

def traverse_depth_first(concept_nx_graph, parent=None):
	node_list = [] #list of pairs (concept_instance, concept_var_name) e.g. ('establish-01', 'e')
	if parent == None:
		parent = nx.topological_sort(concept_nx_graph)[0]
	node_list.append((concept_nx_graph.node[parent]['instance'], parent))
	children = []
	for child in concept_nx_graph.successors(parent):
		if concept_nx_graph.node[child]['parent'] == parent:
			children.append(child)
	if not children:
		return node_list
	ordered_children = [None]*len(children)
	order = []
	for child in children:
		order.append(concept_nx_graph.node[child]['child_num'])
	diff = max(order) + 1 - len(order)
	for child in children:
		ordered_children[concept_nx_graph.node[child]['child_num'] - diff] = child
	for child in ordered_children:
		node_list.extend(traverse_depth_first(concept_nx_graph, parent=child)) 
	return node_list		

vnpb_words_concepts_dict=None

def create_concept_for_unknown_span(span, pos, ner):
	if vnpb_words_concepts_dict.has_key(span):
		#return [concept for concept in vnpb_words_concepts_dict[span]]
		return vnpb_words_concepts_dict[span][0] #Return just the first one for now
	concept = ""	
	if "<" and ">" in ner:
		r = re.search("(.*?)<(.*?)>(.*?)", ner)	
		ner = r.group(2).lower()
		if ner == "date":
			ner = "date-entity"
			date_words = span.strip().replace(",","")
			date_words = "/".join(date_words.split())
			try:
				d = datetime.datetime.strptime(date_words, "%B/%d/%Y")
				concept = ner + "_" + str(d.year) + "_" + str(d.month).lstrip('0') + "_" + str(d.day).lstrip('0')
			except:
				try:
					d = datetime.datetime.strptime(date_words, "%d/%B/%Y")	
					concept = ner + "_" + str(d.year) + "_" + str(d.month).lstrip('0') + "_" + str(d.day).lstrip('0')
				except:
					try:
						d = datetime.datetime.strptime(date_words, "%B/%Y")	
						concept = ner + "_" + str(d.year) + "_" + str(d.month).lstrip('0') + "_X"
					except:
						if re.search("([0-9]{4})",span.split()[0]):
							yyyy = span.split()[0]
							concept = ner + "_" + yyyy + "_X_X"
						else:
							concept = ner + "_"
							concept += "_".join("\"" + w + "\"" for w in span.split())  
		else:
			if ner == "location": ner = "country"
			concept = ner + "_name_"
			concept += "_".join("\"" + w + "\"" for w in span.split())
		return concept

	is_date = re.search("([0-9]*)-([0-9]*)-([0-9]*)", span.split()[0])
	if is_date:
		yyyy = is_date.group(1)
		mm = is_date.group(2)
		dd = is_date.group(3)
		concept = "date-entity_" + yyyy + "_" + mm + "_" + dd
		return concept
	
	is_date = re.search("([0-9]{6})", span.split()[0])
	if is_date:
		date = span.split()[0]
		yyyy = "20" + date[:2]
		mm = date[2:4]
		dd = date[4:]
		concept = "date-entity_" + yyyy + "_" + mm + "_" + dd
		return concept
	
	stemmer=PorterStemmer()
	span_stem = stemmer.stem(span)
	wordnet_lemmatizer = WordNetLemmatizer()
	span_lemma =  wordnet_lemmatizer.lemmatize(span.lower())
	if pos[0] == "V":
		return str(span_lemma)+"-01"
	
	return str(span_lemma)

def create_span_concept_data(sentence, span_concept, pos_line, ner_line, all_concepts):
	span_concept_data = []
	words = sentence.split()
	words_pos = pos_line.split()
	i = 0
	vw_idx = 1
	concept_vw_idx_dict = {}
	while i < len(words):
		span_start = str(i)
		if span_concept.has_key(span_start):
			span_end, span, concept_nx_graph = span_concept[span_start]
			span_from_pos = [word_pos.split("_")[0] for word_pos in words_pos[int(span_start):int(span_end)]]
			assert(span == span_from_pos)
			pos = [word_pos.split("_")[1] for word_pos in words_pos[int(span_start):int(span_end)]]
			node_list = traverse_depth_first(concept_nx_graph)
			concepts = []
			concept_short_names = []
			for (concept_instance, concept_var_name) in node_list:
				concepts.append(concept_instance)
				concept_short_names.append(concept_var_name)
			concept = "_".join(concepts)
			if concept not in all_concepts: #unknown concept, create concept using rules
				#concept_idx = all_concepts.index("UNK")
				concept = create_concept_for_unknown_span(" ".join(span).lower(), " ".join(pos), " ".join(ner_line.split()[int(span_start):int(span_end)]))
				concept = concept.replace("/", "").replace("(", "").replace(")", "").strip()
				all_concepts.append(concept)
			concept_idx = all_concepts.index(concept) 
			concept_short_name = "_".join(concept_short_names)
			concept_nx_graph_root = nx.topological_sort(concept_nx_graph)[0]
			span_concept_data.append([" ".join(span).lower(), " ".join(pos), concept, concept_short_name, " ".join(ner_line.split()[int(span_start):int(span_end)]), concept_nx_graph_root, concept_idx])
			#concept_vw_idx_dict[concept_nx_graph_root] = vw_idx
			for n in concept_nx_graph.nodes():
				concept_vw_idx_dict[n] = vw_idx #assign all nodes in the fragment the same vw_idx so that all outgoing nodes from this fragment are assigned the same vw_idx parent
			i = int(span_end) 
		else:
			[word_from_pos, pos] = words_pos[i].rsplit("_", 1)
			assert(words[i] == word_from_pos)
			concept = "NULL"
			concept_idx = all_concepts.index(concept) 
			span_concept_data.append([words[i].lower(), pos, concept, "NULL", ner_line.split()[i], None, concept_idx])
			i += 1
		vw_idx += 1
	return span_concept_data, concept_vw_idx_dict, all_concepts

visited_nodes = []

def get_node_paths(parent_path, parent, amr_nx_graph):
	#print parent_path
	if parent in visited_nodes:
		return {}
	visited_nodes.append(parent)
	if not amr_nx_graph.successors(parent):
		return {}
	node_paths = {}
	for child in amr_nx_graph.successors(parent):
		child_path = parent_path + '.' + str(amr_nx_graph.node[child]['child_num'])
		node_paths[child_path] = child
		#print node_list
		node_paths.update(get_node_paths(child_path, child, amr_nx_graph))
	return node_paths


forced_alignments = {} # Dictionary: key=instance of node; value=dict with counts of spans aligned to this node in data
my_stopwords = list(string.punctuation) + ['the', 'a', 'to', 'of', 'are', 'is', 'was']

def get_missing_alignment_data(root, amr_nx_graph, alignments, sentence):
	sent_len = len(sentence.split())
	spans = []
	for i in range(1, sent_len):
		spans.append(str(i-1) + "-" + str(i))
	node_paths = {"0": root}
	node_paths.update(get_node_paths("0", root, amr_nx_graph))
	aligned_node_paths = []
	aligned_spans = []
	for alignment in alignments.split():
		span, graph_fragments = alignment.split("|")
		aligned_spans.append(span)
		aligned_node_paths += graph_fragments.split("+")
	#print aligned_spans
	#print spans
	for node_path in node_paths.keys():
		if node_path not in aligned_node_paths:
			node_instance = amr_nx_graph.node[node_paths[node_path]]['instance']
			if node_instance == "multi-sentence":
				continue #since we handle these nodes differently
			if not forced_alignments.has_key(node_instance):
				forced_alignments[node_instance] = {}
			for span in spans:
				if span not in aligned_spans:
					span_start, span_end = span.split('-')
					span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
					if span_words in my_stopwords:
						continue
					if not forced_alignments[node_instance].has_key(span_words):
						forced_alignments[node_instance][span_words] = 0
					forced_alignments[node_instance][span_words] += 1


def add_missing_alignments(root, amr_nx_graph, alignments, sentence):
	sent_len = len(sentence.split())
	spans = []
	for i in range(1, sent_len):
		spans.append(str(i-1) + "-" + str(i))
	node_paths = {"0": root}
	node_paths.update(get_node_paths("0", root, amr_nx_graph))
	aligned_node_paths = []
	aligned_spans = []
	for alignment in alignments.split():
		span, graph_fragments = alignment.split("|")
		aligned_spans.append(span)
		aligned_node_paths += graph_fragments.split("+")
	new_alignments = []
	for node_path in node_paths.keys():
		if node_path not in aligned_node_paths:
			node_instance = amr_nx_graph.node[node_paths[node_path]]['instance']
			if node_instance == "multi-sentence":
				continue #since we handle these nodes differently
			max_count = 0
			most_aligned_span = ""
			most_aligned_span_words = ""
			unaligned_spans = []
			for span in spans:
				if span not in aligned_spans:
					unaligned_spans.append(span)
					span_start, span_end = span.split('-')
					span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
					if span_words in my_stopwords:
						continue
					count = forced_alignments[node_instance][span_words]
					if count > max_count:
						max_count = count
						most_aligned_span = span
						most_aligned_span_words = span_words
			if not unaligned_spans:
				continue
			if max_count == 0:
				span = unaligned_spans[0]
				most_aligned_span = span
				span_start, span_end = span.split('-')
				most_aligned_span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
			new_alignments.append(most_aligned_span + "|" + node_path)
			#print "NEW ALIGNMENT: ", node_instance, most_aligned_span_words
	return alignments + " " +  " ".join(new_alignments)

def get_span_concept(alignment, root, amr_nx_graph, sentence):
	span_num, graph_fragments = alignment.split("|")
	span_start, span_end = span_num.split("-")
	span = sentence.split()[int(span_start):int(span_end)]
	#Create a concept networkx graph and add all nodes in graph_fragments
	concept_nx_graph = nx.DiGraph()
	for graph_fragment in graph_fragments.split("+"):
		parent, attr_dict = root, amr_nx_graph.node[root]
		for child_num in graph_fragment.split(".")[1:]:
			children = amr_nx_graph.successors(parent)
			for child in children:
				if amr_nx_graph.node[child]['parent'] == parent and amr_nx_graph.node[child]['child_num'] == int(child_num):
					parent, attr_dict = child, amr_nx_graph.node[child]
		concept_nx_graph.add_node(parent, attr_dict)
	#Get all edges between the nodes in graph_fragment and add those to concept_nx_graph
	nodes = concept_nx_graph.nodes()
	for i in range(len(nodes)):
		for j in range(i + 1, len(nodes)):
			if amr_nx_graph.has_edge(nodes[i], nodes[j]):
				concept_nx_graph.add_edge(nodes[i], nodes[j], amr_nx_graph.get_edge_data(nodes[i], nodes[j]))
			if amr_nx_graph.has_edge(nodes[j], nodes[i]):
				concept_nx_graph.add_edge(nodes[j], nodes[i], amr_nx_graph.get_edge_data(nodes[j], nodes[i]))
	return (span_start, [span_end, span, concept_nx_graph])	

def write_updated_span_concept_dict(span_concept_dict, train_span_concept_dict_filename):
	merged_span_concept_dict = {}
	for span, concepts in span_concept_dict.iteritems():
		span_tag = span.replace(" ", "_").replace("\'", "")
		merged_span_concept_dict[span_tag] = concepts	

	train_span_concept_dict_file = open(train_span_concept_dict_filename, 'r')

	for line in train_span_concept_dict_file.readlines():
		parts = line.split()
		span_tag = parts[0]
		for part in parts[1:]:
			concept_idx, count = part.split(':')
			concept_idx = int(concept_idx)
			count = int(count)
			if span_tag not in merged_span_concept_dict.keys():
				merged_span_concept_dict[span_tag] = {}
			if concept_idx not in merged_span_concept_dict[span_tag].keys():
				merged_span_concept_dict[span_tag][concept_idx] = 0
			merged_span_concept_dict[span_tag][concept_idx] += count

	#Sort the concepts for each span by their frequency
	for span_tag, concepts in merged_span_concept_dict.iteritems():
		span_concept_dict[span_tag] = OrderedDict(sorted(concepts.items(), key=lambda concepts: concepts[1], reverse=True))

	output_dict_file = open(train_span_concept_dict_filename, 'w')

	for span_tag, concepts in merged_span_concept_dict.iteritems():
		line = span_tag + " "
		for (concept_idx, count) in concepts.iteritems():
			line += str(concept_idx) + ":" + str(count) + " "
		output_dict_file.write(line+"\n")
	
def create_dataset(amr_nx_graphs, amr_aggregated_metadata, all_concepts):
	for value in amr_nx_graphs:
		[root, amr_nx_graph, sentence, alignments, id] = value
		get_missing_alignment_data(root, amr_nx_graph, alignments, sentence)

	span_concept_dataset = {}
	span_concept_dict = {}
	concept_vw_idx_dict_dataset = {}
	for value in amr_nx_graphs:
		span_concept = {}
		[root, amr_nx_graph, sentence, alignments, id] = value
		alignments = add_missing_alignments(root, amr_nx_graph, alignments, sentence)
		for alignment in alignments.split():
			span, concept = get_span_concept(alignment, root, amr_nx_graph, sentence)
			span_concept[span] = concept
		span_concept_data, concept_vw_idx_dict, all_concepts = create_span_concept_data(sentence, span_concept, amr_aggregated_metadata[id][1], amr_aggregated_metadata[id][2], all_concepts)
		span_concept_dataset[id] = span_concept_data
		concept_vw_idx_dict_dataset[id] = concept_vw_idx_dict
		for [span, pos, concept, name, ner, nx_root, concept_idx] in span_concept_data:
			span = span.replace(" ", "_")
			if span_concept_dict.has_key(span):
				if span_concept_dict[span].has_key(concept_idx):
					span_concept_dict[span][concept_idx] += 1
				else:
					span_concept_dict[span][concept_idx] = 1
			else:
				span_concept_dict[span] = {concept_idx:1}
	return span_concept_dataset, span_concept_dict, concept_vw_idx_dict_dataset, all_concepts

def print_vw_format(amr_nx_graphs, span_concept_dataset, concept_vw_idx_dict_dataset, all_relations, output_vw_file):
	for value in amr_nx_graphs:
		[root, amr_nx_graph, sentence, alignments, id] = value
		span_concept_data = span_concept_dataset[id]
		concept_vw_idx_dict = concept_vw_idx_dict_dataset[id]
		for data in span_concept_data:
			span = data[0]
			pos = data[1]
			concept = data[2].lower()
			#short_name = data[3]
			ner = data[4]
			node = data[5]
			concept_idx = data[6]
			span = span.replace(":", ".").replace("|", ".")
			pos = pos.replace(":", ".").replace("|", ".")
			span_tag = span.replace(" ", "_").replace("\'", "")
			if not node: #this is a null concept
				vw_string = "0 0 1 {}|w {} |p {}".format(span_tag, span, pos)
			else:
				parents = amr_nx_graph.predecessors(node)
				tags = []
				parents = [parent for parent in parents if concept_vw_idx_dict.has_key(parent)] #it has an unaligned parent concept, so remove that parent
				for parent in parents:
					relation = amr_nx_graph[parent][node][0]['relation'].lower()
					if relation not in all_relations: #unknown relation, assign it index of UNK
						relation_idx =  all_relations.index("UNK")
					else:
						relation_idx = all_relations.index(relation)
					tags.append(relation)

				if not parents: #this is the root
					vw_string = "0 1 {} ".format(concept_idx)
				else:
					vw_string = "{} {} {} ".format(concept_vw_idx_dict[parents[0]], relation_idx, concept_idx)
				for i in range(1, len(parents)):
					vw_string += "{} {} ".format(concept_vw_idx_dict[parents[i]], relation_idx)

				#vw_string += "|w " + span + "|p " + pos + "|n " + ner 
				vw_string += "{}|w {} |p {}".format(span_tag, span, pos)

			output_vw_file.write(vw_string + "\n")
		output_vw_file.write("\n") 	

def main(argv):
	if len(argv) < 2:
		print "usage: python amr_nx_to_vw_for_test.py <amr_nx_graphs.p> <amr_aggregated_metadata.p> <concepts.p> <relations.p> <span_concept_dict> <vnpb_words_concepts_dict.p> <output_file.vw>"
		return
	amr_nx_graphs_p = argv[0]
	amr_aggregated_metadata_p = argv[1]
	all_concepts = pickle.load(open(argv[2], 'rb'))
	all_relations = pickle.load(open(argv[3], 'rb'))
	train_span_concept_dict_filename = argv[4] 
	global vnpb_words_concepts_dict
	vnpb_words_concepts_dict = pickle.load(open(argv[5], "rb"))
	output_vw_file = open(argv[6], 'w')
	
	#Format of amr_nx_graphs
	#amr_nx_graphs = {id : [root, amr_nx_graph, sentence, alignment]}
	amr_nx_graphs = pickle.load(open(amr_nx_graphs_p, "rb"))

	#Format of amr_aggregated_metadata
	#amr_aggregated_metadata = {id : [sentence, pos, ner]}
	amr_aggregated_metadata = pickle.load(open(amr_aggregated_metadata_p, "rb"))

	span_concept_dataset, span_concept_dict, concept_vw_idx_dict_dataset, all_concepts = create_dataset(amr_nx_graphs, amr_aggregated_metadata, all_concepts)
	write_updated_span_concept_dict(span_concept_dict, train_span_concept_dict_filename)
	print_vw_format(amr_nx_graphs, span_concept_dataset, concept_vw_idx_dict_dataset, all_relations, output_vw_file)
	pickle.dump(all_concepts, open(argv[2], 'wb'))
	
if __name__ == "__main__":
	main(sys.argv[1:])
