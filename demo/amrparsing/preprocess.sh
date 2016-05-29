#!/bin/bash

#PBS -S /bin/sh
#PBS -M raosudha@cs.umd.edu
#PBS -N part_1_force
#PBS -l pmem=5gb
#PBS -m abe
#PBS -q batch
#PBS -l walltime=12:00:00

source /fs/clip-amr/testENV/bin/activate
cd /fs/clip-amr/vowpal_wabbit/demo/amrparsing

python amr_reader.py data/amr-release-1.0-training-full/amr-release-1.0-training-full.aligned data/amr-release-1.0-training-full/amr-release-1.0-training-full.amr_nx_graphs.p > data/amr-release-1.0-training-full/amr-release-1.0-training-full.amr_nx_graphs

python aggregate_sentence_metadata.py data/amr-release-1.0-training-full/amr-release-1.0-training-full.aligned data/amr-release-1.0-training-full/amr-release-1.0-training-full.sentences data/amr-release-1.0-training-full/amr-release-1.0-training-full.pos data/amr-release-1.0-training-full/amr-release-1.0-training-full.ner data/amr-release-1.0-training-full/amr-release-1.0-training-full.parse data/amr-release-1.0-training-full/amr-release-1.0-training-full

python amr_nx_to_vw.py data/amr-release-1.0-training-full/amr-release-1.0-training-full.amr_nx_graphs.p data/amr-release-1.0-training-full/amr-release-1.0-training-full.amr_aggregated_metadata.p data/amr-release-1.0-training-full/amr-release-1.0-training-full.vw data/amr-release-1.0-training-full/concepts.p data/amr-release-1.0-training-full/relations.p data/amr-release-1.0-training-full/span_concept_dict

python amr_reader.py data/amr-release-1.0-test-full/amr-release-1.0-test-full.aligned data/amr-release-1.0-test-full/amr-release-1.0-test-full.amr_nx_graphs.p > amr-release-1.0-test-proxy.amr_nx_graphs

python aggregate_sentence_metadata.py data/amr-release-1.0-test-full/amr-release-1.0-test-full.aligned data/amr-release-1.0-test-full/amr-release-1.0-test-full.sentences data/amr-release-1.0-test-full/amr-release-1.0-test-full.pos data/amr-release-1.0-test-full/amr-release-1.0-test-full.ner data/amr-release-1.0-test-full/amr-release-1.0-test-full.parse data/amr-release-1.0-test-full/amr-release-1.0-test-full

python amr_nx_to_vw.py data/amr-release-1.0-test-full/amr-release-1.0-test-full.amr_nx_graphs.p data/amr-release-1.0-test-full/amr-release-1.0-test-full.amr_aggregated_metadata.p data/amr-release-1.0-test-full/amr-release-1.0-test-full.vw data/amr-release-1.0-test-full/concepts.p data/amr-release-1.0-test-full/relations.p data/amr-release-1.0-test-full/span_concept_dict
