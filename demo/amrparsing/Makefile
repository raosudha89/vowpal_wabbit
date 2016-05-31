SHELL=/bin/bash
VW=/fs/clip-amr/vowpal_wabbit/vowpalwabbit/vw

data_dir=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data
train_data=$(data_dir)/amr-release-1.0-training-full/amr-release-1.0-training-full
test_data=$(data_dir)/amr-release-1.0-test-full/amr-release-1.0-test-full
concepts_dict=$(data_dir)/amr-release-1.0-training-full/concepts.p
relations_dict=$(data_dir)/amr-release-1.0-training-full/relations.p
span_concepts_dict=$(data_dir)/amr-release-1.0-training-full/span_concept_dict
scripts_dir=/fs/clip-amr/vowpal_wabbit/demo/amrparsing
smatch_dir=/fs/clip-amr/smatch_2.0

ifeq ($(INPASS), True)
  INPASS = --inpass
endif

ifeq ($(MULTITASK), True)
  MULTITASK = --multitask
endif

ifeq ($(NN_UNITS),)
  NN_UNITS = 0
endif
.SECONDARY:

all:
	@cat README.md
clean:
	rm -f $(train_data).model $(test_data).pred $(train_data).*.cache  $(train_data)*.writing

amr.model: $(train_data).vw
	@$(VW) --search 118 --search_task amr_parser --amr_num_label 118 --amr_dictionary $(span_concepts_dict) -d $(train_data).vw --search_rollin $(ROLLIN) --search_rollout $(ROLLOUT) -k --cache_file $(train_data).$(PASSES).cache --passes $(PASSES) --holdout_off --search_no_caching -b 25 --search_alpha 1e-5 --search_history_length 3  -f $(train_data).$(PASSES).model --ftrl --nn $(NN_UNITS) $(INPASS) $(MULTITASK)

amr.test.predictions: $(test_data).vw amr.model
	@$(VW) -d $(test_data).vw -t --amr_dictionary $(span_concepts_dict) -i $(train_data).$(PASSES).model -p $(test_data).$(PASSES).pred
 
amr.test.parse: amr.test.predictions 
	python $(scripts_dir)/vw_pred_to_amr.py $(test_data).$(PASSES).pred $(concepts_dict) $(relations_dict) $(test_data).$(PASSES).pred.amr

amr.perf: amr.test.parse
	python $(smatch_dir)/smatch.py -f $(test_data).aligned $(test_data).$(PASSES).pred.amr --pr

.PHONY: all clean
