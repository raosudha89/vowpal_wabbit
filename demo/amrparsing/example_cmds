#Example of a projective case

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_p.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 9 --amr_num_concept 40 -f demo/amrparsing/train_p.model

vowpalwabbit/vw -i demo/amrparsing/train_p.model -t -d demo/amrparsing/train_p.vw -p demo/amrparsing/train_p.pred

#Example of a projective case with null concepts

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_p_null.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 9 --amr_num_concept 40 -f demo/amrparsing/train_p_null.model

vowpalwabbit/vw -i demo/amrparsing/train_p_null.model -t -d demo/amrparsing/train_p_null.vw -p demo/amrparsing/train_p_null.pred

#Example of a non-projective case achievable using our SWAP actions

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_np.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 9 --amr_num_concept 40 -f demo/amrparsing/train_np.model

vowpalwabbit/vw -i demo/amrparsing/train_np.model -t -d demo/amrparsing/train_np.vw -p demo/amrparsing/train_np.pred

#Example of a non-projective case not completely achievable using our SWAP actions

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_np_x.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 9 --amr_num_concept 40 -f demo/amrparsing/train_np_x.model

vowpalwabbit/vw -i demo/amrparsing/train_np_x.model -t -d demo/amrparsing/train_np_x.vw -p demo/amrparsing/train_np_x.pred

#Example of a simple hallucination case
vowpalwabbit/vw --passes 16 -d demo/amrparsing/train_h.vw -k -c --search_rollin oracle --search_task amr_parser --search 50 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 20 --amr_num_concept 50 -f demo/amrparsing/train_h.model

vowpalwabbit/vw -i demo/amrparsing/train_h.model -t -d demo/amrparsing/train_h.vw -p demo/amrparsing/train_h.pred

#Example of a longer hallucination case
vowpalwabbit/vw --passes 16 -d demo/amrparsing/train_h_2.vw -k -c --search_rollin oracle --search_task amr_parser --search 50 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 20 --amr_num_concept 50 -f demo/amrparsing/train_h_2.model

vowpalwabbit/vw -i demo/amrparsing/train_h_2.model -t -d demo/amrparsing/train_h_2.vw -p demo/amrparsing/train_h_2.pred

#Example of hallucination + non-projective case
vowpalwabbit/vw --passes 16 -d demo/amrparsing/train_h_np.vw -k -c --search_rollin oracle --search_task amr_parser --search 50 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --amr_root_label 1 --amr_num_label 20 --amr_num_concept 50 -f demo/amrparsing/train_h_np.model

vowpalwabbit/vw -i demo/amrparsing/train_h_np.model -t -d demo/amrparsing/train_h_np.vw -p demo/amrparsing/train_h_np.pred

#Cmd to run with span concept dictionary
vowpalwabbit/vw --search 50 --search_task amr_parser --amr_dictionary demo/amrparsing/amr_hallucinate.dict  -d demo/amrparsing/amr_hallucinate.vw --search_rollin ref --search_rollout none -k -c --passes 10 --holdout_off --search_wide_output

vowpalwabbit/vw -i demo/amrparsing/amr_hallucinate.model --amr_dictionary demo/amrparsing/amr_hallucinate.dict -t -d demo/amrparsing/amr_hallucinate.vw -p demo/amrparsing/amr_hallucinate.pred
