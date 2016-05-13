vowpalwabbit/vw --passes 100 -d demo/amrparsing/train_np.vw -k -c --search_rollin mix_per_roll --search_task amr_parser --search 12 --search_alpha 1e-5  --search_rollout oracle  --holdout_off --search_history_length 3 --search_no_caching -b 30 --root_label 1 --num_label 7 -f train_np.model

vowpalwabbit/vw -i train_np.model -t -d demo/amrparsing/train_np.vw -p demo/amrparsing/train_np.pred
