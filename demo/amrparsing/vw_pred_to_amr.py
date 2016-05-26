import sys, os
import networkx as nx

NULL_CONCEPT = 1

concepts_dict = {}
def read_concepts(concepts_dict_file):
	for line in concepts_dict_file.readlines():
		concepts_dict[int(line.strip().split()[1])] = line.strip().split()[0].lower()

relations_dict = {}
def read_relations(relations_dict_file):
	for line in relations_dict_file.readlines():
		relations_dict[int(line.strip().split()[1])] = line.strip().split()[0].lower()

amr_root = -1
def to_nx_graph(all_heads, all_tags, all_concepts):
	#print all_heads
	#print all_tags
	#print all_concepts
	global amr_root
	amr_nx_graph = nx.MultiDiGraph()
	for idx in range(1, len(all_concepts)):
		concept = all_concepts[idx]
		if concept == NULL_CONCEPT:
			continue
		amr_nx_graph.add_node(idx, instance=concepts_dict[concept], parents=all_heads[idx])
		if all_heads[idx][0] == 0: #this is the root
			amr_root = idx
			continue #so don't add any edge
		for i, parent in enumerate(all_heads[idx]):
			amr_nx_graph.add_edge(parent, idx, relation=relations_dict[all_tags[idx][i]])
	return amr_nx_graph

shortname_dict = {}
def get_amr_string(root, amr_nx_graph, tab_levels=1):
	amr_string = ""
	print amr_nx_graph.successors(root)
	for child in amr_nx_graph.successors(root):
		if not child in shortname_dict.keys():
			size = len(shortname_dict.keys())
			shortname_dict[child] = "c"+str(size)
			child_amr_string = get_amr_string(child, amr_nx_graph, tab_levels+1)
			amr_string += "\t"*tab_levels + "\t:{0} ".format(shortname_dict[child]) + child_amr_string
		else:
			amr_string += "hello"
			amr_string += "\t:{0} {1}\n".format(shortname_dict[child], amr_nx_graph[root][child]['relation'])

	if not root in shortname_dict.keys():
		size = len(shortname_dict.keys())
		shortname_dict[root] = "c"+str(size)
		amr_string = "({0} / {1}\n".format(shortname_dict[root], amr_nx_graph.node[root]['instance']) + amr_string + ")"
	else:
		amr_string = "{0}".format(amr_nx_graph.node[root]['instance'])
	return amr_string	

def print_nx_graph(nx_graph):
	#print amr_nx_graph.nodes()
	#print amr_nx_graph.edges()	
	print amr_root
	print get_amr_string(amr_root, amr_nx_graph) 

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "usage: vw_pred_to_amr.py <data.pred> <concepts_dict> <relations_dict>"
		sys.exit(0)
	vw_pred_file = open(sys.argv[1], 'r')
	concepts_dict_file = open(sys.argv[2], 'r')
	relations_dict_file = open(sys.argv[3], 'r')
	read_concepts(concepts_dict_file)
	read_relations(relations_dict_file)
	all_heads = [[0]]
	all_tags = [[0]]
	all_concepts = [0]
	for line in vw_pred_file.readlines():
		line = line.strip("\n")
		values = line.split(':')
		if len(values) < 3 or not line:
			if all_heads:
				amr_nx_graph = to_nx_graph(all_heads, all_tags, all_concepts)
				print_nx_graph(amr_nx_graph)
			all_heads = [[0]]
			all_tags = [[0]]
			all_concepts = [0]
		else:
			values = [int(v.strip()) for v in values]
			heads = [values[0]]
			tags = [values[1]]
			concept = values[2]
			for i in range(3, len(values), 2):
				heads.append(values[i])
				tags.append(values[i+1])
			all_heads.append(heads)
			all_tags.append(tags)
			all_concepts.append(concept)	
