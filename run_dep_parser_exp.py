from os import system
from sys import argv
exp_name = argv[1]
def run_lols(train_data, test_data, test_ori_data, passes, beta, rollout, rollin, refType):
	tmpout = 'out'+exp_name
	tmpout2 = 'out2_'+exp_name
	model = 'wsjmodel'+exp_name
	train_option = '-d %s --search_beta %s --search_rollout %s --search_rollin %s '%(train_data, beta, rollout, rollin);
	if refType == 'sub':
		train_option += " --dparser_sub_ref"
	if refType == 'bad':
		train_option += " --dparser_bad_ref"
	system('./vowpalwabbit/vw -c --passes 5 --search_task dep_parser --search 12  --holdout_off -f %s --search_history_length 3 --search_no_caching -b 24 --root_label 8 --num_label 12 %s '%(model,train_option))
	system('./vowpalwabbit/vw -d %s -i %s -t -c  -p %s'%(test_data,model,tmpout))
	system('python parseTestResult.py %s  %s ../data/deps/tags  > %s'%(test_ori_data,tmpout, tmpout2))
	print rollin, rollout, beta, refType
	system('python evaluate.py %s %s'%(tmpout2,test_ori_data))


def run_searn(train_data, test_data, test_ori_data, passes, beta, rollout, rollin, refType):
	tmpout = 'out'+exp_name
	tmpout2 = 'out2_'+exp_name
	model = 'wsjmodel'+exp_name
	train_option = '-d %s '%(train_data);
	if refType == 'sub':
		train_option += " --dparser_sub_ref"
	if refType == 'bad':
		train_option += " --dparser_bad_ref"
	system('./vowpalwabbit/vw --cache_file searn_cache --search_passes_per_policy 1 --search_interpolation policy --passes 5 --search_task dep_parser --search 12  --holdout_off -f %s --search_history_length 3 --search_no_caching -b 24 --root_label 8 --num_label 12 %s '%(model,train_option))
	system('./vowpalwabbit/vw -d %s -i %s -t -c  -p %s'%(test_data,model,tmpout))
	system('python parseTestResult.py %s  %s ../data/deps/tags  > %s'%(test_ori_data,tmpout, tmpout2))
	print 'Searn %s'%refType
	system('python evaluate.py %s %s'%(tmpout2,test_ori_data))


rollin_pool = ['oracle','policy']
beta_pool = ['0', '0.5' , '1']
refType_pool = ['optimal', 'sub', 'bad']

train_data = '../data/deps/wsj02-21.naacl_l.vw' 
test_data = '../data/deps/wsj23.naacl_l.vw'
test_ori_data = '../data/deps/wsj23.naacl'
for refType in refType_pool:
	rollout = "mix_per_roll"
	for rollin in rollin_pool:
		for beta in beta_pool:
			run_lols(train_data, test_data, test_ori_data, 1, beta, rollout, rollin, refType)
	run_searn(train_data, test_data, test_ori_data, 1, beta, rollout, rollin, refType)
