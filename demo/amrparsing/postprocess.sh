python vw_pred_to_amr.py data/amr-release-1.0-training-full/amr-release-1.0-training-full.oracle.pred data/amr-release-1.0-training-full/concepts.p data/amr-release-1.0-training-full/relations.p data/amr-release-1.0-training-full/amr-release-1.0-training-full.oracle.pred.amr 

python smatch.py -f /fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/amr-release-1.0-training-full.aligned /fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-training-full/amr-release-1.0-training-full.oracle.pred.amr --pr

python vw_pred_to_amr.py data/amr-release-1.0-test-full/amr-release-1.0-test-full.oracle.pred data/amr-release-1.0-test-full/concepts.p data/amr-release-1.0-test-full/relations.p data/amr-release-1.0-test-full/amr-release-1.0-test-full.oracle.pred.amr

python smatch.py -f /fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-test-full/amr-release-1.0-test-full.aligned /fs/clip-amr/vowpal_wabbit/demo/amrparsing/data/amr-release-1.0-test-full/amr-release-1.0-test-full.oracle.pred.amr --pr
