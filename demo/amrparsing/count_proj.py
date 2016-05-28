import sys, os
import re
import networkx as nx
import pyparsing
import cPickle as pickle
import matplotlib.pyplot as plt

nodes = []
relations = []
amr_nx_graph = None


def add_edge(node_A, node_B):
	global relations
	global amr_nx_graph
	if amr_nx_graph.has_node(node_A) and amr_nx_graph.has_node(node_B) and relations:
		relation = relations.pop()
		amr_nx_graph.add_edge(node_A, node_B, relation=relation)


def get_all_nodes(amr_graph_as_list):
	global nodes
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			nodes.append(node)
		elif isinstance(element, list):
			get_all_nodes(element)


def add_to_nx_graph(amr_graph_as_list, prev_level_root=None, prev_level_child_num=0, pass_num=1):
	global nodes
	global relations
	global amr_nx_graph
	current_root = None
	curr_level_child_num = 0
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			instance = amr_graph_as_list[i + 1]
			amr_nx_graph.add_node(node, instance=instance, child_num=prev_level_child_num, parent=prev_level_root)
			add_edge(prev_level_root, node)
			current_root = node
			curr_level_child_num = 0
		elif isinstance(element, list):
			add_to_nx_graph(element, current_root, curr_level_child_num)
			curr_level_child_num += 1
		elif element[0] == ":":
			relations.append(element[1:])
		else:
			if i - 1 >= 0 and amr_graph_as_list[i - 1] == '/' or i + 1 < len(amr_graph_as_list) and amr_graph_as_list[
						i + 1] == '/':
				pass
			else:
				if element not in nodes:
					node = current_root + ":" + str(curr_level_child_num) + ":" + element
					amr_nx_graph.add_node(node, instance=element, child_num=curr_level_child_num, parent=current_root)
					curr_level_child_num += 1
					add_edge(current_root, node)
					nodes.append(node)
				else:
					add_edge(current_root, element)
	return current_root


def update_nx_graph(amr_graph_as_list, prev_level_root=None, prev_level_child_num=0):
	global nodes
	global relations
	global amr_nx_graph
	current_root = None
	curr_level_child_num = 0
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			current_root = node
			curr_level_child_num = 0
		elif isinstance(element, list):
			update_nx_graph(element, current_root, curr_level_child_num)
			curr_level_child_num += 1
		elif element[0] == ":":
			pass
		else:
			if i - 1 >= 0 and amr_graph_as_list[i - 1] == '/' or i + 1 < len(amr_graph_as_list) and amr_graph_as_list[
						i + 1] == '/':
				pass
			else:
				if element not in nodes:
					node = current_root + ":" + str(curr_level_child_num) + ":" + element
					amr_nx_graph.add_node(node, instance=element, child_num=curr_level_child_num, parent=current_root)
					curr_level_child_num += 1
					add_edge(current_root, node)
					nodes.append(node)
				else:
					add_edge(current_root, element)
	return current_root

def post_order(G):
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
			parent, children = stack[-1]
			# Visit the parent
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
			visited.append(parent)


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

	return (crossing_edges > 0)





	# for i in range(len(original)):
	# 	for j in range(len(original)):
	#
	# 		if i == j:
	# 			continue
	#
	# 		#Check if there is an edge
	# 		if (original[i],original[j]) not in edge_dict:
	# 			continue
	#
	# 		for k in range(i+1,j):
	# 			succ = [original.index(x) for x in G.succ[original[k]]]
	# 			pred = [original.index(x) for x in G.pred[original[k]]]
	# 			print succ
	# 			print pred










def main(argv):

	#amr_aligned = open("amr-release-1.0-training-full.aligned")
	amr_aligned = open(argv[0])
	line = amr_aligned.readline()
	count = 0
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
			# print "Nodes"
			# print current_amr_graph.nodes()
			# print current_amr_graph.edges()
			span_sorted = sorted([(current_amr_graph.node[x]['span'][0],x) for x in current_amr_graph.nodes()])
			span_sorted = [x[1] for x in span_sorted]
			pre_o = pre_order(current_amr_graph)
			#pre_o =  [current_amr_graph.node[x]['node_label'] for x in pre_o]
			assert len(span_sorted) == len(pre_o)
			# print span_sorted, pre_o
			# print
			is_projective(current_amr_graph,span_sorted)
			print is_projective(current_amr_graph,span_sorted)
			    #print count
			num_1_swaps,num_more_swap = count_swaps(span_sorted,pre_o)
			#print num_1_swaps, num_more_swap
			current_amr_graph = nx.MultiDiGraph()
			count += 1

		line = amr_aligned.readline()

	amr_aligned.close()


if __name__ == "__main__":
	main(sys.argv[1:])
