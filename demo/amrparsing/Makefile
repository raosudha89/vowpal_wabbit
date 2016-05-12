SHELL=/bin/bash
VW=../../vowpalwabbit/vw
python_exe=python2.7

train_data=train
test_data=test
concepts=concepts
relations=relations

.SECONDARY:

all:
	@cat README.md
clean:
	rm -f *.model *.predictions *.parse *.vw *.cache  *~ *.writing

%.check:
	@test -x "$$(which $*)" || {				\
	  echo "ERROR: you need to install $*" 1>&2;		\
	  exit 1;						\
	}

%.vw: 
	@echo "preprocessing amr parse data ..." 1>&2
	@echo "Note that due to the licence issue, we only provide a subset of the corpus" 1>&2
	@$(python_exe) parse_data.py $(train_data) $(train_data).vw
	@$(python_exe) parse_data.py $(test_data) $(test_data).vw

amr.model: $(train_data).vw
	@$(VW) --passes 3 -d $< -k -c --search_rollin mix_per_roll --search_task amr_parser --search 4 --search_alpha 1e-5  --search_rollout oracle  --holdout_off -f $@ --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 4 --nn 5 --ftrl

amr.test.predictions: $(test_data).vw amr.model
	@$(VW) -d $< -t $(search_option) -i amr.model -p $@

amr.test.parse: amr.test.predictions
	@$(python_exe) parse_test_result.py $(test_data) $<  $(tag) > $@

amr.perf: amr.test.parse
	@$(python_exe) evaluate.py amr.test.parse $(test_data)

.PHONY: all clean
