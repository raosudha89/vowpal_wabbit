from os import system
from sys import argv
def run_one(train_data, test_data, test_ori_data, passes, beta, rollout, rollin, refType):
	tmpout = 'out'+argv[1]
	tmpout2 = 'out2_'+argv[1]
	model = 'wsjmodel'+argv[1]
	# only pass data once now
	train_option = '-d %s --search_beta %s --search_rollout %s --search_rollin %s '%(train_data, beta, rollout, rollin);
	if refType == 'sub':
		train_option += " --dparser_sub_ref"
	if refType == 'bad':
		train_option += " --dparser_bad_ref"
	system('./vowpalwabbit/vw  --search_task dep_parser --search 12  --holdout_off -f %s --search_history_length 3 --search_no_caching -b 24 --root_label 8 --num_label 12 '%model + train_option)
	system('./vowpalwabbit/vw -d %s -i %s -t -c  -p %s'%(test_data,model,tmpout))
	system('python ../DepParserExp/script2/parseTestResult.py %s  %s ../data/deps/tags  > %s'%(test_ori_data,tmpout, tmpout2))
	print train_option
	system('python ../DepParserExp/script/evaluate.py %s %s'%(tmpout2,test_ori_data))


#rollin_pool = ['oracle','policy']
#beta_pool = ['0', '0.5' , '1']
refType_pool = ['optimal', 'sub', 'bad']
beta_pool = ['1']
rollin_pool = ['policy']

rollout = "mix_per_roll"
train_data = '../data/deps/wsj02-21.naacl_l.vw' 
test_data = '../data/deps/wsj23.naacl_l.vw'
test_ori_data = '../data/deps/wsj23.naacl'
for refType in refType_pool:
#	if refType != refType_pool[int(argv[1])]:
#		continue
	for rollin in rollin_pool:
		for beta in beta_pool:
			run_one(train_data, test_data, test_ori_data, 1, beta, rollout, rollin, refType)
