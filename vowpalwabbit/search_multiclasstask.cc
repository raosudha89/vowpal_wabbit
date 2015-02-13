/*
CoPyright (c) by respective owners including Yahoo!, Microsoft, and
individual contributors. All rights reserved.  Released under a BSD (revised)
license as described in the file LICENSE.
 */
#include "search_multiclasstask.h"

namespace MulticlassTask { Search::search_task task = { "multiclasstask", run, initialize, finish, NULL, NULL };  }

namespace MulticlassTask {

  struct task_data {
    size_t max_label;
    size_t num_level;
    v_array<uint32_t> y_allowed;
	bool bad_ref;
	bool cost;
  };

  void initialize(Search::search& sch, size_t& num_actions, po::variables_map& vm) {
    task_data * my_task_data = new task_data();
    sch.set_options( 0 );
    sch.set_num_learners(num_actions);
    my_task_data->max_label = num_actions;
	my_task_data->num_level = (size_t)ceil(log(num_actions) /log(2));
	my_task_data->y_allowed.push_back(1);
	my_task_data->y_allowed.push_back(2);

	po::options_description mc_opts("multiclass options");
    mc_opts.add_options()
    ("mc_bad_ref","Use an abitary bad ref")
    ("mc_cost","Use cost matrix");
    sch.add_program_options(vm, mc_opts);
    my_task_data->bad_ref = (vm.count("mc_bad_ref"))?true:false;
    my_task_data->cost = (vm.count("mc_cost"))?true:false;
    sch.set_task_data(my_task_data);
  }

  void finish(Search::search& sch) {   
    task_data * my_task_data = sch.get_task_data<task_data>();
	my_task_data->y_allowed.delete_v();
	delete my_task_data;
  }

  void run(Search::search& sch, vector<example*>& ec) {
    task_data * my_task_data = sch.get_task_data<task_data>();
    size_t gold_label = ec[0]->l.multi.label;
    size_t label = 0;
    size_t learner_id = 0;
	uint32_t filter[5];
	// For ICML exp
	uint32_t cost[5][5];
	for (int i = 0; i <= 4; i++) 
		      for (int j = 0; j <= 4; j++) 
				              if (i == j) cost[i][j] = 0; 
	            else cost[i][j] = 2;
	for(int i=0; i< 5; i++){
		filter[i] = 0;
	}

	cost[0][1] = 1; 
	cost[1][0] = 1; 
	cost[2][1] = 1; 
	cost[3][0] = 3; 
	cost[4][0] = 4;

	for(size_t i=0; i<my_task_data->num_level;i++){
	  size_t mask = 1<<(my_task_data->num_level-i-1);
	  size_t y_allowed_size = (label+mask +1 <= my_task_data->max_label)?2:1;

	  uint32_t best_label =-1;
	  for(int i= 0; i<5; i++){
		  if(!filter[i]){
			  if(best_label ==-1)
				  best_label = i;
			  else if(cost[gold_label-1][i] < cost[gold_label-1][best_label])
				  best_label = i;
		  }
	  }
//	  cerr << best_label << " " << gold_label;
//	  for(int i= 0; i<5; i++)
//		  cerr <<" " << filter[i];
	  //cerr<<endl;
      action oracle = (((best_label)&mask)>0)+1;
	  assert(oracle == 0 || oracle == 1);
	  if(my_task_data->bad_ref)
		  oracle = 1;
      size_t prediction = sch.predict(*ec[0], 0, &oracle, 1, NULL, NULL, my_task_data->y_allowed.begin, y_allowed_size, learner_id); // TODO: do we really need y_allowed?
      learner_id= (learner_id << 1) + prediction;
	  if(prediction == 1)
		  for(int i=label+mask;i < my_task_data->max_label && i < label+mask*2; i++){
			  filter[i] = 1;
//			  cerr<< "d"<<i<<" ";
		  }

	  else {		  
		  for(int i=label;i < my_task_data->max_label && i < label+mask; i++){
			  filter[i] = 1;
//			  cerr<< "d"<<i<<" ";
		  }
	      label += mask;
	  }
	}
    label+=1;
	if(my_task_data->cost)
	    sch.loss(cost[gold_label-1][label-1]);
	else
	    sch.loss(!(label == gold_label));
    if (sch.output().good())
        sch.output() << label << ' ';
  }
}
