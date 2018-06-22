#!/bin/bash
python tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=1 --batch_size=32 --model=resnet50 --allow_growth=1 --num_batches=200
