import sys, os
import networkx as nx
import pdb
import pickle as p

NULL_CONCEPT = 1

def to_nx_graph(all_heads, all_tags, all_concepts):
	print all_heads
	print all_tags
	print all_concepts
	amr_roots = []
	amr_nx_graph = nx.MultiDiGraph()
	for idx in range(1, len(all_concepts)):
		concept = all_concepts[idx]
		if concept == NULL_CONCEPT:
			continue
		amr_nx_graph.add_node(idx, instance=concepts_dict[concept], parents=all_heads[idx])
		if all_heads[idx][0] == 0: #this is the root
			amr_roots.append(idx)
			continue #so don't add any edge
		if len(all_heads[idx]) > 1:
			pdb.set_trace()
		for i, parent in enumerate(all_heads[idx]):
			amr_nx_graph.add_edge(parent, idx, relation=relations_dict[all_tags[idx][i]])
	return amr_nx_graph, amr_roots

shortname_dict = {}
def get_amr_string(root, amr_nx_graph, tab_levels=1):
	amr_string = ""
	#print amr_nx_graph.successors(root)
	for child in amr_nx_graph.successors(root):
		if not child in shortname_dict.keys():
			size = len(shortname_dict.keys())
			child_amr_string = get_amr_string(child, amr_nx_graph, tab_levels+1)
			shortname_dict[child] = "c"+str(size)
			amr_string += "\t"*tab_levels + "\t:{0} ".format(amr_nx_graph[root][child][0]['relation']) + child_amr_string
		else:
			amr_string += "\t:{0} {1}\n".format(amr_nx_graph[root][child][0]['relation'], shortname_dict[child])

	if not root in shortname_dict.keys():
		size = len(shortname_dict.keys())
		shortname_dict[root] = "c"+str(size)
		amr_string = "({0} / {1}\n".format(shortname_dict[root], amr_nx_graph.node[root]['instance']) + amr_string + ")"
	else:
		amr_string = "{0}".format(amr_nx_graph.node[root]['instance'])
	return amr_string	

def print_nx_graph(nx_graph, amr_roots):
	#print amr_nx_graph.nodes()
	#print amr_nx_graph.edges()	
	#print amr_root
	#pdb.set_trace()
	if not amr_roots: #Only null concepts predicted
		amr_nx_graph.add_node(0, instance='multi-sentence', parents=None)
		print get_amr_string(0, amr_nx_graph)
	elif len(amr_roots) > 1:
		amr_nx_graph.add_node(0, instance='multi-sentence', parents=None)
		for i, amr_root in enumerate(amr_roots):
			amr_nx_graph.add_edge(0, amr_root, relation='snt'+str(i+1))
		print get_amr_string(0, amr_nx_graph)
	else:	
		print get_amr_string(amr_roots[0], amr_nx_graph)
	print

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "usage: vw_pred_to_amr.py <data.pred> <all_concepts.p> <all_relations.p>"
		sys.exit(0)
	vw_pred_file = open(sys.argv[1], 'r')
	concepts_dict = p.load(open(sys.argv[2], 'rb'))
	relations_dict = p.load(open(sys.argv[3], 'rb'))
	all_heads = [[0]]
	all_tags = [[0]]
	all_concepts = [0]
	global shortname_dict
	for line in vw_pred_file.readlines():
		line = line.strip("\n")
		values = line.split(':')
		if not values[0].isdigit() or not values[1].isdigit() or not line:
			if all_heads:
				amr_nx_graph, amr_roots = to_nx_graph(all_heads, all_tags, all_concepts)
				print_nx_graph(amr_nx_graph, amr_roots)
			all_heads = [[0]]
			all_tags = [[0]]
			all_concepts = [0]
			shortname_dict = {}
			amr_root = []
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