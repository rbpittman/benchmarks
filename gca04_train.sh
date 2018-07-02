#!/bin/bash
#nvprof --unified-memory-profiling off --metrics dram_read_throughput
python tf_cnn_benchmarks.py --num_gpus=2 --batch_size=16 --model=resnet152_v2 --data_dir=/home/rapittma/imagenet/tf_records
