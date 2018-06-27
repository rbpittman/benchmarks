#!/bin/bash
nvprof --unified-memory-profiling off --metrics dram_read_throughput python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=1 --model=resnet50 --data_dir=/home/rapittma/imagenet/tf_records
