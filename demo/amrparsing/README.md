#Example of a projective case

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_p.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 8 -f demo/amrparsing/train_p.model

vowpalwabbit/vw -i demo/amrparsing/train_p.model -t -d demo/amrparsing/train_p.vw -p demo/amrparsing/train_p.pred

#Example of a projective case with null concepts

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_p_null.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 8 -f demo/amrparsing/train_p_null.model

vowpalwabbit/vw -i demo/amrparsing/train_p_null.model -t -d demo/amrparsing/train_p_null.vw -p demo/amrparsing/train_p_null.pred

#Example of a non-projective case achievable using our SWAP actions

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_np.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 8 -f demo/amrparsing/train_np.model

vowpalwabbit/vw -i demo/amrparsing/train_np.model -t -d demo/amrparsing/train_np.vw -p demo/amrparsing/train_np.pred

#Example of a non-projective case not completely achievable using our SWAP actions

vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_np_x.vw -k -c --search_rollin oracle --search_task amr_parser --search 40 --search_alpha 1e-5  --search_rollout none  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 8 -f demo/amrparsing/train_np_x.model

vowpalwabbit/vw -i demo/amrparsing/train_np_x.model -t -d demo/amrparsing/train_np_x.vw -p demo/amrparsing/train_np_x.pred
