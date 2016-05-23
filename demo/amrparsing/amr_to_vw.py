import sys, os
import re
import networkx as nx
import pyparsing
import cPickle as pickle
import matplotlib.pyplot as plt

amr_nx_graph = None


# def post_order(G):
# 	root = [G.graph['root']]
# 	edge_list = []
# 	visited = []
# 	for start in root:
# 		if start in visited:
# 			continue
#
# 		start_children = list(G[root[0]])
# 		# sort children by span order
# 		start_children_span = sorted([ (G.node[x]['span'][0],x) for x in start_children],reverse=True)
# 		start_children = [p[1] for p in start_children_span]
# 		stack = [(start, start_children)]
# 		#visited.append(start)
# 		while stack:
# 			#print stack
# 			parent, children = stack[-1]
# 			# Visit the parent
# 			# Then visit all children
# 			for i in range(len(children)):
# 				child = children[i]
# 				#print child
# 				if child not in visited:
# 					edge_list.append((parent,child))
# 					#visited.append(child)
# 					new_children = list(G[child])
# 					children_span = sorted([(G.node[x]['span'][0], x) for x in new_children],reverse=True)
# 					#print children_span
# 					new_children = [p[1] for p in children_span]
# 					#stack = [(start, start_children)]
# 					stack.append((child, new_children))
# 			visited.append(parent)


def pre_order(G):
	root = [G.graph['root']]
	edge_list = []
	visited = []
	for start in root:
		if start in visited:
			continue

		start_children = list(G[root[0]])
		# sort children by span order
		start_children_span = sorted([ (G.node[x]['span'][0],x) for x in start_children],reverse=True)
		start_children = [p[1] for p in start_children_span]
		stack = [(start, start_children)]
		#visited.append(start)
		while stack:
			#print stack
			parent, children = stack.pop()
			# Visit the parent
			if parent in visited:
				continue
			visited.append(parent)
			# Then visit all children
			for i in range(len(children)):
				child = children[i]
				#print child
				if child not in visited:
					edge_list.append((parent,child))
					#visited.append(child)
					new_children = list(G[child])
					children_span = sorted([(G.node[x]['span'][0], x) for x in new_children],reverse=True)
					#print children_span
					new_children = [p[1] for p in children_span]
					#stack = [(start, start_children)]
					stack.append((child, new_children))


	return visited


def count_swaps(original,ordered):
	one_swap = 0
	more_swaps = 0
	for i in range(len(original)):
		idx = ordered.index(original[i])
		if idx == i - 1:
			one_swap += 1
		elif idx > i:
			more_swaps += 1

	return one_swap, more_swaps


def is_projective(G,original):

	edge_dict = {x:1 for x in G.edges()}
	#print edge_dict
	crossing_edges = 0

	for each_edge in edge_dict:
		#print G.node[each_edge[0]]
		h = G.node[each_edge[0]]['span'][0]
		t = G.node[each_edge[1]]['span'][0]
		#print h,t
		for each_edge2 in edge_dict:

			h2 = G.node[each_edge2[0]]['span'][0]
			t2 = G.node[each_edge2[1]]['span'][0]

			if t < h:

				h,t=t,h

			if h < h2 < t:
				if t2 < h or t2 > t:
					crossing_edges += 1
			elif h < t2 < t:
				if h2 < h or h2 > t:
					crossing_edges += 1

	#print crossing_edges





