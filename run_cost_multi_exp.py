from os import system
from sys import argv
def run_lols(train_data, test_data,  passes, beta, rollout, rollin, refType):
	tmpout = 'out'+argv[1]
	tmpout2 = 'out2_'+argv[1]
	model = 'mcmodel'+argv[1]
	cache_file = train_data+'_cache_'+argv[1]
	# only pass data once now
	train_option = '--mc_cost -k -c --passes %d --search_no_caching --cache_file %s -d %s --search_beta %s --search_rollout %s --search_rollin %s '%(passes,cache_file, train_data, beta, rollout, rollin);
	if refType == 'bad':
		train_option += " --mc_bad_ref"	
	system('./vowpalwabbit/vw  --search_task multiclasstask --search 5  --holdout_off -f %s -b 24 '%model + train_option)
	system('./vowpalwabbit/vw --mc_cost -d %s -i %s -t -c  -p %s '%(test_data,model,tmpout))

def run_searn(train_data, test_data,  passes, beta, rollout, rollin, refType):
	tmpout = 'out'+argv[1]
	tmpout2 = 'out2_'+argv[1]
	model = 'mcmodel'+argv[1]
	cache_file = train_data+'_cache_'+argv[1]
	# only pass data once now
	train_option = '--mc_cost -k --passes %d --search_no_caching --cache_file %s -d %s'%(passes,cache_file, train_data);	
	if refType == 'bad':
		train_option += " --mc_bad_ref"	
	system('./vowpalwabbit/vw  --search_task multiclasstask --search 5  --holdout_off -f %s -b 24 '%model + train_option)
	system('./vowpalwabbit/vw --mc_cost -d %s -i %s -t -c  -p %s '%(test_data,model,tmpout))

rollin_pool = ['oracle','policy']
beta_pool = ['0',  '0.5','1']
refType_pool = ['optimal',  'bad']
rollout = "mix_per_roll"
train_data = '../cm/kddcup.data.shuf.parse' 
test_data = '../cm/corrected.parse'
#train_data = '../cm/corrected.parse'
for refType in refType_pool:
	run_searn(train_data,test_data, 5, -1, -1, -1, refType)
	for rollin in rollin_pool:
		for beta in beta_pool:
			run_lols(train_data, test_data, 5,  beta, rollout, rollin, refType)
