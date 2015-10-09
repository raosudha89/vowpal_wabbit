/*
  Copyright (c) by respective owners including Yahoo!, Microsoft, and
  individual contributors. All rights reserved.  Released under a BSD (revised)
  license as described in the file LICENSE.
*/
#include "search_amr_parser.h"
#include "gd.h"
#include "cost_sensitive.h"
#include "label_dictionary.h"   // for add_example_namespaces_from_example
#include "vw.h"
#include "vw_exception.h"

namespace AMRParserTask         {  Search::search_task task = { "amr_parser", run, initialize, finish, setup, nullptr};  }

struct task_data {
  example *ex;
};

namespace AMRParserTask {
  using namespace Search;

  const action MAKE_CONCEPT = 1;
  const action RIGHT_ARC 	= 2;
  const action LEFT_ARC  	= 3;
  const action HALLUCINATE  = 4;
  const action SWAP  		= 5;


  void initialize(Search::search& sch, size_t& /*num_actions*/, po::variables_map& vm) {
  
  }

  void finish(Search::search& sch) {
  
  } 

  void inline add_feature(example& ex, uint32_t idx, unsigned char ns, size_t mask, uint32_t multiplier, bool audit=false){
  
  }

  void add_all_features(example& ex, example& src, unsigned char tgt_ns, size_t mask, uint32_t multiplier, uint32_t offset, bool audit=false) {
  
  }
  
  void inline reset_ex(example *ex, bool audit=false){
  
  }

  // arc-hybrid System.
  uint32_t transition_hybrid(Search::search& sch, uint32_t a_id, uint32_t idx, uint32_t t_id) {
  
  }
  
  void extract_features(Search::search& sch, uint32_t idx,  vector<example*> &ec) {
  
  }

  void get_valid_actions(v_array<uint32_t> & valid_action, uint32_t idx, uint32_t n, uint32_t stack_depth, uint32_t state) {
    valid_action.erase();
    if(idx<=n)
      valid_action.push_back( MAKE_CONCEPT );
    if(stack_depth >=2){
      valid_action.push_back( RIGHT_ARC );
      valid_action.push_back( LEFT_ARC );
      //TODO: SWAP
    }
      //TODO: HALLUCINATE
      
  }

  void get_gold_actions(Search::search &sch, uint32_t idx, uint32_t n, v_array<action>& gold_actions){
  
  }

  void setup(Search::search& sch, vector<example*>& ec) {
  
  }    
  
  void run(Search::search& sch, vector<example*>& ec) {

  }
}
