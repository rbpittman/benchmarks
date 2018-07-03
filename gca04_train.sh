#!/bin/bash
#nvprof --unified-memory-profiling off --metrics dram_read_throughput
MODEL=resnet50
BS=16
python tf_cnn_benchmarks.py --num_gpus=2 --batch_size=${BS} --model=${MODEL} --data_dir=/home/rapittma/imagenet/tf_records --summary_verbosity=0 --train_dir=temp_train_dir --trace_file=trace_${MODEL}_${BS}.json
