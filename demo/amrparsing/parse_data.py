from sys import argv

concepts = {}
def read_concepts():
	for line in open('concepts').readlines():
		concepts[line.split()[0]] = int(line.strip().split()[1])

relations = {}
def read_relations():
	for line in open('relations').readlines():
		relations[line.split()[0]] = int(line.strip().split()[1])

if __name__ == '__main__':
	read_concepts()
	read_relations()
	if len(argv) != 3:
		print 'parse_data.py input output'
	data = open(argv[1]).readlines()
	writer = open(argv[2],'w')
	for line in data:
		if line == '\n':
			writer.write('\n')
			continue
		splits = line.strip().lower().split()
		strw = "|w %s"%splits[1].replace(":","COL")
		strp = "|p %s"%splits[2].replace(":","COL")
		head = splits[3]			
		relation = splits[4]
		concept = splits[5]
		strc = "|c %s"%concept
		writer.write('%s %s %s %s:%s%s %s %s\n' % (int(head), relations[relation], concepts[concept], int(head), relation, strw, strp, strc))
	writer.close()

