SHELL=/bin/bash
VW=/fs/clip-amr/vowpal_wabbit/vowpalwabbit/vw

train_data=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/amr-release-1.0-training-full
test_data=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-test-full/amr-release-1.0-test-full
concepts_dict=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/concepts.p
relations_dict=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/relations.p
span_concepts_dict=/fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/span_concept_dict
scripts_dir=/fs/clip-amr/vowpal_wabbit/demo/amrparsing
smatch_dir=/fs/clip-amr/smatch_2.0

.SECONDARY:

all:
	@cat README.md
clean:
	rm -f $(train_data).model $(test_data).pred $(train_data).cache  $(train_data)*.writing

amr.model: $(train_data).vw
	@$(VW) --search 124 --search_task amr_parser --amr_num_label 124 --amr_dictionary $(span_concepts_dict) -d $(train_data).vw --search_rollin ref --search_rollout none -k -c --passes 1 --holdout_off --search_no_caching -b 25 --search_alpha 1e-5 --search_history_length 3  -f $(train_data).model

amr.test.predictions: $(test_data).vw amr.model
	@$(VW) -d $(test_data).vw -t --amr_dictionary $(span_concepts_dict) -i $(train_data).model -p $(test_data).pred
 
amr.test.parse: amr.test.predictions 
	python $(scripts_dir)/vw_pred_to_amr.py $(test_data).pred $(concepts_dict) $(relations_dict) $(test_data).pred.amr

amr.perf: amr.test.parse
	python $(smatch_dir)/smatch.py -f $(test_data).aligned $(test_data).pred.amr --pr

.PHONY: all clean
