/*
Copyright (c) by respective owners including Yahoo!, Microsoft, and
individual contributors. All rights reserved.  Released under a BSD (revised)
license as described in the file LICENSE.
 */
#include "search_test_ldfnonldf.h"
#include "vw.h"

namespace TestLDFNonLDFTask
{
Search::search_task task = { "ldfnonldf", run, initialize, finish, nullptr, nullptr };
namespace CS=COST_SENSITIVE;
struct task_data
{ example* ldf_examples;
  size_t   num_actions;
};
  
void initialize(Search::search& sch, size_t& num_actions, po::variables_map& /*vm*/)
{ sch.set_options( Search::AUTO_CONDITION_FEATURES  |    // automatically add history features to our examples, please
                   Search::AUTO_HAMMING_LOSS        |    // please just use hamming loss on individual predictions -- we won't declare loss
                   Search::EXAMPLES_DONT_CHANGE     |    // we don't do any internal example munging
                   Search::IS_MIXED_LDF             |    // we have multiple learners, some are ldf
                   0);
  //sch.set_num_learners(2);  // 0 will be non-ldf, 1 will be ldf
  vector<bool> is_ldf_vec;
  is_ldf_vec.push_back(false);
  is_ldf_vec.push_back(true);
  sch.set_num_learners(is_ldf_vec);

  CS::wclass default_wclass = { 0., 0, 0., 0. };
  example* ldf_examples = VW::alloc_examples(sizeof(CS::label), num_actions);
  for (size_t a=0; a<num_actions; a++)
  { CS::label& lab = ldf_examples[a].l.cs;
    CS::cs_label.default_label(&lab);
    lab.costs.push_back(default_wclass);
  }

  task_data* data = &calloc_or_throw<task_data>();
  data->ldf_examples = ldf_examples;
  data->num_actions  = num_actions;
  sch.set_task_data<task_data>(data);
}

void finish(Search::search& sch)
{ task_data *data = sch.get_task_data<task_data>();
  for (size_t a=0; a<data->num_actions; a++)
    VW::dealloc_example(CS::cs_label.delete_label, data->ldf_examples[a]);
  free(data->ldf_examples);
  free(data);
}

// this is totally bogus for the example -- you'd never actually do this!
void my_update_example_indicies(Search::search& sch, bool audit, example* ec, uint64_t mult_amount, uint64_t plus_amount)
{ size_t ss = sch.get_stride_shift();
  for (features& fs : *ec)
    for (feature_index& idx : fs.indicies)
      idx = (((idx >> ss) * mult_amount) + plus_amount) << ss;
}
  
void run(Search::search& sch, vector<example*>& ec)
{ task_data *data = sch.get_task_data<task_data>();
  Search::predictor P(sch, (ptag)0);

  for (ptag i=0; i<ec.size(); i++)
  {
    // on even examples, do non-ldf; on odd examples, do ldf
    action prediction;
    action oracle = ec[i]->l.multi.label;
    if ((i % 2) == 0)
      prediction = P.set_learner_id(0).set_tag((ptag)i+1).set_input(*ec[i]).set_oracle(oracle).set_condition_range((ptag)i, sch.get_history_length(), 'p').predict();
    else
    { // ldf

      for (size_t a=0; a<data->num_actions; a++)
      { if (true || sch.predictNeedsExample())   // we can skip this work if `predict` won't actually use the example data
        { VW::copy_example_data(false, &data->ldf_examples[a], ec[i]);  // copy but leave label alone!
          // now, offset it appropriately for the action id
          my_update_example_indicies(sch, true, &data->ldf_examples[a], 28904713, 4832917 * (uint64_t)a);
        }

        // regardless of whether the example is needed or not, the class info is needed
        CS::label& lab = data->ldf_examples[a].l.cs;
        // need to tell search what the action id is, so that it can add history features correctly!
        lab.costs[0].x = 0.;
        lab.costs[0].class_index = (uint64_t)a+1;
        lab.costs[0].partial_prediction = 0.;
        lab.costs[0].wap_value = 0.;
      }

      action pred_id = P.set_learner_id(1).set_tag((ptag)(i+1)).set_input(data->ldf_examples, data->num_actions).set_oracle(oracle-1).set_condition_range(i, sch.get_history_length(), 'p').predict();
      prediction = pred_id+1;  // or ldf_examples[pred_id]->ld.costs[0].weight_index
    }

    if (sch.output().good())
      sch.output() << sch.pretty_label((uint32_t)prediction) << ' ';
  }
}
}

