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

#define val_namespace 100 // valency and distance feature space
#define offset_const 344429

namespace AMRParserTask         {  Search::search_task task = { "amr_parser", run, initialize, finish, setup, nullptr};  }

struct task_data
{ example *ex;
  size_t amr_root_label;
  uint32_t amr_num_label;
  uint32_t amr_num_concept;
  v_array<uint32_t> valid_actions, action_loss, gold_heads, gold_tags, stack, heads, tags, temp, valid_action_temp, gold_concepts, concepts;
  v_array<action> gold_actions, gold_action_temp, valid_tags, valid_concepts;
  v_array<pair<action, float>> gold_action_losses;
  v_array<uint32_t> children[6]; // [0]:num_left_arcs, [1]:num_right_arcs; [2]: leftmost_arc, [3]: second_leftmost_arc, [4]:rightmost_arc, [5]: second_rightmost_arc
  example * ec_buf[13];
};

namespace AMRParserTask
{
using namespace Search;

const action MAKE_CONCEPT         = 1;
const action REDUCE_RIGHT         = 2;
const action REDUCE_LEFT          = 3;
const action SWAP_REDUCE_RIGHT	  = 4;
const action SWAP_REDUCE_LEFT 	  = 5;
const action SHIFT 		  = 6;

const int NUM_ACTIONS = 6;
const int NUM_LEARNERS = 6;
const int NULL_CONCEPT = 1;
const int NO_HEAD = 0; //this is not predicted and hence can be 0
const int NO_EDGE = 0; //this is not predicted and hence can be 0
const int ROOT = 0;

void initialize(Search::search& sch, size_t& /*num_actions*/, po::variables_map& vm)
{ vw& all = sch.get_vw_pointer_unsafe();
  task_data *data = new task_data();
  data->action_loss.resize(NUM_ACTIONS+1);
  data->ex = NULL;
  sch.set_task_data<task_data>(data);
  //sch.set_force_oracle(1);

  new_options(all, "AMR Parser Options")
  ("amr_root_label", po::value<size_t>(&(data->amr_root_label))->default_value(1), "Ensure that there is only one root in each sentence")
  ("amr_num_label", po::value<uint32_t>(&(data->amr_num_label))->default_value(5), "Number of arc labels")
  ("amr_num_concept", po::value<uint32_t>(&(data->amr_num_concept))->default_value(50), "Number of concepts");
  add_options(all);

  check_option<size_t>(data->amr_root_label, all, vm, "amr_root_label", false, size_equal,
                       "warning: you specified a different value for --amr_root_label than the one loaded from regressor. proceeding with loaded value: ", "");
  check_option<uint32_t>(data->amr_num_label, all, vm, "amr_num_label", false, uint32_equal,
                         "warning: you specified a different value for --amr_num_label than the one loaded from regressor. proceeding with loaded value: ", "");

  check_option<uint32_t>(data->amr_num_concept, all, vm, "amr_num_concept", false, uint32_equal,
                         "warning: you specified a different value for --amr_num_concept than the one loaded from regressor. proceeding with loaded value: ", "");

  data->ex = VW::alloc_examples(sizeof(polylabel), 1);
  data->ex->indices.push_back(val_namespace);
  for(size_t i=1; i<14; i++)
    data->ex->indices.push_back((unsigned char)i+'A');
  data->ex->indices.push_back(constant_namespace);

  sch.set_num_learners(NUM_LEARNERS);

  data->valid_tags = v_init<action>();
  for (action a=1; a<data->amr_num_label; a++)
    data->valid_tags.push_back(a);
  
  data->valid_concepts = v_init<action>();
  for (action a=1; a<data->amr_num_concept; a++)
    data->valid_concepts.push_back(a);
  
  const char* pair[] = {"BC", "BE", "BB", "CC", "DD", "EE", "FF", "GG", "EF", "BH", "BJ", "EL", "dB", "dC", "dD", "dE", "dF", "dG", "dd"};
  const char* triple[] = {"EFG", "BEF", "BCE", "BCD", "BEL", "ELM", "BHI", "BCC", "BEJ", "BEH", "BJK", "BEN"};
  vector<string> newpairs(pair, pair+19);
  vector<string> newtriples(triple, triple+12);
  all.pairs.swap(newpairs);
  all.triples.swap(newtriples);

  for (v_string& i : all.interactions)
    i.delete_v();
  all.interactions.erase();
  for (string& i : all.pairs)
    all.interactions.push_back(string2v_string(i));
  for (string& i : all.triples)
    all.interactions.push_back(string2v_string(i));
  sch.set_options(AUTO_CONDITION_FEATURES | NO_CACHING );

  sch.set_label_parser( COST_SENSITIVE::cs_label, [](polylabel&l) -> bool { return l.cs.costs.size() == 0; });
}

void finish(Search::search& sch)
{ task_data *data = sch.get_task_data<task_data>();
  data->valid_actions.delete_v();
  data->valid_action_temp.delete_v();
  data->gold_heads.delete_v();
  data->gold_tags.delete_v();
  data->gold_concepts.delete_v();
  data->stack.delete_v();
  data->heads.delete_v();
  data->tags.delete_v();
  data->concepts.delete_v();
  data->temp.delete_v();
  data->action_loss.delete_v();
  data->gold_actions.delete_v();
  data->valid_tags.delete_v();
  data->valid_concepts.delete_v();
  data->gold_action_losses.delete_v();
  data->gold_action_temp.delete_v();
  VW::dealloc_example(COST_SENSITIVE::cs_label.delete_label, *data->ex);
  free(data->ex);
  for (size_t i=0; i<6; i++) data->children[i].delete_v();
  delete data;
}

void inline add_feature(example& ex, uint64_t idx, unsigned char ns, uint64_t mask, uint64_t multiplier, bool audit=false)
{
  ex.feature_space[(int)ns].push_back(1.0f, (idx * multiplier) & mask);
}

void add_all_features(example& ex, example& src, unsigned char tgt_ns, uint64_t mask, uint64_t multiplier, uint64_t offset, bool audit=false)
{
  features& tgt_fs = ex.feature_space[tgt_ns];
  for (namespace_index ns : src.indices)
    if(ns != constant_namespace) // ignore constant_namespace
        for (feature_index i : src.feature_space[ns].indicies)
            tgt_fs.push_back(1.0f, ((i / multiplier + offset) * multiplier) & mask );
}

void inline reset_ex(example *ex)
{ ex->num_features = 0;
  ex->total_sum_feat_sq = 0;
  for (features& fs : *ex)
    fs.erase();
}

// arc-hybrid System.
size_t transition_hybrid(Search::search& sch, uint64_t a_id, uint32_t idx, uint32_t t_id)
{ task_data *data = sch.get_task_data<task_data>();
  v_array<uint32_t> &heads=data->heads, &stack=data->stack, &gold_heads=data->gold_heads, &gold_tags=data->gold_tags, &tags = data->tags, &gold_concepts=data->gold_concepts, &concepts=data->concepts;
  v_array<uint32_t> *children = data->children;
  if (a_id == MAKE_CONCEPT)
  { concepts[idx] = t_id;
    if (t_id == NULL_CONCEPT)
    {  heads[idx] = NO_HEAD;
       tags[idx] = NO_EDGE;
       sch.loss(gold_concepts[idx] != concepts[idx] ? 3.f : 0.f);
       //cdbg << "NULL_CONCEPT" << endl;
       //cdbg << "idx " << idx << endl;
       //cdbg << "heads " << heads[idx] << endl;
       return idx+1;
    }
    else
    {  sch.loss(gold_concepts[idx] != concepts[idx] ? 1.f : 0.f);
       return idx;
    } 
  }
  else if (a_id == SHIFT)
  { stack.push_back(idx);
    //cdbg << "SHIFT PUSHED " << idx << endl;
    return idx+1;
  }
  else if (a_id == REDUCE_RIGHT)
  { uint32_t last   = stack.last();
    uint32_t   hd     = stack[ stack.size() - 2 ];
    heads[last]     = hd;
    children[5][hd] = children[4][hd];
    children[4][hd] = last;
    children[1][hd] ++;
    tags[last]      = t_id;
    sch.loss(gold_heads[last] != heads[last] ? 2 : (gold_tags[last] != t_id) ? 1.f : 0.f);
    assert(! stack.empty());
    stack.pop();
    return idx;
  }
  else if (a_id == REDUCE_LEFT)
  { size_t last    = stack.last();
    //cdbg << "last " << last << endl;
    heads[last]      = idx;
    children[3][idx] = children[2][idx];
    children[2][idx] = last;
    children[0][idx] ++;
    tags[last]       = t_id;
    sch.loss(gold_heads[last] != heads[last] ? 2 : (gold_tags[last] != t_id) ? 1.f : 0.f);
    assert(! stack.empty());
    stack.pop();
    stack.push_back(idx);
    //cdbg << "RL PUSHED " << idx << endl;
    return idx+1;
  }
  else if (a_id == SWAP_REDUCE_RIGHT)
  {
    size_t last = stack.last();
    stack.pop();
    size_t second_last = stack.last();
    stack.pop();
    size_t third_last = stack.last();
    stack.pop();
    heads[last] = third_last;
    children[5][third_last] = children[4][third_last];
    children[4][third_last] = last;
    children[1][third_last] ++;
    tags[last] = t_id;
    sch.loss(gold_heads[last] != heads[last] ? 2 : (gold_tags[last] != t_id) ? 1.f : 0.f);
    stack.push_back(third_last);
    stack.push_back(second_last);
    return idx; 
  }
  else if (a_id == SWAP_REDUCE_LEFT)
  {
    size_t last = stack.last();
    stack.pop();
    size_t second_last = stack.last();
    stack.pop();
    heads[second_last] = idx;
    children[3][idx] = children[2][idx];
    children[2][idx] = second_last;
    children[0][idx] ++;
    tags[second_last] = t_id;
    sch.loss(gold_heads[second_last] != heads[second_last] ? 2 : (gold_tags[second_last] != t_id) ? 1.f : 0.f);
    stack.push_back(last);
    stack.push_back(idx);
    //cdbg << "SRL PUSHED " << idx << endl;
    return idx+1;
   }
  THROW("transition_hybrid failed");
}

void extract_features(Search::search& sch, uint32_t idx,  vector<example*> &ec)
{ vw& all = sch.get_vw_pointer_unsafe();
  task_data *data = sch.get_task_data<task_data>();
  reset_ex(data->ex);
  uint64_t mask = sch.get_mask();
  uint64_t multiplier = all.wpp << all.reg.stride_shift;
  v_array<uint32_t> &stack = data->stack, &tags = data->tags, *children = data->children, &temp=data->temp;
  example **ec_buf = data->ec_buf;
  example &ex = *(data->ex);

  size_t n = ec.size();
  bool empty = stack.empty();
  size_t last = empty ? 0 : stack.last();

  for(size_t i=0; i<13; i++)
    ec_buf[i] = nullptr;

  // feature based on the top three examples in stack ec_buf[0]: s1, ec_buf[1]: s2, ec_buf[2]: s3
  for(size_t i=0; i<3; i++)
    ec_buf[i] = (stack.size()>i && *(stack.end()-(i+1))!=0) ? ec[*(stack.end()-(i+1))-1] : 0;

  // features based on examples in string buffer ec_buf[3]: b1, ec_buf[4]: b2, ec_buf[5]: b3
  for(size_t i=3; i<6; i++)
    ec_buf[i] = (idx+(i-3)-1 < n) ? ec[idx+i-3-1] : 0;

  // features based on the leftmost and the rightmost children of the top element stack ec_buf[6]: sl1, ec_buf[7]: sl2, ec_buf[8]: sr1, ec_buf[9]: sr2;
  for(size_t i=6; i<10; i++)
    if (!empty && last != 0&& children[i-4][last]!=0)
      ec_buf[i] = ec[children[i-4][last]-1];

  // features based on leftmost children of the top element in bufer ec_buf[10]: bl1, ec_buf[11]: bl2
  for(size_t i=10; i<12; i++)
    ec_buf[i] = (idx <=n && children[i-8][idx]!=0) ? ec[children[i-8][idx]-1] : 0;
  ec_buf[12] = (stack.size()>1 && *(stack.end()-2)!=0 && children[2][*(stack.end()-2)]!=0) ? ec[children[2][*(stack.end()-2)]-1] : 0;

  // unigram features
  for(size_t i=0; i<13; i++)
  { uint64_t additional_offset = (uint64_t)(i*offset_const);
    if (!ec_buf[i])
      add_feature(ex, (uint64_t) 438129041 + additional_offset, (unsigned char)((i+1)+'A'), mask, multiplier);
    else
      add_all_features(ex, *ec_buf[i], 'A'+(unsigned char)(i+1), mask, multiplier, additional_offset, false);
  }

  // Other features
  temp.resize(10);
  temp[0] = empty ? 0: (idx >n? 1: 2+min(5, idx - (uint64_t)last));
  temp[1] = empty? 1: 1+min(5, children[0][last]);
  temp[2] = empty? 1: 1+min(5, children[1][last]);
  temp[3] = idx>n? 1: 1+min(5 , children[0][idx]);
  for(size_t i=4; i<8; i++)
    temp[i] = (!empty && children[i-2][last]!=0)?tags[children[i-2][last]]:15;
  for(size_t i=8; i<10; i++)
    temp[i] = (idx <=n && children[i-6][idx]!=0)? tags[children[i-6][idx]] : 15;

  uint64_t additional_offset = val_namespace*offset_const;
  for(size_t j=0; j< 10; j++)
  {
    additional_offset += j* 1023;
    add_feature(ex, temp[j]+ additional_offset , val_namespace, mask, multiplier);
  }
  size_t count=0;
  for (features fs : *data->ex)
    { fs.sum_feat_sq = (float) fs.size();
      count+= fs.size();
    }

  size_t new_count;
  float new_weight;
  INTERACTIONS::eval_count_of_generated_ft(all, *data->ex, new_count, new_weight);

  data->ex->num_features = count + new_count;
  data->ex->total_sum_feat_sq = (float) count + new_weight;
}

void get_valid_actions(v_array<uint32_t> & valid_action, uint64_t idx, uint64_t n, uint64_t stack_depth, uint64_t state, v_array<uint32_t> &concepts)
{ valid_action.erase();
  if(idx<=n && concepts[idx] == 0)
    valid_action.push_back( MAKE_CONCEPT );
  if(idx<=n && concepts[idx] != 0)
    valid_action.push_back( SHIFT );
  if(stack_depth >=2)
    valid_action.push_back( REDUCE_RIGHT );
  if(stack_depth >=1 && state!=0 && idx<=n && concepts[idx] != 0)
    valid_action.push_back( REDUCE_LEFT );
  if(stack_depth >=3)
    valid_action.push_back( SWAP_REDUCE_RIGHT );
  if(stack_depth >=2 && state!=0 && idx<=n && concepts[idx] != 0)
    valid_action.push_back( SWAP_REDUCE_LEFT);
  //cdbg << "GET_VALID_ACTIONS" << endl;
  //cdbg << "concepts[idx] " << concepts[idx] << endl;
  //cdbg << "valid_actions " << valid_action << endl;
}

bool is_valid(uint64_t action, v_array<uint32_t> valid_actions)
{ for(size_t i=0; i< valid_actions.size(); i++)
    if(valid_actions[i] == action)
      return true;
  return false;
}

void get_gold_actions(Search::search &sch, uint32_t idx, uint64_t n, v_array<action>& gold_actions)
{ gold_actions.erase();
  task_data *data = sch.get_task_data<task_data>();
  v_array<uint32_t> &action_loss = data->action_loss, &stack = data->stack, &gold_heads=data->gold_heads, &valid_actions=data->valid_actions;
  size_t size = stack.size();
  size_t last = (size==0) ? 0 : stack.last();
  
  if (size >=2 && is_valid(SWAP_REDUCE_LEFT, valid_actions) && gold_heads[stack[size-2]] == idx)
  { gold_actions.push_back(SWAP_REDUCE_LEFT);
    //cdbg << "RET SRL" << endl;
    return;
  }

  if (is_valid(REDUCE_LEFT,valid_actions) && gold_heads[last] == idx)
  { gold_actions.push_back(REDUCE_LEFT);
    //cdbg << "RET RL" << endl;
    return;
  }
  
  if (is_valid(SHIFT,valid_actions) &&( stack.empty() || gold_heads[idx] == last)) // becoz if we take any ohter action, we will lose this edge
  { gold_actions.push_back(SHIFT);
    //cdbg << "RET S" << endl;
    return;
  }
  
  for(size_t i = 1; i<=NUM_ACTIONS ; i++)
  {  action_loss[i] = (is_valid(i,valid_actions))?0:100;
     //cdbg << "action_loss " << action_loss[i] << endl;
  }

  if (size >= 3)
  { for(size_t i = 0; i<size-2; i++)
      if(idx <=n && (gold_heads[stack[i]] == idx || gold_heads[idx] == stack[i]))
        action_loss[SHIFT] += 1;
  }
  if(size>0 && gold_heads[last] == idx)
    action_loss[SHIFT] += 1;
  if(size>=2 && gold_heads[stack[size-2]] == idx)
    action_loss[SHIFT] += 1;

  if(size>0)
  { for(size_t i = idx+1; i<=n; i++)
      if(gold_heads[i] == last|| gold_heads[last] == i)
        action_loss[REDUCE_LEFT] +=1;
  }
  if(size>0  && idx <=n && gold_heads[idx] == last)
    action_loss[REDUCE_LEFT] +=1;
  if(size>=2 && gold_heads[last] == stack[size-2]) //i.e. we can't do REDUCE_RIGHT anymore 
    action_loss[REDUCE_LEFT] += 1;
  if(size>=3 && gold_heads[last] == stack[size-3]) //i.e. we can't do SWAP_REDUCE_RIGHT anymore
    action_loss[REDUCE_LEFT] += 1;

  if(size>0 && gold_heads[last] >=idx) // we assume here that every node has only one head. Hallucinated nodes will take care of co-ref
    action_loss[REDUCE_RIGHT] +=1;
  if(size>=3 && gold_heads[last] == stack[size-3])
    action_loss[REDUCE_RIGHT] +=1;
  if(size>0)
  {
    for(size_t i = idx; i<=n; i++)
      if(gold_heads[i] == last)
        action_loss[REDUCE_RIGHT] +=1;
  }
  
  if(size >= 2)
  { if(size>=3 && gold_heads[stack[size-2]] == stack[size-3])
      action_loss[SWAP_REDUCE_LEFT] +=1;
    if(size>=4 && gold_heads[stack[size-2]] == stack[size-4])
      action_loss[SWAP_REDUCE_LEFT] +=1;
    for(size_t i=idx+1; i<=n; i++)
      if(gold_heads[stack[size-2]] == i || gold_heads[i] == stack[size-2])
        action_loss[SWAP_REDUCE_LEFT] +=1;
    if(gold_heads[idx] == stack[size-2])
      action_loss[SWAP_REDUCE_LEFT] +=1;
    if(gold_heads[stack[size-1]] == stack[size-2])
      action_loss[SWAP_REDUCE_LEFT] +=1;
    if(gold_heads[stack[size-1]] == idx)
      action_loss[SWAP_REDUCE_LEFT] +=1;

  }

  if(size>0)
  { for(size_t i=idx; i<=n; i++)
      if(gold_heads[last] == i || gold_heads[i] == last)
        action_loss[SWAP_REDUCE_RIGHT] +=1;
    if(size>=2 && gold_heads[last] == stack[size-2])
      action_loss[SWAP_REDUCE_RIGHT] +=1;
  }

  // return the best actions
  size_t best_action = 2;
  size_t count = 0;
  for(size_t i=2; i<=NUM_ACTIONS; i++)
    if(action_loss[i] < action_loss[best_action])
    { best_action= i;
      count = 1;
      gold_actions.erase();
      gold_actions.push_back((uint32_t)i);
    }
    else if (action_loss[i] == action_loss[best_action])
    { count++;
      gold_actions.push_back(i);
    }
  // return 1 only if no other action is better than 1
  if (action_loss[1] < action_loss[best_action])
  { gold_actions.erase();
    gold_actions.push_back((uint32_t)1);
  }
}

void setup(Search::search& sch, vector<example*>& ec)
{ task_data *data = sch.get_task_data<task_data>();
  v_array<uint32_t> &gold_heads=data->gold_heads, &heads=data->heads, &gold_tags=data->gold_tags, &tags=data->tags, &gold_concepts=data->gold_concepts, &concepts=data->concepts;
  size_t n = ec.size();
  heads.resize(n+1);
  tags.resize(n+1);
  concepts.resize(n+1);
  gold_heads.erase();
  gold_heads.push_back(0);
  gold_tags.erase();
  gold_tags.push_back(0);
  gold_concepts.erase();
  gold_concepts.push_back(0);
  for (size_t i=0; i<n; i++)
  { v_array<COST_SENSITIVE::wclass>& costs = ec[i]->l.cs.costs;
    size_t head,tag,concept;
    head = (costs.size() == 0) ? 0 : costs[0].class_index;
    tag  = (costs.size() <= 1) ? (uint64_t)data->amr_root_label : costs[1].class_index;
    concept  = (costs.size() <= 2) ? 0 : costs[2].class_index;
    if (tag > data->amr_num_label)
      THROW("invalid label " << tag << " which is > num actions=" << data->amr_num_label);
    if (concept > data->amr_num_concept)
      THROW("invalid concept " << concept << " which is > num actions=" << data->amr_num_concept);

    gold_heads.push_back(head);
    gold_tags.push_back(tag);
    gold_concepts.push_back(concept);
    heads[i+1] = 0;
    tags[i+1] = -1;
    concepts[i+1] = 0;

  }
  for(size_t i=0; i<6; i++)
    data->children[i].resize(n+(size_t)1);
}

void run(Search::search& sch, vector<example*>& ec)
{ task_data *data = sch.get_task_data<task_data>();
  v_array<uint32_t> &stack=data->stack, &gold_heads=data->gold_heads, &valid_actions=data->valid_actions, &heads=data->heads, &gold_tags=data->gold_tags, &tags=data->tags, &gold_concepts=data->gold_concepts, &concepts=data->concepts;
  v_array<action> &gold_actions = data->gold_actions;
  v_array<action>& valid_tags = data->valid_tags;
  v_array<action>& valid_concepts = data->valid_concepts;
  uint64_t n = (uint64_t) ec.size();
  //cdbg << "n " << n << endl;
  stack.erase();
  for (size_t i=0; i<=n; i++)
    concepts[i] = 0;
  //cdbg << "stack_size" << stack.size() << endl;
  stack.push_back(ROOT); //if ROOT is pushed into stack then what prevents an AMR from having two roots?
  for(size_t i=0; i<6; i++)
    for(size_t j=0; j<n+1; j++)
      data->children[i][j] = 0;

  int count=1;
  size_t idx = 1;
  Search::predictor P(sch, (ptag) 0);

  //cdbg << "stack_size" << stack.size() << endl;
  while(stack.size()>1 || idx <= n)
  { bool extracted_features = false;
    if(sch.predictNeedsExample())
    { extract_features(sch, idx, ec);
      extracted_features = true;
    }
    get_valid_actions(valid_actions, idx, n, (uint64_t) stack.size(), stack.empty() ? 0 : stack.last(), concepts);
    
    cdbg << "VALID ACTIONS " << valid_actions << endl;
    cdbg << "idx " << idx << endl;
    cdbg << "stack_size " << stack.size() << endl;
    size_t a_id = 0, t_id = 0;

    get_gold_actions(sch, idx, n, gold_actions);
    cdbg << "GOLD ACTIONS " << gold_actions << endl;
    a_id= P.set_tag((ptag) count)
           .set_input(*(data->ex))
           .set_oracle(gold_actions)
           .set_allowed(valid_actions)
           .set_condition_range(count-1, sch.get_history_length(), 'p')
           .set_learner_id(0)
           .predict();
    cdbg << "PREDICTED ACTION " << a_id << endl;
    count++;
    if ((!extracted_features) && sch.predictNeedsExample())
      extract_features(sch, idx, ec);

    if (a_id == MAKE_CONCEPT)
    { uint32_t gold_concept = gold_concepts[idx]; 
      t_id = P.set_tag((ptag) count)
              .set_input(*(data->ex))
              .set_oracle(gold_concept)
              .set_allowed(valid_concepts)
              .set_condition_range(count-1, sch.get_history_length(), 'p')
              .set_learner_id(a_id)
              .predict();
      cdbg << "t_id " << t_id << endl;
    }
    else if (a_id == REDUCE_LEFT || a_id == REDUCE_RIGHT || a_id == SWAP_REDUCE_RIGHT)
    { uint32_t gold_label = gold_tags[stack.last()];
      t_id = P.set_tag((ptag) count)
              .set_input(*(data->ex))
              .set_oracle(gold_label)
              .set_allowed(valid_tags)
              .set_condition_range(count-1, sch.get_history_length(), 'p')
              .set_learner_id(a_id)
              .predict();
      cdbg << "t_id " << t_id << endl;
    }
    else if (a_id == SWAP_REDUCE_LEFT)
    { uint32_t gold_label = gold_tags[stack[stack.size()-2]];
      t_id = P.set_tag((ptag) count)
              .set_input(*(data->ex))
              .set_oracle(gold_label)
              .set_allowed(valid_tags)
              .set_condition_range(count-1, sch.get_history_length(), 'p')
              .set_learner_id(a_id)
              .predict();
      cdbg << "t_id " << t_id << endl;
    }

    count++;
    idx = transition_hybrid(sch, a_id, idx, t_id);
  }
  //only root should be left in the stack at this point
  heads[stack.last()] = 0;
  tags[stack.last()] = (uint64_t)data->amr_root_label;
  sch.loss((gold_heads[stack.last()] != heads[stack.last()]));
  if (sch.output().good())
    for(size_t i=1; i<=n; i++)
      sch.output() << (heads[i])<<":"<<tags[i]<<":"<<concepts[i]<<endl;
      //sch.output() << (heads[i])<<tags[i]<<concepts[i]<<endl;
}
}