def main(argv):

	all_concept = {"null":1}
	all_relations = {"root":0,"noedge":0}
	concept_count = 2
	relation_count = 1
	#amr_aligned = open("amr-release-1.0-training-full.aligned")
	amr_aligned = open(argv[0])
	line = amr_aligned.readline()
	current_amr_graph = nx.MultiDiGraph()
	while (line != ""):
		if line.startswith("# ::id"):
			current_id = line.split()[2]
			current_amr_graph.graph['id'] =  current_id
		elif line.startswith("# ::tok"):
			current_sent = line.strip("# ::tok").strip()
			current_amr_graph.graph['sent'] = current_sent
		elif line.startswith("# ::node"):
			x = line.strip().split('\t')
			curr_node_id = x[1]
			curr_node_label = x[2]
			try:
				current_node_span = [int(p) for p in x[3].split('-')]
				final_span = range(current_node_span[0], current_node_span[1])
				if not final_span:
					final_span = [-1]
			except IndexError:
				final_span = [-1]
			#Add node to graph
			# if curr_node_id not in nodes:
			# 	nodes[curr_node]
			current_amr_graph.add_node(curr_node_id,node_label=curr_node_label,span=final_span)
		elif line.startswith("# ::root"):
			x = line.strip().split('\t')
			current_amr_graph.graph['root'] = x[1]
		elif line.startswith("# ::edge"):
			x = line.strip().split('\t')
			head = x[4]
			tail = x[5]
			label  = x[2]
			current_amr_graph.add_edge(head,tail,key=label,edge_label=label)
		elif line.strip() == "":
			span_sorted = sorted([(current_amr_graph.node[x]['span'][0],current_amr_graph.node[x]['span'][-1],
			x,current_amr_graph.node[x]['span']) for x in current_amr_graph.nodes() if current_amr_graph.node[x]['span'][0] != -1 ])
			for each_edge in current_amr_graph.edges():
				lhs = each_edge[0]
				rhs = each_edge[1]
				lhs_name = current_amr_graph.node[lhs]['node_label']
				rhs_name = current_amr_graph.node[rhs]['node_label']
			#print current_amr_graph.node
			#print span_sorted
			sent_tok = current_amr_graph.graph['sent'].split()
			i = 0
			j = 0
			count = 1
			POS = "UNK"
			extra = 0
			while (i <len(sent_tok)):
				if j == len(span_sorted):
					break
				if span_sorted[j][0] == i:
					node = span_sorted[j][2]
					node_label = current_amr_graph.node[node]['node_label']
					if node_label not in all_concept:
						all_concept[node_label] = concept_count
						concept_count += 1
					parent_info = current_amr_graph.pred[node]
					#If it is a root
					if len(parent_info) == 0:
						print count,"\t",' '.join(sent_tok[i:span_sorted[j][1]+1]),"\t",POS,"\t",0,"\t","ROOT","\t",node_label
					else:
						#We choose a random parent for now
						parent = parent_info.keys()[0]
						label = parent_info[parent].keys()[0]
						if label not in all_relations:
							all_relations[label] = relation_count
							relation_count += 1
						parent_pos = current_amr_graph.node[parent]['span'][0]
						#print p
						print count,"\t",' '.join(sent_tok[i:span_sorted[j][1]+1]),"\t",POS,"\t",parent_pos+1+extra,"\t",label,"\t",node_label

					new_i = span_sorted[j][1] + 1
					j += 1
					if j == len(span_sorted):
						break
					if span_sorted[j][0] != i:
						i = new_i
					else:
						extra += 1
				else:
					print count,"\t",sent_tok[i],"\t",0,"\t","NOEDGE","\t","NULL"
					i += 1
				count += 1
			print
			current_amr_graph = nx.MultiDiGraph()

		line = amr_aligned.readline()

	amr_aligned.close()
	with open("nodes_dict", 'w') as f:
		nodes_list = sorted([ (key,all_concept[key])for key in all_concept],key=lambda x:x[1])
		for each_node in nodes_list:
			f.write("{0}\t{1}\n".format(each_node[0],each_node[1]))

	with open("edges_dict", 'w') as f:
		edges_list = sorted([ (key,all_relations[key])for key in all_relations],key=lambda x:x[1])
		for each_node in edges_list:
			f.write("{0}\t{1}\n".format(each_node[0],each_node[1]))


if __name__ == "__main__":
	main(sys.argv[1:])
