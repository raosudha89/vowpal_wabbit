#Example of projective amr + dep

vowpalwabbit/vw --search 40 --search_task dep_parser,amr_parser -k -c -d demo/multiparsing/train_p.vw --passes 100  --search_rollin oracle --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 8 --amr_root_label 1 --num_label 12 --amr_num_label 8 --amr_num_concept 40 --nn 10 --multitask -f demo/multiparsing/train_p.model

vowpalwabbit/vw -i demo/multiparsing/train_p.model -t -d demo/multiparsing/train_p.vw -p demo/multiparsing/train_p.pred

#Example of non-projective amr + dep

vowpalwabbit/vw --search 40 --search_task dep_parser,amr_parser -k -c -d demo/multiparsing/train_np.vw --passes 100  --search_rollin oracle --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 8 --amr_root_label 1 --num_label 12 --amr_num_label 8 --amr_num_concept 40 --nn 10 --multitask -f demo/multiparsing/train_np.model

vowpalwabbit/vw -i demo/multiparsing/train_np.model -t -d demo/multiparsing/train_np.vw -p demo/multiparsing/train_np.pred 


